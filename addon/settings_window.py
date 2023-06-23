import aqt
import aqt.studydeck
from aqt.qt import *

from . import util
from . import config
from . import text_parser
from . import fonts
from .card_type import CardType
from .note_type_selector import (
    CardTypeRecognizedSelectorWidget,
    WordRecognizedSelectorWidget,
)
from .learn_ahead_selector import LearnAheadSelectorWidget
from .lookup_window import LookupWindow
from .version import VERSION_STRING
from .kanji_forms_url import KANJI_FORMS_URL


def lyt_add_with_label(lyt, widget: QWidget, label: str):
    sub_lyt = QHBoxLayout()
    sub_lyt.addWidget(QLabel(label))
    sub_lyt.addWidget(widget)
    sub_lyt.addStretch()
    lyt.addLayout(sub_lyt)


class CardTypeSettingsWidget(QWidget):
    def __init__(self, card_type):
        super(QWidget, self).__init__()

        self.card_type = card_type

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        deck_lyt = QHBoxLayout()
        lyt.addLayout(deck_lyt)

        deck_lyt.addWidget(QLabel("Deck for new cards:"))
        self.deck_btn = QPushButton(self.card_type.deck_name or "<None>")
        self.deck_btn.clicked.connect(self.on_deck_click)
        deck_lyt.addWidget(self.deck_btn)
        deck_lyt.addStretch()

        self.show_readings_front_box = QCheckBox(
            "Show example word readings on the front of cards"
        )
        self.show_readings_front_box.setChecked(self.card_type.show_readings_front)
        lyt.addWidget(self.show_readings_front_box)

        lyt_max_words = QHBoxLayout()
        lyt.addLayout(lyt_max_words)
        lyt_max_words.addWidget(QLabel("Maximum amount of example words on cards:"))
        self.max_words_box = QSpinBox()
        self.max_words_box.setMinimum(0)
        self.max_words_box.setMaximum(10)
        self.max_words_box.setValue(self.card_type.words_max)
        lyt_max_words.addWidget(self.max_words_box)
        lyt_max_words.addStretch()

        self.only_custom_keywords_box = QCheckBox(
            "If a custom keyword is set, hide predefined keywords"
        )
        self.only_custom_keywords_box.setChecked(self.card_type.only_custom_keywords)
        lyt.addWidget(self.only_custom_keywords_box)

        self.only_custom_stories_box = QCheckBox(
            "If a custom story is set, hide predefined stories"
        )
        self.only_custom_stories_box.setChecked(self.card_type.only_custom_stories)
        lyt.addWidget(self.only_custom_stories_box)

        self.hide_default_words_box = QCheckBox(
            "Only show seen words from your collection, hide unseen and default words"
        )
        self.hide_default_words_box.setChecked(self.card_type.hide_default_words)
        lyt.addWidget(self.hide_default_words_box)

        if self.card_type == CardType.Production:
            self.hide_keywords_box = QCheckBox(
                "Hide keywords (for advanced users, if you already know the example words and recognize the Kanji well)"
            )
            self.hide_keywords_box.setChecked(self.card_type.hide_keywords)
            lyt.addWidget(self.hide_keywords_box)

        self.add_primitives_box = QCheckBox(
            "Automatically create cards for unknown primitives"
        )
        self.add_primitives_box.setChecked(self.card_type.add_primitives)
        lyt.addWidget(self.add_primitives_box)

        self.auto_card_creation_box = QCheckBox(
            'Automatically create kanji cards for unknown kanji in newly added cards (cards/fields must be setup in "Registered Fields" tab)'
        )
        self.auto_card_creation_box.setChecked(self.card_type.auto_card_creation)
        lyt.addWidget(self.auto_card_creation_box)

        self.auto_card_creation_msg_box = QCheckBox(
            "Confirm kanji cards that get added automatically"
        )
        self.auto_card_creation_msg_box.setChecked(
            self.card_type.auto_card_creation_msg
        )
        lyt.addWidget(self.auto_card_creation_msg_box)

        self.auto_card_refresh_box = QCheckBox(
            "Automatically refresh kanji cards with added words (Slows down card creation, but full recalc won't be required that often)"
        )
        self.auto_card_refresh_box.setChecked(self.card_type.auto_card_refresh)
        lyt.addWidget(self.auto_card_refresh_box)

        self.stroke_order_mode_box = QComboBox()
        self.stroke_order_mode_box.addItem("Start fully drawn", "fully_drawn")
        self.stroke_order_mode_box.addItem("Draw strokes one by one", "auto")
        self.stroke_order_mode_box.addItem("Draw all strokes at once", "auto_all")
        self.stroke_order_mode_box.setCurrentIndex(
            self.stroke_order_mode_box.findData(self.card_type.stroke_order_mode)
        )
        lyt_add_with_label(
            lyt, self.stroke_order_mode_box, "Stroke order diagram play mode:"
        )

        self.stroke_order_show_numbers_box = QCheckBox(
            "Default show stroke order numbers"
        )
        self.stroke_order_show_numbers_box.setChecked(
            self.card_type.stroke_order_show_numbers
        )
        lyt.addWidget(self.stroke_order_show_numbers_box)

        self.hide_readings_hover_box = QCheckBox(
            "Hide readings of known words until hovered"
        )
        self.hide_readings_hover_box.setChecked(self.card_type.hide_readings_hover)
        lyt.addWidget(self.hide_readings_hover_box)

        self.show_header_box = QCheckBox("Show Migaku header")
        self.show_header_box.setChecked(self.card_type.show_header)
        lyt.addWidget(self.show_header_box)

        self.show_radicals_box = QCheckBox("Show dictionary radicals")
        self.show_radicals_box.setChecked(self.card_type.show_radicals)
        lyt.addWidget(self.show_radicals_box)

        self.learn_ahead_selector = LearnAheadSelectorWidget(
            self.card_type, no_margin=True
        )
        lyt.addWidget(self.learn_ahead_selector)

        self.note_type_selector = CardTypeRecognizedSelectorWidget(
            self.card_type, no_margin=True
        )
        lyt.addWidget(self.note_type_selector)

        reset_marked_known_btn = QPushButton("Reset Kanji Marked Known")
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
        self.card_type.auto_card_creation_msg = (
            self.auto_card_creation_msg_box.isChecked()
        )
        self.card_type.auto_card_refresh = self.auto_card_refresh_box.isChecked()
        self.card_type.stroke_order_mode = str(self.stroke_order_mode_box.currentData())
        self.card_type.stroke_order_show_numbers = (
            self.stroke_order_show_numbers_box.isChecked()
        )
        self.card_type.hide_readings_hover = self.hide_readings_hover_box.isChecked()
        self.card_type.show_header = self.show_header_box.isChecked()
        self.card_type.show_radicals = self.show_radicals_box.isChecked()
        self.learn_ahead_selector.save_to_config()
        self.note_type_selector.save_to_config()

        aqt.mw.migaku_kanji_db.refresh_learn_ahead()

    def on_deck_click(self):
        r = aqt.studydeck.StudyDeck(
            mw=aqt.mw,
            parent=self,
            title=f"Select deck for {self.card_type.label} cards",
            accept="Choose",
            current=self.card_type.deck_name,
            cancel=False,
        )

        if r.name:
            self.card_type.deck_name = r.name
            self.deck_btn.setText(self.card_type.deck_name or "<None>")

    def on_reset_marked_known(self):
        r = QMessageBox.question(
            self,
            "Migaku Kanji",
            f"Do you really want to reset kanji marked known for {self.card_type.label}?<br><br>"
            "<b>They will not be recoverable.</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        aqt.mw.migaku_kanji_db.reset_marked_known(self.card_type)
        QMessageBox.information(
            self,
            "Migaku Kanji",
            f"Kanji marked known for {self.card_type.label} were reset.",
        )


class FontSelectWidget(QWidget):
    def __init__(self, idx, parent=None):
        super(QWidget, self).__init__(parent)

        self.idx = idx

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        tlyt = QHBoxLayout()
        lyt.addLayout(tlyt)

        tlyt.addWidget(QLabel(f"Font {idx+1}:"))

        self.name_lbl = QLabel()
        tlyt.addWidget(self.name_lbl)

        tlyt.addStretch()

        set_btn = QPushButton("Set")
        set_btn.clicked.connect(self.set_font)
        tlyt.addWidget(set_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_font)
        tlyt.addWidget(reset_btn)

        self.example_lbl = QLabel()
        lyt.addWidget(self.example_lbl)

        self.update()

    def set_font(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Migaku Kanji - Select Font", filter="Fonts (*.ttf *.otf)"
        )
        if path and os.path.exists(path):
            fonts.set_path(self.idx, path)
            self.update()

    def reset_font(self):
        fonts.set_path(self.idx, None)
        self.update()

    def update(self):
        path = fonts.get_path(self.idx)

        font_id = QFontDatabase.addApplicationFont(path)
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font_family = font_families[0]
            font = QFont(font_family, 40)
            self.example_lbl.setFont(font)
            self.name_lbl.setText(font_family)
            self.example_lbl.setText("日国会年大閣海本中欧")
        else:
            name = os.path.splitext(os.path.basename(path))[0]
            self.name_lbl.setText(name)
            font = QFont()
            font.setPointSize(40)
            self.example_lbl.setFont(font)
            self.example_lbl.setText("(No preview available)")


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle("Migaku Kanji - Settings")
        self.setMinimumSize(920, 450)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        if not text_parser.is_available():
            info_lbl = QLabel(
                "<b>WARNING: MeCab failed to initialize. Multiple features will be unavailable.</b>"
            )
            info_lbl.setWordWrap(True)
            lyt.addWidget(info_lbl)

        tabs = QTabWidget()
        lyt.addWidget(tabs)

        def add_tab_scrollable(widget, name):
            scroll_widget = QScrollArea()
            scroll_widget.setWidget(widget)
            scroll_widget.setWidgetResizable(True)
            tabs.addTab(scroll_widget, name)

        self.card_type_widgets = []

        registerd_fields_widget = QWidget()
        registerd_fields_layout = QVBoxLayout()
        registerd_fields_widget.setLayout(registerd_fields_layout)

        self.words_recognized = WordRecognizedSelectorWidget(no_margin=True)
        registerd_fields_layout.addWidget(self.words_recognized)

        add_tab_scrollable(registerd_fields_widget, "Registered Fields")

        for ct in CardType:
            ct_widget = CardTypeSettingsWidget(ct)
            self.card_type_widgets.append(ct_widget)
            add_tab_scrollable(ct_widget, ct.name)

        lookup_tab = QWidget()
        add_tab_scrollable(lookup_tab, "Lookup Window")

        lookup_lyt = QVBoxLayout()
        lookup_tab.setLayout(lookup_lyt)

        self.lookup_stroke_order_mode_box = QComboBox()
        self.lookup_stroke_order_mode_box.addItem("Start fully drawn", "fully_drawn")
        self.lookup_stroke_order_mode_box.addItem("Draw strokes one by one", "auto")
        self.lookup_stroke_order_mode_box.addItem(
            "Draw all strokes at once", "auto_all"
        )
        self.lookup_stroke_order_mode_box.setCurrentIndex(
            self.lookup_stroke_order_mode_box.findData(
                config.get("lookup_stroke_order_mode", "fully_drawn")
            )
        )
        lyt_add_with_label(
            lookup_lyt,
            self.lookup_stroke_order_mode_box,
            "Stroke order diagram play mode:",
        )

        self.lookup_stroke_order_show_numbers_box = QCheckBox(
            "Default show stroke order numbers"
        )
        self.lookup_stroke_order_show_numbers_box.setChecked(
            config.get("lookup_stroke_order_show_numbers", False)
        )
        lookup_lyt.addWidget(self.lookup_stroke_order_show_numbers_box)

        self.lookup_hide_readings_hover_box = QCheckBox(
            "Hide readings of known words until hovered"
        )
        self.lookup_hide_readings_hover_box.setChecked(
            config.get("lookup_hide_readings_hover", False)
        )
        lookup_lyt.addWidget(self.lookup_hide_readings_hover_box)

        self.lookup_show_header_box = QCheckBox("Show Migaku header")
        self.lookup_show_header_box.setChecked(config.get("lookup_show_header", True))
        lookup_lyt.addWidget(self.lookup_show_header_box)

        self.lookup_show_radicals_box = QCheckBox("Show dictionary radicals")
        self.lookup_show_radicals_box.setChecked(
            config.get("lookup_show_radicals", False)
        )
        lookup_lyt.addWidget(self.lookup_show_radicals_box)

        lookup_lyt.addStretch()

        general_tab = QWidget()
        add_tab_scrollable(general_tab, "General")

        general_lyt = QVBoxLayout()
        general_tab.setLayout(general_lyt)

        for i in range(fonts.font_num):
            general_lyt.addWidget(FontSelectWidget(i))

        general_lyt.addStretch()

        reset_custom_keywords_btn = QPushButton("Reset Custom Keywords")
        reset_custom_keywords_btn.clicked.connect(self.on_reset_custom_keywords)
        general_lyt.addWidget(reset_custom_keywords_btn)

        reset_custom_stories_btn = QPushButton("Reset Custom Stories")
        reset_custom_stories_btn.clicked.connect(self.on_reset_custom_stories)
        general_lyt.addWidget(reset_custom_stories_btn)

        reset_db_btn = QPushButton("Reset Database")
        reset_db_btn.clicked.connect(self.on_reset_db)
        general_lyt.addWidget(reset_db_btn)

        about_tab = QWidget()
        add_tab_scrollable(about_tab, "About")

        about_lyt = QVBoxLayout()
        about_tab.setLayout(about_lyt)

        about_lbl = QLabel(
            f"<h2>Migaku Kanji GOD - {VERSION_STRING}</h2>"
            f'<p>You can suggest changes to the Kanji dataset <a href="{KANJI_FORMS_URL}">here</a>.</p>'
            "<h3>Third-Party Libraries</h3>"
            "<p>Migaku Kanji uses several third-party libraries to function. Below are links to homepages and licenses of these:</p>"
            '<p><a href="https://mbilbille.github.io/dmak/">Draw Me A Kanji (dmak.js)</a> is used for the kanji diagram, and was created by Matthieu Bilbille and released under the <a href="https://github.com/mbilbille/dmak/blob/master/LICENSE">MIT</a> license.</p>'
            '<p>DMAK uses <a href="https://dmitrybaranovskiy.github.io/raphael/">Raphaël</a>, which is copyright © 2008-2013 Dmitry Baranovskiy, Sencha Labs and released under the <a href="http://dmitrybaranovskiy.github.io/raphael/license.html">MIT</a> license.</p>'
            '<p>DMAK also uses <a href="http://kanjivg.tagaini.net/">KanjiVG</a>, which is copyright © 2009-2018 Ulrich Apel and released under the <a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share Alike 3.0</a> license.</p>'
            '<p><a href="https://foosoft.net/projects/yomichan/">Yomichan</a> is used for distributing furigana, and is copyright © 2016-2021 Yomichan Authors and released under the <a href="https://github.com/FooSoft/yomichan/blob/master/LICENSE">GNU General Public License</a>.</p>'
            '<p><a href="https://taku910.github.io/mecab/">MeCab</a> is used for parsing Japanese text, and was created by Taku Kudo and the Nippon Telegraph and Telephone Corporation and released under the <a href="https://github.com/taku910/mecab/blob/master/mecab/GPL">GPL</a>, <a href="https://github.com/taku910/mecab/blob/master/mecab/LGPL">LGPL</a> and <a href="https://github.com/taku910/mecab/blob/master/mecab/BSD">BSD</a> licenses.</p>'
            '<p><a href="https://ccd.ninjal.ac.jp/unidic/">UniDic</a> is used as dictionary for MeCab, and is copyright © 2011-2021 The UniDic Consortium and released under the <a href="https://ccd.ninjal.ac.jp/unidic/copying/GPL">GPL</a>, <a href="https://ccd.ninjal.ac.jp/unidic/copying/LGPL">LGPL</a> and <a href="https://ccd.ninjal.ac.jp/unidic/copying/BSD">BSD</a> licenses.</p>'
            "<h3>License</h3>"
            '<p><a href="https://github.com/migaku-official/Migaku-Kanji-Addon">Migaku Kanji GOD</a> is copyright © 2022 Migaku Ltd. and released under the <a href="https://github.com/migaku-official/Migaku-Kanji-Addon/blob/main/LICENCE">GNU General Public License v3.0</a>.</p>'
        )
        about_lbl.setWordWrap(True)
        about_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        about_lbl.linkActivated.connect(aqt.utils.openLink)

        about_lyt.addWidget(about_lbl)
        about_lyt.addStretch()

    def closeEvent(self, event):
        self.words_recognized.save_to_config()
        for ct_widget in self.card_type_widgets:
            ct_widget.save_to_config()
        config.set(
            "lookup_stroke_order_mode",
            str(self.lookup_stroke_order_mode_box.currentData()),
        )
        config.set(
            "lookup_stroke_order_show_numbers",
            self.lookup_stroke_order_show_numbers_box.isChecked(),
        )
        config.set(
            "lookup_hide_readings_hover",
            self.lookup_hide_readings_hover_box.isChecked(),
        )
        config.set("lookup_show_header", self.lookup_show_header_box.isChecked())
        config.set("lookup_show_radicals", self.lookup_show_radicals_box.isChecked())
        config.write()

        for ct in CardType:
            aqt.mw.migaku_kanji_db.recalc_user_cards(ct)

        CardType.upsert_all_models()

    def on_reset_db(self):
        r = QMessageBox.question(
            self,
            "Migaku Kanji",
            "Do you really want to reset the Migaku Kanji Database?<br><br>"
            "<b>All kanji manually marked known, custom stories and keywords will be lost!</b><br><br>"
            "Kanji cards and their progress will remain.",
            QMessageBox.StandardButton.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        aqt.mw.migaku_kanji_db.reset()
        QMessageBox.information(
            self, "Migaku Kanji", "The Migaku Kanji database was reset."
        )

    def on_reset_custom_keywords(self):
        r = QMessageBox.question(
            self,
            "Migaku Kanji",
            "Do you really want to reset all custom keywords?<br><br>"
            "<b>They will not be recoverable.</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        aqt.mw.migaku_kanji_db.reset_custom_keywods()
        QMessageBox.information(self, "Migaku Kanji", "Custom keywords were reset.")

    def on_reset_custom_stories(self):
        r = QMessageBox.question(
            self,
            "Migaku Kanji",
            "Do you really want to reset all custom stories?<br><br>"
            "<b>They will not be recoverable.</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        aqt.mw.migaku_kanji_db.reset_custom_stories()
        QMessageBox.information(self, "Migaku Kanji", "Custom stories were reset.")

    @classmethod
    def show_modal(cls, parent=None):
        LookupWindow.close_instance()  # To make sure everything updates
        dlg = cls(parent=parent)
        return dlg.exec()
