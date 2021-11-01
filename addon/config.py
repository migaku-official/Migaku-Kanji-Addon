import aqt


_config = aqt.mw.addonManager.getConfig(__name__)

def write():
    aqt.mw.addonManager.writeConfig(__name__, _config)

def get(key, default=None):
    if not key in _config and type(default) in [list, dict]:
        _config[key] = default.copy()
    return _config.get(key, default)

def set(key, value, do_write=False):
    _config[key] = value
    if do_write:
        write()

def has(key):
    return key in _config
