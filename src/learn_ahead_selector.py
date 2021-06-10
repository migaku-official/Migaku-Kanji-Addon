import aqt
from aqt.qt import *

from .card_type import CardType
from . import config


class LearnAheadSelectorWidget(QWidget):

    def __init__(self, card_type, parent=None, no_margin=False):
        super(QWidget, self).__init__(parent)

        self.card_type = card_type

        self.setFocusPolicy(Qt.NoFocus)

        self.deck_list = sorted(
            [x.name for x in aqt.mw.col.decks.all_names_and_ids()]
        )

        lyt = QVBoxLayout(self)
        if no_margin:
            lyt.setContentsMargins(0, 0, 0, 0)

        info_lbl = QLabel(
            F'Select for which decks kanji {self.card_type.label} cards should be created ahead. ' \
             'The value specifies for how many cards ahead kanji cards should be created. ' \
             'Note that only cards/fields setup in the "Registered Fields" tab are scanned.'
        )
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Deck', 'Learn-Ahead Card Count', ''])
        self.table.verticalHeader().hide()
        lyt.addWidget(self.table)

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
        self.table.horizontalHeader().resizeSection(1, 175)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.load_from_config()


    def set_data(self, data):
        self.clear()

        for data_entry in data:
            self.add_line(data_entry)


    def get_data(self):
        data = []

        for rid in range(self.table.rowCount()):
            deck = self.table.cellWidget(rid, 0).currentText()
            num = self.table.cellWidget(rid, 1).value()
            data.append(
                { 'deck': deck, 'num': num }
            )

        return data


    def clear(self):
        self.remove_btns.clear()
        self.table.clearContents()
        self.table.setRowCount(0)

    
    def add_line(self, data_entry=None):
        rid = self.table.rowCount()
        self.table.insertRow(rid)

        deck_box = QComboBox()
        deck_box.addItems(self.deck_list)

        num_box = QSpinBox()
        num_box.setMinimum(1)
        num_box.setMaximum(150)
        num_box.setValue(25)        # <- defalt learn-ahead card count

        remove_btn = QPushButton('✖')
        remove_btn.setMaximumWidth(remove_btn.sizeHint().height())
        remove_btn.clicked.connect(self.on_remove)
        self.remove_btns.append(remove_btn)

        self.table.setCellWidget(rid, 0, deck_box)
        self.table.setCellWidget(rid, 1, num_box)
        self.table.setCellWidget(rid, 2, remove_btn)

        if data_entry:
            deck_box.setCurrentText(data_entry['deck'])
            num_box.setValue(data_entry['num'])


    def on_remove(self):
        remove_btn = self.sender()
        rid = self.remove_btns.index(remove_btn)

        del self.remove_btns[rid]
        self.table.removeRow(rid)


    def load_from_config(self):
        data = config.get('card_type_learn_ahead').get(self.card_type.label, [])
        self.set_data(data)


    def save_to_config(self):
        data = self.get_data()
        config.get('card_type_learn_ahead')[self.card_type.label] = data