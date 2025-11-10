from TaskTonic import *
from TaskTonic.ttLoggers import ttScreenLogService

class MyProcess(ttTonic):
    def __init__(self, context=None, dup_at=0):
        super().__init__(context=context)
        self.dup_at = dup_at

    def ttse__on_start(self):
        self.log('Started')
        self._tts__process(0)

    def _tts__process(self, count):
        count += 1
        self.log(f'Processing {count}')
        if count == 10:
            self.finish()
        else:
            if count == self.dup_at:
                self.log('duplicate')
                self.bind(MyProcess, dup_at=0)
            self._tts__process(count)

    def ttse__on_finished(self):
        self.log('Finished')

class MyMachine(ttCatalyst):
    def ttse__on_start(self):
        self.to_state('init')
        self.tmr = self.bind(ttTimerRepeat, .5, name='stepper', sparkle_back=self.ttsc__step)
        self.log(f'Timer: {self.tmr}')

    def _ttss__main_catalyst_finished(self):
        pass # compleets catalyst after main catalyst stopped

    def ttse__on_enter(self):
        # self.log(f'Entering state {self.get_current_state_name()}')
        pass

    def ttsc_init__step(self, timer_info):
        self.log(f'timer info: {timer_info}')
        self.to_state('s1')

    def ttsc_s1__step(self, timer_info):
        self.to_state('s2')
    def ttsc_s2__step(self, timer_info):
        self.to_state('s3')
    def ttsc_s3__step(self, timer_info):
        self.log('Logging in state 4')
        self.to_state('s4')
    def ttsc_s4__step(self, timer_info):
        self.finish()


class myMixDrink(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    # def creating_main_catalyst(self):
    #     pass

    def creating_starting_tonics(self):
        MyProcess(dup_at=3)
        MyMachine()#log_mode='quiet')

if __name__ == "__main__":
    myMixDrink()
