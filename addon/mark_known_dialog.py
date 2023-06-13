import aqt
from aqt.qt import *

import anki.find

from . import util
from . import text_parser
from .card_type_radio_buttons import CardTypeRadioButtons


class MarkKnownDialog(QDialog):

    presets = [
        ('JLPT',                 'jlpt',           1, 5,     5,  5),
        ('Kanken',               'kanken',         1, 10,    10, 10),
        ('Frequency',            'frequency_rank', 1, 99999, 1,  25),
        ('School Year',          'grade',          1, 6,     1,  1),
        ('RTK ID (Edition 1-5)', 'heisig_id5',     1, 99999, 1,  25),
        ('RTK ID (Edition 6+)',  'heisig_id6',     1, 99999, 1,  25),
        ('WaniKani',             'wk',             1, 60,    1,  1),
    ]


    def __init__(self, initial_kanji=None, parent=None):
        super(QDialog, self).__init__(parent)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Mark Kanji Known')

        info_lbl = QLabel('All kanji in the box below will be marked known for the specified learning type when you press OK.\n\n' \
                          'Kanji that have a kanji card associated with them will not be marked.\n\n' \
                          'If you want to unmark a kanji later, go to the lookup browser and hit the "Unmark as known" button. ' \
                          'You can also mark individual kanji known by Shift-clicking on the "Create Recognition/Production Card" buttons in the lookup browser.')
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        lyt.addWidget(QLabel('<hr>'))

        self.ct_selector = CardTypeRadioButtons()
        lyt.addWidget(self.ct_selector)

        self.txt_box = QPlainTextEdit()
        self.txt_box.setPlaceholderText('Enter Kanji which should be marked known')
        lyt.addWidget(self.txt_box)

        hlyt = QHBoxLayout()
        lyt.addLayout(hlyt)

        preset_btn = QPushButton('Load Preset')
        preset_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        preset_btn.clicked.connect(self.on_load_preset)
        hlyt.addWidget(preset_btn)

        self.preset_box = QComboBox()
        self.preset_box.addItems(p[0] for p in self.presets)
        self.preset_box.currentIndexChanged.connect(self.on_preset_change)
        hlyt.addWidget(self.preset_box)

        self.min_box = QSpinBox()
        self.min_box.setMaximumWidth(75)
        hlyt.addWidget(self.min_box)

        to_lbl = QLabel('to')
        to_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hlyt.addWidget(to_lbl)

        self.max_box = QSpinBox()
        self.max_box.setMaximumWidth(75)
        hlyt.addWidget(self.max_box)

        self.on_preset_change() # init first preset min/max

        if initial_kanji:
            self.txt_box.setPlainText(
                ''.join(text_parser.filter_cjk(initial_kanji))
            )
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.mark_known)
        btn_box.rejected.connect(self.reject)
        lyt.addWidget(btn_box)

    
    def on_preset_change(self):
        preset = self.presets[self.preset_box.currentIndex()]

        for box in [self.min_box, self.max_box]:
            box.setMinimum(preset[2])
            box.setMaximum(preset[3])
        self.min_box.setValue(preset[4])
        self.max_box.setValue(preset[5])


    def on_load_preset(self):
        preset = self.presets[self.preset_box.currentIndex()]

        column = preset[1]
        min_ = self.min_box.value()
        max_ = self.max_box.value()

        if min_ > max_:
            min_, max_ = max_, min_

        aqt.mw.migaku_kanji_db.crs.execute(
            F'SELECT * FROM characters WHERE {column} >= {min_} AND {column} <= {max_}'
        )

        characters = [x[0] for x in aqt.mw.migaku_kanji_db.crs.fetchall()]
        self.txt_box.setPlainText(''.join(characters))


    def mark_known(self):
        card_type = self.ct_selector.current_card_type
        characters = text_parser.filter_cjk(self.txt_box.toPlainText())
        aqt.mw.migaku_kanji_db.mass_set_characters_known(card_type, characters)
        self.accept()


    @classmethod
    def show_modal(cls, *args, **kwargs):
        dlg = cls(*args, **kwargs)
        return dlg.exec()



class MarkKnownFromNotesDialog(QDialog):

    def __init__(self, note_ids, parent=None):
        super(QDialog, self).__init__(parent)

        self.note_ids = note_ids

        self.setWindowIcon(util.default_icon())
        self.setWindowTitle('Migaku Kanji - Mark Kanji From Notes Known')

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        info_lbl = QLabel('All selected fields from selected notes will be scanned for kanji that appear in them.\n\n' \
                          'After you click OK you can review which kanji should be marked known and to which learning format this should apply.')
        info_lbl.setWordWrap(True)
        lyt.addWidget(info_lbl)

        lyt.addWidget(QLabel('<hr>'))

        lyt.addWidget(QLabel('Fields:'))

        self.list_box = QListWidget()
        for field_name in anki.find.fieldNamesForNotes(aqt.mw.col, note_ids):
            itm = QListWidgetItem(field_name)
            itm.setCheckState(Qt.Unchecked)
            self.list_box.addItem(itm)
        lyt.addWidget(self.list_box)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.on_ok)
        btn_box.rejected.connect(self.reject)
        lyt.addWidget(btn_box)

        self.resize(500, 350)


    def on_ok(self):
        checked_fields = set()
        for i in range(self.list_box.count()):
            itm = self.list_box.item(i)
            field_name = itm.data(Qt.ItemDataRole.DisplayRole)
            field_checked = itm.checkState() == Qt.CheckState.Checked
            if field_checked:
                checked_fields.add(field_name)

        kanji = set()

        for nid in self.note_ids:
            note = aqt.mw.col.getNote(nid)

            for field_name in checked_fields:
                note_field_names = aqt.mw.col.models.fieldNames(note.model())
                
                if field_name in note_field_names:
                    kanji.update(
                        text_parser.filter_cjk(note[field_name])
                    )

        dlg = MarkKnownDialog(kanji, self)
        r = dlg.exec()
        if r == QDialog.Accepted:
            self.accept()


    @classmethod
    def show_modal(cls, note_ids, parent=None):

        if note_ids is None or len(note_ids) < 1:
            return

        dlg = cls(note_ids, parent)
        return dlg.exec()
