import os
from collections import OrderedDict

import anki
from aqt.qt import *

from .errors import InvalidDeckError


addon_dir = os.path.dirname(__file__)
user_files_dir = os.path.join(addon_dir, 'user_files')


def assure_user_dir():
    os.makedirs(user_files_dir, exist_ok=True)

def addon_path(*path_parts):
    return os.path.join(addon_dir, *path_parts)

def user_path(*path_parts):
    return os.path.join(user_files_dir, *path_parts)

def make_pixmap(*file_parts):
    path = addon_path('img', *file_parts)
    return QPixmap(path)

def make_icon(*file_parts):
    path = addon_path('img', *file_parts)
    return QIcon(path)

def default_icon():
    return make_icon('migaku_200.png')


def unique_characters(string):
    return list(OrderedDict((c, True) for c in string).keys())




import aqt
from aqt.qt import *


def error_msg(parent, msg):
    QMessageBox.information(parent, 'Migaku Kanji', msg)


def error_msg_on_error(parent, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return True
    except InvalidDeckError as e:
        error_msg(
            parent,
            F'No or invalid deck selected for {e.card_type.label} cards.\n\n'
            F'Please go to the settings and select the deck into which new {e.card_type.label} cards should be added.'
        )
        return False


def open_browser(text):
    browser = aqt.DialogManager._dialogs['Browser'][1]
    if not browser:
        aqt.mw.onBrowse()
        browser = aqt.DialogManager._dialogs['Browser'][1]
    if browser:
        browser.form.searchEdit.lineEdit().setText(text)
        browser.onSearchActivated()
        browser.raise_()
        browser.activateWindow()


def open_browser_cardids(card_ids):
    try:
        search_str = ','.join([str(cid) for cid in card_ids])
    except TypeError:
        search_str = str(card_ids)
    open_browser(F'"cid:{search_str}"')


def open_browser_noteids(note_ids):
    try:
        search_str = ','.join([str(nid) for nid in note_ids])
    except TypeError:
        search_str = str(note_ids)
    open_browser(F'"nid:{search_str}"')
