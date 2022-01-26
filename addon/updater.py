import anki
import aqt

from . import util
from . import text_parser


download_and_install_addon_original = aqt.addons.download_and_install_addon

def download_and_install_addon(mgr, client, id):
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
        r = download_and_install_addon_original(mgr, client, id)
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

aqt.addons.download_and_install_addon = download_and_install_addon
