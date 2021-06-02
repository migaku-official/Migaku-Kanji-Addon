import json
import base64
from collections import OrderedDict

import anki
import aqt
from aqt.qt import *

from . import util
from .card_type import CardType



class LookupWindow(QDialog):

    instance = None

    addon_web_uri = F'/_addons/{__name__.split(".")[0]}'    # uhhhhh
    kanjivg_uri = addon_web_uri + '/kanjivg/'

    @classmethod
    def web_uri(cls, name):
        return cls.addon_web_uri + '/web/' + name

    @classmethod
    def font_uri(cls, name):
        return cls.addon_web_uri + '/fonts/' + name


    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle('Migaku Kanji - Lookup')
        self.setWindowIcon(util.default_icon())
        self.setMinimumSize(400, 300)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        search_lyt = QHBoxLayout()
        lyt.addLayout(search_lyt)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('字')
        self.search_bar.returnPressed.connect(self.on_search_submit)
        search_lyt.addWidget(self.search_bar)

        search_btn = QPushButton('🔍')
        search_btn.setFixedWidth(search_btn.sizeHint().height())
        search_btn.clicked.connect(self.on_search_submit)
        search_lyt.addWidget(search_btn)

        self.keep_tab_on_search_box = QCheckBox('Keep tabs open')
        self.keep_tab_on_search_box.setChecked(False)
        search_lyt.addWidget(self.keep_tab_on_search_box)

        results_lyt = QVBoxLayout()
        results_lyt.setSpacing(0)
        results_lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addLayout(results_lyt)

        self.tab_bar = QTabBar()
        self.tab_bar.setAutoHide(True)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.currentChanged.connect(self.on_tab_change)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_bar.customContextMenuRequested.connect(self.on_tab_bar_context_menu_request)
        results_lyt.addWidget(self.tab_bar)


        def read_web_file(name):
            return open(util.addon_path('web', name), 'r', encoding='UTF-8').read()

        self.web = aqt.webview.AnkiWebView()

        # this mess isn't needed with updated styles fix eventually~~~ can also use bundled jquery then lol
        bundled_js = self.web.bundledScript('webview.js')

        html_head = \
             '<head>' \
            F'{aqt.mw.baseHTML()}' \
            F'{bundled_js}' \
             '<style>\n' \
            F'@font-face {{ font-family: Rubik; src: url("{self.font_uri("Rubik.ttf")}"); }}\n' \
            F'@font-face {{ font-family: kanji_font1; src: url("{self.font_uri("NotoSerifJP.otf")}"); }}\n' \
            F'@font-face {{ font-family: kanji_font2; src: url("{self.font_uri("NotoSansJP.otf")}"); }}\n' \
            F'@font-face {{ font-family: kanji_font3; src: url("{self.font_uri("HachiMaruPop.ttf")}"); }}\n' \
            F'@font-face {{ font-family: kanji_font4; src: url("{self.font_uri("ArmedLemon.ttf")}"); }}\n' \
             '\n</style>' \
            F'<link rel="stylesheet" href="{self.web_uri("lookup_style.css")}">' \
            F'<script src="{self.web_uri("jquery.js")}"></script>' \
            F'<script src="{self.web_uri("raphael.js")}"></script>' \
            F'<script src="{self.web_uri("dmak.js")}"></script>' \
            F'<script>let kanjivg_uri="{self.kanjivg_uri}";</script>' \
             '</head>'

        html_body = read_web_file('lookup.html')

        style_class = 'dark' if aqt.theme.theme_manager.night_mode else 'light'

        self.web.onBridgeCmd = self.on_bridge_cmd
        self.web.setHtml('<!doctype html><html class="' + style_class + '">' + html_head + '<body class="' + style_class + '">' + html_body + '</body></html>')
        self.set_result_data(None) # Load welcome screen
        results_lyt.addWidget(self.web)

        self.resize(1075, 775)


    def set_result_data(self, data):

        # Really cannot be bothered to escape the json
        data_json = json.dumps(data)
        data_json_b64_b = base64.b64encode(data_json.encode('utf-8'))
        data_json_b64 = str(data_json_b64_b, 'utf-8')

        self.web.eval(F'set_data(\'{data_json_b64}\');')


    def on_bridge_cmd(self, cmd):
        args = cmd.split('-')
        if len(args) < 1:
            return

        def arg_from(i):
            j = 0
            for _ in range(i):
                j = cmd.find('-', j) + 1
            return cmd[j:]

        if args[0] == 'show_card_id':
            util.open_browser_cardids(int(args[1]))
        elif args[0] == 'show_word':
            util.open_browser_noteids([int(x) for x in args[1].split(',')])
        elif args[0] == 'create': 
            card_type = CardType[args[1]]
            character = args[2]
            util.error_msg_on_error(
                self,
                aqt.mw.migaku_kanji_db.make_cards_from_characters,
                card_type, character, 'Kanji Card Creation'
            )
            self.refresh()
        elif args[0] == 'mark': 
            card_type = CardType[args[1]]
            character = args[2]
            known = args[3] == '1'
            aqt.mw.migaku_kanji_db.set_character_known(card_type, character, known)
            self.refresh()
        elif args[0] == 'open':
            text = args[1]
            self.search(text, internal=True)
        elif args[0] == 'custom_keyword':
            character = args[1]
            old_keyword = arg_from(2)
            new_keyowrd, r = QInputDialog.getText(
                self,
                'Migaku Kanji - Set custom keyword',
                F'Set custom keyword for {character}:',
                text=old_keyword
            )
            if r:
                aqt.mw.migaku_kanji_db.set_character_usr_keyowrd(character, new_keyowrd)
                self.refresh()
        elif args[0] == 'custom_story':
            character = args[1]
            old_story = arg_from(2)
            new_story, r = QInputDialog.getMultiLineText(
                self,
                'Migaku Kanji - Set custom story',
                F'Set custom story for {character}:',
                text=old_story
            )
            if r:
                aqt.mw.migaku_kanji_db.set_character_usr_story(character, new_story)
                self.refresh()
        else:
            print('Unhandled bridge command:', args)


    def on_search_submit(self):
        text = self.search_bar.text()
        self.search(text)


    def search(self, text, internal=False):
        unique_characters = util.unique_characters(text)

        # Don't emit signal for every tab change
        self.tab_bar.blockSignals(True)

        # Close tabs if requested
        if not internal and not self.keep_tab_on_search_box.isChecked():
            self.close_all_tabs()

        # Open a tab for every character, close duplicates
        for c in unique_characters:
            if not c.strip():
                continue

            for tab_i in reversed(range(self.tab_bar.count())):
                tab_text = self.tab_bar.tabText(tab_i)
                if tab_text == c:
                    self.tab_bar.removeTab(tab_i)
            self.tab_bar.addTab(c)

        # Find tab of first searched character
        if len(unique_characters):
            for tab_i in range(self.tab_bar.count()):
                tab_text = self.tab_bar.tabText(tab_i)
                if tab_text == unique_characters[0]:
                    self.tab_bar.setCurrentIndex(tab_i)

        # Reenable signals
        self.tab_bar.blockSignals(False)

        # Search for current tab
        self.refresh()


    def on_tab_change(self, tab_i):
        result_data = None

        if tab_i >= 0:
            character = self.tab_bar.tabText(tab_i)
            result_data = aqt.mw.migaku_kanji_db.get_kanji_result_data(character)

        self.set_result_data(result_data)


    def on_tab_bar_context_menu_request(self, pos):
        tab_i = self.tab_bar.tabAt(pos)

        if tab_i >= 0:
            menu = QMenu(self)

            action = menu.addAction('Close Tab')
            action.triggered.connect(lambda: self.close_tab(tab_i))

            menu.addSeparator()

            action = menu.addAction('Close Other Tabs')
            action.triggered.connect(lambda: self.close_other_tabs(tab_i))

            action = menu.addAction('Close Tabs to the Left')
            action.triggered.connect(lambda: self.close_other_tabs(tab_i, close_left=True, close_right=False))

            action = menu.addAction('Close Tabs to the Right')
            action.triggered.connect(lambda: self.close_other_tabs(tab_i, close_left=False, close_right=True))

            action = menu.addAction('Close all Tabs')
            action.triggered.connect(self.close_all_tabs)

            menu.exec_(QCursor.pos())

    def close_tab(self, tab_idx):
        self.tab_bar.removeTab(tab_idx)

    def close_other_tabs(self, tab_i, close_left=True, close_right=True):
        if close_right:
            for i in range(self.tab_bar.count()-1, tab_i, -1):
                self.close_tab(i)
        if close_left:
            for i in range(tab_i-1, -1, -1):
                self.close_tab(i)

    def close_all_tabs(self):
        for i in reversed(range(self.tab_bar.count())):
            self.close_tab(i)

    def refresh(self):
        self.on_tab_change(self.tab_bar.currentIndex())


    @classmethod
    def open(cls, search_text=None):
        if cls.instance is None:
            cls.instance = LookupWindow()
        cls.instance.show()
        cls.instance.raise_()
        cls.instance.activateWindow()
        if search_text:
            search_text = search_text.strip()
            if search_text:
                cls.instance.search(search_text)



def attempt_webview_lookup(web_view):
    text = web_view.selectedText()
    LookupWindow.open(text)



# Add shortcuts for lookups
key_sequence = QKeySequence('Ctrl+Shift+K')


# Main web view
aqt.mw.kanji_lookup_shortcut = QShortcut(key_sequence, aqt.mw)
aqt.mw.kanji_lookup_shortcut.activated.connect(lambda: attempt_webview_lookup(aqt.mw.web))


# Editor
def Editor_install_kanji_shortcut(self):
    self.parentWindow.kanji_lookup_shortcut = QShortcut(key_sequence, self.parentWindow)
    self.parentWindow.kanji_lookup_shortcut.activated.connect(lambda: attempt_webview_lookup(self.web))

aqt.editor.Editor.setupWeb = anki.hooks.wrap(
    aqt.editor.Editor.setupWeb, Editor_install_kanji_shortcut
)


# Previewer
def Previewer_install_kanji_shortcut(self):
    self.kanji_lookup_shortcut = QShortcut(key_sequence, self._web)
    self.kanji_lookup_shortcut.activated.connect(lambda: attempt_webview_lookup(self._web))

aqt.previewer.Previewer.open = anki.hooks.wrap(
    aqt.previewer.Previewer.open, Previewer_install_kanji_shortcut
)


# Migaku dictionary
def apply_migaku_dict_hooks():
    aqt.gui_hooks.collection_did_load.remove(apply_migaku_dict_hooks)   # Only do this once

    from inspect import getmodule

    try:
        dict_module_main = getmodule(aqt.mw.refreshMigakuDictConfig)
    except AttributeError:
        # No dict addon
        return

    dict_module = getmodule(aqt.mw.refreshMigakuDictConfig)
    midict_module = getmodule(dict_module.DictInterface)

    def dict_interface_hook(self):
        self.hotkeyKanji = QShortcut(key_sequence, self)
        self.hotkeyKanji.activated.connect(lambda: attempt_webview_lookup(self.dict._page))

    def card_exporter_hook(self):

        def card_exporter_search_kanji(self):
            focused = self.scrollArea.focusWidget()
            if type(focused).__name__ in ['MILineEdit', 'MITextEdit']:
                text = focused.selectedText()
                LookupWindow.open(text)

        self.hotkeyKanji = QShortcut(key_sequence, self.scrollArea)
        self.hotkeyKanji.activated.connect(lambda: card_exporter_search_kanji(self))

    midict_module.DictInterface.setHotkeys = anki.hooks.wrap(
        midict_module.DictInterface.setHotkeys, dict_interface_hook
    )

    midict_module.CardExporter.setHotkeys = anki.hooks.wrap(
        midict_module.CardExporter.setHotkeys, card_exporter_hook
    )

aqt.gui_hooks.profile_did_open.append(apply_migaku_dict_hooks)
