import aqt
from aqt.qt import *

import anki.find

from . import config
from . import util
from . import text_parser
from .card_type_radio_buttons import CardTypeRadioButtons


class CreateCardsFromNotesDialog(QDialog):

    def __init__(self, note_ids, parent=None):
        super(QDialog, self).__init__(parent)

        self.note_ids = note_ids

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Create Cards From Notes')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        info_lbl = QLabel('Select the card type for which you want to create kanji cards.\n\n' \
                          'All selected fields will be scanned for kanji you do not yet have cards in your collection for and have not marked known.\n\n' \
                          'You are able to confirm the cards that will be created after pressing OK.')
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        lyt.addWidget(QLabel('<hr>'))

        self.ct_selector = CardTypeRadioButtons()
        lyt.addWidget(self.ct_selector)

        lyt.addWidget(QLabel('Fields:'))

        self.list_box = QListWidget()
        last_checked = config.get('cards_from_notes_last_checked', {})
        for field_name in anki.find.fieldNamesForNotes(aqt.mw.col, note_ids):
            itm = QListWidgetItem(field_name)
            itm.setCheckState(
                Qt.Checked if (field_name in last_checked and last_checked[field_name]) else Qt.Unchecked
            )
            self.list_box.addItem(itm)
        lyt.addWidget(self.list_box)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.create_cards)
        btn_box.rejected.connect(self.reject)
        lyt.addWidget(btn_box)

        self.resize(530, 530)


    def create_cards(self):

        card_type = self.ct_selector.current_card_type

        checked_fields = set()
        checked_fields_states = {}
        for i in range(self.list_box.count()):
            itm = self.list_box.item(i)
            field_name = itm.data(Qt.ItemDataRole.DisplayRole)
            field_checked = itm.checkState() == Qt.CheckState.Checked
            if field_checked:
                checked_fields.add(field_name)
            checked_fields_states[field_name] = field_checked

        kanji = set()

        for nid in self.note_ids:
            note = aqt.mw.col.getNote(nid)

            for field_name in checked_fields:
                # could cahce this but meh
                note_field_names = aqt.mw.col.models.fieldNames(note.model())
                
                if field_name in note_field_names:
                    kanji.update(
                        text_parser.filter_cjk(note[field_name])
                    )

        aqt.mw.migaku_kanji_db.recalc_user_cards(card_type)
        new_kanji = aqt.mw.migaku_kanji_db.new_characters(card_type, kanji)

        if len(new_kanji):
            r = aqt.qt.QMessageBox.question(
                self,
                'Migaku Kanji',
                F'Do you want to create kanji {card_type.label} cards for these kanji?\n\n' + ' '.join(new_kanji)
            )

            if r == aqt.qt.QMessageBox.Yes:

                util.error_msg_on_error(
                    self,
                    aqt.mw.migaku_kanji_db.make_cards_from_characters,
                    card_type, new_kanji, 'Created Kanji Cards From Notes'
                )

                aqt.mw.migaku_kanji_db.recalc_user_cards(card_type)

        else:
            aqt.qt.QMessageBox.information(
                self,
                'Migaku Kanji',
                F'You already have kanji {card_type.label} cards or marked them known for all kanji occuring in the selected notes with the selected fields!'
            )

        config.get('cards_from_notes_last_checked', {}).update(checked_fields_states)
        config.write()

        self.accept()


    @classmethod
    def show_modal(cls, note_ids, parent):

        if note_ids is None or len(note_ids) < 1:
            return

        dlg = cls(note_ids, parent)
        return dlg.exec()
