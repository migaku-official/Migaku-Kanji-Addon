import anki
import aqt
from aqt.qt import *

import json

from . import util
from .lookup_window import LookupWindow
from . import text_parser
from . import config
from .card_type import CardType
from .version import KANJI_FORMS_URL


# Handler for interactive card buttons

def reviewer_bridge_hook(reviewer: aqt.reviewer.Reviewer, cmd, _old):

    # mostly copy paste from lookup window
    # TODO: remove dupe
    args = cmd.split('-')

    def arg_from(i):
        j = 0
        for _ in range(i):
            j = cmd.find('-', j) + 1
        return cmd[j:]

    if len(args):
        if args[0] == 'show_card_id':
            util.open_browser_cardids(int(args[1]))
            return
        elif args[0] == 'show_word':
            util.open_browser_noteids([int(x) for x in args[1].split(',')])
            return
        elif args[0] == 'open':
            LookupWindow.open(args[1])
            return
        elif args[0] == 'custom_keyword':
            character = args[1]
            old_keyword = arg_from(2)
            new_keyowrd, r = QInputDialog.getText(
                aqt.mw,
                'Migaku Kanji - Set custom keyword',
                F'Set custom keyword for {character}:',
                text=old_keyword
            )
            if r:
                aqt.mw.requireReset()
                aqt.mw.migaku_kanji_db.set_character_usr_keyowrd(character, new_keyowrd)
                aqt.mw.maybeReset()
            return
        elif args[0] == 'custom_story':
            character = args[1]
            old_story = arg_from(2)
            new_story, r = QInputDialog.getMultiLineText(
                aqt.mw,
                'Migaku Kanji - Set custom story',
                F'Set custom story for {character}:',
                text=old_story
            )
            if r:
                aqt.mw.requireReset()
                aqt.mw.migaku_kanji_db.set_character_usr_story(character, new_story)
                aqt.mw.maybeReset()
            return
        elif args[0] == 'delete_mark':
            character = args[1]
            card_type = CardType[args[2]]
            ask = args[3] != 'false'

            if ask:
                r = QMessageBox.question(aqt.mw,
                                         'Migaku Kanji',
                                        F'Do you want to delete this card and mark the kanji {character} known for {card_type.label}?\n\n'
                                         'You can press the shift key to bypass this confirmation in future.')
                if r != QMessageBox.Yes:
                    return

            aqt.mw.requireReset()
            aqt.mw.migaku_kanji_db.set_character_known(card_type, character)
            reviewer.card.col.remNotes([reviewer.card.nid])
            aqt.mw.migaku_kanji_db.recalc_user_cards(card_type)
            aqt.mw.maybeReset()
            return
        elif args[0] == 'search_dict':
            word = args[1]
            util.search_dict(word)
            return
        elif args[0] == 'suggest_change':
            character = args[1]

            key_sequence = QKeySequence(Qt.CTRL + Qt.Key_F).toString(QKeySequence.NativeText)

            r = QMessageBox.question(aqt.mw,
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
            return

    _old(reviewer, cmd)


aqt.reviewer.Reviewer._linkHandler = anki.hooks.wrap(
    aqt.reviewer.Reviewer._linkHandler,
    reviewer_bridge_hook,
    'around'
)


# Handler for reviewing new cards

def check_learn_ahead(did):

    deck = aqt.mw.col.decks.get(did)

    for ct in CardType:
        ct_max = 0
        for e in config.get('card_type_learn_ahead').get(ct.label, []):
            if e['deck'] == deck['name']:
                ct_max = max(ct_max, e['num'])
                
        new = aqt.mw.migaku_kanji_db.new_learn_ahead_kanji(ct, did, ct_max)
        if len(new):
            util.error_msg_on_error(
                aqt.mw,
                aqt.mw.migaku_kanji_db.make_cards_from_characters,
                ct, new, None
            )

def reviewer_will_answer_hook(status, reviewer, card: anki.collection.Card):
    proceed, ease = status

    # Learning card?
    if card.type == 0:
        check_learn_ahead(card.did)

    return status


aqt.gui_hooks.reviewer_will_answer_card.append(reviewer_will_answer_hook)