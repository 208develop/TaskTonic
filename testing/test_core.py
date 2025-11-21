# test_core.py
import pytest
from TaskTonic import ttEssence, ttFormula


# --- Mock Classes ---
class SimpleEssence(ttEssence):
    pass

class EssenceWithService(ttEssence):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.srv = self.bind(MockService)

class MockService(ttEssence):
    _tt_is_service = "MySingletonService"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_count = 1
        self.access_count = 0

    def _init_service(self, context=None, **kwargs):
        self.access_count += 1


class CoreFormula(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/testing/dont_start_catalysts', True),
            ('tasktonic/log/to', 'off'),
            ('tasktonic/log/default', 'stealth'),
        )

    def creating_starting_tonics(self):
        pass


# --- Tests ---

def test_ledger_registration():
    """Test of essences correct een ID krijgen en in de ledger komen."""
    f = CoreFormula()

    # check creating of main catalyst
    main_catalyst = f.ledger.get_essence_by_id(0)
    assert main_catalyst.id == 0
    assert main_catalyst.name == 'main_catalyst'
    assert main_catalyst.context is None

    t1 = SimpleEssence(name="Ess1", context=-1)
    assert t1.id == 1
    assert t1.name == "Ess1"


    t2 = SimpleEssence(name="Ess2", context=-1)
    assert t2.id == 2
    assert t2.name == "Ess2"

    assert t1.id != t2.id

    # Check ledger lookup
    retrieved = f.ledger.get_essence_by_name("Ess1")
    assert retrieved == t1


def test_parent_child_binding():
    """Test parent-child relaties en automatische cleanup."""
    f = CoreFormula()
    parent = SimpleEssence(context=-1)

    # Bind a child
    child = parent.bind(SimpleEssence)
    assert child.context == parent
    assert child.id in parent.bindings

    # Finish parent -> must also finish child
    parent.finish()

    # both must be 'finished' (id -1 after unregister)
    assert parent.id == -1
    assert child.id == -1


def test_service_singleton():
    """Test of een Service echt maar 1x wordt aangemaakt."""
    f = CoreFormula()

    assert f.ledger.get_service_essence('MySingletonService') is None

    # create service from context -1
    srv = MockService(context=-1)

    assert f.ledger.get_service_essence('MySingletonService') == srv
    assert srv.my_record.get('service', '--not found--') == 'MySingletonService'
    assert srv.id == 1
    assert srv.init_count == 1
    assert srv.access_count == 1

    # first client, using the service
    client_a = EssenceWithService(context=-1)
    first_id = client_a.srv.id
    assert srv.init_count == 1
    assert srv.access_count == 2
    assert len(srv.service_context) == 1

    # second client, using the service
    client_b = EssenceWithService(context=-1)
    assert srv.init_count == 1
    assert srv.access_count == 3
    assert len(srv.service_context) == 2

    # check services
    assert client_a.srv is client_b.srv
    assert client_b.srv.id == first_id
    assert set(srv.service_context) == {client_a, client_b}

    # finish essence that uses the service
    client_a.finish()
    assert set(srv.service_context) == {client_b}
    assert client_a.id == -1
    assert client_a.srv.id == first_id

    # finish essence that uses the service
    client_b.finish()
    assert set(srv.service_context) == set()
    assert client_b.id == -1
    assert client_b.srv.id == -1 # last context finished -> service finished





