import sys
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt

from TaskTonic import ttFormula, ttTimerSingleShot
from TaskTonic.ttTonicStore import ttPyside6Ui, ttPysideWindow, ttPysideWidget


class TrafficLightWidget(ttPysideWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl = QLabel("INIT")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("font-size: 30px; font-weight: bold; padding: 20px; background: #333; color: white;")
        self.layout.addWidget(self.lbl)

        # Widget naam: btn_next
        self.btn_next = QPushButton("Next State")
        self.layout.addWidget(self.btn_next)

    # --- State Machine Event Handling ---

    # Syntax: ttqt_<state>__<widget>__<signal>
    # TaskTonic maakt hiervan automatisch één wrapper 'ttqt__btn_next__clicked'
    # en zorgt dat de juiste methode wordt aangeroepen op basis van de state.

    def ttqt_red__btn_next__clicked(self):
        self.log("Klik in ROOD -> ga naar GROEN")
        self.to_state('green')

    def ttqt_green__btn_next__clicked(self):
        self.log("Klik in GROEN -> ga naar GEEL")
        self.to_state('yellow')

    def ttqt_yellow__btn_next__clicked(self):
        self.log("Klik in GEEL -> ga naar ROOD")
        self.to_state('red')

    def ttse_yellow__on_timer(self, info):
        self.log("Timer!! -> ga naar ROOD")
        self.to_state('red')

    def ttqt__btn_next__released(self):
        self.log('button released')

    def ttqt_red__btn_next__pressed(self):
        self.log('button pressed in state red')


    # --- Lifecycle ---

    def ttse__on_start(self):
        self.to_state('red')

    def ttse__on_enter(self):
        state = self.get_current_state_name()

        # Update UI
        self.lbl.setText(state.upper())
        colors = {'red': '#f00', 'green': '#0f0', 'yellow': '#ff0'}
        self.lbl.setStyleSheet(f"font-size: 30px; padding: 20px; background: {colors.get(state)}; color: black;")

        self.bind(ttTimerSingleShot, seconds=2)

    def ttse_red__on_exit(self):
        self.log('exit red')
        # todo: waar komt put_sparkle vandaan rond to state??? (er komt er 1 extra als deze method er niet is)
        # todo: waarom duurt afsluiten zo lang, na indrukken [x] op window
        #  + Process finished with exit code -1073741819 (0xC0000005)
        # todo: mainwindow on_start duurt 1.2 sec!!??


class MainWindow(ttPysideWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("TaskTonic + PySide6 Pluggable Syntax")
        self.resize(300, 250)

        self.light = self.bind(TrafficLightWidget)
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
        ttPyside6Ui(name='main_catalyst')

    def creating_starting_tonics(self):
        MainWindow(context=-1)


if __name__ == "__main__":
    TrafficFormula()