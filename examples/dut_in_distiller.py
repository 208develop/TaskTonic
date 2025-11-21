from TaskTonic import *
from TaskTonic.utils import ttDistiller
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
        self.bind(ttTimerSingleShot, 2)
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
        ttDistiller()

    def creating_starting_tonics(self):
        DUT(name='TonicUnderTest')

def print_status(status, filter=None):
    print('=== Sparkling ==')
    for t in status.get('sparkle_trace', []):
        if filter is None or filter == t['id']:
            e = t['at_enter']
            x = t['at_exit']
            ts = e['@']
            te = x['@']
            l_ts = f'{time.strftime("%H%M%S", time.localtime(ts))}.{int((ts - int(ts)) * 1000):03d}'
            l_te = f'{time.strftime("%H%M%S", time.localtime(te))}.{int((te - int(te)) * 1000):03d}'
            l_duration = f'{(te-ts):2.3f}'
            print(
                f"{t['id']:03d} - {t['tonic']}.{t['sparkle']} ( {t['args']}, {t['kwargs']} )\n"
                f"   at enter            at exit\n"
                f"   {l_ts}          {l_te}      --> {l_duration}s\n"
                f"   {e['state']:<20}{x['state']:<20}"
            )
    print(f'>> stopped : {status["stop_condition"]}, duration {(status["end@"]-status["start@"]):2.03f}s, Catalyst Status {status["status"]}')

recipe = TestRecipe()
distiller = recipe.ledger.get_essence_by_id(0) # main catalyst = distiller
dut = recipe.ledger.get_essence_by_name('TonicUnderTest')

print(dut._index_to_state)
print(dut.sparkles)


print_status(distiller.sparkle( timeout=5, till_state_in='paused'),2)

print('start timer')
dut.ttsc__start_timer()

print_status(distiller.sparkle( timeout=5, till_state_in='wait_on_timer'),2)
print_status(distiller.sparkle( timeout=5, till_sparkle_in='ttse__on_timer'),2)
print_status(distiller.sparkle( timeout=3))

print('finishing')
print_status(distiller.finish_distiller(), 2)
