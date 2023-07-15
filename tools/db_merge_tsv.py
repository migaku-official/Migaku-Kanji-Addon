import sqlite3
import json
import sys
import os
import re

# Creates a list of single-character Unicode kanjis and [primitive] tags
# For example '[banner]也' -> ['\[banner\]','也'] 
def custom_list(l):
    g = re.findall(r'([^\[]|\[.+\])',l)
    return g

ext_tsv_path = sys.argv[1] if len(sys.argv) > 1 else "kanji-ext.tsv"
db_path = sys.argv[2] if len(sys.argv) > 2 else "kanji.db"

db_path = os.path.abspath(db_path)

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

def to_json_list_str(d):
    if d!= '':
        return json.dumps(d.replace(' ','').split(','))
    return '[]'

def to_list_str(d):
    if d!= '':
        return str( d.replace(' ','').split(',') )
    return '[]'

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
    (9,"radicals", to_list_str, None),
]


for l in open(ext_tsv_path, "r", encoding="utf-8"):
    d = l.replace("\n", "").split("\t")
    if d[0] == 'Kanji':  # omit the header
        continue

    if len(d) != 10:
        print("Error! Wrong length in data: ",d)
        continue

    kanji = d[0].strip()

    print("Processing", kanji)

    # Check if card already exists for character
    crs.execute(
        f'SELECT {",".join(fields)} FROM characters WHERE character == (?)',
        (kanji,),
    )

    res = crs.fetchall()
    if len(res) > 0:

        old = list(res[0])
        converted_d = d

        for data, (idx, name, load_func, _) in zip(d, field_conversion):
            converted_d[idx] = load_func(data)
        if old != converted_d:

            print("Old card: ",old)
            print("Updated card: ", converted_d)
            update_d = converted_d[1:] + [converted_d[0]]
            crs.execute(update_sql, update_d)
            con.commit()

    else:
        converted_d = d
        for data, (idx, name, load_func, _) in zip(d, field_conversion):
            converted_d[idx] = load_func(data)
        print("New card: ", converted_d)

        crs.execute(insert_sql, converted_d)
        con.commit()


##################################################################
print("Reconstructing primitive_of lists..")

crs.execute("SELECT * FROM characters")
data = crs.fetchall()

column_names = [description[0] for description in crs.description]
print("kanji.db column names:", column_names)

poi = column_names.index('primitive_of')
pi = column_names.index('primitives')
ci = column_names.index('character')
ri = column_names.index('radicals')
fi = column_names.index('frequency_rank') 



########################## EXPERIMENTAL STUFF ############
# Keeping this setting on will allow radicals to reference their usage in kanji via primitive_of list
# instead of restricting it to more complex primitives. 
# For example 施 has a radical list '方ノ一也' and primitive list '[banner]也'. We would like
# to back-reference this from radicals viewpoint so that when viewing the page for kanji 方 we could see 
# that it's used as a component in 施 even though 方 is part of more complex [banner] primitive in that kanji.

# Keeping this disabled for now because it just creates just so new references, 
# which many of them are not very useful. For example 田　refers to all kanjis that have 由 primitive...
regard_also_radicals_as_primitives = False   
# In case the option above is set, we would like to limit this to more common kanjis so that
# list for 人 doesn't get flooded with extra-rare kanjis
radical_reference_frequency_cutoff = 2000
#############################################################

primitive_of_dict = dict()

# Create a lookup table for primitives that are being used by kanjis or other primitives
for row in data:
    character = row[ci]
    primitives = custom_list(row[pi])
    frequency_rank = row[fi]

    for p in primitives:
        if p not in primitive_of_dict:
            primitive_of_dict[p] = ""
        if p != character:
            primitive_of_dict[p] += character

    # Experimental setting, disabled for now..
    if regard_also_radicals_as_primitives and frequency_rank < radical_reference_frequency_cutoff:
        radicals = list(row[ri])
        for r in radicals:
            if r not in primitive_of_dict:
                primitive_of_dict[r] = ""
            if r != character:
                primitive_of_dict[r] += character

# Calculate missing primitive_of references
for row in data:
    character = row[ci]
    orig_primitive_of = custom_list(row[poi])
    orig_primitive_of_set = set(orig_primitive_of)
    if character in primitive_of_dict:
        primitive_of_set = set(custom_list(primitive_of_dict[character]))
    else:
        primitive_of_set = set()

    if primitive_of_set != orig_primitive_of_set:
        print(character,"\t","Existing refs:",len(orig_primitive_of_set),
              "Missing from updated list:",orig_primitive_of_set - primitive_of_set,
              "Missing from existing list:",primitive_of_set-orig_primitive_of_set) 

        if primitive_of_set > orig_primitive_of_set:
            #print(*row)
            new_primitive_of_set = primitive_of_set | orig_primitive_of_set
            print("\tUpdated primitives_of:", new_primitive_of_set)
            new_data = [''.join(new_primitive_of_set), character]
            crs.execute(update_prim_of_sql, new_data)

            con.commit()
        else:
            print("\tLet's not remove any references for now..")

con.close()
