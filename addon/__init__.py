from .card_type import CardType
from . import kanji
from .lookup_window import LookupWindow
from .settings_window import SettingsWindow
from .add_cards_dialog import AddCardsDialog
from .stats_window import StatsWindow
from .create_cards_from_notes_dialog import CreateCardsFromNotesDialog
from .mark_known_dialog import MarkKnownDialog, MarkKnownFromNotesDialog
from .convert_notes_dialog import ConvertNotesDialog
from . import card_layout
from . import reviewer
from . import version
from . import util
from . import updater


import anki
import aqt
from aqt.qt import *


# Allow webviews accessing kanjivg svgs, web data for lookups and fonts
aqt.mw.addonManager.setWebExports(
    __name__, r"(kanjivg/.*\.svg|kanjivg-supplementary/.*\.svg|primitives/.*\.svg|web/.*|fonts/.*|user_files/fonts/.*)"
)


def setup_menu():
    submenu = QMenu("Kanji", aqt.mw)

    lookup_action = QAction("Lookup", aqt.mw)
    lookup_action.setShortcut(_("Ctrl+L"))
    lookup_action.triggered.connect(on_loopup)
    submenu.addAction(lookup_action)

    stats_action = QAction("Stats", aqt.mw)
    stats_action.triggered.connect(on_stats)
    submenu.addAction(stats_action)

    add_kanji_action = QAction("Add New Cards", aqt.mw)
    add_kanji_action.triggered.connect(on_add_cards)
    submenu.addAction(add_kanji_action)

    mark_known_action = QAction("Mark Known", aqt.mw)
    mark_known_action.triggered.connect(on_mark_known)
    submenu.addAction(mark_known_action)

    recalc_action = QAction("Refresh Cards", aqt.mw)
    recalc_action.triggered.connect(on_recalc)
    submenu.addAction(recalc_action)

    settings_action = QAction("Settings", aqt.mw)
    settings_action.setMenuRole(QAction.MenuRole.NoRole)
    settings_action.triggered.connect(on_settings)
    submenu.addAction(settings_action)

    aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), submenu)


def on_loopup():
    LookupWindow.open()


def on_stats():
    StatsWindow.open()


def on_add_cards():
    AddCardsDialog.show_modal(aqt.mw)


def on_mark_known():
    MarkKnownDialog.show_modal(parent=aqt.mw)


def on_recalc():
    class RecalcThread(QThread):
        progress_update = pyqtSignal(str)

        def run(self):
            aqt.mw.migaku_kanji_db.recalc_all(callback=self.on_callback)

        def on_callback(self, txt):
            self.progress_update.emit(txt)

    class ProgressBox(QDialog):
        def __init__(self, parent):
            super(QDialog, self).__init__(parent)
            self.setWindowIcon(util.default_icon())
            self.setWindowTitle("Refreshing Kanji")
            self.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.setMinimumWidth(300)
            lyt = QVBoxLayout()
            self.setLayout(lyt)
            self.lbl = QLabel()
            self.bar = QProgressBar()
            self.bar.setTextVisible(False)
            self.bar.setMinimum(0)
            self.bar.setMaximum(0)
            lyt.addWidget(self.lbl)
            lyt.addWidget(self.bar)

        def on_progress(self, txt):
            self.lbl.setText(txt)

        def reject(self):
            # Hack
            pass

    box = ProgressBox(aqt.mw)
    box.show()

    thread = RecalcThread(aqt.mw)
    thread.finished.connect(box.accept)
    thread.progress_update.connect(box.on_progress)
    thread.start()


def on_settings():
    SettingsWindow.show_modal(aqt.mw)


aqt.mw.addonManager.setConfigAction(__name__, on_settings)


def on_profile_open():
    CardType.upsert_all_models()

    util.assure_user_dir()
    lrv_path = util.user_path("last_run_version")
    try:
        with open(lrv_path, "r", encoding="utf-8") as f:
            lrv = f.read()
    except OSError:
        lrv = ""

    if lrv != version.VERSION_STRING:
        on_recalc()

    with open(lrv_path, "w", encoding="utf-8") as f:
        f.write(version.VERSION_STRING)


aqt.mw.migaku_kanji_db = kanji.KanjiDB()
aqt.gui_hooks.profile_did_open.append(on_profile_open)
setup_menu()


def setup_browser_menu(browser):
    browser.form.menuEdit.addSeparator()

    create_cards_action = QAction("Create Kanji Cards From Selection", browser)
    create_cards_action.triggered.connect(
        lambda: CreateCardsFromNotesDialog.show_modal(browser.selectedNotes(), browser)
    )

    mark_known_action = QAction("Mark Kanji Known From Selection", browser)
    mark_known_action.triggered.connect(
        lambda: MarkKnownFromNotesDialog.show_modal(browser.selectedNotes(), browser)
    )

    convert_notes_action = QAction(
        "Convert Selected Notes To Migaku Kanji Cards", browser
    )
    convert_notes_action.triggered.connect(
        lambda: ConvertNotesDialog.show_modal(browser.selectedNotes(), browser)
    )

    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(create_cards_action)
    browser.form.menuEdit.addAction(mark_known_action)
    browser.form.menuEdit.addAction(convert_notes_action)

    browser.form.menu_Notes.insertAction(
        browser.form.actionManage_Note_Types, create_cards_action
    )
    browser.form.menu_Notes.insertAction(
        browser.form.actionManage_Note_Types, mark_known_action
    )
    browser.form.menu_Notes.insertAction(
        browser.form.actionManage_Note_Types, convert_notes_action
    )
    browser.form.menu_Notes.insertSeparator(browser.form.actionManage_Note_Types)


aqt.gui_hooks.browser_menus_did_init.append(setup_browser_menu)


add_note_no_hook = anki.collection.Collection.add_note


def add_note(col, note, deck_id):
    r = add_note_no_hook(col, note, deck_id)
    aqt.mw.migaku_kanji_db.on_note_update(note.id, deck_id, is_new=True)
    return r


anki.collection.Collection.add_note = add_note
