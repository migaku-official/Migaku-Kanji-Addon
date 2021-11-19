import aqt
import anki

from .bridge_actions import handle_bridge_action


try:
    Previewer = aqt.browser.previewer.Previewer
except:
    Previewer = aqt.previewer.Previewer



def previewer_bridge_hook(previewer: Previewer, cmd: str, _old):

    if not handle_bridge_action(cmd, previewer=previewer):
        return _old(previewer, cmd)


Previewer._on_bridge_cmd = anki.hooks.wrap(
    Previewer._on_bridge_cmd,
    previewer_bridge_hook,
    'around'
)
