import aqt
import aqt.studydeck
from aqt.qt import *

from . import util
from . import config
from . import text_parser
from . import fonts
from .card_type import CardType
from .note_type_selector import CardTypeRecognizedSelectorWidget, WordRecognizedSelectorWidget
from .learn_ahead_selector import LearnAheadSelectorWidget
from .lookup_window import LookupWindow
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
        lyt_max_words.addWidget(QLabel('Maximum amount of example words on cards:'))
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

        self.hide_default_words_box = QCheckBox('Only show words from your collection, hide default words')
        self.hide_default_words_box.setChecked(self.card_type.hide_default_words)
        lyt.addWidget(self.hide_default_words_box)

        if self.card_type == CardType.Production:
            self.hide_keywords_box = QCheckBox('Hide keywords (for advanced users, if you already know the example words and recognize the Kanji well)')
            self.hide_keywords_box.setChecked(self.card_type.hide_keywords)
            lyt.addWidget(self.hide_keywords_box)

        self.add_primitives_box = QCheckBox('Automatically create cards for unknown primitives')
        self.add_primitives_box.setChecked(self.card_type.add_primitives)
        lyt.addWidget(self.add_primitives_box)

        self.auto_card_creation_box = QCheckBox('Automatically create kanji cards for unknown kanji in newly added cards (cards/fields must be setup in "Registered Fields" tab)')
        self.auto_card_creation_box.setChecked(self.card_type.auto_card_creation)
        lyt.addWidget(self.auto_card_creation_box)

        self.auto_card_creation_msg_box = QCheckBox('Confirm kanji cards that get added automatically')
        self.auto_card_creation_msg_box.setChecked(self.card_type.auto_card_creation_msg)
        lyt.addWidget(self.auto_card_creation_msg_box)

        self.auto_card_refresh_box = QCheckBox('Automatically refresh kanji cards with added words (Slows down card creation, but full recalc won\'t be required that often)')
        self.auto_card_refresh_box.setChecked(self.card_type.auto_card_refresh)
        lyt.addWidget(self.auto_card_refresh_box)

        self.stroke_order_autoplay_box = QCheckBox('Autoplay stroke order from start')
        self.stroke_order_autoplay_box.setChecked(self.card_type.stroke_order_autoplay)
        lyt.addWidget(self.stroke_order_autoplay_box)

        self.stroke_order_show_numbers_box = QCheckBox('Default show stroke order numbers')
        self.stroke_order_show_numbers_box.setChecked(self.card_type.stroke_order_show_numbers)
        lyt.addWidget(self.stroke_order_show_numbers_box)

        self.hide_readings_hover_box = QCheckBox('Hide readings of known words until hovered')
        self.hide_readings_hover_box.setChecked(self.card_type.hide_readings_hover)
        lyt.addWidget(self.hide_readings_hover_box)

        self.show_header_box = QCheckBox('Show Migaku header')
        self.show_header_box.setChecked(self.card_type.show_header)
        lyt.addWidget(self.show_header_box)

        self.learn_ahead_selector = LearnAheadSelectorWidget(self.card_type, no_margin=True)
        lyt.addWidget(self.learn_ahead_selector)

        self.note_type_selector = CardTypeRecognizedSelectorWidget(self.card_type, no_margin=True)
        lyt.addWidget(self.note_type_selector)

        reset_marked_known_btn = QPushButton('Reset Kanji Marked Known')
        reset_marked_known_btn.clicked.connect(self.on_reset_marked_known)
        lyt.addWidget(reset_marked_known_btn)

    
    def save_to_config(self):
        self.card_type.show_readings_front = self.show_readings_front_box.isChecked()
        self.card_type.words_max = self.max_words_box.value()
        self.card_type.only_custom_keywords = self.only_custom_keywords_box.isChecked()
        self.card_type.only_custom_stories = self.only_custom_stories_box.isChecked()
        self.card_type.hide_default_words = self.hide_default_words_box.isChecked()
        if self.card_type == CardType.Production:
            self.card_type.hide_keywords = self.hide_keywords_box.isChecked()
        self.card_type.add_primitives = self.add_primitives_box.isChecked()
        self.card_type.auto_card_creation = self.auto_card_creation_box.isChecked()
        self.card_type.auto_card_creation_msg = self.auto_card_creation_msg_box.isChecked()
        self.card_type.auto_card_refresh = self.auto_card_refresh_box.isChecked()
        self.card_type.stroke_order_autoplay = self.stroke_order_autoplay_box.isChecked()
        self.card_type.stroke_order_show_numbers = self.stroke_order_show_numbers_box.isChecked()
        self.card_type.hide_readings_hover = self.hide_readings_hover_box.isChecked()
        self.card_type.show_header = self.show_header_box.isChecked()
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


    def on_reset_marked_known(self):
        r = QMessageBox.question(self,
                                'Migaku Kanji',
                                F'Do you really want to reset kanji marked known for {self.card_type.label}?<br><br>'
                                '<b>They will not be recoverable.</b>',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r != QMessageBox.Yes:
            return
        aqt.mw.migaku_kanji_db.reset_marked_known(self.card_type)
        QMessageBox.information(self, 'Migaku Kanji', F'Kanji marked known for {self.card_type.label} were reset.')



class FontSelectWidget(QWidget):

    def __init__(self, idx, parent=None):
        super(QWidget, self).__init__(parent)

        self.idx = idx

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        tlyt = QHBoxLayout()
        lyt.addLayout(tlyt)

        tlyt.addWidget(QLabel(F'Font {idx+1}:'))

        self.name_lbl = QLabel()
        tlyt.addWidget(self.name_lbl)

        tlyt.addStretch()

        set_btn = QPushButton('Set')
        set_btn.clicked.connect(self.set_font)
        tlyt.addWidget(set_btn)

        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self.reset_font)
        tlyt.addWidget(reset_btn)

        self.example_lbl = QLabel('日国会年大閣海本中欧')
        self.pixel_size = self.example_lbl.font().pixelSize()
        lyt.addWidget(self.example_lbl)

        self.update()


    def set_font(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Migaku Kanji - Select Font', filter='Fonts (*.ttf *.otf)')
        if path and os.path.exists(path):
            fonts.set_path(self.idx, path)
            self.update()


    def reset_font(self):
        fonts.set_path(self.idx, None)
        self.update()


    def update(self):
        path = fonts.get_path(self.idx)
        name = os.path.splitext(os.path.basename(path))[0]
        self.name_lbl.setText(name) # fallback

        font_id = QFontDatabase.addApplicationFont(path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 40)

        self.name_lbl.setText(font_family)
        self.example_lbl.setFont(font)



class SettingsWindow(QDialog):

    KANJI_FORMS_URL = 'https://docs.google.com/spreadsheets/d/1aw0ihw0RpmejWLTUynrFYjmOfLdzcPVrDX7UM50lwBY/edit#gid=2109245908'

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Settings - ' + VERSION_STRING)
        self.setMinimumSize(920, 450)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        if self.KANJI_FORMS_URL:
            kanji_forms_lbl = QLabel(F'You can suggest changes to the Kanji dataset <a href="{self.KANJI_FORMS_URL}">here</a>.')
            kanji_forms_lbl.setWordWrap(True)
            lyt.addWidget(kanji_forms_lbl)

        if not text_parser.is_available():
            info_lbl = QLabel('<b>WARNING: The Migaku Japanese add-on is not installed or enabled. Multiple features will be unavailable.</b>')
            info_lbl.setWordWrap(True)
            lyt.addWidget(info_lbl)

        tabs = QTabWidget()
        lyt.addWidget(tabs)

        self.card_type_widgets = []

        registerd_fields_widget = QWidget()
        registerd_fields_layout = QVBoxLayout()
        registerd_fields_widget.setLayout(registerd_fields_layout)

        self.words_recognized = WordRecognizedSelectorWidget(no_margin=True)
        registerd_fields_layout.addWidget(self.words_recognized)

        self.only_seen_words_box = QCheckBox('Only use words from already seen cards as example words (Beta)')
        self.only_seen_words_box.setChecked(config.get('only_seen_words', False))
        registerd_fields_layout.addWidget(self.only_seen_words_box)

        tabs.addTab(registerd_fields_widget, 'Registered Fields')

        for ct in CardType:
            ct_widget = CardTypeSettingsWidget(ct)
            self.card_type_widgets.append(ct_widget)
            tabs.addTab(ct_widget, ct.name)
    
        lookup_tab = QWidget()
        tabs.addTab(lookup_tab, 'Lookup Window')

        lookup_lyt = QVBoxLayout()
        lookup_tab.setLayout(lookup_lyt)

        self.lookup_stroke_order_autoplay_box = QCheckBox('Autoplay stroke order from start')
        self.lookup_stroke_order_autoplay_box.setChecked(config.get('lookup_stroke_order_autoplay', False))
        lookup_lyt.addWidget(self.lookup_stroke_order_autoplay_box)

        self.lookup_stroke_order_show_numbers_box = QCheckBox('Default show stroke order numbers')
        self.lookup_stroke_order_show_numbers_box.setChecked(config.get('lookup_stroke_order_show_numbers', False))
        lookup_lyt.addWidget(self.lookup_stroke_order_show_numbers_box)

        self.lookup_hide_readings_hover_box = QCheckBox('Hide readings of known words until hovered')
        self.lookup_hide_readings_hover_box.setChecked(config.get('lookup_hide_readings_hover', False))
        lookup_lyt.addWidget(self.lookup_hide_readings_hover_box)

        self.lookup_show_header_box = QCheckBox('Show Migaku header')
        self.lookup_show_header_box.setChecked(config.get('lookup_show_header', True))
        lookup_lyt.addWidget(self.lookup_show_header_box)

        lookup_lyt.addStretch()

        general_tab = QWidget()
        tabs.addTab(general_tab, 'General')

        general_lyt = QVBoxLayout()
        general_tab.setLayout(general_lyt)

        for i in range(fonts.font_num):
            general_lyt.addWidget(
                FontSelectWidget(i)
            )

        general_lyt.addStretch()

        reset_custom_keywords_btn = QPushButton('Reset Custom Keywords')
        reset_custom_keywords_btn.clicked.connect(self.on_reset_custom_keywords)
        general_lyt.addWidget(reset_custom_keywords_btn)

        reset_custom_stories_btn = QPushButton('Reset Custom Stories')
        reset_custom_stories_btn.clicked.connect(self.on_reset_custom_stories)
        general_lyt.addWidget(reset_custom_stories_btn)

        reset_db_btn = QPushButton('Reset Database')
        reset_db_btn.clicked.connect(self.on_reset_db)
        general_lyt.addWidget(reset_db_btn)


    def closeEvent(self, event):
        self.words_recognized.save_to_config()
        config.set('only_seen_words', self.only_seen_words_box.isChecked())
        for ct_widget in self.card_type_widgets:
            ct_widget.save_to_config()
        config.set('lookup_stroke_order_autoplay', self.lookup_stroke_order_autoplay_box.isChecked())
        config.set('lookup_stroke_order_show_numbers', self.lookup_stroke_order_show_numbers_box.isChecked())
        config.set('lookup_hide_readings_hover', self.lookup_hide_readings_hover_box.isChecked())
        config.set('lookup_show_header', self.lookup_show_header_box.isChecked())
        config.write()

        for ct in CardType:
            aqt.mw.migaku_kanji_db.recalc_user_cards(ct)

        CardType.upsert_all_models()


    def on_reset_db(self):
        r = QMessageBox.question(self,
                                'Migaku Kanji',
                                'Do you really want to reset the Migaku Kanji Database?<br><br>'
                                '<b>All kanji manually marked known, custom stories and keywords will be lost!</b><br><br>'
                                'Kanji cards and their progress will remain.',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r != QMessageBox.Yes:
            return
        aqt.mw.migaku_kanji_db.reset()
        QMessageBox.information(self, 'Migaku Kanji', 'The Migaku Kanji database was reset.')


    def on_reset_custom_keywords(self):
        r = QMessageBox.question(self,
                                'Migaku Kanji',
                                'Do you really want to reset all custom keywords?<br><br>'
                                '<b>They will not be recoverable.</b>',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r != QMessageBox.Yes:
            return
        aqt.mw.migaku_kanji_db.reset_custom_keywods()
        QMessageBox.information(self, 'Migaku Kanji', 'Custom keywords were reset.')


    def on_reset_custom_stories(self):
        r = QMessageBox.question(self,
                                'Migaku Kanji',
                                'Do you really want to reset all custom stories?<br><br>'
                                '<b>They will not be recoverable.</b>',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r != QMessageBox.Yes:
            return
        aqt.mw.migaku_kanji_db.reset_custom_stories()
        QMessageBox.information(self, 'Migaku Kanji', 'Custom stories were reset.')
        


    @classmethod
    def show_modal(cls, parent=None):
        LookupWindow.close_instance()     # To make sure everything updates
        dlg = cls(parent=parent)
        return dlg.exec_()
