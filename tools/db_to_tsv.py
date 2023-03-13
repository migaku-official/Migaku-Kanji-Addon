import sqlite3
import json
import sys
import os


db_path = sys.argv[1] if len(sys.argv) > 1 else 'kanji.db'
tsv_path = sys.argv[2] if len(sys.argv) > 2 else 'kanji.tsv'

db_path = os.path.abspath(db_path)

con = sqlite3.connect(db_path)
crs = con.cursor()

crs.execute('SELECT * FROM characters')
data = crs.fetchall()


f = open(tsv_path, 'w', encoding='utf-8')

def fw(*args):
    if '\t' in ''.join(args):
        raise ValueError('TSV ERROR')

    f.write('\t'.join(args))
    f.write('\n')

fw('Kanji', 'Meanings', 'Primitive Alternatives', 'Primitives', 'Heisig Keyword (1-5)', 'Heisig Keyword (6+)', 'Primitive Keywords', 'Heisig Story', 'Heisig Comment', 'Radicals')

def j2c(d):
    return ', '.join(json.loads(d))

for d in data:
    fw(d[0], j2c(d[5]), d[12], d[10], d[15] or '', d[16] or '', j2c(d[11]), d[17] or '', d[18] or '', d[19])

f.close()
