#
# Merges changed kanjis/primitives listed in kanji-ext.tsv with kanji.db
# Recalculates also primitives-of list
#
import sqlite3
import json
import sys
import os
import re
import logging

# Creates a list of single-character Unicode kanjis and [primitive] tags
# For example '[banner]也' -> ['\[banner\]','也'] 
def custom_list(l):
    g = re.findall(r'([^\[]|\[[^\]]+\])',l)
    return g


# create multi-line string for better readibility in markdown tables
def multiLine(src_list,n):    
    chunks = [src_list[i:i+n] for i in range(0, len(src_list), n)]
    lines = [ ''.join(chunk) for chunk in chunks ]            
    return '<br>'.join(lines)


ext_tsv_path = sys.argv[1] if len(sys.argv) > 1 else "addon/kanji-ext.tsv"
db_path = sys.argv[2] if len(sys.argv) > 2 else "addon/kanji.db"
log_path = sys.argv[3] if len(sys.argv) > 3 else "db_merge_log.md"
db_path = os.path.abspath(db_path)

### set up logging
targets = logging.StreamHandler(sys.stdout), logging.FileHandler(log_path,'w+')
logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=targets)


con = sqlite3.connect(db_path)
#con.row_factory = sqlite3.Row
crs = con.cursor()

fields = [
    "character",
    "meanings",
    "primitive_alternatives",
    "primitives",
    "heisig_keyword5",
    "heisig_keyword6",
    "primitive_keywords",
    "heisig_story",
    "heisig_comment",
    "radicals",
]

update_fields = fields[1:]

insert_sql = (
    f'INSERT OR IGNORE into characters ({",".join(fields)}) values ({",".join("?"*len(fields))})'
)
update_sql = (
    f'UPDATE characters SET {"=? , ".join(update_fields)}=? WHERE character=?'
)
update_prim_of_sql = (
    f'UPDATE characters SET primitive_of=? WHERE character=?'
)

def to_json_list_str(csv):
    if csv!= '':
        item_list = csv.split(',')
        clean_list = [item.strip() for item in item_list]
        return json.dumps(clean_list)
    return '[]'

def j2c(d):
    return ", ".join(json.loads(d))


# (field_name, load_function, column)
_ = lambda x: x
field_conversion = [
    (0,"character", _, None),
    (1,"meanings", to_json_list_str, None),
    (2,"primitive_alternatives", _, None),
    (3,"primitives", _, None),
    (4,"heisig_keyword5", _, None),
    (5,"heisig_keyword6", _, None),
    (6,"primitive_keywords", to_json_list_str, None),
    (7,"heisig_story", _, None),
    (8,"heisig_comment", _, None),
    (9,"radicals", _, None),
]

field_conversion_reverse = [
    (0,"character", _, None),
    (1,"meanings", j2c, None),
    (2,"primitive_alternatives", _, None),
    (3,"primitives", _, None),
    (4,"heisig_keyword5", _, None),
    (5,"heisig_keyword6", _, None),
    (6,"primitive_keywords", j2c, None),
    (7,"heisig_story", _, None),
    (8,"heisig_comment", _, None),
    (9,"radicals", _, None),
]



processed_kanji_list = []
total_changes = 0

for l in open(ext_tsv_path, "r", encoding="utf-8"):
    
    d = l.replace("\n", "").split("\t")
    if len(d[0]) == 0:
        logging.info("")
        continue
    if d[0] == 'Kanji':  # omit the header
        continue
    if d[0][0]=='#':  # only log the comments
        # modify the comments so they look better in markdown
        hash_count = d[0].count('#')
        cleaned_comment = d[0].replace('#', '')
        if hash_count > 5:
            logging.info('----')
            comment = '## ' + cleaned_comment
        elif hash_count > 1:
            comment = '###' + cleaned_comment
        else:
            comment = '####' + cleaned_comment
        logging.info(comment)
        continue

    if len(d) != 10:
        raise Exception("Error! Wrong length in data: %s" % str(d))

    kanji = d[0].strip()

    if kanji in processed_kanji_list:
        raise Exception("Kanji %s already processed! Remove duplicate" % kanji)
    
    processed_kanji_list.append(kanji)

    # create header
    pretty_header = kanji
    if d[4] != '':
        pretty_header += ' ' + d[6]
        if d[6] != '':
            pretty_header += ' / ' + d[6]
    elif d[6] != '':
        pretty_header += ' ' + d[6]
    pretty_header += ' (' + d[1] + ')'

    # Check if card already exists for character
    crs.execute(
        f'SELECT {",".join(fields)} FROM characters WHERE character == (?)',
        (kanji,),
    )

    res = crs.fetchall()
    if len(res) > 0:

        old = list(res[0])

        # old data: create value strings for better readibility
        old_string = dict()
        for data, (idx, name, load_func, _) in zip(old, field_conversion_reverse):
            old_string[idx] = load_func(data)

        # convert data to json format for modifying to database
        converted_d = d.copy()
        for data, (idx, name, load_func, _) in zip(d, field_conversion):
            converted_d[idx] = load_func(data)

        if old != converted_d:

            logging.info('#### ' + pretty_header)

            logging.info("| Field | Old value | New value |" )
            logging.info("|---|---|---|" )

            for (idx, field_name, _, _,) in field_conversion:
                if old[idx] != converted_d[idx] and not (old[idx] is None and converted_d[idx]==''):
                    logging.info("| %s | %s | %s |" % (field_name.ljust(20), old_string[idx], d[idx]))
                    total_changes += 1

            update_d = converted_d[1:] + [converted_d[0]]
            crs.execute(update_sql, update_d)
            con.commit()

    else:
        logging.info("#### %s (NEW ITEM)" % pretty_header)

        logging.info("| Field | Value |" )
        logging.info("|---|---|" )

        # convert data to json format for modifying to database
        converted_d = d.copy()
        for data, (idx, field_name, load_func, _) in zip(d, field_conversion):
            converted_d[idx] = load_func(data)
            logging.info("| %s | %s |" % (field_name, d[idx]))
            total_changes += 1

        crs.execute(insert_sql, converted_d)
        con.commit()

logging.info("Processed %d items with total %d changes" % (len(processed_kanji_list), total_changes))

##################################################################
print("Reconstructing primitive_of lists..")

crs.execute("SELECT * FROM characters")
data = crs.fetchall()

column_names = [description[0] for description in crs.description]
print("kanji.db column names:", column_names)

poi_i = column_names.index('primitive_of')
pi_i = column_names.index('primitives')
ci_i = column_names.index('character')
ri_i = column_names.index('radicals')
fi_i = column_names.index('frequency_rank')
hk_i = column_names.index('heisig_keyword6') 
pk_i = column_names.index('primitive_keywords') 
m_i = column_names.index('meanings') 

primitive_of_dict = dict()

# Create a lookup table for primitives that are being used by kanjis or other primitives
for row in data:
    character = row[ci_i]
    primitives = custom_list(row[pi_i])
    frequency_rank = row[fi_i]

    for p in primitives:
        if p not in primitive_of_dict:
            primitive_of_dict[p] = ""
        if p != character:
            primitive_of_dict[p] += character


# Calculate missing primitive_of references

logging.info("# Changes in primitives-of list")
logging.info("| Kanji | Meaning/Keyword | Added | Removed |")
logging.info("|---|---|---|---|")
for row in data:
    character = row[ci_i]
    orig_primitive_of = custom_list(row[poi_i])
    orig_primitive_of_set = set(orig_primitive_of)
    if character in primitive_of_dict:
        primitive_of_set = set(custom_list(primitive_of_dict[character]))
    else:
        primitive_of_set = set()

    # extract the best representation for the kanji/primitive name
    if row[hk_i] is not None and row[hk_i] != '':
        name = row[hk_i]
    elif row[pk_i] is not None and row[pk_i] != '[]':
        name = j2c(row[pk_i])
    elif row[m_i] is not None and row[m_i] != '[]':
        name = j2c(row[m_i])
    else:
        name = ""

    if primitive_of_set != orig_primitive_of_set:

        added = multiLine(list(primitive_of_set-orig_primitive_of_set),10)
        removed = multiLine(list(orig_primitive_of_set - primitive_of_set),10)
        logging.info('|' + character + " | " + name + " | " + added + " | " + removed + ' |')
        new_primitive_of_set = primitive_of_set
        new_data = [''.join(new_primitive_of_set), character]
        crs.execute(update_prim_of_sql, new_data)

        con.commit()

con.close()
