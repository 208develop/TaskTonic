import sys
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt

from TaskTonic import *
from TaskTonic.ttTonicStore import ttPyside6Ui, ttPysideWindow, ttPysideWidget


class TrafficLightWidget(ttPysideWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tm_next = None

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl = QLabel("INIT")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("font-size: 30px; font-weight: bold; padding: 20px; background: #333; color: white;")
        self.layout.addWidget(self.lbl)

        # Widget naam: btn_next
        self.btn_next = QPushButton("Next State")
        self.layout.addWidget(self.btn_next)

    # --- Lifecycle ---

    def ttse__on_start(self):
        self.to_state('red')
        self.tm_next = ttTimerPausing(name='tm_next').pause()

    # --- State Machine Event Handling ---

    # Syntax: ttqt_<state>__<widget>__<signal>
    # TaskTonic maakt hiervan automatisch één wrapper 'ttqt__btn_next__clicked'
    # en zorgt dat de juiste methode wordt aangeroepen op basis van de state.

    def set_color(self, color):
        self.lbl.setText(color.upper())
        colors = {'red': '#f00', 'green': '#0f0', 'yellow': '#ff0', 'off': '#222'}
        self.lbl.setStyleSheet(f"font-size: 30px; padding: 20px; background: {colors.get(color)}; color: black;")

    def ttse_red__on_enter(self):
        self.log('COLOR RED')
        self.set_color('red')

    def ttqt_red__btn_next__clicked(self):
        self.to_state('green')

    def ttse_green__on_enter(self):
        self.log('COLOR GREEN')
        self.set_color('green')
        self.tm_next.change_timer(seconds=5).resume()

    def ttqt_green__btn_next__clicked(self):
        self.log("Klik in GROEN -> ga naar GEEL")
        self.to_state('yellow')

    def ttse_green__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('yellow')

    def ttse_yellow__on_enter(self):
        self.log('COLOR YELLOW')
        self.set_color('yellow')
        self.tm_next.change_timer(seconds=2.5).resume()

    def ttqt_yellow__btn_next__clicked(self):
        self.log("Klik in GEEL -> ga naar ROOD")
        self.to_state('red')

    def ttse_yellow__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('red')

    def ttse__on_exit(self):
        # for all states:
        self.tm_next.pause()
        self.log('COLOR OFF')
        self.set_color('off')

    # def ttqt__btn_next__released(self):
    #     self.log('button released')
    #
    # def ttqt_red__btn_next__pressed(self):
    #     self.log('button pressed in state red')

class MainWindow(ttPysideWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("TaskTonic + PySide6 Pluggable Syntax")
        self.resize(300, 250)

        self.light = TrafficLightWidget()
        self.setCentralWidget(self.light)

    def ttse__on_start(self):
        self.show()


class TrafficFormula(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttPyside6Ui(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        MainWindow()


if __name__ == "__main__":
    TrafficFormula()