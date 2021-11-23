from anki.notes import Note
import aqt
from aqt import AnkiQt
from aqt.qt import *
from aqt.clayout import CardLayout

from .card_type import CardType
from . import util

def CardLayout_init_hook(self, mw: AnkiQt, note: Note, *args, **kwargs):
    if note:
        note_type = note.note_type()
        if any(card_type.model_name == note_type['name'] for card_type in CardType):
            parent = kwargs.get('parent', mw)
            r = QMessageBox.question(
                parent,
                'Migaku Kanji',
                'You cannot edit Migaku Kanji note types from Anki because your changes would be lost as they are constantly replaced when you change settings.\n\n'
                'You are able to edit the template for the note type by editing the corresponding HTML and CSS files inside the add-on directory.\n\n'
                'Do you want to open that directory now?\n\n'
                'Note: If you edit the templates be aware that updates to the add-on will overwrite those files.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if r == QMessageBox.Yes:
                aqt.utils.openFolder(
                    util.addon_path('web')
                )
            return
    return CardLayout_init(self, mw, note, *args, **kwargs)

CardLayout_init = CardLayout.__init__
CardLayout.__init__ = CardLayout_init_hook
