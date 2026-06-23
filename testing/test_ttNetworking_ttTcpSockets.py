import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import TcpDictSocketHandler


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TcpMockServer(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []
        self.client_connected = False

    def ttse__on_start(self):
        self.net = TcpDictSocketHandler(as_server=True, host='127.0.0.1', port=self.port)
        self.to_state('waiting')

    def ttse__on_socket_connected(self, addr):
        self.client_connected = True
        self.to_state('connected')

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)
        data['echo'] = True
        self.net.ttsc__send_data(data)


class TcpMockClient(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []

    def ttse__on_start(self):
        self.net = TcpDictSocketHandler(as_client=True, host='127.0.0.1', port=self.port)
        self.to_state('connecting')

    def ttse__on_socket_connected(self, addr):
        self.to_state('connected')

    def ttsc_connected__send_test(self, payload):
        self.net.ttsc__send_data(payload)

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)


class TcpTestFormula(ttFormula):
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
        self.server = TcpMockServer(port=self.port, name="ServerTonic")
        self.client = TcpMockClient(port=self.port, name="ClientTonic")


def test_tcp_socket_flow():
    """Tests the connection, transmission, and teardown of a TCP stream."""
    port = get_free_port()
    app = TcpTestFormula(port)
    dist = app.distiller

    # 1. Wait for connection
    connect_contract = {
        'timeout': 3.0,
        'stop_match_count': 'all',
        'tonics': {
            'ClientTonic': {
                'till_state_in': ['connected']
            },
            'ServerTonic': {
                'probes': ['client_connected'],
                'stop_on_probe': {'client_connected': True}
            }
        }
    }

    dist.sparkle(contract=connect_contract)

    assert app.client.get_current_state_name() == 'connected'
    assert app.server.client_connected is True

    # 2. Send and receive data
    app.client.ttsc_connected__send_test({"msg": "Hello"})

    echo_contract = {
        'timeout': 3.0,
        'stop_match_count': 1,
        'tonics': {
            'ClientTonic': {
                'till_sparkle_in': ['ttse__on_socket_data']
            }
        }
    }

    dist.sparkle(contract=echo_contract)

    assert len(app.server.received_data) == 1
    assert app.server.received_data[0]["msg"] == "Hello"
    assert app.client.received_data[0]["echo"] is True

    dist.teardown_test_environment()
