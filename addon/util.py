import os
import sys
import re
from collections import OrderedDict
import re

import anki
import aqt
from aqt.qt import *

from .errors import InvalidDeckError

addon_dir = os.path.dirname(__file__)
addon_id = os.path.basename(addon_dir)
user_files_dir = os.path.join(addon_dir, "user_files")
addon_web_base = f'/_addons/{__name__.split(".")[0]}'  # uhhh

def assure_user_dir():
    os.makedirs(user_files_dir, exist_ok=True)

def addon_path(*path_parts):
    return os.path.join(addon_dir, *path_parts)

def user_path(*path_parts):
    return os.path.join(user_files_dir, *path_parts)

def col_media_path(*path_parts):
    return os.path.join(aqt.mw.col.media.dir(), *path_parts)

def addon_web_uri(*path_parts):
    return addon_web_base + "/" + "/".join(path_parts)

def read_web_file(name):
    path = addon_path("web", name)
    if not os.path.exists(path):
        return "%s NOT FOUND!" % path
    with open(addon_path("web", name), "r", encoding="UTF-8") as file:
        data = file.read()
    return data

def read_web_file_with_includes(name):
    data = read_web_file(name)
    
    include_list = re.findall(r'(<!--[ ]*#include file="([^"]+)"[ ]*-->)',data)
    for include_tag, include_file in include_list:
        inc_data = read_web_file(include_file)
        data = data.replace(include_tag,inc_data)
    return data

def make_pixmap(*file_parts):
    path = addon_path("img", *file_parts)
    return QPixmap(path)

def make_icon(*file_parts):
    path = addon_path("img", *file_parts)
    return QIcon(path)

def default_icon():
    return make_icon("migaku.png")

# Creates a list of single-character Unicode kanjis and [primitive] tags
# For example '[banner]也' -> ['\[banner\]','也'] 
def custom_list(l):
    g = re.findall(r'([^\[]|\[[^\]]+\])',l)
    return g

def unique_characters(string):
    l = custom_list(string)
    return list(OrderedDict((c, True) for c in l).keys())

import aqt
from aqt.qt import *

def get_pixmap_from_tag(kanji, size):
    img = kanji[1:-1]
    path = addon_path('primitives','%s.svg' % img)
    pixmap = QIcon(path).pixmap(QSize(size,size))
    return pixmap

def log(*args):
    print("[Migaku Kanji]", *args)


def error_msg(parent, msg):
    QMessageBox.information(parent, "Migaku Kanji", msg)


def error_msg_on_error(parent, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return True
    except InvalidDeckError as e:
        error_msg(
            parent,
            f"No or invalid deck selected for {e.card_type.label} cards.\n\n"
            f"Please go to the settings and select the deck into which new {e.card_type.label} cards should be added.",
        )
        return False


def raise_window(window: QWidget):
    window.setWindowState(
        (window.windowState() & ~Qt.WindowState.WindowMinimized)
        | Qt.WindowState.WindowActive
    )
    window.raise_()
    window.activateWindow()


def open_browser(text):
    browser = aqt.dialogs.open("Browser", aqt.mw)
    browser.form.searchEdit.lineEdit().setText(text)
    browser.onSearchActivated()
    # For newer Anki versions:
    #   aqt.dialogs.open('Browser', aqt.mw, search=(text,))
    raise_window(browser)


def open_browser_cardids(card_ids):
    try:
        search_str = ",".join([str(cid) for cid in card_ids])
    except TypeError:
        search_str = str(card_ids)
    open_browser(f'"cid:{search_str}"')


def open_browser_noteids(note_ids):
    try:
        search_str = ",".join([str(nid) for nid in note_ids])
    except TypeError:
        search_str = str(note_ids)
    open_browser(f'"nid:{search_str}"')


def search_dict(word):
    if hasattr(aqt.mw, "migaku_connection"):
        aqt.mw.migaku_connection.search_dict(word)
    elif hasattr(aqt.mw, "dictionaryInit"):
        dict_plugin_main = sys.modules[aqt.mw.dictionaryInit.__module__]
        dict_plugin_main.searchTermList([word])
    else:
        url = "https://jisho.org/search/" + word
        aqt.utils.openLink(url)
