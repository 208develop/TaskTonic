from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from TaskTonic import ttFormula, ttLog
from TaskTonic.ttTonicStore import ttPyside6Ui, ttPysideWindow, ttPysideWidget


class ToggleGreetingWidget(ttPysideWidget):

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Label component named: lbl_text
        self.lbl_text = QLabel("--")
        self.lbl_text.setAlignment(Qt.AlignCenter)
        self.lbl_text.setStyleSheet("font-size: 20px; padding: 25px; background: #222; color: #fff;")
        self.layout.addWidget(self.lbl_text)

        # Button component named: btn_toggle
        self.btn_toggle = QPushButton("Toggle Greeting")
        self.btn_toggle.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.btn_toggle)

    def ttse__on_start(self):
        self.to_state("world")

    # --- STATE: IDLE ---
    def ttse_world__on_enter(self):
        self.lbl_text.setText("Hello World")

    def ttqt_world__btn_toggle__clicked(self):
        self.to_state("tasktonic")

    # --- STATE: GREET ---
    def ttse_tasktonic__on_enter(self):
        self.lbl_text.setText("Hello TaskTonic")

    def ttqt_tasktonic__btn_toggle__clicked(self):
        self.to_state("world")


class MainWindow(ttPysideWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("TaskTonic PySide6 Hello World")
        self.resize(400, 200)

        self.toggle_widget = ToggleGreetingWidget()
        self.setCentralWidget(self.toggle_widget)

    def ttse__on_start(self):
        self.show()


class HelloPySideFormula(ttFormula):

    def creating_formula(self):
        return {
            'tasktonic/log/to': 'ip',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttPyside6Ui(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        MainWindow()


if __name__ == "__main__":
    HelloPySideFormula()