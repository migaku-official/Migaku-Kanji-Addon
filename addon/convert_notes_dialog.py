import anki

import aqt
from aqt.qt import *

from . import util
from .card_type import CardType


class ConvertNotesDialog(QDialog):

    def __init__(self, old_model_id, note_ids, parent=None):
        super(QDialog, self).__init__(parent)

        self.old_model = aqt.mw.col.models.get(old_model_id)
        self.card_type_ords = {}
        for tmpl in self.old_model['tmpls']:
            self.card_type_ords[tmpl['name']] = tmpl['ord']

        data_srcs = [f['name'] for f in self.old_model['flds']]

        self.note_ids = note_ids

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Convert Notes')

        info_lbl = QLabel('Using this you can convert existing kanji cards to Migaku kanji cards.\n\n' \
                          'WARNING: If you convert notes for which a Migaku kanji card already exist, only the already existing Migaku card will remain!')
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        lyt.addWidget(QLabel('<hr>'))

        lyt.addWidget(QLabel('Select the field that contains the Kanji'))
        self.character_box = QComboBox()
        self.character_box.addItems(data_srcs)
        lyt.addWidget(self.character_box)

        card_grp = QGroupBox('Select learning format for cards from old note type')
        lyt.addWidget(card_grp)
        card_lyt = QGridLayout()
        card_grp.setLayout(card_lyt)

        ct_srcs = ['None'] + list(self.card_type_ords.keys())

        self.card_type_boxes = {}

        for i, ct in enumerate(CardType):
            card_lyt.addWidget(QLabel(F'{ct.name}:'), i, 0)
            cb = QComboBox()
            cb.addItems(ct_srcs)
            self.card_type_boxes[ct] = cb
            card_lyt.addWidget(cb, i, 1)

        field_grp = QGroupBox('Select fields from which data should be imported')        
        lyt.addWidget(field_grp)
        field_lyt = QGridLayout()
        field_grp.setLayout(field_lyt)

        i = 0
        field_lyt.addWidget(QLabel('Custom Keyword'), i, 0)
        self.keyword_box = QComboBox()
        self.keyword_box.addItems(['None'] + data_srcs)
        field_lyt.addWidget(self.keyword_box, i, 1)

        i += 1
        field_lyt.addWidget(QLabel('Custom Story'), i, 0)
        self.story_box = QComboBox()
        self.story_box.addItems(['None'] + data_srcs)
        field_lyt.addWidget(self.story_box, i, 1)

        self.move_cards_box = QCheckBox('Move converted cards to corresponding deck')
        self.move_cards_box.setChecked(True)
        lyt.addWidget(self.move_cards_box)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.convert)
        btn_box.rejected.connect(self.reject)
        lyt.addWidget(btn_box)


    # TODO: May allow just doing this
    def import_usr_data(self):

        character_fld = self.character_box.currentText()
        keyword_fld = None if self.keyword_box.currentIndex() < 1 else self.keyword_box.currentText()
        story_fld = None if self.story_box.currentIndex() < 1 else self.story_box.currentText()

        keywords = {}
        stories = {}

        for nid in self.note_ids:
            note = aqt.mw.col.getNote(nid)

            char = note[character_fld].lstrip()
            if len(char) < 1:
                continue
            char = char[0]

            if keyword_fld:
                keyword = note[keyword_fld].strip()
                if keyword:
                    keywords[char] = keyword

            if story_fld:
                story = note[story_fld].strip()
                if story:
                    stories[char] = story

        aqt.mw.migaku_kanji_db.mass_set_character_usr_keyowrd(keywords)
        aqt.mw.migaku_kanji_db.mass_set_character_usr_story(stories)


    def convert(self):

        used_indexes = set()
        for box in self.card_type_boxes.values():
            idx = box.currentIndex()
            if idx > 0:
                if idx in used_indexes:
                    QMessageBox.information(self, 'Migaku Kanji', 'You cannot convert a single card type to multiple kanji card types!')
                    return
                used_indexes.add(idx)

        if len(used_indexes) < 1:
            QMessageBox.information(self, 'Migaku Kanji', 'Select at least one target kanji card type!')
            return
        
        if len(used_indexes) != len(self.card_type_ords):
            r = QMessageBox.question(self, 'Migaku Kanji', 'Not all card types will be converted and will be lost. Do you want to continue?')
            if r != QMessageBox.Yes:
                return

        move_cards = self.move_cards_box.isChecked()

        # get target deck ids if needed
        ct_deck_ids = {}
        for ct in CardType:
            box = self.card_type_boxes[ct]
            if box.currentIndex() < 1:
                continue
            deck_name = ct.deck_name
            deck = aqt.mw.col.decks.byName(deck_name)
            if deck is None:
                util.error_msg(
                    self,
                    F'No or invalid deck selected for {ct.label} cards.\n\n'
                    F'Please go to the settings and select the deck into which new {ct.label} cards should be added.'
                )
                return
            ct_deck_ids[ct] = deck['id']

        self.import_usr_data()

        character_fld = self.character_box.currentText()
        char_nids = {}

        for nid in self.note_ids:
            note = aqt.mw.col.getNote(nid)

            char = note[character_fld].lstrip()
            if len(char) < 1:
                continue
            char = char[0]

            char_nids[char] = nid

        aqt.mw.requireReset()

        db = aqt.mw.migaku_kanji_db

        for ct in CardType:
            
            box = self.card_type_boxes[ct]
            if box.currentIndex() < 1:
                continue
            
            deck_id = ct_deck_ids[ct]

            ord_ = self.card_type_ords[box.currentText()]

            db.recalc_user_cards(ct)

            new_chars = db.new_characters(ct, char_nids.keys())
            for char in char_nids:

                # Only allow importing if no Migaku Kanji card exists... UGLY
                find_filter = F'"note:{ct.model_name}" AND "Character:{char}"'
                note_ids = aqt.mw.col.find_notes(find_filter)

                if len(note_ids):
                    # Migaku Kanji card exists
                    continue

                nid = char_nids[char]

                note = db.make_card_unsafe(ct, char)
                note.flush()
                card_id = aqt.mw.col.db.scalar('SELECT id FROM cards WHERE nid = ? AND ord = ?', nid, ord_)

                if card_id is None:
                    # DB already messed up
                    continue

                # Now the ugly part...

                # 1) Nuke all cards from new note that were automatically created
                aqt.mw.col.db.execute('DELETE FROM cards WHERE nid = ?', note.id)

                # 2 Assign old card to new note, move card if requested
                if move_cards:
                    aqt.mw.col.db.execute('UPDATE cards SET nid = ?, did = ? WHERE id = ?', note.id, deck_id, card_id)
                else:
                    aqt.mw.col.db.execute('UPDATE cards SET nid = ? WHERE id = ?', note.id, card_id)

                # 3) Pray that we didn't mess up the db

            db.recalc_user_cards(ct)

        aqt.mw.col.db.commit()

        # Finally remove the old cards/notes
        model_id_rows = aqt.mw.col.db.all('DELETE FROM cards WHERE nid in %s' % anki.utils.ids2str(self.note_ids))
        model_id_rows = aqt.mw.col.db.all('DELETE FROM notes WHERE id in %s' % anki.utils.ids2str(self.note_ids))
        aqt.mw.col.db.commit()

        aqt.mw.maybeReset()

        self.accept()


    @classmethod
    def show_modal(cls, note_ids, parent=None):

        if note_ids is None or len(note_ids) < 1:
            return

        model_id_rows = aqt.mw.col.db.all('SELECT DISTINCT mid FROM notes WHERE id in %s' % anki.utils.ids2str(note_ids))

        if len(model_id_rows) > 1:
            util.error_msg(parent, 'Please only select notes from a single note type!')
            return

        model_id = model_id_rows[0][0]

        for ct in CardType:
            ct_model_name = ct.model_name
            ct_model = aqt.mw.col.models.byName(ct_model_name)
            if ct_model['id'] == model_id:
                util.error_msg(parent, 'The selected notes are already in the Migaku Kanji note type!')
                return

        dlg = cls(model_id, note_ids, parent)
        return dlg.exec()
