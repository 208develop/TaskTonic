from TaskTonic import *
from TaskTonic.ttLoggers import ttScreenLogService


class MyService(ttTonic):
    _tt_is_service = "my_service"
    _tt_base_essence = True

class MyProcess(ttTonic):
    def __init__(self, dup_at=0):
        super().__init__()
        self.dup_at = dup_at

    def ttse__on_start(self):
        self.log('Started')
        self.srv = MyService()
        self._tts__process(0)

    def _tts__process(self, count):
        count += 1
        self.log(f'Processing {count}')
        if count == 10:
            self.finish()
            pass
        else:
            if count == self.dup_at:
                self.log('duplicate')
                MyProcess(dup_at=0)
            self._tts__process(count)

    def ttse__on_finished(self):
        self.log('Finished')
        s = self.ledger.sdump()
        self.log(s)



class MyMachine(ttTonic):
    def ttse__on_start(self):
        self.srv = MyService()
        self.to_state('init')
        self.step_tmr = ttTimerRepeat(.5, name='stepper', sparkle_back=self.ttsc__step)
        self.disp_tmr = ttTimerRepeat(1, name='display', sparkle_back=self.ttsc__disp)

    def _ttss__main_catalyst_finished(self):
        pass # compleets catalyst after main catalyst stopped

    def ttsc__disp(self, timer_info):
        self.log(f'Called by: {ttSparkleStack().source}')

    def ttse__on_enter(self):
        self.log(f'Entering state {self.get_current_state_name()}')

    def ttse__on_exit(self):
        self.log(f'Exiting state {self.get_current_state_name()}')

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
        self.step_tmr.stop()
        self.finish()

    def ttse__on_finished(self):
        self.log('Finished')

class myMixDrink(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'DEMO PROJECT'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        p=MyProcess(dup_at=3)
        m=MyMachine()#log_mode='quiet')
#
if __name__ == "__main__":
    myMixDrink()
