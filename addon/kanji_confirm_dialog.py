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

    def __init__(self):
        super().__init__()
        self.kanji = []
        self.states = defaultdict(lambda: 0)

    def add(self, kanji):
        new_kanji = []
        for k in kanji:
            if k not in self.kanji:
                new_kanji.append(k)
        if len(new_kanji) > 0:
            self.beginInsertRows(QModelIndex(), len(self.kanji), len(self.kanji) + len(new_kanji) - 1)
            self.kanji.extend(new_kanji)
            self.endInsertRows()

    def data(self, idx, role):
        if not idx.isValid():
            return QVariant()
        k = self.kanji[idx.row()]
        if role == Qt.DisplayRole:
            return str(k)
        if role == Qt.BackgroundRole:
            s = self.states[k]
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

    def __init__(self):
        super().__init__()

        self._model = KanjiMarkModel()
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

    def add(self, kanji):
        self._model.add(kanji)

    def to_add(self):
        return self._model.to_add()
    
    def to_mark(self):
        return self._model.to_mark()



class KanjiConfirmDialog(QDialog):

    instance = None

    def __init__(self, parent=None, ct_kanji=dict()):
        super().__init__(parent)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Found New Kanji')

        self.setWindowModality(Qt.ApplicationModal)

        info_lbl = QLabel(
            'If a Kanji is marked green, a card will be created. Blue ones will be marked known. Red ones will be ignored.\n\n'
            'Click kanji to cycle through the states.\n'
        )
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        self.ct_widgets = {}
        self.ct_labels = {}

        for ct in CardType:
            ct_label = QLabel(ct.name)
            ct_label.setHidden(True)
            lyt.addWidget(ct_label)
            self.ct_labels[ct] = ct_label

            ct_kmw = KanjiMarkWidget()
            ct_kmw.setHidden(True)
            lyt.addWidget(ct_kmw)
            self.ct_widgets[ct] = ct_kmw

        self.resize(500, 400)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.accepted.connect(self.accept)
        lyt.addWidget(btn_box)

        self.add_kanji(ct_kanji)


    def on_close(self):
        if KanjiConfirmDialog.instance == self:
            KanjiConfirmDialog.instance = None


    def add_kanji(self, ct_kanji):
        for ct in ct_kanji:
            ct_kmw = self.ct_widgets[ct]
            kanji = ct_kanji[ct]
            ct_kmw.add(kanji)
            ct_kmw.setHidden(False)
            self.ct_labels[ct].setHidden(False)


    def accept(self):

        db = aqt.mw.migaku_kanji_db

        for ct in self.ct_widgets:
            ctw = self.ct_widgets[ct]
            to_add = ctw.to_add()

            if len(to_add) < 1:
                continue

            util.error_msg_on_error(
                self,
                db.make_cards_from_characters,
                ct, to_add, 'Automatic Kanji Card Cration'
            )

            to_mark = ctw.to_mark()
            db.mass_set_characters_known(ct, to_mark)

        self.on_close()
        super().accept()


    def reject(self):
        r = QMessageBox.question(
            self,
            'Migaku Kanji',
            'Do you really want to ignore these Kanji? No kanji cards will be created and none will be marked known.'
        )
        if r == QMessageBox.Yes:
            self.on_close()
            super().reject()


    @classmethod
    def _show_new_kanji(cls, ct_kanji, parent=None):
        if cls.instance is None:
            cls.instance = cls(parent, ct_kanji)
            cls.instance.show()
        else:
            cls.instance.add_kanji(ct_kanji)
            util.raise_window(cls.instance)

    @classmethod
    def show_new_kanji(cls, ct_kanji, parent=None):
        aqt.mw.taskman.run_on_main(
            lambda: cls._show_new_kanji(ct_kanji, parent)
        )
