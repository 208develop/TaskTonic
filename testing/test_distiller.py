# test_distiller.py
import pytest
import time
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot
from TaskTonic.ttTonicStore import ttDistiller


# --- Definitie van de Device Under Test (DUT) ---
class DUT(ttTonic):
    def ttse__on_start(self):
        self.to_state('init')

    def ttse_init__on_enter(self):
        self.to_state('paused')

    def ttsc_paused__start_timer(self):
        # Start een timer van 2 seconden
        self.bind(ttTimerSingleShot, 2)
        self.to_state('wait_on_timer')

    def ttse_wait_on_timer__on_timer(self, info):
        # Wordt aangeroepen als de timer afloopt (default handler)
        self.to_state('finished_cycle')

    def ttse_finished_cycle__on_enter(self):
        pass  # empty state


# --- Definitie van de Test Formula ---
class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',  # Geen output tijdens tests
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        # We gebruiken de Distiller in plaats van de standaard Catalyst
        ttDistiller()

    def creating_starting_tonics(self):
        DUT(name="MyDevice")


# --- De Test ---
def test_dut_flow_with_timer():
    # 1. Initialiseer de applicatie
    recipe = TestRecipe()

    # 2. Haal de referenties op via de Ledger
    ledger = recipe.ledger
    distiller = ledger.get_essence_by_id(0)  # Main catalyst is altijd ID 0
    dut = ledger.get_essence_by_name("MyDevice")  # Zoek op naam is veiliger dan ID

    assert isinstance(distiller, ttDistiller)
    assert dut is not None
    assert set(dut._index_to_state) == {'init', 'paused', 'wait_on_timer', 'finished_cycle'}

    # 3. STAP 1: Start de distiller en run tot de DUT in 'paused' komt.
    # Dit test de initiële flow: on_start -> init -> paused
    status = distiller.sparkle(timeout=1, till_state_in=['paused'])

    # Verifieer dat we gestopt zijn vanwege de state trigger, niet door timeout
    stop_conditions = status.get('stop_condition', [])
    assert 'state_trigger: [paused]' in stop_conditions
    assert dut.get_current_state_name() == 'paused'

    # 4. STAP 2: Vuur handmatig een commando af (start timer)
    dut.ttsc__start_timer()

    # Run de distiller tot de status verandert naar 'wait_on_timer'
    status = distiller.sparkle(timeout=1, till_state_in=['wait_on_timer'])
    assert dut.get_current_state_name() == 'wait_on_timer'

    # 5. STAP 3: Wacht op de timer.
    # De Distiller spoelt de tijd automatisch vooruit als er geen sparkles zijn,
    # maar er wel actieve timers zijn.
    status = distiller.sparkle(timeout=5, till_sparkle_in=['ttse__on_timer'])

    # Check of de timer event daadwerkelijk is afgegaan
    assert 'sparkle_trigger: [ttse__on_timer]' in status.get('stop_condition', [])

    # Check of de logica na de timer de state heeft aangepast
    assert dut.get_current_state_name() == 'finished_cycle'

    # finish DUT
    dut.finish()
    status = distiller.sparkle(timeout=.5)
    assert dut.id == -1

    # 6. Opruimen
    distiller.finish_distiller()
    assert distiller.sparkling == False
