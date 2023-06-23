from aqt.qt import *

from .card_type import CardType


class CardTypeRadioButtons(QWidget):
    card_type_changed = pyqtSignal(object)

    def __init__(self, initial_card_type=None, vertical=False, parent=None):
        super(QWidget, self).__init__(parent)

        if vertical:
            self.lyt = QVBoxLayout()
        else:
            self.lyt = QHBoxLayout()
        self.lyt.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.lyt)

        if initial_card_type is None:
            initial_card_type = CardType.Recognition
        self.current_card_type = initial_card_type

        self.mapping = {}
        for ct in CardType:
            rb = QRadioButton(ct.name)
            self.lyt.addWidget(rb)
            if ct == self.current_card_type:
                rb.setChecked(True)
            self.mapping[rb] = ct
            rb.toggled.connect(self.on_rb_change)

    def add_custom_radio_button(self, button):
        self.lyt.addWidget(button)
        button.toggled.connect(self.on_rb_change)

    def on_rb_change(self, val):
        if val == True:
            rb = self.sender()

            # Ugly ugly ugly
            if rb not in self.mapping:
                self.current_card_type = None
            else:
                ct = self.mapping[rb]
                self.current_card_type = ct

            self.card_type_changed.emit(self.current_card_type)
