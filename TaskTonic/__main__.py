import os

START_CODE = """\
from TaskTonic import *

\"\"\"
Welcome to TaskTonic!

This is Hello World, the TaskTonic way.
Look at it, try it, and read the docs
\"\"\"

class HelloWorld(ttTonic):
    def __init__(self, interval=1.5):
        super().__init__()
        self.interval = interval

    def ttse__on_start(self):
        ttTimerRepeat(seconds=self.interval, name='tm_step')
        self.to_state('hello')

    def ttse_hello__on_enter(self):
        self.log('Hello world')

    def ttse_hello__on_tm_step(self, tinfo):
        self.to_state('welcome')

    def ttse_welcome__on_enter(self):
        self.log('Welcome to TaskTonic')

    def ttse_welcome__on_tm_step(self, tinfo):
        self.to_state('ending')

    def ttse_ending__on_tm_step(self, tinfo):
        self.ttsc__finish()


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'HELLO WORLD'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),
        )

    def creating_starting_tonics(self):
        HelloWorld(1.5)
        # HelloWorld(.2) # you can try a second tonic!!!


if __name__ == '__main__':
    myApp()
"""


def generate_starter_file():
    filename = "hello_tasktonic.py"

    print("🍹 Welkom bij TaskTonic!")

    if os.path.exists(filename):
        print(f"⚠️ Je hebt al een '{filename}' in deze map staan.")
        return

    # Maak het bestand aan voor de gebruiker
    with open(filename, "w", encoding="utf-8") as f:
        f.write(START_CODE)

    print(f"✅ We hebben een startbestand voor je klaargezet: {filename}")
    print(f"🚀 Open het bestand in je editor, of test het direct met:")
    print(f"   python {filename}")


if __name__ == "__main__":
    generate_starter_file()