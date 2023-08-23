import json
import base64
from collections import OrderedDict

import anki
import aqt
from aqt.qt import *

from . import util
from . import fonts
from . import config


key_sequence = QKeySequence("Ctrl+Shift+K")
key_sequence_txt = key_sequence.toString(QKeySequence.SequenceFormat.NativeText)


class LookupWindow(QDialog):
    instance = None

    kanjivg_uri = util.addon_web_base + "/kanjivg/"
    primitives_uri = util.addon_web_base + "/primitives/"

    @classmethod
    def web_uri(cls, name):
        return util.addon_web_base + "/web/" + name

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle("Migaku Kanji - Lookup")
        self.setWindowIcon(util.default_icon())
        self.setMinimumSize(400, 300)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        search_lyt = QHBoxLayout()
        lyt.addLayout(search_lyt)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("字")
        self.search_bar.returnPressed.connect(self.on_search_submit)
        search_lyt.addWidget(self.search_bar)

        search_btn = QPushButton("🔍")
        search_btn.setFixedWidth(search_btn.sizeHint().height())
        search_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        search_btn.clicked.connect(self.on_search_submit)
        search_lyt.addWidget(search_btn)

        self.keep_tab_on_search_box = QCheckBox("Keep tabs open")
        self.keep_tab_on_search_box.setChecked(False)
        self.keep_tab_on_search_box.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        self.tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_bar.customContextMenuRequested.connect(
            self.on_tab_bar_context_menu_request
        )
        results_lyt.addWidget(self.tab_bar)

        self.web = aqt.webview.AnkiWebView()

        # this mess isn't needed with updated styles fix eventually~~~ can also use bundled jquery then lol
        bundled_js = self.web.bundledScript("webview.js")

        fonts_css = fonts.ui_css()

        html_head = (
            "<head>"
            f"{aqt.mw.baseHTML()}"
            f"{bundled_js}"
            "<style>"
            f"{fonts_css}\n"
            ".dark::-webkit-scrollbar { background: #2f2f31; }\n"
            ".dark::-webkit-scrollbar-thumb { background: #656565; border-radius: 8px; }\n"
            "</style>"
            f'<link rel="stylesheet" href="{self.web_uri("styles.css")}">'
            f'<script src="{self.web_uri("jquery.js")}"></script>'
            f'<script>let kanjivg_uri="{self.kanjivg_uri}";</script>'
            f'<script>let primitives_uri="{self.primitives_uri}";</script>'
            f'<script src="{self.web_uri("dmak.js")}"></script>'
            f'<script src="{self.web_uri("raphael.js")}"></script>'
            f'<script src="{self.web_uri("japanese-util.js")}"></script>'
            f'<script src="{self.web_uri("common.js")}"></script>'
            "</head>"
        )
        common_back = (
            f'<script src="{self.web_uri("common_back.js")}"></script>'
        )

        body_html = util.read_web_file_with_includes("lookup.html")

        settings = {
            "stroke_order_mode": config.get("lookup_stroke_order_mode", "fully_drawn"),
            "stroke_order_show_numbers": config.get(
                "lookup_stroke_order_show_numbers", False
            ),
            "hide_readings_hover": config.get("lookup_hide_readings_hover", False),
            "show_header": config.get("lookup_show_header", True),
            "show_radicals": config.get("lookup_show_radicals", False),
        }
        settings_html = f"""
            <script>
                var settings = JSON.parse('{json.dumps(settings)}');
            </script>
        """

        keys = key_sequence_txt.split("+")
        keys_html = " + ".join(
            f'<span class="key">{key.upper()}</span>' for key in keys
        )

        set_keys_html = f"""
            <script>
                $('.key-sequence').html('{keys_html}');
            </script>
        """

        style_class = "dark" if aqt.theme.theme_manager.night_mode else "light"

        self.web.onBridgeCmd = self.on_bridge_cmd
        self.web.setHtml(
            '<!doctype html><html class="'
            + style_class
            + '">'
            + html_head
            + '<body class="'
            + style_class
            + '">'
            + settings_html
            + body_html
            + common_back
            + set_keys_html
            + "</body></html>"
        )
        self.set_result_data(None)  # Load welcome screen
        results_lyt.addWidget(self.web)

        self.resize(1075, 775)

    def set_result_data(self, data):
        # Really cannot be bothered to escape the json
        data_json = json.dumps(data)
        data_json_b64_b = base64.b64encode(data_json.encode("utf-8"))
        data_json_b64 = str(data_json_b64_b, "utf-8")

        self.web.eval(f"set_data('{data_json_b64}');")

    def on_bridge_cmd(self, cmd):
        from .bridge_actions import handle_bridge_action

        if not handle_bridge_action(cmd, lookup_window=self):
            print("Unhandled bridge command:", cmd)

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
            result_data = aqt.mw.migaku_kanji_db.get_kanji_result_data(
                character, user_data=True
            )

        self.set_result_data(result_data)

    def on_tab_bar_context_menu_request(self, pos):
        tab_i = self.tab_bar.tabAt(pos)

        if tab_i >= 0:
            menu = QMenu(self)

            action = menu.addAction("Close Tab")
            action.triggered.connect(lambda: self.close_tab(tab_i))

            menu.addSeparator()

            action = menu.addAction("Close Other Tabs")
            action.triggered.connect(lambda: self.close_other_tabs(tab_i))

            action = menu.addAction("Close Tabs to the Left")
            action.triggered.connect(
                lambda: self.close_other_tabs(tab_i, close_left=True, close_right=False)
            )

            action = menu.addAction("Close Tabs to the Right")
            action.triggered.connect(
                lambda: self.close_other_tabs(tab_i, close_left=False, close_right=True)
            )

            action = menu.addAction("Close all Tabs")
            action.triggered.connect(self.close_all_tabs)

            menu.exec(QCursor.pos())

    def close_tab(self, tab_idx):
        self.tab_bar.removeTab(tab_idx)

    def close_other_tabs(self, tab_i, close_left=True, close_right=True):
        if close_right:
            for i in range(self.tab_bar.count() - 1, tab_i, -1):
                self.close_tab(i)
        if close_left:
            for i in range(tab_i - 1, -1, -1):
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

    @classmethod
    def close_instance(cls):
        if cls.instance is None:
            return
        cls.instance.close()
        cls.instance = None


def attempt_webview_lookup(web_view):
    text = web_view.selectedText()
    LookupWindow.open(text)


# Add shortcuts for lookups

# Main web view
aqt.mw.kanji_lookup_shortcut = QShortcut(key_sequence, aqt.mw)
aqt.mw.kanji_lookup_shortcut.activated.connect(
    lambda: attempt_webview_lookup(aqt.mw.web)
)


# Editor
def Editor_install_kanji_shortcut(self):
    self.parentWindow.kanji_lookup_shortcut = QShortcut(key_sequence, self.parentWindow)
    self.parentWindow.kanji_lookup_shortcut.activated.connect(
        lambda: attempt_webview_lookup(self.web)
    )


aqt.editor.Editor.setupWeb = anki.hooks.wrap(
    aqt.editor.Editor.setupWeb, Editor_install_kanji_shortcut
)


# Previewer
def Previewer_install_kanji_shortcut(self):
    self.kanji_lookup_shortcut = QShortcut(key_sequence, self._web)
    self.kanji_lookup_shortcut.activated.connect(
        lambda: attempt_webview_lookup(self._web)
    )


aqt.previewer.Previewer.open = anki.hooks.wrap(
    aqt.previewer.Previewer.open, Previewer_install_kanji_shortcut
)


# Migaku dictionary
def apply_migaku_dict_hooks():
    aqt.gui_hooks.collection_did_load.remove(
        apply_migaku_dict_hooks
    )  # Only do this once

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
        self.hotkeyKanji.activated.connect(
            lambda: attempt_webview_lookup(self.dict._page)
        )

    def card_exporter_hook(self):
        def card_exporter_search_kanji(self):
            focused = self.scrollArea.focusWidget()
            if type(focused).__name__ in ["MILineEdit", "MITextEdit"]:
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


# Add entry in context menus


def on_webview_context_menu(webview, menu):
    action = menu.addAction(f"Search Kanji ({key_sequence_txt})")
    action.triggered.connect(lambda: attempt_webview_lookup(webview))


aqt.gui_hooks.webview_will_show_context_menu.append(on_webview_context_menu)
aqt.gui_hooks.editor_will_show_context_menu.append(on_webview_context_menu)
