from typing import Optional

import aqt
from aqt.qt import *

from . import util
from .lookup_window import LookupWindow
from .kanji_forms_url import KANJI_FORMS_URL
from .card_type import CardType



class CustomKeywordsDialog(QDialog):

    def __init__(self, character, parent=None):
        super().__init__(parent)

        self.character = character

        old_keyword, old_primitive_keyword = aqt.mw.migaku_kanji_db.get_character_usr_keyowrd(character)
        
        self.setWindowTitle('Migaku Kanji - Set custom keyword')
        lyt = QVBoxLayout()
        self.setLayout(lyt)

        lyt.addWidget(QLabel(F'Set custom keyword for {character}:'))
        self.keyword_edit = QLineEdit(old_keyword)
        lyt.addWidget(self.keyword_edit)

        lyt.addWidget(QLabel(F'Set custom primitive keyword for {character}:'))
        self.primitive_keyword_edit = QLineEdit(old_primitive_keyword)
        lyt.addWidget(self.primitive_keyword_edit)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lyt.addWidget(btns)

        self.resize(475, self.sizeHint().height())

    
    def accept(self):
        aqt.mw.migaku_kanji_db.set_character_usr_keyowrd(
            self.character,
            self.keyword_edit.text(),
            self.primitive_keyword_edit.text()
        )
        super().accept()



def handle_bridge_action(cmd, lookup_window: Optional[LookupWindow] = None, reviewer: Optional[aqt.reviewer.Reviewer] = None):
    args = cmd.split('-')

    if not len(args):
        return False

    def arg_from(i):
        j = 0
        for _ in range(i):
            j = cmd.find('-', j) + 1
        return cmd[j:]

    parent = lookup_window or aqt.mw

    if args[0] == 'show_card_id':
        util.open_browser_cardids(int(args[1]))
        return True

    elif args[0] == 'show_word':
        util.open_browser_noteids([int(x) for x in args[1].split(',')])
        return True

    elif args[0] == 'create' and lookup_window:
        card_type = CardType[args[1]]
        character = args[2]
        util.error_msg_on_error(
            parent,
            aqt.mw.migaku_kanji_db.make_cards_from_characters,
            card_type, character, 'Kanji Card Creation'
        )
        lookup_window.refresh()
        return True

    elif args[0] == 'mark' and lookup_window:
        card_type = CardType[args[1]]
        character = args[2]
        known = args[3] == '1'
        aqt.mw.migaku_kanji_db.set_character_known(card_type, character, known)
        lookup_window.refresh()

    elif args[0] == 'open':
        text = args[1]
        if lookup_window:
            lookup_window.search(text, internal=True)
        else:
            LookupWindow.open(text)
        return True

    elif args[0] == 'custom_keyword':
        character = args[1]
        if reviewer:
            aqt.mw.requireReset()
        r = CustomKeywordsDialog(character, parent).exec()
        if r == QDialog.Accepted:
            if reviewer:
                aqt.mw.maybeReset()
            else:
                lookup_window.refresh()
        return True

    elif args[0] == 'custom_story':
        character = args[1]
        old_story = arg_from(2)
        new_story, r = QInputDialog.getMultiLineText(
            parent,
            'Migaku Kanji - Set custom story',
            F'Set custom story for {character}:',
            text=old_story
        )
        if r:
            if not lookup_window:
                aqt.mw.requireReset()
            aqt.mw.migaku_kanji_db.set_character_usr_story(character, new_story)
            if not lookup_window:
                aqt.mw.maybeReset()
            else:
                lookup_window.refresh()
        return True

    elif args[0] == 'delete_mark' and reviewer:
        character = args[1]
        card_type = CardType[args[2]]
        ask = args[3] != 'false'

        if ask:
            r = QMessageBox.question(aqt.mw,
                                        'Migaku Kanji',
                                    F'Do you want to delete this card and mark the kanji {character} known for {card_type.label}?\n\n'
                                        'You can press the shift key to bypass this confirmation in future.')
            if r != QMessageBox.Yes:
                return True

        aqt.mw.migaku_kanji_db.set_character_known(card_type, character)
        reviewer.card.col.remNotes([reviewer.card.nid])
        aqt.mw.migaku_kanji_db.recalc_user_cards(card_type)
        aqt.mw.reset(False)
        return True

    elif args[0] == 'search_dict':
        word = args[1]
        util.search_dict(word)
        return True

    elif args[0] == 'suggest_change':
        character = args[1]

        key_sequence = QKeySequence(Qt.CTRL + Qt.Key_F).toString(QKeySequence.SequenceFormat.NativeText)

        r = QMessageBox.question(parent,
                                 'Migaku Kanji',
                                F'Do you want to suggest a change to the data for {character}?\n\n'
                                F'On the sheet that will open, search for the data you want to change using {key_sequence}. '
                                 'Right click the cell you want to suggest a change for, then select "Comment" and enter the data you suggest and optionally the reason on why the data should be changed. '
                                 'Finally confirm your comment.\n\n'
                                F'Your clipboard will also be set to {character}.\n\n'
                                 'Thank you!')
        if r == QMessageBox.Yes:
            aqt.mw.app.clipboard().setText(character)
            aqt.utils.openLink(KANJI_FORMS_URL)
        return True

    return False
