from collections import namedtuple, OrderedDict, defaultdict

import anki

import aqt
from aqt.qt import *

from . import util
from . import config
from . import text_parser
from . import fonts
from .card_type import CardType
from .lookup_window import LookupWindow
from .card_type_radio_buttons import CardTypeRadioButtons


class OrderedDefaultListDict(OrderedDict):
    def __missing__(self, key):
        self[key] = value = []
        return value


def card_ival(card):
    if card.ivl is None:
        return 0
    if card.ivl < 0:
        return (-card.ivl) / (24 * 60 * 60)
    return card.ivl


def format_grade(n):
    if n > 6:
        return "中学校"

    numbers = "０１２３４５６７８９"
    return f"小学校{numbers[n]}年"


class WordKanjiWorker(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super(QObject, self).__init__()
        self.word_kanji_ival = defaultdict(int)

    def run(self):
        # yeah this code slow and copy pasted a few too many times lmao who cares
        for entry in config.get("word_recognized", []):
            entry_note = entry["note"]
            entry_card = entry["card"]
            entry_deck = entry["deck"]
            entry_field = entry["field"]

            find_filter = [f'"note:{entry_note}"', f'"card:{entry_card+1}"']
            if entry_deck != "All":
                find_filter.append(f'"deck:{entry_deck}"')

            entry_note_ids = aqt.mw.col.find_notes(" AND ".join(find_filter))

            for note_id in entry_note_ids:
                note = aqt.mw.col.getNote(note_id)
                field_value = note[entry_field]
                for card in note.cards():
                    ival = card_ival(card)
                    for c in field_value:
                        self.word_kanji_ival[c] = max(self.word_kanji_ival[c], ival)
        self.finished.emit()


class StatsWindow(QDialog):
    # Label, sort column, additional filter, order, level decorator function, only show ones with existing card
    options = [
        ("日本語能力試験 (JLPT)", "jlpt", None, "DESC", lambda x: f"N{x}", False),
        ("日本漢字能力検定 (Kanken)", "kanken", None, "DESC", lambda x: f"Level {x}", False),
        ("学年 (School Year)", "grade", "grade <= 8", "ASC", format_grade, False),
        ("常用 (Jōyō)", "frequency_rank", "grade <= 8", "ASC", None, False),
        (
            "人名用 (Jinmeiyō)",
            "frequency_rank",
            "grade >= 9 AND grade <= 10",
            "ASC",
            None,
            False,
        ),
        (
            "Remembering the Kanji (1st-5th edition)",
            "heisig_id5",
            None,
            "ASC",
            None,
            False,
        ),
        (
            "Remembering the Kanji (6th+ edition)",
            "heisig_id6",
            None,
            "ASC",
            None,
            False,
        ),
        ("WaniKani", "wk", None, "ASC", lambda x: f"Level {x}", False),
        ("All with Card in Collection", "frequency_rank", None, "ASC", None, True),
    ]

    instance = None

    @classmethod
    def web_uri(cls, name):
        return util.addon_web_base + "/web/" + name

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)

        StatsWindow.instance = self

        self.word_kanji_ival = None

        self.setWindowTitle("Migaku Kanji - Stats")
        self.setWindowIcon(util.default_icon())
        self.setMinimumSize(400, 300)

        lyt = QVBoxLayout()
        self.setLayout(lyt)

        options_lyt = QHBoxLayout()
        lyt.addLayout(options_lyt)

        options_lyt.addStretch()

        self.ct_selector = CardTypeRadioButtons()
        self.ct_selector.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        options_lyt.addWidget(self.ct_selector)

        self.registered_btn = QRadioButton("Registered Fields")
        self.ct_selector.add_custom_radio_button(self.registered_btn)

        self.options_box = QComboBox()
        for label, *_ in self.options:
            self.options_box.addItem(label)
        options_lyt.addWidget(self.options_box)

        options_lyt.addStretch()

        self.web = aqt.webview.AnkiWebView()
        self.web.onBridgeCmd = self.on_bridge_cmd
        lyt.addWidget(self.web)

        bundled_js = self.web.bundledScript("webview.js")
        style_class = "dark" if aqt.theme.theme_manager.night_mode else "light"

        html = f"""
            <!doctype html>
            <html class="{style_class}">
                {aqt.mw.baseHTML()}
                {bundled_js}
                <style>
                    {fonts.ui_css()}
                </style>
                <link rel="stylesheet" href="{self.web_uri('stats_styles.css')}">
                <script src="{self.web_uri('jquery.js')}"></script>
                <script>
                    let can_mark = false;

                    function kanji_click(evt)
                    {{
                        if (evt.shiftKey)
                        {{
                            if (can_mark)
                            {{
                                if ($(this).hasClass('unknown'))
                                {{
                                    $(this).removeClass('unknown');
                                    $(this).addClass('marked_known');
                                    pycmd('mark-' + $(this).text() + '-1');
                                }}
                                    
                                else if ($(this).hasClass('marked_known'))
                                {{
                                    $(this).removeClass('marked_known');
                                    $(this).addClass('unknown');
                                    pycmd('mark-' + $(this).text() + '-0');
                                }}

                                document.getSelection().removeAllRanges();
                            }}
                        }}
                        else
                            pycmd('show_kanji-' + $(this).text());
                    }}
                </script>
            <head>

            </head>

            <body class="{style_class} fullColor">
                <div class="container {style_class}">
                    <div class="tooltip_toggle">
                    i
                    <div class="tooltip_background"></div>
                        <div class="tooltip_content">
                            <div class="row">
                                <span class="kanji unknown">磨</span>
                                <p>Unknown (no card)</p>
                            </div>
                            <div class="row">
                                <span class="kanji unknown_with_card">磨</span>
                                <p>Unknown (unstudied card)</p>
                            </div>
                            <div class="row">
                                <span class="kanji learning">磨</span>
                                <p>Learning (card with interval less than 21 days)</p>
                            </div>
                            <div class="row">
                                <span class="kanji known">磨</span>
                                <p>Known (card with interval greater than 21 days)</p>
                            </div>

                            <hr>

                            <div id="color_toggle_row">
                                <input type="checkbox" class="toggle" id="switch" checked />
                                <label for="switch" class="toggle">Toggle</label>
                                <span>Full color kanji</span>
                            </div>
                        </div>
                    </div>
                    <span id="dynamic"></span>
                </div>
                <script>
                    $('#switch').change(function(){{ $('body').toggleClass('fullColor', this.checked); }});
                </script>
            </body>
        </html>
        """

        self.web.setHtml(html)

        self.ct_selector.card_type_changed.connect(self.refresh)
        self.options_box.currentIndexChanged.connect(self.refresh)

        self.refresh()

    def closeEvent(self, evt):
        if StatsWindow.instance == self:
            StatsWindow.instance = None
        return QDialog.closeEvent(self, evt)

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_F11:
            self.toggle_fullscreen()
            return
        return QDialog.keyPressEvent(self, evt)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def start_kanji_word_worker(self):
        aqt.mw.progress.start(label="Accumulating word kanji...", immediate=True)
        aqt.mw.progress._win.setWindowTitle("Kanji Stats")

        self.word_kanji_worker_thread = QThread()
        self.word_kanji_worker = WordKanjiWorker()
        self.word_kanji_worker.moveToThread(self.word_kanji_worker_thread)
        self.word_kanji_worker_thread.started.connect(self.word_kanji_worker.run)
        self.word_kanji_worker.finished.connect(self.word_kanji_worker_thread.quit)
        self.word_kanji_worker_thread.finished.connect(self.kanji_word_worker_done)
        self.word_kanji_worker_thread.start()

    def kanji_word_worker_done(self):
        self.word_kanji_ival = self.word_kanji_worker.word_kanji_ival
        self.word_kanji_worker.deleteLater()
        self.word_kanji_worker_thread.deleteLater()
        aqt.mw.progress.finish()
        self.refresh()

    def refresh(self):
        option = self.options[self.options_box.currentIndex()]
        option_label = option[0]
        column = option[1]
        additional_filter = option[2]
        order = option[3]
        level_decorator = option[4]
        only_with_card = option[5]
        registered_cards = self.registered_btn.isChecked()

        if registered_cards:
            if self.word_kanji_ival is None:
                self.start_kanji_word_worker()
                # automatically recalls refresh when done
                return

            if only_with_card:
                # More horrific code here...
                wks = ",".join(
                    f'"{wk}"' for wk in text_parser.filter_cjk(self.word_kanji_ival)
                )
                aqt.mw.migaku_kanji_db.crs.execute(
                    "SELECT characters.character, frequency_rank "
                    f"FROM characters WHERE characters.character IN ({wks}) ORDER BY frequency_rank ASC"
                )
                qr = aqt.mw.migaku_kanji_db.crs.fetchall()

            else:
                where = f"{column} NOT NULL"

                if additional_filter:
                    where += " AND " + additional_filter

                aqt.mw.migaku_kanji_db.crs.execute(
                    f"SELECT characters.character, {column} "
                    "FROM characters "
                    f"WHERE {where} ORDER BY {column} {order} "
                )
                qr = aqt.mw.migaku_kanji_db.crs.fetchall()

            r = []

            for char, col in qr:
                ival = None
                if char in self.word_kanji_ival:
                    ival = self.word_kanji_ival[char]
                r.append((char, col, ival))

        else:
            card_type = self.ct_selector.current_card_type

            if only_with_card:
                where = f"usr.{card_type.label}_card_ids.card_id NOT NULL"
            else:
                where = f"{column} NOT NULL"

            if additional_filter:
                where += " AND " + additional_filter

            aqt.mw.migaku_kanji_db.crs.execute(
                f"SELECT characters.character, {column}, card_id "
                "FROM characters "
                f"LEFT JOIN usr.{card_type.label}_card_ids ON characters.character == usr.{card_type.label}_card_ids.character "
                f"WHERE {where} ORDER BY {column} {order} "
            )
            r = aqt.mw.migaku_kanji_db.crs.fetchall()

        curr_lvl = None
        is_open = False

        categories = OrderedDefaultListDict()

        for kanji, lvl, card_id_or_ival in r:
            if level_decorator is None:
                lvl = 0

            ivl_days = 0
            card_id = None
            marked_known = False

            if registered_cards:
                card_id = 0 if card_id_or_ival else None
                ivl_days = card_id_or_ival or 0

            else:
                card_id = card_id_or_ival

                if card_id is not None:
                    if card_id < 0:  # marked known
                        marked_known = True
                    else:
                        try:
                            card = aqt.mw.col.get_card(card_id)
                            ivl_days = card_ival(card)
                        except (
                            Exception
                        ):  # cannot be more specifc as this is different in anki versions
                            card_id = None
                            ivl_days = 0

            entry = (kanji, card_id, ivl_days, marked_known)
            categories[lvl].append(entry)

        good = 0
        count = 0

        category_pts = []
        for category, entries in categories.items():
            category_good = 0
            entry_pts = []

            for kanji, card_id, ival, marked_known in entries:
                if marked_known:
                    class_ = "marked_known"
                    category_good += 1
                elif card_id is None:
                    class_ = "unknown"
                elif ival == 0:
                    class_ = "unknown_with_card"
                elif ival < 21:
                    class_ = "learning"
                else:
                    class_ = "known"
                    category_good += 1

                if kanji[0] == "[":
                    img = kanji[1:-1]
                    path = util.addon_web_uri('primitives','%s.svg' % img)
                    kanji = f'<img src="{path}">'
                entry_pts.append(f'<span class="kanji {class_}">' + kanji + "</span>")

            category_count = len(entries)

            count += category_count
            good += category_good

            category_percentage = 0
            if category_count > 0:
                category_percentage = category_good / category_count * 100

            category_pts.append(f'<div class="kanjis_category">')
            if level_decorator:
                category_pts.append(f'<div class="header">')
                category_label = level_decorator(category)
                category_pts.append(f"<h2>{category_label}</h2>")
                category_pts.append(
                    f"<h3>{category_good} / {category_count} - {category_percentage:.2f}%</h3>"
                )
                category_pts.append("</div>")
            category_pts.append('<div class="kanjis">')
            category_pts.extend(entry_pts)
            category_pts.append("</div>")
            category_pts.append("</div>")

        html_pts = []

        percentage = 0
        if count > 0:
            percentage = good / count * 100

        html_pts.append('<div class="header">')
        html_pts.append(f"<h1>{option_label}</h1>")
        html_pts.append(f"<h3>{good} / {count} - {percentage:.2f}%</h3>")
        html_pts.append("</div>")

        if level_decorator:
            html_pts.append("<hr>")

        html_pts.extend(category_pts)

        can_mark = self.ct_selector.current_card_type is None
        self.web.eval(f'can_mark = {"false" if can_mark else "true"};')
        self.web.eval('$("#dynamic").html(\'' + "".join(html_pts) + "');")
        self.web.eval('$(".kanjis_category .kanji").click(kanji_click);')

    def on_bridge_cmd(self, cmd):
        args = cmd.split("-")
        if len(args) < 1:
            return

        if args[0] == "show_kanji":
            LookupWindow.open(args[1])
        elif args[0] == "mark":
            card_type = self.ct_selector.current_card_type
            if card_type is None:
                return
            character = args[1]
            known = args[2] == "1"
            aqt.mw.migaku_kanji_db.set_character_known(card_type, character, known)
            # JS does the refreshing itself
        else:
            print("Unhandled bridge command:", args)

    @classmethod
    def open(cls):
        if StatsWindow.instance:
            StatsWindow.instance.raise_()
            StatsWindow.instance.activateWindow()
        else:
            window = StatsWindow(aqt.mw)
            window.show()
