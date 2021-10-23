import aqt
from aqt.qt import *

from . import util
from .card_type import CardType


class AddCardsDialog(QDialog):

    # Label, column, order, condition
    options = [
        ('Frequency',     'frequency_rank', 'ASC',  '< 999999'),
        ('RTK 1-5 Order', 'heisig_id5',     'ASC',  'NOT NULL'),
        ('RTK 6+ Order',  'heisig_id6',     'ASC',  'NOT NULL'),
        ('JLPT',          'jlpt',           'DESC', 'NOT NULL'),
        ('Kanken',        'kanken',         'DESC', 'NOT NULL'),
        ('School Year',   'grade',          'ASC',  'NOT NULL'),
    ]

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle('Migaku Kanji - Add cards')
        self.setWindowIcon(util.default_icon())

        lyt = QGridLayout()
        self.setLayout(lyt)

        i = 0
        info_lbl = QLabel('This will create the chosen amount of kanji cards of the specified type.\n\n'\
                          'If you for example select 20 cards with "Frequency" selected, '\
                          'the first 20 unknown kanji with the highest frequency are added.\n\n'\
                          'In the beginning it is recommended that you add a few dozen cards based off the RTK order. '\
                          'After that we recommend you to use the deck learn ahead feature if you are using a premade starter deck. '\
                          'If not we recommend adding kanji based off frequency or add Kanji as you encounter them using automatic '\
                          'kanji card creation for newly added cards.\n\n'\
                          'All mentioned features can be enabled from the settings.')
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl, i, 0, 1, 2)

        i += 1

        lyt.addWidget(QLabel('<hr>'), i, 0, 1, 2)

        i += 1
        lyt.addWidget(QLabel('Type:'), i, 0)
        radio_lyt = QHBoxLayout()
        lyt.addLayout(radio_lyt, i, 1)
        self.radio_recognition = QRadioButton('Recognition')
        self.radio_recognition.setChecked(True)
        radio_lyt.addWidget(self.radio_recognition)
        self.radio_production = QRadioButton('Production')
        radio_lyt.addWidget(self.radio_production)

        i += 1
        lyt.addWidget(QLabel('Max Amount:'), i, 0)
        self.amt_box = QSpinBox()
        self.amt_box.setMinimum(1)
        self.amt_box.setMaximum(500)
        self.amt_box.setValue(10)
        lyt.addWidget(self.amt_box, i, 1)

        i += 1
        lyt.addWidget(QLabel('Select by:'), i, 0)
        self.option_box = QComboBox()
        for (label, *_) in self.options:
            self.option_box.addItem(label)
        lyt.addWidget(self.option_box, i, 1)

        i += 1
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.add_cards)
        btn_box.rejected.connect(self.reject)
        lyt.addWidget(btn_box, i, 0, 1, 2)


    def add_cards(self):

        ct = CardType.Production if self.radio_production.isChecked() else CardType.Recognition
        amt = self.amt_box.value()
        option = self.options[self.option_box.currentIndex()]
        column = option[1]
        order = option[2]
        condition = option[3]

        aqt.mw.migaku_kanji_db.recalc_user_cards(ct)
        chars = aqt.mw.migaku_kanji_db.find_next_characters(
            ct, amt, column, order, condition
        )

        if len(chars) < 1:
            QMessageBox.information(
                self,
                'Kanji Cards',
                F'You already have {ct.label} cards for all kanji in the specified selection!'
            )
            return

        r = util.error_msg_on_error(
            self,
            aqt.mw.migaku_kanji_db.make_cards_from_characters,
            ct, chars, 'Kanji Cards Addition'
        )

        aqt.mw.migaku_kanji_db.recalc_user_cards(ct)

        if r:
            QMessageBox.information(
                self,
                'Added Kanji Cards',
                F'Added {amt} {ct.name} kanji cards:\n\n{" ".join(chars)}'
            )
            self.accept()
        else:
            self.reject()


    @classmethod
    def show_modal(cls, parent=None):
        dlg = cls(parent=parent)
        return dlg.exec_()
