import json
from .util import custom_list

def j2c(d):
    if d is not None:
        item = json.loads(d)
        return ", ".join(item)
    else:
        return ""

def csv_to_list(csv):
    value_list = csv.split(',')
    return [value.strip() for value in value_list]

# (field_name, load_function, column)
_ = lambda x: x
requested_fields = [
    ("character", _, "characters.character"),
    #("stroke_count", _, None),
    ("onyomi", j2c, None),
    ("kunyomi", j2c, None),
    ("nanori", j2c, None),
    ("meanings", j2c, None),
    ("frequency_rank", _, None),
    #("grade", _, None),
    #("jlpt", _, None),
    ("kanken", _, None),
    ("primitives", _, None),
    ("primitive_of", _, None),
    ("primitive_keywords", j2c, None),
    ("primitive_alternatives", _, None),
    #("heisig_id5", _, None),
    #("heisig_id6", _, None),
    ("heisig_keyword5", _, None),
    ("heisig_keyword6", _, None),
    ("heisig_story", _, None),
    ("heisig_comment", _, None),
    ("radicals", _, None),
    #("words_default", _, None),
    ("koohi_stories", j2c, None),
    #("wk", _, None),
    ("usr_keyword", _, "usr.keywords.usr_keyword"),
    ("usr_primitive_keyword", _, "usr.keywords.usr_primitive_keyword"),
    ("usr_story", _, "usr.stories.usr_story"),
]

sql_fields = ",".join((rf[2] if rf[2] else rf[0]) for rf in requested_fields)

joins = [
    f"LEFT OUTER JOIN usr.keywords ON characters.character == usr.keywords.character ",
    f"LEFT OUTER JOIN usr.stories ON characters.character == usr.stories.character ",
]
sql_joins_txt = "".join(joins)

# This conversion table links radicals to their Heisig primitive counterpart to allow 
# for better search capability. Few of them have identical visual look but differ 
# only in Unicode.
radical_conversion_table = {
    'ノ' : '丿',
    '｜' : '丨',
    '⺅' : '亻',
    '⺾' : '艹',
    '爿' : '丬',
    '辶' : '辶',
}

# When two characters reference each other as alternatives (for example 艹 -> 艸 and 艸 -> 艹 )
# then we want to link to the character which is the primary primitive.
primary_primitives = ['艹','扌','⻖','⻏','川','罒','冫','月']

class SearchEngine:

    def __init__(self, db_cursor):
        self.crs = db_cursor
        self.keyword_set_cache = dict()
        self.keyword_cache = dict()
        self.radical_set_cache = dict()
        self.radical_name_set_cache = dict()
        self.radical_name_cache = dict()
        self.primitive_list_cache = dict()
        self.rec_primitive_list_cache = dict()
        self.rec_primitive_name_list_cache = dict()
        self.rec_primitive_name_cache = dict()
        self.reading_set_cache = dict()
        self.reading_cache = dict()
        self.meaning_set_cache = dict()
        self.meaning_cache = dict()
        self.stories_cache = dict()
        self.primitive_alternative_cache = dict()
        self.frequency_points = dict()

        self.init_cache()

    def radical_to_primitive(self,r):
        # First do unicode conversion because some radicals in the list might use slightly
        # # different (albeit visually indistinguishable) unicode character.
        if r in radical_conversion_table:
            r = radical_conversion_table[r]
        # .. then reference the main primitive instead if this is an alternative primitive
        if r not in primary_primitives and r in self.primitive_alternative_cache:
            r = self.primitive_alternative_cache[r]
        return r

    def recursively_find_all_primitives(self, character):
        if character not in self.primitive_list_cache:
            return [character]
        primitives = self.primitive_list_cache[character] or list()
        if len(primitives) == 1 and character in primitives:
            # skip all the primitives that have only themselves listed as primitives
            return [character]
        found_primitives = primitives.copy()
        # recursively find all primitives
        for p in primitives:
            if p != character:
                new_primitives = self.recursively_find_all_primitives(p)
                for np in new_primitives:
                    if np not in found_primitives:
                        found_primitives.append(np)
        return found_primitives

    def update_recursive_primitive_cache(self,character):
        rec_primitive_list = self.recursively_find_all_primitives(character)
        if len(rec_primitive_list) > 0:
            rec_primitive_names_list = list()
            for p in rec_primitive_list:
                if p in self.keyword_set_cache:
                    kw_set = self.keyword_set_cache[p]
                    for kw in kw_set:
                        rec_primitive_names_list.append(kw)
                else:
                    print("Note! Kanji %s references primitive %s without a keyword" % (character,p))

            rec_primitive_names = ','.join(rec_primitive_names_list)
            self.rec_primitive_list_cache[character] = rec_primitive_list
            self.rec_primitive_name_list_cache[character] = rec_primitive_names_list
            self.rec_primitive_name_cache[character] = rec_primitive_names

    def init_cache(self):
        self.update_cache()

        # By iterating through a radicals list of each kanji,
        # create a cache set of radical names and also a free text cache for partial matching
        for c,radical_set in self.radical_set_cache.items():
            if len(radical_set) > 0:
                radical_names_set = set()
                for r in radical_set:
                    # We want to get keywords from the associated primitive
                    r = self.radical_to_primitive(r)
                    if r in self.keyword_set_cache:
                        radical_names_set.update(self.keyword_set_cache[r])
                radical_names = ','.join(radical_names_set)
                self.radical_name_set_cache[c] = radical_names_set
                self.radical_name_cache[c] = radical_names

        print("Search engine cache initialization complete!")

    # Update cache for a character. If character is None, then update cache for all characters
    def update_cache(self, character=None):

        if character:
            self.crs.execute(
                f"SELECT {sql_fields} FROM characters {sql_joins_txt} WHERE characters.character=?",
                (character,),
            )
        else:
            self.crs.execute(
                f"SELECT {sql_fields} FROM characters {sql_joins_txt} " 
            )

        raw_data = self.crs.fetchall()

        if raw_data:
            for raw_row in raw_data:

                # convert json escaping to comma separated value lists
                d = {}
                for data, (name, load_func, _) in zip(raw_row, requested_fields):
                    d[name] = load_func(data) or ''

                c = d['character']

                # create a bunch of caches: sets of values for exact matching and then string
                # representation for partial matching

                # Keywords..
                kw_set= set()
                kw_set.add(d['heisig_keyword5'])
                kw_set.add(d['heisig_keyword6'])
                kw_set.add(d['usr_keyword'].lower())
                kw_set.update(csv_to_list(d['primitive_keywords'].lower()))
                kw_set.update(csv_to_list(d['usr_primitive_keyword'].lower()))
                if '' in kw_set:
                    kw_set.remove('')
                if len(kw_set)>0:
                    keywords = ','.join(list(kw_set))
                    self.keyword_cache[c] = keywords
                    self.keyword_set_cache[c] = kw_set

                # Primitives..
                if len(d['primitives'])>0:
                    self.primitive_list_cache[c] = custom_list(d['primitives'])

                # Radicals..
                if len(d['radicals'])>0:
                    self.radical_set_cache[c] = set(custom_list(d['radicals']))

                # Readings..
                reading_set= set()
                reading_set.update(csv_to_list(d['onyomi']))
                reading_set.update(csv_to_list(d['kunyomi']))
                reading_set.update(csv_to_list(d['nanori']))
                if '' in reading_set:
                    reading_set.remove('')
                if len(reading_set)>0:
                    readings = ','.join(list(reading_set))
                    self.reading_cache[c] = readings
                    self.reading_set_cache[c] = reading_set

                # Meanings..
                meaning_set= set()
                meaning_set.update(csv_to_list(d['meanings']))
                if '' in meaning_set:
                    meaning_set.remove('')
                if len(meaning_set)>0:
                    self.meaning_cache[c] = d['meanings']
                    self.meaning_set_cache[c] = meaning_set

                # Stories..
                st = d['usr_story'].lower() + d['koohi_stories'].lower()             
                st += d['heisig_story'].lower()
                st += d['heisig_comment'].lower()
                self.stories_cache[c] = st

                # Frequency ranking points: Prioritize high frequency (and higher Kanken grade) kanjis.
                points = 0
                if d['frequency_rank'] is not None and d['frequency_rank'] != '':
                    fr_points = (4000 - d['frequency_rank'])/400
                    if fr_points <= 0:
                        fr_points = 0
                    points += fr_points
                if d['kanken'] is not None and d['kanken'] != '':
                    points += 11 - float(d['kanken'])
                if points > 0:
                    self.frequency_points[c] = points

                # create a reverse lookup table for primitive alternatives
                if len(d['primitive_alternatives']) > 0:
                    prim_alt_list = custom_list(d['primitive_alternatives'])
                    for p in prim_alt_list:
                        self.primitive_alternative_cache[p] = c

        # Recursively iterate through a primitives list of each kanji
        # (i.e. create a list of primitives the kanji uses, down to the basic building blocks)
        # With this list create a cache set of primitives, their names and also a free text cache for partial matching
        if not character:
            for c in self.primitive_list_cache.keys():
                self.update_recursive_primitive_cache(c)
        else:
            if character in self.primitive_list_cache.keys():
                self.update_recursive_primitive_cache(c)


    def get_matching_characters(self, search_terms, pool, is_a_set, results, max_results):
        for search_term,required_count in search_terms.items():
            if is_a_set and required_count>1:
                # we want more than 1 occurence but this is a set -> not found
                return results

        for character, data in pool.items():
            found = True
            for search_term,required_count in search_terms.items():
                if required_count>1:
                    if data.count(search_term) < required_count:
                        found = False
                else:
                    if search_term not in data and character != search_term:
                        found = False
            if found:
                if character not in results:
                    results.append(character)
                if len(results)>=max_results:
                    return results
        return results


    def get_matching_characters_with_scoring(self, search_terms, pool, is_a_set, pool_priority, kanji_scores, kanji_matches):
        for search_term,required_count in search_terms.items():
            if is_a_set and required_count>1:
                # we want more than 1 occurence but this is a set -> not found
                return

        for character, data in pool.items():
            for search_term, required_count in search_terms.items():
                found = False
                if required_count>1:
                    if data.count(search_term) >= required_count:
                        found = True
                else:
                    if search_term in data or character == search_term:
                        found = True

                if found:
                    if character in kanji_scores:
                        kanji_scores[character] += pool_priority
                        kanji_matches[character].add(search_term)
                    else:
                        kanji_scores[character] = pool_priority
                        kanji_matches[character] = {search_term}
                    if character in self.frequency_points:
                        kanji_scores[character] += self.frequency_points[character]


    def get_matching_characters_from_list_of_pools(self, search_terms, pool_list, max_results):

        if len(search_terms) == 1:
            # In the case of only one search term its a matter of simple exhaustive search
            # until enough matches are found. Search crams through all search pools 
            # (keywords, primitive names, free text search) starting
            # from the most prioritized one
            results = []
            for pool_priority, pool, is_a_set in pool_list:
                self.get_matching_characters(search_terms, pool, is_a_set, results, max_results)
                if len(results)>=max_results:
                    return results
            return results

        else:
            # In the case of many search terms it's a bit trickier. We want to give each kanji
            # points - the higher points the more matched search terms in high priority pools
            kanji_scores = dict()   # score for each kanji
            kanji_matches = dict() # how many search terms were matched

            for pool_priority, pool, is_a_set in pool_list:
                self.get_matching_characters_with_scoring(search_terms, pool, is_a_set, pool_priority, kanji_scores, kanji_matches)

            # remove those kanjis that didn't match all the search terms
            for kanji, matched_search_terms in kanji_matches.items():
                if len(matched_search_terms) < len(search_terms):
                    kanji_scores.pop(kanji)

            # return only the matching kanjis with highest scoring
            sorted_kanji_scores = sorted(kanji_scores.items(), key=lambda x:x[1], reverse=True)
            sorted_kanji_scores = list(dict(sorted_kanji_scores).keys())
            if len(sorted_kanji_scores) > max_results:
                return sorted_kanji_scores[:max_results]
            
            return sorted_kanji_scores


    def search(self, search_str, max_results=15):

        if search_str == '':
            return []

        # clean up search terms
        search_terms_list = search_str.split(',')
        if '' in search_terms_list:
            search_terms_list.remove('')
        search_terms_list = [x.strip() for x in search_terms_list]

        # check if a required occurrence multiplier for the search term is given..
        search_terms_dict = dict()
        for term in search_terms_list:
            if '*' in term:
                elements = term.split('*')
                if len(elements)==2:
                    try:
                        elements = [x.strip() for x in elements]
                        if elements[0].isdigit():
                            search_terms_dict[elements[1]] = int(elements[0])
                        elif elements[1].isdigit():
                            search_terms_dict[elements[0]] = int(elements[1])
                    except:
                        # incomplete/invalid search term
                        pass
            else:
                if term in search_terms_dict:
                    search_terms_dict[term] += 1
                else:
                    search_terms_dict[term] = 1
                
        # A list of search pools, each having a distinct priority
        priority_list = [
            # [ priority, pool, the_pool_is_a_set ]
            [30,self.keyword_set_cache,True],
            [26,self.keyword_cache,False],
            [20,self.rec_primitive_list_cache,False], 
            [18,self.rec_primitive_name_list_cache,False],
            [16,self.rec_primitive_name_cache,False],
            [14,self.meaning_set_cache,True],
            [12,self.meaning_cache,False],
            [10,self.stories_cache,False],
            [8,self.radical_set_cache,True],
            [7,self.radical_name_set_cache,True],
            [6,self.radical_name_cache,False],
            [5,self.reading_set_cache,True],
            [4,self.reading_cache,False],
        ]

        results = self.get_matching_characters_from_list_of_pools(search_terms_dict, priority_list, max_results)

        return list(results)