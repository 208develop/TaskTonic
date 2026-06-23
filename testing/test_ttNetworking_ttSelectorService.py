import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import SelectorService


class DummySocketTonic(ttTonic):
    """
    A simple Tonic to test if the SelectorService can register sockets
    without crashing or causing infinite loops.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dummy_sock = None
        self.selector = None

    def _tt_post_init_action(self):
        from TaskTonic import ttLedger
        ledger = ttLedger()

        self.selector = ledger.get_service_essence('selector_handling_service')
        if not self.selector:
            self.selector = SelectorService()

        super()._tt_post_init_action()

    def ttse__on_start(self):
        self.dummy_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dummy_sock.setblocking(False)

        self.selector.register(
            sock=self.dummy_sock,
            context=self,
            rd_sparkle=self.ttse__on_dummy_data,
            wr_sparkle=self.ttse__on_dummy_data
        )


    def ttse__on_dummy_data(self, data=None):
        pass

    def ttse__on_finished(self):
        if self.dummy_sock and self.selector:
            self.selector.unregister(sock=self.dummy_sock)
            self.dummy_sock.close()


class EngineTestFormula(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'off'),
            ('tasktonic/log/default', 'stealth')
        )

    def creating_main_catalyst(self):
        ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.dummy = DummySocketTonic(name="DummyTonic")


def test_selector_service_registration():
    """
    Validates that the base OS-level engine boots up and accepts socket registrations.
    """
    app = EngineTestFormula()
    dist = app.ledger.get_tonic_by_name('tt_main_catalyst')

    dist.start_sparkling()

    contract = {
        'timeout': 2.0,
        'stop_match_count': 1,
        'tonics': {
            'DummyTonic': {
                'till_sparkle_in': ['ttse__on_start']
            }
        }
    }

    try:
        trace = dist.sparkle(contract=contract)
        assert 'contract_met' in trace['stop_condition']
    finally:
        dist.finish_distiller()
