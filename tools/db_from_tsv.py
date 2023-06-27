import os
import sqlite3
import sys
import os


tsv_path = sys.argv[1] if len(sys.argv) > 1 else "kanji.tsv"
db_path = sys.argv[2] if len(sys.argv) > 2 else "kanji.db"

db_path = os.path.abspath(db_path)


try:
    os.remove(db_path)
except:
    pass

conn = sqlite3.connect(db_path)


create_sql = """CREATE TABLE characters (
    character TEXT NOT NULL PRIMARY KEY,
    stroke_count INTEGER DEFAULT NULL,
    onyomi TEXT DEFAULT "[]",
    kunyomi TEXT DEFAULT "[]",
    nanori TEXT DEFAULT "[]",
    meanings TEXT DEFAULT "[]",
    frequency_rank INTEGER DEFAULT 999999,
    grade INTEGER DEFAULT NULL,
    jlpt INTEGER DEFAULT NULL,
    kanken INTEGER DEFAULT NULL,
    primitives TEXT DEFAULT "",
    primitive_meanings TEXT DEFAULT "[]",
    primitive_alternatives TEXT DEFAULT "",
    heisig_id5 INTEGER DEFAULT NULL,
    heisig_id6 INTEGER DEFAULT NULL,
    heisig_keyword5 TEXT DEFAULT NULL,
    heisig_keyword6 TEXT DEFAULT NULL,
    heisig_story TEXT DEFAULT NULL,
    heisig_comment TEXT DEFAULT NULL,
    radicals TEXT DEFAULT "",
    words_default TEXT DEFAULT "[]",
    koohi_stories TEXT DEFAULT "[]"
)"""

conn.execute(create_sql)
fields = [l.split()[0] for l in create_sql.split("\n") if l.startswith(" ")]


db_kanji = []

for l in open(tsv_path, "r", encoding="utf-8"):
    d = l.replace("\n", "").split("\t")
    if len(d) != 7:
        continue
    kanji = d[0].strip()
    if len(kanji) != 1:
        continue

insert_sql = (
    f'INSERT into characters ({",".join(fields)}) values ({",".join("?"*len(fields))})'
)
conn.executemany(insert_sql, db_kanji)


conn.commit()
conn.close()
