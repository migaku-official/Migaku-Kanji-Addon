import anki
import aqt
from aqt.qt import *

from . import util
from . import config
from .card_type import CardType
from .bridge_actions import handle_bridge_action


# Handler for interactive card buttons


def reviewer_bridge_hook(reviewer: aqt.reviewer.Reviewer, cmd, _old):
    if not handle_bridge_action(cmd, reviewer=reviewer):
        return _old(reviewer, cmd)


aqt.reviewer.Reviewer._linkHandler = anki.hooks.wrap(
    aqt.reviewer.Reviewer._linkHandler, reviewer_bridge_hook, "around"
)


# Handler for reviewing new cards


def check_learn_ahead(did):
    deck = aqt.mw.col.decks.get(did)

    for ct in CardType:
        ct_max = 0
        for e in config.get("card_type_learn_ahead", {}).get(ct.label, []):
            if e["deck"] == deck["name"]:
                ct_max = max(ct_max, e["num"])

        new = aqt.mw.migaku_kanji_db.new_learn_ahead_kanji(ct, did, ct_max)
        if len(new):
            util.error_msg_on_error(
                aqt.mw, aqt.mw.migaku_kanji_db.make_cards_from_characters, ct, new, None
            )


def reviewer_will_answer_hook(status, reviewer, card: anki.collection.Card):
    proceed, ease = status

    # Learning card?
    if card.type == 0:
        check_learn_ahead(card.did)
        aqt.mw.migaku_kanji_db.on_note_update(card.nid, card.did, is_new=False)

    return status


aqt.gui_hooks.reviewer_will_answer_card.append(reviewer_will_answer_hook)


def learn_ahead_refresh_on_review_start(state, old_state):
    if state == "review":
        aqt.mw.migaku_kanji_db.refresh_learn_ahead()


aqt.gui_hooks.state_will_change.append(learn_ahead_refresh_on_review_start)
