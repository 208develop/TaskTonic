import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import UdpDictSocketHandler


def get_free_port():
    """Finds a free port to prevent 'Address already in use' errors."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class UdpEchoServer(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = None

    def ttse__on_start(self):
        self.udp = UdpDictSocketHandler(host='127.0.0.1', port=self.port, as_server=True)

    def ttse__on_udp_data(self, data, addr):
        self.received_data = data
        data['echo'] = True
        self.udp.ttsc__send_data(data, addr)


class UdpPingClient(ttTonic):
    def __init__(self, target_port, **kwargs):
        super().__init__(**kwargs)
        self.target_port = target_port
        self.received_reply = None

    def ttse__on_start(self):
        self.udp = UdpDictSocketHandler(as_server=False)
        self.to_state('sending')

    def ttse_sending__on_enter(self):
        payload = {"action": "ping"}
        self.udp.ttsc__send_data(payload, ('127.0.0.1', self.target_port))

    def ttse__on_udp_data(self, data, addr):
        self.received_reply = data


class UdpTestFormula(ttFormula):
    def __init__(self, port):
        self.port = port
        super().__init__()

    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'off'),
        )

    def creating_main_catalyst(self):
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.server = UdpEchoServer(port=self.port, name="Server")
        self.client = UdpPingClient(target_port=self.port, name="Client")


def test_udp_ping_pong():
    """Tests if a UDP client can successfully ping a server and receive an echo."""
    port = get_free_port()
    app = UdpTestFormula(port)
    dist = app.distiller

    contract = {
        'timeout': 2.0,
        'stop_match_count': 1,
        'tonics': {
            'Client': {
                'till_sparkle_in': ['ttse__on_udp_data']
            }
        }
    }

    trace = dist.sparkle(contract=contract)

    assert 'contract_met' in trace['stop_condition']
    assert app.server.received_data['action'] == 'ping'
    assert app.client.received_reply['echo'] is True

    dist.teardown_test_environment()
