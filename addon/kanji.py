import os
import json
import base64
import sqlite3
from collections import defaultdict, OrderedDict
from threading import RLock

import anki
import aqt

from .util import addon_path, user_path, assure_user_dir, unique_characters, custom_list
from .errors import InvalidStateError, InvalidDeckError
from .card_type import CardType
from . import config
from . import text_parser
from .kanji_confirm_dialog import KanjiConfirmDialog


kanji_db_path = addon_path("kanji.db")
user_db_path = user_path("user.db")


def clean_character_field(f):
    f = f.lstrip()
    f = text_parser.html_regex.sub("", f)
    if len(f):
        # Leave [primitive_tag] as it is, otherwise return the single unicode character
        if f[0] == '[':
            return f
        return f[0]
    return ""

class KanjiDB:
    def __init__(self):
        self.initialize()

    # Open db
    def initialize(self):
        # check_same_thread set to false to allow gui thread updating while stuff is updated
        # only one thread ever accesses the db
        self.con = sqlite3.connect(kanji_db_path, check_same_thread=False)
        self.lock = RLock()

        self.crs = self.con.cursor()
        self.crs.execute("PRAGMA case_sensitive_like=OFF")

        assure_user_dir()
        self.crs.execute(f'ATTACH DATABASE "{user_db_path}" AS usr;')

        for ct in CardType:
            # Negative card id -> manually marked as known
            self.crs.execute(
                f"CREATE TABLE IF NOT EXISTS usr.{ct.label}_card_ids("
                "character TEXT NOT NULL PRIMARY KEY,"
                "card_id INTEGER NOT NULL"
                ")"
            )

        self.crs.execute(
            "CREATE TABLE IF NOT EXISTS usr.words("
            "note_id INTEGER NOT NULL,"
            "word TEXT NOT NULL,"
            'reading TEXT DEFAULT "",'
            "is_new INTEGER DEFAULT 0"
            ")"
        )

        self.crs.execute(
            "CREATE TABLE IF NOT EXISTS usr.keywords("
            "character TEXT NOT NULL PRIMARY KEY,"
            'usr_keyword TEXT DEFAULT "",'
            'usr_primitive_keyword TEXT DEFAULT ""'
            ")"
        )

        self.crs.execute(
            "CREATE TABLE IF NOT EXISTS usr.stories("
            "character TEXT NOT NULL PRIMARY KEY,"
            "usr_story TEXT NOT NULL"
            ")"
        )

        self.con.commit()

        # Updates

        try:
            self.crs.execute(
                "ALTER TABLE usr.words ADD COLUMN is_new INTEGER DEFAULT 0"
            )
            self.con.commit()
        except sqlite3.OperationalError:
            pass

        try:
            self.crs.execute(
                'ALTER TABLE usr.keywords ADD COLUMN usr_primitive_keyword TEXT DEFAULT ""'
            )
            self.con.commit()
        except sqlite3.OperationalError:
            pass

    # Close db
    def shutdown(self):
        self.crs.close()
        self.con.close()

    def crs_execute(self, __sql: str, __parameters=()):
        with self.lock:
            self.crs.execute(__sql, __parameters)

    def crs_execute_and_commit(self, __sql: str, __parameters=()):
        with self.lock:
            self.crs.execute(__sql, __parameters)
            self.con.commit()

    def crs_executemany_and_commit(self, __sql: str, __seq_of_parameters):
        with self.lock:
            self.crs.executemany(__sql, __seq_of_parameters)
            self.con.commit()

    def crs_execute_and_fetch_one(self, __sql: str, __parameters=()):
        with self.lock:
            self.crs.execute(__sql, __parameters)
            r = self.crs.fetchone()
        return r

    def crs_execute_and_fetch_all(self, __sql: str, __parameters=()):
        with self.lock:
            self.crs.execute(__sql, __parameters)
            r = self.crs.fetchall()
        return r

    def reset(self):
        for ct in CardType:
            self.crs_execute(f"DELETE FROM usr.{ct.label}_card_ids")
        self.crs_execute("DELETE FROM usr.words")
        self.crs_execute("DELETE FROM usr.keywords")
        self.crs_execute("DELETE FROM usr.stories")

    def reset_marked_known(self, card_type):
        self.crs_execute(f"DELETE FROM usr.{card_type.label}_card_ids WHERE card_id=-1")

    def reset_custom_keywods(self):
        self.crs_execute("DELETE FROM usr.keywords")

    def reset_custom_stories(self):
        self.crs_execute("DELETE FROM usr.stories")

    def get_related_characters(self, character: str):
        raw_data = self.crs_execute_and_fetch_one(
            f"SELECT primitives, primitive_of FROM characters "
            "WHERE characters.character = (?)",
            (character,),
        )

        if raw_data is None:
            return None
        
        return custom_list(raw_data[0]) + custom_list(raw_data[1])

    # Recursivly finds new characters given a specific character
    def _new_characters_find(self, card_type, character, out, max_characters=-1):
        # Check if max characters already reached
        if max_characters >= 0 and len(out) >= max_characters:
            return

        # Check if character was already handled
        if character in out:
            return

        # Get primitives
        primitives_result = self.crs_execute_and_fetch_one(
            "SELECT primitives FROM characters " "WHERE character == (?)", (character,)
        )

        if primitives_result is None:
            print(f"Lookup of primitive {character} failed.")
            return
        primitives = primitives_result[0]
        primitives = custom_list(primitives)

        # Recusivly add primitives that need to be learned if enabled
        if card_type.add_primitives:
            for p in primitives:
                if p == character:
                    continue
                self._new_characters_find(card_type, p, out, max_characters)

        # Check if max characters already reached
        if max_characters >= 0 and len(out) >= max_characters:
            return

        # Check if card already exists for character
        table = f"usr.{card_type.label}_card_ids"
        r = self.crs_execute_and_fetch_one(
            f"SELECT COUNT(*) FROM {table} "
            "WHERE character == (?) AND card_id NOT NULL",
            (character,),
        )

        if r[0] != 0:
            return

        out.append(character)

    # Recursivley find new characters to learn
    def new_characters(self, card_type, input_data, max_characters=-1):
        if type(input_data) == str:
            input_data = set(input_data)

        ret = []
        for c in input_data:
            self._new_characters_find(card_type, c, ret, max_characters)
        return ret

    def find_next_characters(
        self,
        card_type,
        max_characters,
        column="frequency_rank",
        order="ASC",
        condition=None,
    ):
        table = f"usr.{card_type.label}_card_ids"

        if condition is None:
            condition = ""
        else:
            condition = f"AND {column} {condition} "

        r = self.crs_execute_and_fetch_all(
            "SELECT characters.character FROM characters "
            f"LEFT OUTER JOIN {table} ON characters.character == {table}.character "
            f"WHERE {table}.card_id IS NULL "
            f"{condition}"
            f"ORDER BY {column} {order} "
            "LIMIT (?)",
            (max_characters,),
        )
        candidates = [x[0] for x in r]

        return self.new_characters(card_type, candidates, max_characters)

    # Recalc all kanji cards created
    def recalc_user_cards(self, card_type):
        table = f"usr.{card_type.label}_card_ids"

        self.crs_execute(
            f"DELETE FROM {table} WHERE card_id >= 0"
        )  # don't nuke words manually marked known!

        character_card_ids = {}

        recognized_types = (
            config.get("card_type_recognized", {}).get(card_type.label, []).copy()
        )

        recognized_types.append(
            {
                "deck": "All",
                "note": card_type.model_name,
                "card": 0,
                "field": "Character",
            }
        )

        for entry in recognized_types:
            entry_note = entry["note"]
            entry_card = entry["card"]
            entry_deck = entry["deck"]
            entry_field = entry["field"]

            find_filter = [f'"note:{entry_note}"', f'"card:{entry_card+1}"']
            if entry_deck != "All":
                find_filter.append(f'"deck:{entry_deck}"')

            card_ids = aqt.mw.col.find_cards(" AND ".join(find_filter))

            for card_id in card_ids:
                card = aqt.mw.col.getCard(card_id)
                note = card.note()
                character = clean_character_field(note[entry_field])
                character_card_ids[character] = card_id

        self.crs_executemany_and_commit(
            f"INSERT OR REPLACE INTO {table} (character, card_id) values (?,?)",
            character_card_ids.items(),
        )

    # Recalc user all works associated with kanji from notes
    def recalc_user_words(self):
        if not text_parser.is_available():
            return

        recognized_types = config.get("word_recognized", [])

        note_id_words = set()

        note_ids_not_new = set()

        for check_new in [False, True]:
            for entry in recognized_types:
                entry_note = entry["note"]
                entry_card = entry["card"]
                entry_deck = entry["deck"]
                entry_field = entry["field"]

                find_filter = [f'"note:{entry_note}"', f'"card:{entry_card+1}"']
                if entry_deck != "All":
                    find_filter.append(f'"deck:{entry_deck}"')
                if check_new:
                    find_filter.append("(is:new AND -is:suspended)")
                else:
                    find_filter.append("(is:learn OR is:review)")

                entry_note_ids = aqt.mw.col.find_notes(" AND ".join(find_filter))

                for note_id in entry_note_ids:
                    if not check_new:
                        note_ids_not_new.add(note_id)

                    note = aqt.mw.col.getNote(note_id)
                    field_value = note[entry_field]
                    words = text_parser.get_cjk_words(field_value, reading=True)

                    for word in words:
                        note_id_words.add((note_id, *word))

        self.crs_execute("DELETE FROM usr.words")

        insert_note_id_words = set()
        for note_id, word, reading in note_id_words:
            is_new = note_id not in note_ids_not_new
            insert_note_id_words.add((note_id, word, reading, is_new))

        # Insert new mapping
        self.crs_executemany_and_commit(
            "INSERT INTO usr.words (note_id,word,reading,is_new) VALUES (?,?,?,?)",
            insert_note_id_words,
        )

    def on_note_update(self, note_id, deck_id, is_new=False):
        try:
            note = aqt.mw.col.getNote(note_id)
        except Exception:
            # TODO: properly check if this is related to card import/export instead of this mess.
            return

        # Could allow more features if Migaku JA isn't installed but too lazy rn
        if not text_parser.is_available():
            return

        # Remove existing word entries for note
        self.crs_execute_and_commit("DELETE FROM usr.words WHERE note_id = (?)", (note_id,))

        # Add words from note
        words = set()

        for wr in config.get("word_recognized", []):
            wr_note = wr["note"]
            wr_deck_name = wr["deck"]
            wr_field = wr["field"]

            wr_model = aqt.mw.col.models.byName(wr_note)
            if wr_model is None:
                continue
            if note.mid != wr_model["id"]:
                continue

            if wr_deck_name != "All":
                wr_deck = aqt.mw.col.decks.byName(wr_deck_name)
                if wr_deck is None:
                    continue
                if deck_id != wr_deck["id"]:
                    continue

            field_value = note[wr_field]
            words.update(text_parser.get_cjk_words(field_value, reading=True))

        self.crs_executemany_and_commit(
            "INSERT INTO usr.words (note_id,word,reading,is_new) VALUES (?,?,?,?)",
            [(note_id, w, r, is_new) for (w, r) in words],
        )

        # Get unique kanji
        kanji = set()

        for wr in words:
            kanji.update(text_parser.filter_cjk(wr[0]))

        # Update kanji notes
        for ct in CardType:
            if not ct.auto_card_refresh:
                continue

            mid = ct.model_id()
            for k in kanji:
                r = self.crs_execute_and_fetch_one(
                    f"SELECT card_id FROM usr.{ct.label}_card_ids WHERE character = (?)",
                    (k,),
                )
                if r:
                    cid = r[0]
                    try:
                        card = aqt.mw.col.getCard(cid)
                    except Exception:  # anki.errors.NotFoundError for newer versions
                        continue
                    if card:
                        note = card.note()
                        if note:
                            if note.mid == mid:
                                self.refresh_note(note, do_flush=True)

        # Create new cards
        if is_new:
            new_kanji_for_msg = OrderedDict()

            for ct in CardType:
                if not ct.auto_card_creation:
                    continue

                self.recalc_user_cards(ct)
                new_chars = self.new_characters(ct, kanji)

                if len(new_chars) > 0:
                    if ct.auto_card_creation_msg:
                        new_kanji_for_msg[ct] = new_chars
                    else:
                        self.make_cards_from_characters(
                            ct, new_chars, "Automatic Kanji Card Cration"
                        )

            if len(new_kanji_for_msg) > 0:
                KanjiConfirmDialog.show_new_kanji(new_kanji_for_msg, aqt.mw)

    def refresh_learn_ahead(self):
        for ct in CardType:
            for e in config.get("card_type_learn_ahead", {}).get(ct.label, []):
                deck_name = e["deck"]
                max_num = e["num"]

                deck = aqt.mw.col.decks.byName(deck_name)
                if deck is None:
                    continue
                deck_id = deck["id"]

                new = self.new_learn_ahead_kanji(ct, deck_id, max_num)

                if len(new) < 1:
                    continue

                try:
                    self.make_cards_from_characters(ct, new, None)
                except InvalidStateError:
                    # Ignore this silently...
                    pass

    # checks learn ahead for a given deck
    def new_learn_ahead_kanji(self, card_type, deck_id, max_cards):
        nids = aqt.mw.col.db.all(
            f"SELECT c.nid FROM cards as c WHERE did={deck_id} AND type=0 ORDER BY c.due AND queue>=0 LIMIT {max_cards}"
        )

        kanji_seen = set()
        kanji = []  # to preserve order

        for [nid] in nids:
            note = aqt.mw.col.getNote(nid)

            for wr in config.get("word_recognized", []):
                wr_note = wr["note"]
                wr_deck_name = wr["deck"]
                wr_field = wr["field"]

                wr_model = aqt.mw.col.models.byName(wr_note)
                if wr_model is None:
                    continue
                if note.mid != wr_model["id"]:
                    continue

                if wr_deck_name != "All":
                    wr_deck = aqt.mw.col.decks.byName(wr_deck_name)
                    if wr_deck is None:
                        continue
                    if deck_id != wr_deck["id"]:
                        continue

                field_value = note[wr_field]
                for k in text_parser.filter_cjk(field_value):
                    if k not in kanji_seen:
                        kanji.append(k)

        return aqt.mw.migaku_kanji_db.new_characters(card_type, kanji)

    # Returns a list of tuples: (word, reading, note id list, is_new)
    # Seen ones first, then sorted by amount of note ids.
    def get_character_words(self, character):
        character_wildcard = f"%{character}%"
        r = self.crs_execute_and_fetch_all(
            "SELECT note_id, word, reading, is_new FROM usr.words WHERE word LIKE (?)",
            (character_wildcard,),
        )

        words_dict = defaultdict(list)
        words_not_new = set()

        for note_id, word, reading, is_new in r:
            words_dict[(word, reading)].append(note_id)
            if not is_new:
                words_not_new.add((word, reading))

        word_list = []
        for (word, reading), note_ids in words_dict.items():
            is_new = (word, reading) not in words_not_new
            word_list.append((word, reading, note_ids, is_new))

        word_list.sort(key=lambda entry: (not entry[3], len(entry[2])), reverse=True)

        return word_list

    def set_character_usr_keyowrd(self, character, keyword, primitive_keyword):
        self.crs_execute_and_commit(
            "INSERT OR REPLACE INTO usr.keywords (character,usr_keyword,usr_primitive_keyword) VALUES (?,?,?)",
            (character, keyword, primitive_keyword),
        )

        self.refresh_notes_for_character(character)

    def get_character_usr_keyowrd(self, character):
        r = self.crs_execute_and_fetch_one(
            "SELECT usr_keyword, usr_primitive_keyword FROM usr.keywords WHERE character=?",
            (character,),
        )
        if r:
            return (r[0], r[1])
        else:
            return ("", "")

    # TODO: Also allow setting primitive keywords
    def mass_set_character_usr_keyowrd(self, character_keywords):
        self.crs_executemany_and_commit(
            "INSERT OR REPLACE INTO usr.keywords (character,usr_keyword) VALUES (?,?)",
            character_keywords.items(),
        )

    def set_character_usr_story(self, character, story):
        self.crs_execute_and_commit(
            "INSERT OR REPLACE INTO usr.stories (character,usr_story) VALUES (?,?)",
            (character, story),
        )

        self.refresh_notes_for_character(character)

    def mass_set_character_usr_story(self, character_stories):
        self.crs_executemany_and_commit(
            "INSERT OR REPLACE INTO usr.stories (character,usr_story) VALUES (?,?)",
            character_stories.items(),
        )

    def set_character_known(self, card_type, character, known=True):
        if known == True:
            self.crs_execute_and_commit(
                f"INSERT OR REPLACE INTO usr.{card_type.label}_card_ids (character,card_id) VALUES (?,?)",
                (character, -1),
            )
        else:
            self.crs_execute_and_commit(
                f"DELETE FROM usr.{card_type.label}_card_ids WHERE character == ?",
                (character,),
            )

    def mass_set_characters_known(self, card_type, characters):
        self.crs_executemany_and_commit(
            f"INSERT OR IGNORE INTO usr.{card_type.label}_card_ids (character,card_id) VALUES (?,?)",
            [(c, -1) for c in characters],
        )

    def refresh_notes_for_character(self, character):
        ct_find_filter = [f'"note:{ct.model_name}"' for ct in CardType]
        ct_filter = " OR ".join(ct_find_filter)
        ct_filter = f"({ct_filter})" if ct_filter != "" else ""
        related_characters = (self.get_related_characters(character) or []) + [character]
        related_chars_filter = [f'"Character:{character}"' for character in related_characters]
        related_chars_filter = " OR ".join(related_chars_filter)

        # mind the parens
        note_ids = aqt.mw.col.find_notes(f"({ct_filter}) AND ({related_chars_filter})")

        for note_id in note_ids:
            note = aqt.mw.col.getNote(note_id)
            self.refresh_note(note, do_flush=True)

    def make_card_unsafe(self, card_type, character):
        from . import add_note_no_hook

        deck_name = card_type.deck_name
        model_name = card_type.model_name

        deck = aqt.mw.col.decks.byName(deck_name)
        if deck is None:
            raise InvalidDeckError(card_type)
        deck_id = deck["id"]

        model = aqt.mw.col.models.byName(model_name)

        note = anki.notes.Note(aqt.mw.col, model)
        note["Character"] = character
        self.refresh_note(note)
        add_note_no_hook(aqt.mw.col, note, deck_id)

        return note

    def make_cards_from_characters(self, card_type, new_characters, checkpoint=None):
        from . import add_note_no_hook

        # Just to be sure...
        self.recalc_user_cards(card_type)

        characters = self.new_characters(card_type, new_characters)

        deck_name = card_type.deck_name
        model_name = card_type.model_name

        deck = aqt.mw.col.decks.byName(deck_name)
        if deck is None:
            raise InvalidDeckError(card_type)

        if checkpoint is not None:
            aqt.mw.checkpoint(checkpoint)

        deck_id = deck["id"]
        model = aqt.mw.col.models.byName(model_name)

        for c in characters:
            note = anki.notes.Note(aqt.mw.col, model)
            note["Character"] = c
            self.refresh_note(note)
            add_note_no_hook(aqt.mw.col, note, deck_id)

        self.recalc_user_cards(card_type)

    def refresh_note(self, note, do_flush=False):
        c = clean_character_field(note["Character"])
        if len(c) < 1:
            return
        note["Character"] = c

        r = self.get_kanji_result_data(c, card_ids=False)
        data_json = json.dumps(r, ensure_ascii=True)
        data_json_b64_b = base64.b64encode(data_json.encode("utf-8"))
        data_json_b64 = str(data_json_b64_b, "utf-8")
        note["MigakuData"] = data_json_b64

        if c[0] == '[':
            svg_name = c[1:-1] + ".svg"
        else:
            svg_name = "%05x.svg" % ord(c)

        # Try to find the KanjiVG file first in supplementary directory and
        # only then from the main repository
        svg_path = addon_path("kanjivg-supplementary", svg_name)
        if not os.path.exists(svg_path):
            svg_path = addon_path("kanjivg", svg_name)
            if not os.path.exists(svg_path):
                svg_path = ''

        if svg_path != '':
            with open(svg_path, "r", encoding="utf-8") as file:
                svg_data = file.read()

            note["StrokeOrder"] = svg_data
        else:
            note["StrokeOrder"] = ""

        if do_flush:
            note.flush()

    # If the deck has cards that have now references for new primitives 
    # which are not yet included in the stack, add them.
    def add_missing_characters(self):
        new_kanji_for_msg = OrderedDict()

        for ct in CardType:
            if not ct.add_primitives:
                continue

            find_filter = f'"note:{ct.model_name}"'
            note_ids = aqt.mw.col.find_notes(find_filter)

            all_characters_in_the_deck = []
            for i, note_id in enumerate(note_ids):
                note = aqt.mw.col.getNote(note_id)
                c = clean_character_field(note["Character"])
                all_characters_in_the_deck.append(c)

            new_characters = self.new_characters(ct, all_characters_in_the_deck, -1)
            if len(new_characters) > 0:
                new_kanji_for_msg[ct] = new_characters

        if len(new_kanji_for_msg) > 0:
            KanjiConfirmDialog.show_new_kanji(new_kanji_for_msg, aqt.mw)

    # Recalc everything
    def recalc_all(self, callback=None):
        if callback:
            callback("Scanning kanji cards...")

        for ct in CardType:
            self.recalc_user_cards(ct)

        if callback:
            callback("Refreshing collection words...")

        self.recalc_user_words()

        self.add_missing_characters()

        find_filter = [f'"note:{ct.model_name}"' for ct in CardType]
        note_ids = aqt.mw.col.find_notes(" OR ".join(find_filter))
        num_notes = len(note_ids)

        for i, note_id in enumerate(note_ids):
            note = aqt.mw.col.getNote(note_id)
            self.refresh_note(note, do_flush=True)

            if callback and ((i + 1) % 25) == 0:
                callback(f"Refreshing kanji cards... ({i+1}/{num_notes})")

    def get_kanji_result_data(
        self,
        character,
        card_ids=True,
        detail_primitives=True,
        detail_primitive_of=True,
        words=True,
        user_data=False,
    ):
        ret = {
            "character": character,
            "has_result": False,
        }

        # (field_name, load_function, column)
        _ = lambda x: x
        requested_fields = [
            ("stroke_count", _, None),
            ("onyomi", json.loads, None),
            ("kunyomi", json.loads, None),
            ("nanori", json.loads, None),
            ("meanings", json.loads, None),
            ("frequency_rank", _, None),
            ("grade", _, None),
            ("jlpt", _, None),
            ("kanken", _, None),
            ("primitives", custom_list, None),
            ("primitive_of", custom_list, None),
            ("primitive_keywords", json.loads, None),
            ("primitive_alternatives", custom_list, None),
            ("heisig_id5", _, None),
            ("heisig_id6", _, None),
            ("heisig_keyword5", _, None),
            ("heisig_keyword6", _, None),
            ("heisig_story", _, None),
            ("heisig_comment", _, None),
            ("radicals", list, None),
            ("words_default", json.loads, None),
            ("koohi_stories", json.loads, None),
            ("wk", _, None),
            ("usr_keyword", _, "usr.keywords.usr_keyword"),
            ("usr_primitive_keyword", _, "usr.keywords.usr_primitive_keyword"),
            ("usr_story", _, "usr.stories.usr_story"),
        ]

        if card_ids:
            for ct in CardType:
                requested_fields.append(
                    (f"{ct.label}_card_id", _, f"usr.{ct.label}_card_ids.card_id")
                )

        fields = ",".join((rf[2] if rf[2] else rf[0]) for rf in requested_fields)

        joins = [
            f"LEFT OUTER JOIN usr.keywords ON characters.character == usr.keywords.character ",
            f"LEFT OUTER JOIN usr.stories ON characters.character == usr.stories.character ",
        ]
        if card_ids:
            joins.extend(
                f"LEFT OUTER JOIN usr.{ct.label}_card_ids ON characters.character == usr.{ct.label}_card_ids.character "
                for ct in CardType
            )
        joins_txt = "".join(joins)

        raw_data = self.crs_execute_and_fetch_one(
            f"SELECT {fields} FROM characters {joins_txt} "
            "WHERE characters.character = (?)",
            (character,),
        )

        if raw_data:
            ret["has_result"] = True

            for data, (name, load_func, _) in zip(raw_data, requested_fields):
                ret[name] = load_func(data)

            if words:
                ret["words"] = self.get_character_words(character)

            if detail_primitives:
                primitives_detail = []

                for pc in ret["primitives"]:
                    primitives_detail.append(
                        self.get_kanji_result_data(
                            pc,
                            card_ids=False,
                            detail_primitives=False,
                            detail_primitive_of=False,
                            words=False,
                        )
                    )

                ret["primitives_detail"] = primitives_detail

            if detail_primitive_of:
                primitive_of_detail = []

                for pc in ret["primitive_of"]:
                    primitive_of_detail.append(
                        self.get_kanji_result_data(
                            pc,
                            card_ids=False,
                            detail_primitives=False,
                            detail_primitive_of=False,
                            words=False,
                        )
                    )

                ret["primitive_of_detail"] = primitive_of_detail

            if user_data:
                ret["user_data"] = {}
                for ct in CardType:
                    ct_card_id = ret[f"{ct.label}_card_id"]
                    ct_user_data = ""
                    if ct_card_id:
                        try:
                            ct_card = aqt.mw.col.getCard(ct_card_id)
                            ct_user_data = ct_card.note()["UserData"]
                        except:
                            pass
                    ret["user_data"][ct.label] = ct_user_data

        return ret
