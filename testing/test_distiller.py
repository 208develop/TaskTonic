import pytest
import time
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot, ttLedger
from TaskTonic.ttTonicStore.ttDistiller import ttDistiller


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def reset_ledger():
    """Zorgt voor een schone lei voor elke test en wacht op background threads."""
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

    yield

    if ttLedger._instance:
        for t in ttLedger._instance.tonics:
            if t and hasattr(t, 'sparkling') and t.id > 0:
                start_t = time.time()
                while t.sparkling and time.time() - start_t < 1.0:
                    time.sleep(0.01)

        ttLedger._instance.records = []
        ttLedger._instance.tonics = []
        ttLedger._instance.formula = None

    ttLedger._instance = None
    ttLedger._singleton_init_done = False


# ==============================================================================
# TONICS VOOR TESTS
# ==============================================================================

class DUT(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.tm = None
        self.cycle_count = 0  # Toegevoegd voor de stop_on_probe test

    def ttse__on_start(self):
        self.to_state('init')

    def ttse_init__on_enter(self):
        self.to_state('paused')

    def ttsc_paused__start_timer(self, delay=2.0):
        # Start een timer, variabel gemaakt voor de OR-logica test
        self.tm = ttTimerSingleShot(seconds=delay)
        self.to_state('wait_on_timer')

    def ttse_wait_on_timer__on_timer(self, info):
        # Wordt aangeroepen als de timer afloopt
        self.cycle_count += 1
        self.to_state('finished_cycle')

    def ttse_finished_cycle__on_enter(self):
        pass  # empty state

    def ttsc__dut_finish(self):
        self.ttsc__finish()


class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',  # Geen output tijdens tests
            'tasktonic/log/default': 'stealth',
        }

    def creating_main_catalyst(self):
        # We gebruiken de Distiller in plaats van de standaard Catalyst
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        DUT(name="MyDevice")


# ==============================================================================
# TEST 1: BACKWARDS COMPATIBILITY (Legacy Syntax)
# ==============================================================================

def test_dut_flow_with_timer():
    recipe = TestRecipe()
    ledger = recipe.ledger
    distiller = recipe.distiller
    dut = ledger.get_tonic_by_name("MyDevice")

    assert isinstance(distiller, ttDistiller)
    assert dut is not None
    assert set(dut._index_to_state) == {'init', 'paused', 'wait_on_timer', 'finished_cycle'}

    # STAP 1: Oude platte syntax
    status = distiller.sparkle(timeout=1.0, till_state_in=['paused'])
    assert 'state_trigger: [paused]' in status.get('stop_condition', [])
    assert dut.get_current_state_name() == 'paused'

    # STAP 2: Vuur handmatig een commando af
    dut.ttsc__start_timer(delay=2.0)
    status = distiller.sparkle(timeout=1.0, till_state_in=['wait_on_timer'])
    assert dut.get_current_state_name() == 'wait_on_timer'

    # STAP 3: Wacht op de timer via de oude global sparkle_in check
    status = distiller.sparkle(timeout=5.0, till_sparkle_in=['ttse__on_timer'])
    assert 'sparkle_trigger: [ttse__on_timer]' in status.get('stop_condition', [])
    assert dut.get_current_state_name() == 'finished_cycle'

    # Finish
    dut.ttsc__dut_finish()
    status = distiller.sparkle(timeout=0.5)
    assert 'catalyst finished' in status['stop_condition']

    distiller.finish_distiller()


# ==============================================================================
# TEST 2: ADVANCED CONTRACTS (Multi-Tonic, AND/OR logic, Probes)
# ==============================================================================

class MultiDeviceRecipe(TestRecipe):
    def creating_starting_tonics(self):
        # We spawnen er nu TWEE om AND/OR logica te testen
        DUT(name="Device_Fast")
        DUT(name="Device_Slow")


def test_advanced_distiller_contracts():
    recipe = MultiDeviceRecipe()
    ledger = recipe.ledger
    distiller = recipe.distiller
    dev_fast = ledger.get_tonic_by_name("Device_Fast")
    dev_slow = ledger.get_tonic_by_name("Device_Slow")

    # --- DEEL 1: De 'AND' Conditie (stop_match_count: 'all') ---
    # We wachten expliciet tot BEIDE devices gepauzeerd zijn
    trace1 = distiller.sparkle(contract={
        'timeout': 2.0,
        'stop_match_count': 'all',
        'tonics': {
            'Device_Fast': {'till_state_in': ['paused']},
            'Device_Slow': {'till_state_in': ['paused']}
        }
    })

    assert 'contract_met: 2/2 tonics matched' in trace1['stop_condition']
    assert dev_fast.get_current_state_name() == 'paused'
    assert dev_slow.get_current_state_name() == 'paused'

    # --- DEEL 2: De 'OR' Conditie met Probes (stop_match_count: 1) ---
    # We geven ze ongelijke timers
    dev_fast.ttsc__start_timer(delay=0.5)
    dev_slow.ttsc__start_timer(delay=2.5)

    # We vertellen de Distiller te stoppen zodra de ALLEREERSTE Tonic klaar is.
    # We checken dit puur op basis van de interne variabele via 'stop_on_probe'.
    trace2 = distiller.sparkle(contract={
        'timeout': 5.0,
        'stop_match_count': 1,  # Stop als er 1 matcht!
        'tonics': {
            'Device_Fast': {
                'probes': ['cycle_count'],
                'stop_on_probe': {'cycle_count': 1}
            },
            'Device_Slow': {
                'probes': ['cycle_count'],
                'stop_on_probe': {'cycle_count': 1}
            }
        }
    })

    assert 'contract_met: 1/1 tonics matched' in trace2['stop_condition']

    # Omdat Device_Fast een timer van 0.5 had, moet deze klaar zijn
    assert dev_fast.cycle_count == 1
    assert dev_fast.get_current_state_name() == 'finished_cycle'

    # Device_Slow is trager en moet nog steeds wachten
    assert dev_slow.cycle_count == 0
    assert dev_slow.get_current_state_name() == 'wait_on_timer'

    # --- DEEL 3: Wacht op de trage ---
    distiller.sparkle(contract={
        'timeout': 5.0,
        'stop_match_count': 1,
        'tonics': {
            'Device_Slow': {'till_state_in': ['finished_cycle']}
        }
    })

    assert dev_slow.cycle_count == 1

    # Cleanup
    dev_fast.ttsc__dut_finish()
    dev_slow.ttsc__dut_finish()
    distiller.finish_distiller()