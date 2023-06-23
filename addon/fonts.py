import os
import shutil

from . import config
from . import util


defaults = [
    "SawarabiGothic.ttf",
    "nagayama_kai08.otf",
    "ArmedBanana.ttf",
    "KouzanGyousho.otf",
]
font_num = len(defaults)
config_default = [None] * font_num


def get_col_name(idx):
    name = get_name(idx)
    return f"_kanji_font{idx+1}_{name}"


def get_col_path(idx):
    return util.col_media_path(get_col_name(idx))


def get_addon_uri(idx):
    user_name = config.get("fonts", config_default)[idx]
    if user_name is None:
        return util.addon_web_uri("fonts", defaults[idx])
    return util.addon_web_uri("user_files", "fonts", user_name)


def get_path(idx):
    user_name = config.get("fonts", config_default)[idx]
    if user_name is None:
        return util.addon_path("fonts", defaults[idx])
    return util.user_path("fonts", user_name)


def get_name(idx):
    name_wprefix = os.path.basename(get_path(idx))
    i = name_wprefix.find("_")
    return name_wprefix[i + 1 :]


def set_path(idx, path):
    font_cfg = config.get("fonts", config_default)

    # Remove from collection media
    old_font_path_col = get_col_path(idx)
    try:
        os.remove(old_font_path_col)
    except OSError:
        pass

    # Remove from user dir
    old_user_name = font_cfg[idx]
    if old_user_name is not None:
        font_path_user = util.user_path("fonts", old_user_name)
        try:
            os.remove(font_path_user)
        except OSError:
            pass

    # Reset to default?
    if path is None:
        font_cfg[idx] = None

    # Custom file
    else:
        name = f"font{idx+1}_{os.path.basename(path)}"
        font_cfg[idx] = name

        user_fonts_dir = util.user_path("fonts")
        os.makedirs(user_fonts_dir, exist_ok=True)

        dst_path = os.path.join(user_fonts_dir, name)

        # Copy to user_files/fonts
        shutil.copy(path, dst_path)

    config.set("fonts", font_cfg, do_write=True)

    # Copy to collection media
    shutil.copy(get_path(idx), get_col_path(idx))


def card_css():
    ret = []
    for idx in range(font_num):
        col_name = get_col_name(idx)
        ret.append(
            f'@font-face {{ font-family: kanji_font{idx+1}; src: url("{col_name}"); }}'
        )
    return "\n".join(ret)


def ui_css():
    ret = []
    for idx in range(font_num):
        uri = get_addon_uri(idx)
        ret.append(
            f'@font-face {{ font-family: kanji_font{idx+1}; src: url("{uri}"); }}'
        )
    return "\n".join(ret)


def assure_col_media():
    for idx in range(font_num):
        shutil.copy(get_path(idx), get_col_path(idx))
