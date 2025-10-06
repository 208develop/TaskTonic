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


class myMixDrink(ttFormula):
    def creating_formula(self):
        return {

        }

    # def creating_main_catalyst(self):
    #     pass

    def creating_starting_tonics(self):
        MyTonic(-1, dup_at=3)


if __name__ == "__main__":
    myMixDrink()
