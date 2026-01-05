from TaskTonic import *

class HelloWorld(ttTonic):
    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)

    def ttse__on_start(self):
        self.tts__hello()

    def tts__hello(self):
        self.log('Hello ')
        self.tts__world()

    def tts__world(self):
        self.log('world, ')
        self.tts__welcome()

    def tts__welcome(self):
        self.log('welcome ')
        self.tts__to()

    def tts__to(self):
        self.log('to ')
        self.tts__tasktonic()

    def tts__tasktonic(self):
        self.log('TaskTonic!')
        self.finish()


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

    def creating_starting_tonics(self):
        HelloWorld()


if __name__ == '__main__':
    myApp(
