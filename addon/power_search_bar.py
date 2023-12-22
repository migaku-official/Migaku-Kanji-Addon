from . import util
import aqt
from aqt.qt import *


class ResultsBar():

    def __init__(self, layout, max_results, result_button_size, on_select_result_function, hide_empty_buttons=True):
        self.hide_empty_buttons = hide_empty_buttons
        self.on_select_result_function = on_select_result_function
        self.max_results = max_results
        self.button_size = result_button_size

        # search result buttons
        self.buttons_lyt = QHBoxLayout()

        layout.addLayout(self.buttons_lyt)
        self.buttons_lyt.setSpacing(3)
        self.buttons_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.buttons = []

        if aqt.theme.theme_manager.night_mode:
            self.color = QColor( 0xe9, 0xe9, 0xe9 )
            self.background_color = QColor( 0x45, 0x45, 0x45 )
        else:
            self.color = QColor( 0x20, 0x20, 0x20 )
            self.background_color = QColor( 0xe9, 0xe9, 0xe9 )
            
        btn_style_sheet = \
            f"color: {self.color.name()};" \
            f"background-color: {self.background_color.name()};"

        btn_style_sheet += \
            "font-size: 20px;" \
            "border-style: ridge;" \
            "border-width: 2px;" \
            "border-radius: 6px;" \
            "padding: 2px;"

        for i in range(max_results):
            result_btn = QPushButton('   ', objectName='result_btn_' + str(i+1))
            result_btn.setStyleSheet(btn_style_sheet)
            result_btn.setFixedWidth(result_button_size)
            result_btn.setFixedHeight(result_button_size)
            result_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            result_btn.clicked.connect(lambda state, x=result_btn: self.on_button_click(x))
            result_btn.character = None
            if self.hide_empty_buttons:
                result_btn.setVisible(False)
            else:
                result_btn.setText('')
            self.buttons_lyt.addWidget(result_btn)
            self.buttons.append(result_btn)


    def set_contents(self, contents):
        idx = 0
        for r in contents:
            if idx < self.max_results:
                btn = self.buttons[idx]
                btn.setVisible(True)
                if r[0] == '[':
                    btn.setText('')
                    icon_size = int(self.button_size*0.8)
                    pixmap = util.get_pixmap_from_tag(r, icon_size*2, self.color) # to avoid smoothing we double the size and then resize below
                    icon = QIcon(pixmap)
                    btn.setIcon(icon)
                    btn.setIconSize(QSize(icon_size,icon_size))
                else:
                    # normal unicode kanji character
                    btn.setText(r)
                    btn.setIcon(QIcon())
                btn.character = r
                idx += 1
        for i in range(idx,self.max_results):
            # clear/hide rest of the buttons
            btn = self.buttons[i]
            btn.character = None
            if self.hide_empty_buttons:
                btn.setVisible(False)
            else:
                btn.setText('')
                btn.setIcon(QIcon())


    def on_button_click(self, button):
        text = button.text()
        if button.character is not None:
            self.on_select_result_function(button.character)



class PowerSearchBar():

    def __init__(self, search_bar_layout, search_results_layout, max_results, result_button_width, on_select_result_function, hide_empty_result_buttons=True):

        self.on_select_result_function = on_select_result_function
        self.max_results = max_results

        # search bar
        self.input_bar = QLineEdit()
        self.input_bar.setPlaceholderText("")
        self.input_bar.returnPressed.connect(self.on_power_search_submit)
        self.input_bar.textChanged.connect(self.on_power_search_changed)
        search_bar_layout.addWidget(self.input_bar)

        self.results_bar = ResultsBar(search_results_layout, max_results, result_button_width, on_select_result_function, hide_empty_result_buttons)


    def on_power_search_changed(self):
        text = self.input_bar.text()
        result = aqt.mw.migaku_kanji_db.search_engine.search(text, self.max_results)
        self.results_bar.set_contents(result)

    def on_power_search_submit(self):
        btn = self.results_bar.buttons[0]
        if btn.character is not None:
            # There is a match from search engine --> Do not do any additional searches 
            # but just select the first match
            self.on_select_result_function(btn.character)
        else:
            text = self.input_bar.text()
            if len(text) > 0:
                # retain the old functionality of the search bar: Open many tabs (one for each character)
                self.on_select_result_function(text)


    def clear(self):
        self.input_bar.setText("")
        self.results_bar.set_contents([])