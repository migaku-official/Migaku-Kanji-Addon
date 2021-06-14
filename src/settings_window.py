import aqt
import aqt.studydeck
from aqt.qt import *

from . import util
from . import config
from . import text_parser
from .card_type import CardType
from .note_type_selector import CardTypeRecognizedSelectorWidget, WordRecognizedSelectorWidget
from .learn_ahead_selector import LearnAheadSelectorWidget
from .version import VERSION_STRING


class CardTypeSettingsWidget(QWidget):

    def __init__(self, card_type):
        super(QWidget, self).__init__()

        self.card_type = card_type

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        deck_lyt = QHBoxLayout()
        lyt.addLayout(deck_lyt)

        deck_lyt.addWidget(QLabel('Deck for new cards:'))
        self.deck_btn = QPushButton(self.card_type.deck_name or '<None>')
        self.deck_btn.clicked.connect(self.on_deck_click)
        deck_lyt.addWidget(self.deck_btn)
        deck_lyt.addStretch()

        self.show_readings_front_box = QCheckBox('Show example word readings on the front of cards')
        self.show_readings_front_box.setChecked(self.card_type.show_readings_front)
        lyt.addWidget(self.show_readings_front_box)

        lyt_max_words = QHBoxLayout()
        lyt.addLayout(lyt_max_words)
        lyt_max_words.addWidget(QLabel('Maxium amount of example words on cards:'))
        self.max_words_box = QSpinBox()
        self.max_words_box.setMinimum(0)
        self.max_words_box.setMaximum(10)
        self.max_words_box.setValue(self.card_type.words_max)
        lyt_max_words.addWidget(self.max_words_box)
        lyt_max_words.addStretch()

        self.only_custom_keywords_box = QCheckBox('If a custom keyword is set, hide predefined keywords')
        self.only_custom_keywords_box.setChecked(self.card_type.only_custom_keywords)
        lyt.addWidget(self.only_custom_keywords_box)

        self.only_custom_stories_box = QCheckBox('If a custom story is set, hide predefined stories')
        self.only_custom_stories_box.setChecked(self.card_type.only_custom_stories)
        lyt.addWidget(self.only_custom_stories_box)

        self.add_primitives_box = QCheckBox('Automatically create cards for unknown primitives')
        self.add_primitives_box.setChecked(self.card_type.add_primitives)
        lyt.addWidget(self.add_primitives_box)

        self.auto_card_creation_box = QCheckBox('Automatically create kanji cards for unknown kanji in newly added cards (cards/fields must be setup in "Registered Fields" tab)')
        self.auto_card_creation_box.setChecked(self.card_type.auto_card_creation)
        lyt.addWidget(self.auto_card_creation_box)

        self.auto_card_creation_msg_box = QCheckBox('Show a notification if kanji cards get added automatically')
        self.auto_card_creation_msg_box.setChecked(self.card_type.auto_card_creation_msg)
        lyt.addWidget(self.auto_card_creation_msg_box)

        self.auto_card_refresh_box = QCheckBox('Automatically refresh kanji cards with added words (Slows down card creation, but full recalc won\'t be required that often)')
        self.auto_card_refresh_box.setChecked(self.card_type.auto_card_refresh)
        lyt.addWidget(self.auto_card_refresh_box)

        self.learn_ahead_selector = LearnAheadSelectorWidget(self.card_type, no_margin=True)
        lyt.addWidget(self.learn_ahead_selector)

        self.note_type_selector = CardTypeRecognizedSelectorWidget(self.card_type, no_margin=True)
        lyt.addWidget(self.note_type_selector)

    
    def save_to_config(self):
        self.card_type.show_readings_front = self.show_readings_front_box.isChecked()
        self.card_type.words_max = self.max_words_box.value()
        self.card_type.only_custom_keywords = self.only_custom_keywords_box.isChecked()
        self.card_type.only_custom_stories = self.only_custom_stories_box.isChecked()
        self.card_type.add_primitives = self.add_primitives_box.isChecked()
        self.card_type.auto_card_creation = self.auto_card_creation_box.isChecked()
        self.card_type.auto_card_creation_msg = self.auto_card_creation_msg_box.isChecked()
        self.card_type.auto_card_refresh = self.auto_card_refresh_box.isChecked()
        self.learn_ahead_selector.save_to_config()
        self.note_type_selector.save_to_config()

        aqt.mw.migaku_kanji_db.refresh_learn_ahead()


    def on_deck_click(self):
        r = aqt.studydeck.StudyDeck(
            mw=aqt.mw, 
            parent=self,
            title=F'Select deck for {self.card_type.label} cards',
            accept='Choose',
            current=self.card_type.deck_name,
            cancel=False,
        )

        if r.name:
            self.card_type.deck_name = r.name
            self.deck_btn.setText(self.card_type.deck_name or '<None>')



class SettingsWindow(QDialog):

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Settings - ' + VERSION_STRING)
        self.setMinimumSize(920, 450)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        if not text_parser.is_available():
            info_lbl = QLabel('<b>WARNING: The Migaku Japanese add-on is not installed or enabled. Multiple features will be unavailable.</b>')
            info_lbl.setWordWrap(True)
            lyt.addWidget(info_lbl)

        tabs = QTabWidget()
        lyt.addWidget(tabs)

        self.card_type_widgets = []

        self.words_recognized = WordRecognizedSelectorWidget()
        tabs.addTab(self.words_recognized, 'Registered Fields')

        for ct in CardType:
            ct_widget = CardTypeSettingsWidget(ct)
            self.card_type_widgets.append(ct_widget)
            tabs.addTab(ct_widget, ct.name)


    def closeEvent(self, event):
        self.words_recognized.save_to_config()
        for ct_widget in self.card_type_widgets:
            ct_widget.save_to_config()
        config.write()

        for ct in CardType:
            aqt.mw.migaku_kanji_db.recalc_user_cards(ct)

        CardType.upsert_all_models()



    @classmethod
    def show_modal(cls, parent=None):
        dlg = cls(parent=parent)
        return dlg.exec_()
