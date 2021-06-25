from collections import defaultdict

import aqt
from aqt.qt import *

from . import util
from .card_type import CardType
from .lookup_window import LookupWindow


class KanjiMarkModel(QAbstractListModel):

    state_colors = [
        '#41d0b6',
        '#2cadf6',
        '#f9371c',
    ]

    def __init__(self, kanji):
        super(QAbstractListModel, self).__init__()
        self.kanji = kanji
        self.states = defaultdict(lambda: 0)

    def data(self, idx, role):
        if not idx.isValid():
            return QVariant()
        k = self.kanji[idx.row()]
        s = self.states[k]
        if role == Qt.DisplayRole:
            return self.kanji[idx.row()]
        if role == Qt.BackgroundRole:
            return QColor(self.state_colors[s])
        return QVariant()

    def rowCount(self, parent):
        return len(self.kanji)

    def cycle(self, idx):
        if idx.isValid():
            i = idx.row()
            k = self.kanji[i]
            s = self.states[k]
            s += 1
            if s > 2: s = 0
            self.states[k] = s
            self.dataChanged.emit(idx, idx)

    def with_state(self, state):
        ret = []
        for k in self.kanji:
            if self.states[k] == state:
                ret.append(k)
        return ret

    def to_add(self):
        return self.with_state(0)
    
    def to_mark(self):
        return self.with_state(1)
        



class KanjiMarkWidget(QListView):

    def __init__(self, kanji):
        super(QListView, self).__init__()

        self._model = KanjiMarkModel(kanji)
        self.setModel(self._model)

        self.setFlow(QListView.LeftToRight)
        self.setResizeMode(QListView.Adjust)
        font = self.font()
        font.setPixelSize(35)
        self.setFont(font)
        self.setSpacing(5)
        self.setViewMode(QListView.IconMode)
        self.setSelectionMode(QAbstractItemView.NoSelection)

    def mousePressEvent(self, event):
        pos = event.pos()
        idx = self.indexAt(pos)

        if event.modifiers() == Qt.ShiftModifier:
            txt = self._model.data(idx, Qt.DisplayRole)
            if txt:
                LookupWindow.open(txt)
        else:
            self._model.cycle(idx)

    def mouseDoublePressEvent(self, event):
        self.mousePressEvent(event) # hack

    def to_add(self):
        return self._model.to_add()
    
    def to_mark(self):
        return self._model.to_mark()




class KanjiConfirmDialog(QDialog):

    def __init__(self, ct_kanji, parent=None):
        super(QDialog, self).__init__(parent)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Found New Kanji')

        info_lbl = QLabel(
            'If a Kanji is marked green, a card will be created. Blue ones will be marked known. Red ones will be ignored.\n\n'
            'Click kanji to cylce through the states.\n'
        )
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        self.ct_widgets = {}

        for ct in ct_kanji.keys():
            kanji = ct_kanji[ct]

            lyt.addWidget(QLabel(ct.name))
            ct_kmw = KanjiMarkWidget(kanji)
            lyt.addWidget(ct_kmw)
            self.ct_widgets[ct] = ct_kmw

        self.resize(500, 400)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.accepted.connect(self.accept)
        lyt.addWidget(btn_box)


    def accept(self):

        for ct in self.ct_widgets:
            ctw = self.ct_widgets[ct]

            db = aqt.mw.migaku_kanji_db

            to_add = ctw.to_add()
            util.error_msg_on_error(
                self,
                db.make_cards_from_characters,
                ct, to_add, 'Automatic Kanji Card Cration'
            )

            to_mark = ctw.to_mark()
            db.mass_set_characters_known(ct, to_mark)

        super().accept()
