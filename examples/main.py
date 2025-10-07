from TaskTonic import *

class MyTonic(ttTonic):
    def __init__(self, context, dup_at=0):
        super().__init__(context)
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
                self.bind(MyTonic, dup_at=0)
            self._tts__process(count)

    def ttse__on_finished(self):
        self.log('Finished')

class MyMachine(ttTonic):
    def ttse__on_start(self):
        self.to_state('init')
        self.ttsc__stepping()

    def ttsc__stepping(self):
        self.log('stepping')
        self.ttsc__step()
        self.ttsc__step()
        self.ttsc__step()
        self.ttsc__step()
        self.ttsc__step()
        self.ttsc__step1()
        self.ttsc__step()


    def ttse__on_enter(self):
        self.log(f'Entering state {self.get_current_state_name()}')

    def ttsc_init__step(self):
        self.to_state('s1')

    def ttsc_s1__step(self): self.to_state('s2')
    def ttsc_s2__step(self): self.to_state('s3')
    def ttsc_s3__step1(self): self.to_state('s4')
    def ttsc_s4__step(self): self.finish()


class myMixDrink(ttFormula):
    def creating_formula(self):
        return {

        }

    # def creating_main_catalyst(self):
    #     pass

    def creating_starting_tonics(self):
        # MyTonic(-1, dup_at=3)
        MyMachine(-1)

if __name__ == "__main__":
    myMixDrink()
