import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import HttpServerHandler, HttpClientHandler


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class WebhookServerTonic(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_webhook = None

    def ttse__on_start(self):
        self.server = HttpServerHandler(port=self.port)

    def ttse__on_socket_data(self, request_data):
        self.received_webhook = request_data


class WebhookClientTonic(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_response = None

    def ttse__on_start(self):
        self.client = HttpClientHandler(host='127.0.0.1', port=self.port)
        # self.to_state('connecting')

    def ttse__on_socket_connected(self, addr):
        # Fire the HTTP GET request as soon as the TCP connection is established
        self.client.ttsc_connected__get(path="/test_webhook")

    def ttse__on_socket_data(self, response_data):
        self.received_response = response_data


class HttpTestFormula(ttFormula):
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
        self.server = WebhookServerTonic(port=self.port, name="Server")
        self.client = WebhookClientTonic(port=self.port, name="Client")


def test_http_webhook_flow():
    """Tests if the HTTP Server can receive a GET request and send a 200 OK back."""
    port = get_free_port()
    app = HttpTestFormula(port)
    dist = app.distiller

    # Wait until BOTH tonics have received their data
    contract = {
        'timeout': 3.0,
        'stop_match_count': 'all',
        'tonics': {
            # 'Server': {
            #     'till_sparkle_in': ['ttse__on_socket_data']
            # },
            'Client': {
                'till_sparkle_in': ['ttse__on_socket_data']
            }
        }
    }

    trace = dist.sparkle(contract=contract)

    assert 'contract_met' in trace['stop_condition']
    assert app.server.received_webhook['url'] == '/test_webhook'
    assert '200 OK' in app.client.received_response['body']

    dist.teardown_test_environment()
