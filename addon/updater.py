import anki
import aqt

from . import util
from . import text_parser


def update_migaku_kanji_db(*args, _old, **kwargs):
    has_db = hasattr(aqt.mw, 'migaku_kanji_db')
    util.log('Updating...')
    if has_db:
        try:
            aqt.mw.migaku_kanji_db.shutdown()
            util.log('DB shutdown')
        except Exception as e:
            util.log('DB shutdown error:', e)
    try:
        text_parser.parser.stop()
        util.log('Parser stopped')
    except Exception as e:
        util.log('Parser stop error:', e)
    try:
        r = _old(*args, **kwargs)
    except Exception as e:
        util.log('Add-on download/install failure:', e)
        raise e
    if has_db:
        try:
            aqt.mw.migaku_kanji_db.initialize()
            util.log('DB re-initialized')
        except Exception as e:
            util.log('DB re-initialize error:', e)
    try:
        text_parser.parser.start()
        util.log('Parser restarted')
    except Exception as e:
        util.log('Parser start error:', e)
    util.log('Update done')
    return r


aqt.addons.download_addons = anki.hooks.wrap(aqt.addons.download_addons, update_migaku_kanji_db, pos='around')
