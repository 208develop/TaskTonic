from TaskTonic import *
from TaskTonic.ttTonicStore import ttDistiller
import json, time

class DUT(ttTonic):
    def ttse__on_start(self):
        self.log('DUT started')
        self.to_state('init')

    def ttse__on_finished(self):
        self.log('DUT finished')

    def ttse__on_enter(self):
        self.log('generic state enter')

    def ttse_init__on_enter(self):
        self.to_state('paused')

    def ttsc_paused__start_timer(self):
        ttTimerSingleShot(seconds=2)
        self.to_state('wait_on_timer')

    def ttse_wait_on_timer__on_timer(self, info):
        self.to_state('paused')

class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        self.dist = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.dut = DUT(name='TonicUnderTest')

recipe = TestRecipe()
distiller = recipe.dist
dut = recipe.dut

print(dut._index_to_state)
print(dut.sparkles)

distiller.stat_print(distiller.sparkle( timeout=5, till_state_in='paused'), dut.id)

print('start timer')
dut.ttsc__start_timer()

distiller.stat_print(distiller.sparkle( timeout=5, till_state_in='wait_on_timer'), dut.id)
distiller.stat_print(distiller.sparkle( timeout=5, till_sparkle_in='ttse__on_timer'), dut.id)
distiller.stat_print(distiller.sparkle( timeout=3))

print('finishing')
distiller.stat_print(distiller.finish_distiller(), 2)
