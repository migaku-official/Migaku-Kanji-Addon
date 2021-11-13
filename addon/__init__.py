from .card_type import CardType
from . import kanji
from .lookup_window import LookupWindow
from .settings_window import SettingsWindow
from .add_cards_dialog import AddCardsDialog
from .stats_window import StatsWindow
from .create_cards_from_notes_dialog import CreateCardsFromNotesDialog
from .mark_known_dialog import MarkKnownDialog, MarkKnownFromNotesDialog
from .convert_notes_dialog import ConvertNotesDialog
from . import reviewer
from . import version
from . import util


import anki
import aqt
from aqt.qt import *


# Allow webviews accessing kanjivg svgs, web data for lookups and fonts
aqt.mw.addonManager.setWebExports(__name__, r"(kanjivg/.*\.svg|web/.*|fonts/.*|user_files/fonts/.*)")



def setup_menu():

    add_menu = False
    if not hasattr(aqt.mw, 'MigakuMainMenu'):
        aqt.mw.MigakuMainMenu = QMenu('Migaku', aqt.mw)
        add_menu = True
    if not hasattr(aqt.mw, 'MigakuMenuSettings'):
        aqt.mw.MigakuMenuSettings = []
    if not hasattr(aqt.mw, 'MigakuMenuActions'):
        aqt.mw.MigakuMenuActions = []

    # submenu = QMenu('Kanji', aqt.mw)
    # aqt.mw.MigakuMenuActions.append(submenu)

    lookup_action = QAction('Kanji Lookup', aqt.mw)
    lookup_action.triggered.connect(on_loopup)
    # submenu.addAction(add_kanji_action)
    aqt.mw.MigakuMenuActions.append(lookup_action)

    stats_action = QAction('Kanji Stats', aqt.mw)
    stats_action.triggered.connect(on_stats)
    # submenu.addAction(stats_action)
    aqt.mw.MigakuMenuActions.append(stats_action)

    add_kanji_action = QAction('Add New Kanji Cards', aqt.mw)
    add_kanji_action.triggered.connect(on_add_cards)
    # submenu.addAction(add_kanji_action)
    aqt.mw.MigakuMenuActions.append(add_kanji_action)

    mark_known_action = QAction('Mark Kanji Known', aqt.mw)
    mark_known_action.triggered.connect(on_mark_known)
    # submenu.addAction(mark_known_action)
    aqt.mw.MigakuMenuActions.append(mark_known_action)

    recalc_action = QAction('Refresh Kanji Cards', aqt.mw)
    recalc_action.triggered.connect(on_recalc)
    # submenu.addAction(recalc_action)
    aqt.mw.MigakuMenuActions.append(recalc_action)

    settings_action = QAction('Kanji Settings', aqt.mw)
    settings_action.triggered.connect(on_settings)
    # submenu.addAction(settings_action)
    aqt.mw.MigakuMenuSettings.append(settings_action)

    aqt.mw.MigakuMainMenu.clear()
    for act in aqt.mw.MigakuMenuSettings:
        aqt.mw.MigakuMainMenu.addAction(act)
    aqt.mw.MigakuMainMenu.addSeparator()
    for act in aqt.mw.MigakuMenuActions:
        if isinstance(act, QAction):
            aqt.mw.MigakuMainMenu.addAction(act)
        elif isinstance(act, QMenu):
            aqt.mw.MigakuMainMenu.addMenu(act)

    if add_menu:
        aqt.mw.form.menubar.insertMenu(aqt.mw.form.menuHelp.menuAction(), aqt.mw.MigakuMainMenu)  


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
            self.setWindowTitle('Refreshing Kanji')
            self.setWindowModality(Qt.ApplicationModal)
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
    lrv_path = util.user_path('last_run_version')
    try:
        lrv = open(lrv_path, 'r').read()
    except OSError:
        lrv = ''

    if lrv != version.VERSION_STRING:
        on_recalc()

    open(lrv_path, 'w').write(version.VERSION_STRING)


aqt.mw.migaku_kanji_db = kanji.KanjiDB()
aqt.gui_hooks.profile_did_open.append(on_profile_open)
setup_menu()


def setup_browser_menu(browser):
    browser.form.menuEdit.addSeparator()

    create_cards_action = QAction('Create Kanji Cards From Selection', browser)
    create_cards_action.triggered.connect(
        lambda: CreateCardsFromNotesDialog.show_modal(browser.selectedNotes(), browser)
    )
    browser.form.menuEdit.addAction(create_cards_action)

    mark_known_action = QAction('Mark Kanji Known From Selection', browser)
    mark_known_action.triggered.connect(
        lambda: MarkKnownFromNotesDialog.show_modal(browser.selectedNotes(), browser)
    )
    browser.form.menuEdit.addAction(mark_known_action)

    convert_notes_action = QAction('Convert Selected Notes To Migaku Kanji Cards', browser)
    convert_notes_action.triggered.connect(
        lambda: ConvertNotesDialog.show_modal(browser.selectedNotes(), browser)
    )
    browser.form.menuEdit.addAction(convert_notes_action)

aqt.gui_hooks.browser_menus_did_init.append(setup_browser_menu)


def note_added(col, note, deck_id):
    aqt.mw.migaku_kanji_db.on_note_update(note.id, deck_id, is_new=True)

add_note_no_hook = anki.collection.Collection.add_note
anki.collection.Collection.add_note = anki.hooks.wrap(
    anki.collection.Collection.add_note,
    note_added,
    'after'
)
