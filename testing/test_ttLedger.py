import pytest
import sys


# --- Mocks for dependencies in ttEssence ---
# We must mock the classes that ttEssence imports and uses.

class ttDummyLogServer:
    """Mock for the dummy logger."""

    def put_log(self, log):
        pass


class ttScreenLogServer(ttDummyLogServer):
    """Mock for the screen logger."""
    pass


# Create a mock module and add it to sys.modules
mock_loggers_module = type(sys)('TaskTonic.ttLoggers.ttScreenLogger')
mock_loggers_module.ttScreenLogService = ttScreenLogServer
sys.modules['TaskTonic.ttLoggers.ttScreenLogger'] = mock_loggers_module

# --- End of Mocks ---

# Import the classes to be tested
from TaskTonic.ttLedger import ttLedger, RWLock
from TaskTonic.ttEssence import ttEssence, __ttEssenceMeta, ttLog


def reset_ledger_singleton():
    """
    Helper function to fully reset the ttLedger singleton
    between test classes.
    """
    ttLedger._lock = RWLock()
    ttLedger._instance = None
    ttLedger._singleton_init_done = False


class TestEssenceLedger:
    @pytest.fixture()
    def ledger(self):
        """
        Fixture to provide a single, class-scoped ledger
        and reset it after the class.
        """
        reset_ledger_singleton()
        l = ttLedger()
        l.update_formula({})  # init formula empty
        yield l
        reset_ledger_singleton()

    def test_ledger_init(self, ledger):
        """Tests that the ledger initializes and formula works."""
        assert ledger.formula.get('') == {}
        ledger.update_formula((
            ('tester/my_list[]/name', 'Essence0'),
            ('tester/my_list[]/name', 'Essence1'),
            ('tester/param', 1),
        ))

        assert ledger.formula.get('tester/') == {
            'my_list': [
                {'name': 'Essence0', }, {'name': 'Essence1', },
            ],
            'param': 1,
        }

    def test_ledger_registration_and_lookup(self, ledger):
        """
        Tests basic registration and lookup by ID and Name.
        """
        e1 = ttEssence(name='FirstEssence')

        # Check ID assignment
        assert e1.id == 0
        assert e1.name == 'FirstEssence'

        # Check direct lookup
        assert ledger.get_essence_by_id(0) is e1
        assert ledger.get_essence_by_name('FirstEssence') is e1

        # Check record
        assert ledger.records[0] == {
            'context_id': -1,
            'id': 0,
            'name': 'FirstEssence',
            'type': 'ttEssence',
        }

        # Test non-existent lookups
        assert ledger.get_essence_by_id(99) is None
        assert ledger.get_essence_by_name('WrongName') is None
        assert ledger.get_id_by_name('WrongName') == -1

    def test_ledger_bind_and_finish(self, ledger):
        """
        Tests the bind/unbind and register/unregister logic.
        """
        parent_essence = ttEssence(name='Parent')
        assert len(parent_essence.bindings) == 0
        assert parent_essence.id == 0

        # Bind a new child
        child_essence = parent_essence.bind(ttEssence, name='Child')  # ID 1
        assert child_essence.context is parent_essence
        assert len(parent_essence.bindings) == 1
        assert parent_essence.bindings[0] == child_essence.id
        assert child_essence.id == 1

        # Check ledger records
        assert ledger.essences[0] is parent_essence
        assert ledger.essences[1] is child_essence
        assert ledger.records[1]['context_id'] == parent_essence.id

        # Finish the child
        child_essence.finish()

        # Check that it's unbound from parent
        assert len(parent_essence.bindings) == 0

        # Check that the slot in the ledger is now empty
        assert ledger.essences[1] is None
        assert ledger.records[1] is None

        # Check that a new essence re-uses the empty slot
        grand_child = parent_essence.bind(ttEssence, name='GrandChild')
        assert grand_child.id == 1  # Re-used ID 1


class TestEssence:
    @pytest.fixture(scope='class')
    def essence(self):
        reset_ledger_singleton()
        l = ttLedger()
        l.update_formula({})  # init formula empty
        e = ttEssence()
        yield e
        reset_ledger_singleton()

    def test_essence_init(self, essence):
        assert len(essence.ledger.records) == 1
        assert essence.id == 0
        assert essence.name == '00.ttEssence'  # Default name format


# --- New Test Class for Service/Singleton Functionality ---

class TestEssenceServices:
    # --- Dummy Service Classes ---
    class MyService(ttEssence):
        _tt_is_service = "MyService"  # Identify by class var

    class MyOtherService(ttEssence):
        _tt_is_service = "OtherService"

    class ServiceWithInit(ttEssence):
        _tt_is_service = "ServiceWithInit"

        def __init__(self, srv_param, **kwargs):
            self.init_val = srv_param
            self.init_run_count = 1
            super().__init__(**kwargs)

    class ServiceWithServiceInit(ttEssence):
        _tt_is_service = "ServiceWithServiceInit"

        def __init__(self, **kwargs):
            self.access_log = []
            super().__init__(**kwargs)

        def _init_service(self, ctxt_param, **kwargs):
            self.access_log.append(ctxt_param)

    # --- Fixture ---
    @pytest.fixture(scope='function')
    def ledger(self):
        """
        Function-scoped fixture: We need a fresh ledger
        for *every single test* to ensure singletons
        are cleanly created and tested.
        """
        reset_ledger_singleton()
        l = ttLedger()
        l.update_formula({})  # init formula empty
        yield ttLedger()
        reset_ledger_singleton()

    # --- Tests ---

    def test_service_is_singleton(self, ledger):
        """Tests that multiple calls return the same instance."""
        s1 = self.MyService()
        s2 = self.MyService()
        assert s1 is s2
        assert len(ledger.records) == 1

    def test_init_runs_only_once(self, ledger):
        """Tests that __init__ is skipped on the second call."""
        s1 = self.ServiceWithInit(srv_param=123)
        assert s1.init_val == 123

        s2 = self.ServiceWithInit(srv_param=456)
        assert s2 is s1
        # The value should NOT be updated, proving __init__ was skipped
        assert s1.init_val == 123

    def test_init_service_runs_every_time(self, ledger):
        """Tests that _init_service is called on every access."""
        s1 = self.ServiceWithServiceInit(ctxt_param='A')
        assert s1.access_log == ['A']

        s2 = self.ServiceWithServiceInit(ctxt_param='B')
        assert s2 is s1
        # The list should be appended to, proving _init_service ran again
        assert s1.access_log == ['A', 'B']

    def test_service_name_is_injected_from_class_var(self, ledger):
        """
        Tests that the metaclass correctly injects the service name
        from the class variable `_tt_is_service` into the `name` param.
        """
        s1 = self.MyService()
        assert s1.name == "MyService"
        assert ledger.records[0]['name'] == "MyService"

    def test_service_name_is_used_from_kwarg(self, ledger):
        """
        Tests that the `service=` kwarg overrides the class var
        and correctly injects the name.
        """
        # Call with 'service' kwarg
        s1 = self.MyService(service="MyService_Test")
        assert s1.name == "MyService_Test"

        # Call again to test singleton lookup
        s2 = self.MyService(service="MyService_Test")
        assert s1 is s2
        assert len(ledger.records) == 1

    def test_different_services_are_different_singletons(self, ledger):
        """Tests that two different service classes are not the same."""
        s1 = self.MyService()
        s2 = self.MyOtherService()
        assert s1 is not s2
        assert len(ledger.records) == 2
        assert ledger.records[0]['name'] == "MyService"
        assert ledger.records[1]['name'] == "OtherService"

    def test_ledger_record_is_updated_with_service_name(self, ledger):
        """
        Tests that the metaclass correctly calls update_record
        to flag the essence as a service in the ledger.
        """
        s1 = self.MyService()
        assert ledger.records[s1.id]['service'] == "MyService"

    def test_get_service_essence_finds_service(self, ledger):
        """
        Tests that the new ledger method get_service_essence
        can retrieve the service.
        """
        s1 = self.MyService()

        found = ledger.get_service_essence("MyService")
        assert s1 is found

        not_found = ledger.get_service_essence("NonExistentService")
        assert not_found is None


# import pytest
#
# from TaskTonic.ttLedger import ttLedger, RWLock
# from TaskTonic.ttEssence import ttEssence
#
# def reset_ledger_singleton():
#     ttLedger._lock = RWLock()
#     ttLedger._instance = None
#     ttLedger._singleton_init_done = False
#
# class TestEssenceLedger:
#     @pytest.fixture(scope='class')
#     def ledger(self):
#         reset_ledger_singleton()
#         l = ttLedger()
#         yield l
#         reset_ledger_singleton()
#
#     def test_ledger_init(self, ledger):
#         assert ledger.formula is None
#         ledger.update_formula((
#             ('tasktonic/fixed-id[]/name', 'Essence0'),
#             ('tasktonic/fixed-id[]/name', 'Essence1'),
#         ))
#
#         assert ledger.formula.get('tasktonic/') == {
#             'fixed-id': [
#                 {'name': 'Essence0', }, {'name': 'Essence1', },
#             ],
#         }
#
#     def test_ledger_register_essence_fixed_id(self, ledger):
#         assert ledger.essences[0].__class__.__name__ == '__FIXED_ID'
#         e = ttEssence(name='Essence0', fixed_id=0)
#         assert ledger.essences[0] == e
#
#         assert ledger.records[0] == {
#             'context_id': -1,
#             'fixed_id': True,
#             'id': 0,
#             'name': 'Essence0',
#             'type': 'ttEssence',
#         }
#
#     def test_ledger_register_essence_fixed_id_str(self, ledger):
#         e = ttEssence(name='Essence1', fixed_id='Essence1')
#         assert ledger.records[1] == {
#             'context_id': -1,
#             'fixed_id': True,
#             'id': 1,
#             'name': 'Essence1',
#             'type': 'ttEssence',
#         }
#
#     def test_ledger_register_next_essence(self, ledger):
#         e = ledger.get_essence_by_name('Essence1')
#         assert len(e.bindings) == 0
#
#         e1 = e.bind(ttEssence)
#         assert e1.context == e
#         assert len(e.bindings) == 1
#
#         assert ledger.essences[2] == e1
#         assert ledger.records[2] == {
#             'context_id': 1,
#             'id': 2,
#             'name': '02.ttEssence',
#             'type': 'ttEssence',
#         }
#         assert ledger.essences[1].bindings[0] == e1.id
#
#         e1.finish()
#         assert len(e.bindings) == 0
#         assert ledger.essences[2] is None
#         assert ledger.records[2] is None
#
#
# class TestEssence:
#     @pytest.fixture(scope='class')
#     def essence(self):
#         reset_ledger_singleton()
#         e = ttEssence()
#         yield e
#         reset_ledger_singleton()
#
#     def test_essence_init(self, essence):
#         assert len(essence.ledger.records) == 1
