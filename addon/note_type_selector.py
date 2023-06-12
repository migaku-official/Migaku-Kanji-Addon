import aqt
from aqt.qt import *

from .card_type import CardType
from . import config



class NoteTypeSelectorWidget(QWidget):

    def __init__(self, info_text=None, note_filter=lambda n: True, parent=None, no_margin=False, field_label='Field'):
        super(QWidget, self).__init__(parent)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.deck_list = ['All'] + sorted(
            [x.name for x in aqt.mw.col.decks.all_names_and_ids()]
        )

        self.note_list = sorted(
            [n.name for n in aqt.mw.col.models.all_names_and_ids() if note_filter(n)]
        )

        lyt = QVBoxLayout(self)
        if no_margin:
            lyt.setContentsMargins(0, 0, 0, 0)

        if info_text:
            info_lbl = QLabel(info_text)
            info_lbl.setWordWrap(True)
            lyt.addWidget(info_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Deck', 'Note Type', 'Card Type', field_label, ''])
        self.table.verticalHeader().hide()
        lyt.addWidget(self.table)

        self.note_boxes = []
        self.remove_btns = []

        btns_lyt = QHBoxLayout()
        lyt.addLayout(btns_lyt)

        add_btn = QPushButton('Add')
        add_btn.clicked.connect(self.add_line)
        btns_lyt.addWidget(add_btn)

        clear_btn = QPushButton('Clear All')
        clear_btn.clicked.connect(self.clear)
        btns_lyt.addWidget(clear_btn)

        btns_lyt.addStretch()

        button_dimension = add_btn.sizeHint().height()

        self.table.horizontalHeader().setMinimumSectionSize(button_dimension)
        self.table.horizontalHeader().resizeSection(0, 175)
        self.table.horizontalHeader().resizeSection(1, 300)
        self.table.horizontalHeader().resizeSection(2, 175)
        self.table.horizontalHeader().resizeSection(3, 175)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)


    def set_data(self, data):
        self.clear()

        for data_entry in data:
            self.add_line(data_entry)


    def get_data(self):
        data = []

        for rid in range(self.table.rowCount()):
            deck = self.table.cellWidget(rid, 0).currentText()
            note = self.table.cellWidget(rid, 1).currentText()
            card = self.table.cellWidget(rid, 2).currentIndex()
            field = self.table.cellWidget(rid, 3).currentText()
            data.append(
                { 'deck': deck, 'note': note, 'card': card, 'field': field }
            )

        return data


    def clear(self):
        self.note_boxes.clear()
        self.remove_btns.clear()
        self.table.clearContents()
        self.table.setRowCount(0)


    def add_line(self, data_entry=None):
        rid = self.table.rowCount()
        self.table.insertRow(rid)

        deck_box = QComboBox()
        deck_box.addItems(self.deck_list)

        note_box = QComboBox()
        self.note_boxes.append(note_box)
        note_box.currentIndexChanged.connect(self.on_note_change)

        card_box = QComboBox()
        field_box = QComboBox()

        remove_btn = QPushButton('✖')
        remove_btn.setMaximumWidth(remove_btn.sizeHint().height())
        remove_btn.clicked.connect(self.on_remove)
        self.remove_btns.append(remove_btn)

        self.table.setCellWidget(rid, 0, deck_box)
        self.table.setCellWidget(rid, 1, note_box)
        self.table.setCellWidget(rid, 2, card_box)
        self.table.setCellWidget(rid, 3, field_box)
        self.table.setCellWidget(rid, 4, remove_btn)

        # Causes on_note_change to fire and populates dependent columns
        note_box.addItems(self.note_list)

        if data_entry:
            deck_box.setCurrentText(data_entry['deck'])
            note_box.setCurrentText(data_entry['note'])
            card_box.setCurrentIndex(data_entry['card'])
            field_box.setCurrentText(data_entry['field'])


    def on_note_change(self):
        note_box = self.sender()
        rid = self.note_boxes.index(note_box)

        card_box = self.table.cellWidget(rid, 2)
        field_box = self.table.cellWidget(rid, 3)

        note_name = note_box.currentText()

        cards = [f['name'] for f in aqt.mw.col.models.byName(note_name)['tmpls']]
        card_box.clear()
        card_box.addItems(cards)

        fields = [f['name'] for f in aqt.mw.col.models.byName(note_name)['flds']]
        field_box.clear()
        field_box.addItems(fields)

    def on_remove(self):
        remove_btn = self.sender()
        rid = self.remove_btns.index(remove_btn)

        del self.note_boxes[rid]
        del self.remove_btns[rid]
        self.table.removeRow(rid)



class CardTypeRecognizedSelectorWidget(NoteTypeSelectorWidget):

    def __init__(self, card_type, parent=None, no_margin=False):
        self.card_type = card_type
        info_text = F'Select which additional cards are recognized as existing kanji {self.card_type.label} cards. ' \
                    'These cards will not be modified by this add-on.'
        note_filter = lambda n: not n.name.startswith('Migaku')

        super().__init__(info_text, note_filter, parent, no_margin, field_label='Kanji Character Field')
        self.load_from_config()


    def load_from_config(self):
        data = config.get('card_type_recognized', {}).get(self.card_type.label, [])
        self.set_data(data)


    def save_to_config(self):
        data = self.get_data()
        config.get('card_type_recognized', {})[self.card_type.label] = data



class WordRecognizedSelectorWidget(NoteTypeSelectorWidget):

    def __init__(self, parent=None, no_margin=False):
        info_text = 'The Registered Fields are used for multiple purposes:<ul>' \
                    '<li>These fields are used to extract example words shown in the lookup browser and on kanji cards</li>' \
                    '<li>If you have learn-ahead decks specified, only these fields are scanned</li>' \
                    '<li>You can view stats for the kanji from the specified fields on the stats page</li>' \
                    '</ul>'

        # Don't allow selecting kanji cards
        invalid_notes = [ct.model_name for ct in CardType]
        note_filter = lambda n: n.name not in invalid_notes

        super().__init__(info_text, note_filter, parent, no_margin)
        self.load_from_config()


    def load_from_config(self):
        data = config.get('word_recognized', [])
        self.set_data(data)


    def save_to_config(self):
        data = self.get_data()
        config.set('word_recognized', data)
