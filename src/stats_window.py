from collections import namedtuple, OrderedDict

import aqt
from aqt.qt import *

from . import util

from .card_type import CardType
from .lookup_window import LookupWindow
from .card_type_radio_buttons import CardTypeRadioButtons

class OrderedDefaultListDict(OrderedDict):

    def __missing__(self, key):
        self[key] = value = []
        return value


def format_counter(x):
    if x == 1:
        return '1st'
    if x == 2:
        return '2nd'
    if x == 3:
        return '3rd'
    return F'{x}th'

class StatsWindow(QDialog):

    # Label, sort column, order, level decorator function, only show ones with existing card
    options = [
        ('JLPT',                                    'jlpt',           'DESC', lambda x: F'N{x}',                      False),
        ('Kanken',                                  'kanken',         'DESC', lambda x: F'Level {x}',                 False),
        ('School Year',                             'grade',          'ASC',  lambda x: F'{format_counter(x)} Grade', False),
        ('Remembering the Kanji (1st-5th edition)', 'heisig_id5',     'ASC',  None,                                   False),
        ('Remembering the Kanji (6th+ edition)',    'heisig_id6',     'ASC',  None,                                   False),
        ('All Kanji in Collection',                 'frequency_rank', 'ASC',  None,                                   True ),
    ]

    addon_web_uri = F'/_addons/{__name__.split(".")[0]}'    # uhhhhh

    @classmethod
    def web_uri(cls, name):
        return cls.addon_web_uri + '/web/' + name

    @classmethod
    def font_uri(cls, name):
        return cls.addon_web_uri + '/fonts/' + name

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle('Migaku Kanji - Stats')
        self.setWindowIcon(util.default_icon())
        self.setMinimumSize(400, 300)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        options_lyt = QHBoxLayout()
        lyt.addLayout(options_lyt)

        options_lyt.addStretch()

        self.ct_selector = CardTypeRadioButtons()
        self.ct_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        options_lyt.addWidget(self.ct_selector)

        self.options_box = QComboBox()
        for (label, *_) in self.options:
            self.options_box.addItem(label)
        options_lyt.addWidget(self.options_box)

        options_lyt.addStretch()

        self.web = aqt.webview.AnkiWebView()
        self.web.onBridgeCmd = self.on_bridge_cmd
        lyt.addWidget(self.web)

        self.staic_html = \
             '<style>\n' \
            F'@font-face {{ font-family: kanji_font1; src: url("{self.font_uri("yumin.ttf")}"); }}\n' \
            F'@font-face {{ font-family: kanji_font2; src: url("{self.font_uri("yugothb.ttc")}"); }}\n' \
            F'@font-face {{ font-family: kanji_font3; src: url("{self.font_uri("hgrkk.ttc")}"); }}\n' \
             '\n</style>' \
            F'<link rel="stylesheet" href="{self.web_uri("stats_style.css")}">' \
             '<script>function kanji_click() { pycmd("show_kanji-" + $(this).text()); }</script>'

        self.ct_selector.card_type_changed.connect(self.refresh)
        self.options_box.currentIndexChanged.connect(self.refresh)

        self.refresh()


    def refresh(self):
        
        option = self.options[self.options_box.currentIndex()]
        option_label = option[0]
        column = option[1]
        order = option[2]
        level_decorator = option[3]
        only_with_card = option[4]

        card_type = self.ct_selector.current_card_type

        if only_with_card:
            where = F'usr.{card_type.label}_card_ids.card_id NOT NULL'
        else:
            where = F'{column} NOT NULL'

        aqt.mw.migaku_kanji_db.crs.execute(
            F'SELECT characters.character, {column}, card_id ' \
                 'FROM characters ' \
                F'LEFT JOIN usr.{card_type.label}_card_ids ON characters.character == usr.{card_type.label}_card_ids.character ' \
                F'WHERE {where} ORDER BY {column} {order} '
        )
        r = aqt.mw.migaku_kanji_db.crs.fetchall()

        curr_lvl = None
        is_open = False
        

        categories = OrderedDefaultListDict()
        Entry = namedtuple('Entry', 'kanji card_id ival')

        for (kanji, lvl, card_id) in r:

            if level_decorator is None:
                lvl = 0

            ivl_days = 0

            if card_id is not None:
                card = aqt.mw.col.getCard(card_id)
                if card.ivl is None:
                    ivl_days = 0
                if card.ivl < 0:
                    ivl_days = (-card.ivl) / (24*60*60)
                else:
                    ivl_days = card.ivl

            entry = Entry(kanji, card_id, ivl_days)
            categories[lvl].append(entry)


        good = 0
        count = 0

        category_pts = []
        for category, entries in categories.items():
            category_good = 0
            entry_pts = []

            for (kanji, card_id, ival) in entries:
                if card_id is None:
                    color = '#f82226'
                elif ival == 0:         # card, but no interval
                    color = '#f84c2a'
                elif ival < 21:         # seen
                    color = '#f8d732'
                else:                   # known
                    color = '#74f82d'
                    category_good += 1

                entry_pts.append(F'<div style="background-color:{color}">' + kanji + '</div>')

            category_count = len(entries)

            count += category_count
            good += category_good

            category_pts.append(F'<div class="kanji_category">')
            if level_decorator:
                category_label = level_decorator(category)
                category_pts.append(F'<div class="kanji_category_header">{category_label}</div>')
                category_pts.append(F'<div class="kanji_category_stats">{category_good} / {category_count} - {(category_good/category_count*100):.2f}%</div>')
            category_pts.append('<div class="kanji_category_entries">')
            category_pts.extend(entry_pts)
            category_pts.append('</div>')
            category_pts.append('</div>')

        html_pts = []

        html_pts.append('<div class="header">')
        html_pts.append(F'<div class="header_text">{option_label}</div>')
        html_pts.append(F'<div class="stats">{good} / {count} - {(good/count*100):.2f}%</div>')
        html_pts.append('</div>')

        html_pts.append('<hr>')

        html_pts.extend(category_pts)

        html_pts.append(
            '<script>$(".kanji_category_entries div").click(kanji_click);</script>'
        )

        self.web.stdHtml(
            self.staic_html + ''.join(html_pts)
        )


    def on_bridge_cmd(self, cmd):
        args = cmd.split('-')
        if len(args) < 1:
            return

        if args[0] == 'show_kanji':
            LookupWindow.open(args[1])
        else:
            print('Unhandled bridge command:', args)



    @classmethod
    def open(cls):
        window = StatsWindow(aqt.mw)
        window.show()
