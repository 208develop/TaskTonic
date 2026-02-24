# test_core.py
import pytest
from TaskTonic import ttLiquid, ttFormula


# --- Mock Classes ---
class SimpleLiquid(ttLiquid):
    def __init__(self, create_child=False, **kwargs):
        super().__init__(**kwargs)
        self.se = SimpleLiquid() if create_child else None

    def get_child_essence(self):
            return self.se

class LiquidWithService(ttLiquid):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.srv = MockService()


class MockService(ttLiquid):
    _tt_is_service = "MySingletonService"
    _tt_base_essence = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_count = 1
        self.access_count = 0

    def _tt_init_service_base(self, base, **kwargs):
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
    main_catalyst = f.ledger.get_tonic_by_name('tt_main_catalyst')
    assert main_catalyst.id == 0
    assert main_catalyst.name == 'tt_main_catalyst'
    assert main_catalyst.base is None

    t1 = SimpleLiquid(name="Ess1")
    assert t1.id == 1
    assert t1.name == "Ess1"


    t2 = SimpleLiquid(name="Ess2")
    assert t2.id == 2
    assert t2.name == "Ess2"

    assert t1.id != t2.id

    # Check ledger lookup
    retrieved = f.ledger.get_tonic_by_name("Ess1")
    assert retrieved == t1


def test_parent_child_binding():
    """Test parent-child relaties en automatische cleanup."""
    f = CoreFormula()
    parent = SimpleLiquid(create_child=True)

    # get the bound child
    child = parent.get_child_essence()

    assert child.base == parent
    assert child in parent.infusions

    # Finish parent -> must also finish child
    parent.finish()

    # both must be 'finished' (id -1 after unregister)
    assert parent.id == -1
    assert child.id == -1

#
# def test_service_singleton():
#     """Test of een Service echt maar 1x wordt aangemaakt."""
#     f = CoreFormula()
#
#     assert f.ledger.get_service_essence('MySingletonService') is None
#
#     # create service from context -1
#     srv = MockService()
#
#     assert f.ledger.get_service_essence('MySingletonService') == srv
#     assert srv.name == 'MySingletonService'
#     assert srv.id == 1
#     assert srv.init_count == 1
#     assert srv.access_count == 1
#
#     # first client, using the service
#     client_a = LiquidWithService(name='client_a')
#     first_id = client_a.srv.id
#     assert srv in client_a.infusions
#     assert srv.init_count == 1
#     assert srv.access_count == 2
#     assert len(srv.service_bases) == 2 # serv is also included
#
#     # second client, using the service
#     client_b = LiquidWithService(name='client_b')
#     assert srv in client_b.infusions
#     assert srv.init_count == 1
#     assert srv.access_count == 3
#     assert len(srv.service_bases) == 3
#
#     # check services
#     assert client_a.srv is client_b.srv
#     assert client_b.srv.id == first_id
#     assert set(srv.service_bases) == {None, client_a, client_b}
#
#     # finish essence that uses the service
#     client_a.finish()
#     assert set(srv.service_bases) == {None, client_b}
#     assert client_a.id == -1
#     assert srv.id == 1 # stil active
#
#     # finish essence that uses the service
#     client_b.finish()
#     assert set(srv.service_bases) == {None, }
#     assert client_b.id == -1
#     assert srv.id == 1  # stil active
#
#     # finish service
#     srv.finish()
#     assert srv.id == -1  # last base finished -> service finished
#




