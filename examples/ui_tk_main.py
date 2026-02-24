import tkinter as tk

from TaskTonic import *
from TaskTonic.ttTonicStore import ttTkinterUi, ttTkinterFrame

class TrafficLightWidget(ttTkinterFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tm_next = None

    def setup_ui(self):
        # We gebruiken pack in plaats van QVBoxLayout
        self.lbl = tk.Label(self, text="INIT", font=("Arial", 30, "bold"), width=10, bg="#333", fg="white")
        self.lbl.pack(pady=20)

        # Widget naam: btn_next
        self.btn_next = tk.Button(self, text="Next State", font=("Arial", 14))
        self.btn_next.pack(pady=10)

    # --- Lifecycle ---

    def ttse__on_start(self):
        self.to_state('red')
        self.tm_next = ttTimerPausing(name='tm_next').pause()

    # --- State Machine Event Handling ---

    def set_color(self, color):
        colors = {'red': '#f00', 'green': '#0f0', 'yellow': '#ff0', 'off': '#222'}
        self.lbl.config(text=color.upper(), bg=colors.get(color, '#222'), fg="black")

    def ttse_red__on_enter(self):
        self.log('COLOR RED')
        self.set_color('red')

    # Tkinter syntax voor het 'command' attribuut van een button
    def tttk_red__btn_next__command(self):
        self.to_state('green')

    def ttse_green__on_enter(self):
        self.log('COLOR GREEN')
        self.set_color('green')
        self.tm_next.change_timer(seconds=5).resume()

    def tttk_green__btn_next__command(self):
        self.log("Klik in GROEN -> ga naar GEEL")
        self.to_state('yellow')

    def ttse_green__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('yellow')

    def ttse_yellow__on_enter(self):
        self.log('COLOR YELLOW')
        self.set_color('yellow')
        self.tm_next.change_timer(seconds=2.5).resume()

    def tttk_yellow__btn_next__command(self):
        self.log("Klik in GEEL -> ga naar ROOD")
        self.to_state('red')

    def ttse_yellow__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('red')

    def ttse__on_exit(self):
        self.tm_next.pause()
        self.log('COLOR OFF')
        self.set_color('off')


class MainWindow(ttTonic):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # In Tkinter is het root window al aangemaakt door de Catalyst
        self.root = self.base.root
        self.root.title("TaskTonic + Tkinter Pluggable Syntax")
        self.root.geometry("300x250")

        # Voeg de TrafficLightWidget toe aan het hoofdscherm
        self.light = TrafficLightWidget(parent=self.root)
        self.light.pack(expand=True, fill=tk.BOTH)

    def ttse__on_start(self):
        # We vangen het sluiten van het venster af om TaskTonic netjes af te sluiten
        self.root.protocol("WM_DELETE_WINDOW", self.ttsc__finish)

    def ttse__on_finished(self):
        # Als de MainWindow tonic klaar is, sluiten we Tkinter netjes af
        self.root.destroy()


class TrafficFormula(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttTkinterUi(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        MainWindow()


if __name__ == "__main__":
    TrafficFormula()