from TaskTonic import *

class HelloWorld(ttTonic):
    def __init__(self, name=None, log_mode=None):
        super().__init__(name, log_mode)

    def ttse__on_start(self):
        ttTimerRepeat(seconds=1.5, name='tm_step')
        self.to_state('hello')

    def ttse_hello__on_enter(self):
        self.log('Hello world')

    def ttse_hello__on_tm_step(self, tinfo):
        self.to_state('welcome')

    def ttse_welcome__on_enter(self):
        self.log('Welcome to TaskTonic')

    def ttse_welcome__on_tm_step(self, tinfo):
        self.to_state('ending')

    def ttse_welcome__on_tm_step(self, tinfo):
        self.ttsc__finish()


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'ip'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        HelloWorld()


if __name__ == '__main__':
    app = myApp()
    print((app.ledger.sdump()))

