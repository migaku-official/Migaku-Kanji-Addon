import anki
import aqt
from aqt.qt import *

import json

from . import util
from .lookup_window import LookupWindow


def reviewer_bridge_hook(reviewer, cmd, _old):

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

    _old(reviewer, cmd)
    


aqt.reviewer.Reviewer._linkHandler = anki.hooks.wrap(
    aqt.reviewer.Reviewer._linkHandler,
    reviewer_bridge_hook,
    'around'
)
