import aqt
from aqt.qt import *

from . import util
from .card_type import CardType


class AddCardsDialog(QDialog):
    # Label, column, order, condition
    options = [
        ("Frequency", "frequency_rank", "ASC", "< 999999"),
        ("RTK 1-5 Order", "heisig_id5", "ASC", "NOT NULL"),
        ("RTK 6+ Order", "heisig_id6", "ASC", "NOT NULL"),
        ("JLPT", "jlpt", "DESC", "NOT NULL"),
        ("Kanken", "kanken", "DESC", "NOT NULL"),
        ("School Year", "grade", "ASC", "NOT NULL"),
        ("WaniKani", "wk", "ASC", "NOT NULL"),
    ]

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle("Migaku Kanji - Add cards")
        self.setWindowIcon(util.default_icon())

        lyt = QGridLayout()
        self.setLayout(lyt)

        i = 0
        info_lbl = QLabel(
            "This will create the chosen amount of kanji cards of the specified type.\n\n"
            'If you for example select 20 cards with "Frequency" selected, '
            "the first 20 unknown kanji with the highest frequency are added.\n\n"
            "In the beginning it is recommended that you add a few dozen cards based off the RTK order. "
            "After that we recommend you to use the deck learn ahead feature if you are using a premade starter deck. "
            "If not we recommend adding kanji based off frequency or add Kanji as you encounter them using automatic "
            "kanji card creation for newly added cards.\n\n"
            "All mentioned features can be enabled from the settings."
        )
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl, i, 0, 1, 2)

        i += 1

        lyt.addWidget(QLabel("<hr>"), i, 0, 1, 2)

        i += 1
        lyt.addWidget(QLabel("Type:"), i, 0)
        radio_lyt = QHBoxLayout()
        lyt.addLayout(radio_lyt, i, 1)
        self.radio_recognition = QRadioButton("Recognition")
        self.radio_recognition.setChecked(True)
        radio_lyt.addWidget(self.radio_recognition)
        self.radio_production = QRadioButton("Production")
        radio_lyt.addWidget(self.radio_production)

        i += 1
        lyt.addWidget(QLabel("Max Amount:"), i, 0)
        self.amt_box = QSpinBox()
        self.amt_box.setMinimum(1)
        self.amt_box.setMaximum(500)
        self.amt_box.setValue(10)
        lyt.addWidget(self.amt_box, i, 1)

        i += 1
        lyt.addWidget(QLabel("Select by:"), i, 0)
        self.option_box = QComboBox()
        for label, *_ in self.options:
            self.option_box.addItem(label)
        self.option_box.addItem("Manual Selection")
        self.option_box.currentIndexChanged.connect(self.on_option_changed)
        lyt.addWidget(self.option_box, i, 1)

        i += 1
        self.manual_box = QPlainTextEdit()
        self.manual_box.setPlaceholderText(
            "Enter kanji that should be added.\n\n"
            "Non kanji characters, duplicates and kanji you already know are ignored.\n\n"
            "You can also paste any text of which you want to learn all kanji."
        )
        self.manual_box.setHidden(True)
        lyt.addWidget(self.manual_box, i, 0, 1, 2)

        i += 1
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.add_cards)
        btn_box.rejected.connect(self.reject)
        lyt.addWidget(btn_box, i, 0, 1, 2)

        self.update_fixed_size()

    def update_fixed_size(self):
        self.setFixedSize(self.sizeHint())

    def is_manual_selected(self):
        return self.option_box.currentIndex() == len(self.options)

    def on_option_changed(self, idx):
        is_manual = self.is_manual_selected()
        self.amt_box.setEnabled(not is_manual)
        self.manual_box.setHidden(not is_manual)
        self.update_fixed_size()

    def add_cards(self):
        ct = (
            CardType.Production
            if self.radio_production.isChecked()
            else CardType.Recognition
        )

        aqt.mw.migaku_kanji_db.recalc_user_cards(ct)

        if self.is_manual_selected():
            text = self.manual_box.toPlainText().strip()

            if not text:
                QMessageBox.information(
                    self,
                    "Kanji Cards",
                    "Please enter the kanji you want to learn in the text box.",
                )
                return

            new_chars = aqt.mw.migaku_kanji_db.new_characters(
                ct, util.unique_characters(text)
            )

        else:
            amt = self.amt_box.value()
            option = self.options[self.option_box.currentIndex()]
            column = option[1]
            order = option[2]
            condition = option[3]

            new_chars = aqt.mw.migaku_kanji_db.find_next_characters(
                ct, amt, column, order, condition
            )

        add_amt = len(new_chars)

        if add_amt < 1:
            QMessageBox.information(
                self,
                "Kanji Cards",
                f"You already have {ct.label} cards for all kanji in the specified selection!",
            )
            return

        r = util.error_msg_on_error(
            self,
            aqt.mw.migaku_kanji_db.make_cards_from_characters,
            ct,
            new_chars,
            "Kanji Cards Addition",
        )

        aqt.mw.migaku_kanji_db.recalc_user_cards(ct)

        if r:
            QMessageBox.information(
                self,
                "Added Kanji Cards",
                f'Added {add_amt} {ct.name} kanji cards:\n\n{" ".join(new_chars)}',
            )
            self.accept()
        else:
            self.reject()

    @classmethod
    def show_modal(cls, parent=None):
        dlg = cls(parent=parent)
        return dlg.exec()
