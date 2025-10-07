import pytest

from TaskTonic.ttLedger import ttLedger, RWLock
from TaskTonic.ttEssence import ttEssence

def reset_ledger_singleton():
    ttLedger._lock = RWLock()
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

class TestEssenceLedger:
    @pytest.fixture(scope='class')
    def ledger(self):
        reset_ledger_singleton()
        l = ttLedger()
        yield l
        reset_ledger_singleton()

    def test_ledger_init(self, ledger):
        assert ledger.formula is None
        ledger.update_formula((
            ('tasktonic/fixed-id[]/name', 'Essence0'),
            ('tasktonic/fixed-id[]/name', 'Essence1'),
        ))

        assert ledger.formula.get('tasktonic/') == {
            'fixed-id': [
                {'name': 'Essence0', }, {'name': 'Essence1', },
            ],
        }

    def test_ledger_register_essence_fixed_id(self, ledger):
        assert ledger.essences[0].__class__.__name__ == '__FIXED_ID'
        e = ttEssence(-1, name='Essence0', fixed_id=0)
        assert ledger.essences[0] == e

        assert ledger.records[0] == {
            'context_id': -1,
            'fixed_id': True,
            'id': 0,
            'name': 'Essence0',
            'type': 'ttEssence',
        }

    def test_ledger_register_essence_fixed_id_str(self, ledger):
        e = ttEssence(-1, name='Essence1', fixed_id='Essence1')
        assert ledger.records[1] == {
            'context_id': -1,
            'fixed_id': True,
            'id': 1,
            'name': 'Essence1',
            'type': 'ttEssence',
        }

    def test_ledger_register_next_essence(self, ledger):
        e = ledger.get_essence_by_name('Essence1')
        assert len(e.bindings) == 0

        e1 = e.bind(ttEssence)
        assert e1.context == e
        assert len(e.bindings) == 1

        assert ledger.essences[2] == e1
        assert ledger.records[2] == {
            'context_id': 1,
            'id': 2,
            'name': '02.ttEssence',
            'type': 'ttEssence',
        }
        assert ledger.essences[1].bindings[0] == e1.id

        e1.finished()
        assert len(e.bindings) == 0
        assert ledger.essences[2] is None
        assert ledger.records[2] is None


class TestEssence:
    @pytest.fixture(scope='class')
    def essence(self):
        e = ttEssence(-1)
        yield e
        reset_ledger_singleton()

    def test_essence_init(self, essence):
        assert len(essence.ledger.records) == 1
