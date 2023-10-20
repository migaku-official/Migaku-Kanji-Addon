from collections import defaultdict
import aqt
from aqt.qt import (
    QDialog,
    QDialogButtonBox,
    QAbstractListModel,
    QAbstractItemView,
    QColor,
    QLabel,
    QListView,
    QMessageBox,
    Qt,
    QModelIndex,
    QVariant,
    QVBoxLayout,
    QBrush,
)

from . import util
from .card_type import CardType
from .lookup_window import LookupWindow


class KanjiMarkModel(QAbstractListModel):
    state_colors = [
        "#41d0b6",
        "#2cadf6",
        "#f9371c",
    ]

    def __init__(self):
        super().__init__()
        self.kanji = []
        self.states = defaultdict(lambda: 0)

    def add(self, kanji_list):
        new_kanji = [kanji for kanji in kanji_list if kanji not in self.kanji]

        if len(new_kanji) == 0:
            return

        self.beginInsertRows(
            QModelIndex(),
            len(self.kanji),
            len(self.kanji) + len(new_kanji) - 1,
        )
        self.kanji.extend(new_kanji)
        self.endInsertRows()

    def data(self, idx, role):
        if not idx.isValid():
            return QVariant()

        kanji = self.kanji[idx.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            # This should be a QBrush, but we also use the method
            if kanji[0] != '[':
                return str(kanji)
        if role == Qt.ItemDataRole.DecorationRole:
            if kanji[0] == '[':
                return util.get_pixmap_from_tag(kanji, 35)
        if role == Qt.ItemDataRole.BackgroundRole:
            state = self.states[kanji]
            return QBrush(QColor(self.state_colors[state]))

        return QVariant()

    def rowCount(self, _parent):
        return len(self.kanji)

    def cycle(self, idx):
        if idx.isValid():
            kanji = self.kanji[idx.row()]
            state = self.states[kanji]
            state += 1
            if state > 2:
                state = 0

            self.states[kanji] = state
            self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.BackgroundRole])

    def with_state(self, state: int):
        return [kanji for kanji in self.kanji if self.states[kanji] == state]

    def to_add(self):
        return self.with_state(0)

    def to_mark(self):
        return self.with_state(1)


class KanjiMarkWidget(QListView):
    def __init__(self):
        super().__init__()

        self._model = KanjiMarkModel()
        self.setModel(self._model)

        self.setFlow(QListView.Flow.LeftToRight)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        font = self.font()
        font.setPixelSize(35)
        self.setFont(font)
        self.setSpacing(5)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

    def mousePressEvent(self, event):
        pos = event.pos()
        idx = self.indexAt(pos)

        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            txt = self._model.data(idx, Qt.ItemDataRole.DisplayRole)
            if txt and isinstance(txt, str):
                LookupWindow.open(txt)
        else:
            self._model.cycle(idx)

    def mouseDoublePressEvent(self, event):
        self.mousePressEvent(event)  # hack

    def add(self, kanji):
        self._model.add(kanji)

    def to_add(self):
        return self._model.to_add()

    def to_mark(self):
        return self._model.to_mark()


class KanjiConfirmDialog(QDialog):
    instance = None

    def __init__(self, parent=None, ct_kanji={}):
        super().__init__(parent)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle("Migaku Kanji - Found New Kanji")

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        info_lbl = QLabel(
            "If a Kanji is marked green, a card will be created. Blue ones will be marked known. Red ones will be ignored.\n\n"
            "Click kanji to cycle through the states.\n"
        )
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        self.card_type_widgets = {}
        self.card_type_labels = {}

        for card_type in CardType:
            card_type_label = QLabel(card_type.name)
            card_type_label.setHidden(True)
            lyt.addWidget(card_type_label)
            self.card_type_labels[card_type] = card_type_label

            ct_kmw = KanjiMarkWidget()
            ct_kmw.setHidden(True)
            lyt.addWidget(ct_kmw)
            self.card_type_widgets[card_type] = ct_kmw

        self.resize(500, 400)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        lyt.addWidget(button_box, Qt.AlignmentFlag.AlignRight)

        self.add_kanji(ct_kanji)

    def on_close(self):
        if KanjiConfirmDialog.instance == self:
            KanjiConfirmDialog.instance = None

    def add_kanji(self, ct_kanji):
        for ct in ct_kanji:
            ct_kmw = self.card_type_widgets[ct]
            kanji = ct_kanji[ct]
            ct_kmw.add(kanji)
            ct_kmw.setHidden(False)
            self.card_type_labels[ct].setHidden(False)

    def accept(self):
        database = aqt.mw.migaku_kanji_db

        for ct in self.card_type_widgets:
            ctw = self.card_type_widgets[ct]
            to_add = ctw.to_add()

            if len(to_add) < 1:
                continue

            util.error_msg_on_error(
                self,
                database.make_cards_from_characters,
                ct,
                to_add,
                "Automatic Kanji Card Cration",
            )

            to_mark = ctw.to_mark()
            database.mass_set_characters_known(ct, to_mark)

        self.on_close()
        super().accept()

    def reject(self):
        response = QMessageBox.question(
            self,
            "Migaku Kanji",
            "Do you really want to ignore these Kanji? No kanji cards will be created and none will be marked known.",
        )
        if response == QMessageBox.StandardButton.Yes:
            self.on_close()
            super().reject()

    @classmethod
    def _show_new_kanji(cls, card_type_kanji, parent=None):
        if cls.instance is None:
            cls.instance = cls(parent, card_type_kanji)
            cls.instance.show()
        else:
            cls.instance.add_kanji(card_type_kanji)
            util.raise_window(cls.instance)

    @classmethod
    def show_new_kanji(cls, card_type_kanji, parent=None):
        aqt.mw.taskman.run_on_main(lambda: cls._show_new_kanji(card_type_kanji, parent))
