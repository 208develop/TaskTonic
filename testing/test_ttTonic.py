import pytest
import threading
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller


# --- Definition of a child Tonic to test infusions ---
class MockInfusion(ttTonic):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.is_finished = False

    def ttse__on_start(self):
        self.is_running = True
        self.is_finished = False

    def ttse__on_finished(self):
        self.is_running = False
        self.is_finished = True


# --- Definition of the Device Under Test (DUT) ---
class StateMachineTestTonic(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.action_log = []
        self.received_list_id = None
        self.child = None

    # --- TEST INTERFACE --------------------------------------------------------
    def ttsc__reenter_current_state(self):
        self.reenter_current_state()
    def ttsc__start_up_infusion(self):
        self.child = MockInfusion()
    # ---------------------------------------------------------------------------

    def ttse__on_start(self):
        self.action_log.append("on_start")
        self.to_state('idle')

    def ttse__on_finished(self):
        self.action_log.append("on_finished")

    def ttsc__test_state(self, state):
        self.to_state(state)

    # --- State Machine Handlers ---
    def ttse_idle__on_enter(self):
        self.action_log.append("enter_idle")

    def ttse_idle__on_exit(self):
        self.action_log.append("exit_idle")

    def ttse_active__on_enter(self):
        self.action_log.append("enter_active")

    def ttse_active__on_exit(self):
        self.action_log.append("exit_active")

    # --- Sparkles with Parameters ---
    def ttsc__receive_data(self, data_list, data_dict):
        self.action_log.append("receive_data")
        self.received_list_id = id(data_list)

    # --- State-bound Sparkles ---
    def ttsc_active__process_task(self):
        self.action_log.append("process_active")

    def ttsc__process_task(self):
        self.action_log.append("process_default")

    def ttsc__dut_finish(self):
        self.ttsc__finish()


# --- Definition of the Test Formula ---
class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        StateMachineTestTonic(name="TestDevice")


# --- Pytest Fixtures ---
@pytest.fixture
def setup_distiller():
    """Fixture to set up and tear down the Distiller and DUT for each test."""
    recipe = TestRecipe()
    ledger = recipe.ledger
    distiller = ledger.get_tonic_by_name('tt_main_catalyst')
    dut = ledger.get_tonic_by_name("TestDevice")

    yield distiller, dut

    # Teardown
    distiller.finish_distiller()


# --- Test Cases ---
def test_thread_safety_and_parameter_copying(setup_distiller):
    distiller, dut = setup_distiller

    # Wait for the device to reach the idle state
    distiller.sparkle(timeout=1.0, till_state_in=['idle'])
    assert "enter_idle" in dut.action_log

    original_list = [9, 8, 7]
    original_dict = {"status": "testing"}
    original_list_id = id(original_list)

    # Simulate an external event coming from a different thread (e.g. UI or Network)
    def background_worker():
        dut.ttsc__receive_data(original_list, original_dict)

    thread = threading.Thread(target=background_worker)
    thread.start()
    thread.join()

    # Wait for the catalyst to process the specific sparkle
    distiller.sparkle(timeout=1.0, till_sparkle_in=['ttsc__receive_data'])

    assert "receive_data" in dut.action_log

    if dut.received_list_id == original_list_id:
        pytest.fail("Mutable parameters were not copied across threads!")


def test_state_machine_transitions(setup_distiller):
    distiller, dut = setup_distiller

    # INIT
    status = distiller.sparkle(timeout=1.0, till_state_in=['idle'])
    assert 'state_trigger: [idle]' in status.get('stop_condition', [])
    dut.action_log.clear()


    # STAP 1: Normal transition to 'active'
    dut.ttsc__to_state('active')
    status = distiller.sparkle(timeout=1.0, till_state_in=['active'])

    assert 'state_trigger: [active]' in status.get('stop_condition', [])
    assert "exit_idle" in dut.action_log
    assert "enter_active" in dut.action_log

    dut.action_log.clear()

    # STAP 2: Idempotent transition (should do nothing)
    dut.ttsc__to_state('active')
    distiller.sparkle(timeout=0.2)  # Process queue, no trigger expected

    assert "exit_active" not in dut.action_log
    assert "enter_active" not in dut.action_log

    # STAP 3: Forced re-entry of the current state
    dut.ttsc__reenter_current_state()
    # Or explicitly: dut.to_state('active', force_reenter=True)
    distiller.sparkle(timeout=0.2)

    assert "exit_active" in dut.action_log
    assert "enter_active" in dut.action_log


def test_state_bound_sparkles(setup_distiller):
    distiller, dut = setup_distiller

    distiller.sparkle(timeout=1.0, till_state_in=['idle'])

    # Calling process_task in 'idle' should hit the default handler
    dut.ttsc__process_task()
    distiller.sparkle(timeout=0.5)

    assert "process_default" in dut.action_log
    assert "process_active" not in dut.action_log

    dut.action_log.clear()

    # Move to 'active' state
    dut.ttsc__to_state('active')
    distiller.sparkle(timeout=1.0, till_state_in=['active'])

    # Calling process_task in 'active' should hit the state-bound handler
    dut.ttsc__process_task()
    distiller.sparkle(timeout=0.5, till_sparkle_in=['ttsc_active__process_task'])

    assert "process_active" in dut.action_log
    assert "process_default" not in dut.action_log


def test_cleanup_infusions_on_finish(setup_distiller):
    distiller, dut = setup_distiller

    dut.ttsc__start_up_infusion()
    distiller.sparkle(timeout=0.5)

    child_tonic = distiller.ledger.get_tonic_by_name('02.MockInfusion')

    assert child_tonic is not None

    if not child_tonic.is_running:
        pytest.fail("Child infusion did not start.")

    # Finish the parent DUT
    dut.ttsc__dut_finish()

    # Wait until the catalyst runs out of things to do or the DUT finishes
    distiller.sparkle(timeout=1.0)

    if not child_tonic.is_finished:
        pytest.fail("Child infusion was not finished when the parent finished.")

