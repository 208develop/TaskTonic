from TaskTonic import ttCatalyst
from TaskTonic.ttLedger import ttLedger
from TaskTonic.ttTonic import ttTonic
from TaskTonic.ttCatalyst import ttCatalyst
import pytest, time, queue



class TonicTester(ttCatalyst):
    """A test harness for ttTonic instances."""

    def __init__(self, tonic_class, *args, **kwargs):
        """
        Initializes the tester and the tonic instance under test.

        :param tonic_class: The class of the tonic to be tested (e.g., MyTonic).
        :param args: Positional arguments for the tonic's constructor.
        :param kwargs: Keyword arguments for the tonic's constructor.
        """

        # replaces code in ttFormula, to init the catalyst for testing
        l=ttLedger()
        l.update_formula({
            'tasktonic/fixed-id[]/name': 'main_catalyst',  # main_catalyst has always id 0
            'tasktonic/log/default': 'full',
            'tasktonic/log/to': 'test',
        })

        super().__init__(name="TonicTester", fixed_id=0)

        self.logs = []
        self.tonic = self.bind(tonic_class, *args, **kwargs)

    def start_sparkling(self):
        pass  # disabled standard sparkling

    def log_callback(self, log):
        self.logs.append(log.copy())

    def get_sparkles(self):
        """Returns the discovered interface of the tonic."""
        return self.tonic.sparkles

    def get_states(self):
        """Returns the discovered states of the tonic."""
        return self.tonic._index_to_state

    def get_name(self):
        """Returns the name of the tonic under test."""
        return self.tonic.name

    def get_log(self, index=-1):
        """Returns a captured log entry by index."""
        if self.logs:
            return self.logs[index]
        return None

    def step(self, timeout=1.0):
        """
        Executes a single sparkle from the queue.

        :param timeout: Time to wait for a sparkle to appear.
        :return: True if a step was executed, False otherwise.
        """
        try:
            instance, sparkle_method, args, kwargs = self.catalyst_queue.get(timeout=timeout)
            instance._execute_sparkle(sparkle_method, *args, **kwargs)
            return True
        except queue.Empty:
            return False

    def step_till_empty(self, max_steps=100):
        """
        Executes sparkles until the queue is empty.

        :param max_steps: A safeguard against infinite loops.
        :raises TimeoutError: If queue not empty within max_steps steps
        """
        for _ in range(max_steps):
            if not self.step(timeout=0.01):
                break

        if not self.catalyst_queue.empty():
            raise TimeoutError(f"Queue not empty within {max_steps} steps.")

    def step_till_state(self, state, timeout=5.0):
        """
        Executes sparkles until the tonic reaches a specific state.

        :param state: The target state name (str).
        :param timeout: Maximum time to wait to reach the state.
        :raises TimeoutError: If the state is not reached within the timeout.
        """
        start_time = time.time()
        while self.tonic.get_current_state_name() != state:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Tonic did not reach state '{state}' within {timeout}s.")
            if not self.step(timeout=0.1):
                # Queue is empty but we haven't reached the state
                time.sleep(0.1)

# --- Example Tonic to be Tested ---

class MyTestTonic(ttTonic):
    def __init__(self, context=None):
        super().__init__(name="TestTonic", context=context)
        self.log_push = self._log_push # overwrite log push for testing

    # reroute logger to test context
    def _log_push(self, log):
        if log is None: return
        self.context.log_callback(log)


    def ttse__on_start(self):
        self.log("MyTonic has started!")
        self.to_state('waiting')

    def ttsc_waiting__process(self):
        self.log("Processing command received.")
        self.to_state('processing')

    def tts_processing__step1(self):
        self.to_state('finished')

    def ttsc_finished__reset(self):
        self.to_state('waiting')

# --- Pytest Script ---

@pytest.fixture
def tester():
    """Provides a clean TonicTester instance for each test."""
    tester = TonicTester(MyTestTonic)
    yield tester
    ttLedger._instance = None  # reset ledger


# --- Static Tests ---
def test_static_name(tester):
    """Tests if the tonic's name is set correctly."""
    assert tester.get_name() == "TestTonic"


def test_static_states_discovered(tester):
    """Tests if all states are discovered correctly."""
    assert sorted(tester.get_states()) == ['finished', 'processing', 'waiting']


def test_static_interface_discovered(tester):
    """Tests if the public interface is discovered."""
    interface = tester.get_sparkles()
    assert 'ttsc__process' in interface
    assert 'ttsc__reset' in interface
    assert 'ttse__on_start' in interface


def test_initial_log_exists(tester):
    """Tests if the initialization log was captured."""
    init_log = tester.get_log(0)  # Get the first log
    assert init_log is not None
    sys = init_log.get('sys')
    assert sys is not None
    assert sys.get('created') == True
    assert sys.get('name') == 'TestTonic'
    assert sys.get('type') == 'MyTestTonic'
    assert sys.get('states') == ['finished', 'processing', 'waiting']
    assert 'tts__step1' in sys.get('sparkles')
    assert 'ttsc__process' in sys.get('sparkles')
    assert 'ttsc__reset' in sys.get('sparkles')
    assert 'ttse__on_finished' in sys.get('sparkles')
    assert 'ttse__on_start' in sys.get('sparkles')


# --- Dynamic Tests ---
def test_dynamic_initialization_flow(tester):
    """Tests the execution of sparkles queued during __init__."""
    # The queue should contain on_start
    assert tester.catalyst_queue.qsize() == 5

    tester.step_till_empty()

    assert tester.catalyst_queue.empty()
    assert tester.tonic.get_current_state_name() == 'waiting'

    # Check the last log entry, which should be the on_enter for 'waiting'
    last_log = tester.get_log(-1)
    assert last_log.get('sparkle') == 'ttse__on_enter'
    assert last_log.get('state') == tester.tonic.state


def test_dynamic_command_and_state_change(tester):
    """Tests queueing a command and executing it to change state."""
    tester.step_till_empty()  # Run init sparkles
    assert tester.tonic.get_current_state_name() == 'waiting'

    # Queue a new command
    tester.tonic.ttsc__process()
    assert tester.catalyst_queue.qsize() == 1

    tester.step()  # Execute the process command

    assert tester.catalyst_queue.empty()
    assert tester.tonic.get_current_state_name() == 'processing'


def test_dynamic_step_till_state(tester):
    """Tests the step_till_state helper method."""
    tester.step_till_empty()  # Go to 'waiting' state

    # Queue multiple commands
    tester.tonic.ttsc__process()  # waiting -> processing
    # The next command (reset) is not defined for 'processing', so it will do nothing
    tester.tonic.ttsc__reset()

    tester.step_till_state('processing', timeout=1.0)

    # We should have reached the state
    assert tester.tonic.get_current_state_name() == 'processing'
    # But the queue should still have one item left
    assert not tester.catalyst_queue.empty()


def test_dynamic_timeout_error(tester):
    """Tests if step_till_state raises a TimeoutError correctly."""
    tester.step_till_empty()

    # No commands are queued, so we can never reach the 'finished' state
    with pytest.raises(TimeoutError):
        tester.step_till_state('finished', timeout=0.3)


