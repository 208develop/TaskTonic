import pytest
import time
import socket
import struct
import pickle
from TaskTonic import ttTonic, ttFormula, ttLedger
from TaskTonic.ttTonicStore.ttDistiller import ttDistiller
from TaskTonic.ttTonicStore.ttIpSockets import DictSocketHandler


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def reset_ledger():
    """Zorgt voor een schone lei voor elke test en wacht op background threads."""
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

    yield

    if ttLedger._instance:
        # Wacht heel even tot alle achtergrond Catalysts (zoals SelectorHandler)
        # daadwerkelijk hun thread hebben afgesloten vóórdat we de administratie vernietigen.
        for t in ttLedger._instance.tonics:
            if t and hasattr(t, 'sparkling') and t.id > 0:
                start_t = time.time()
                while t.sparkling and time.time() - start_t < 1.0:
                    time.sleep(0.01)

        ttLedger._instance.records = []
        ttLedger._instance.tonics = []
        ttLedger._instance.formula = None

    ttLedger._instance = None
    ttLedger._singleton_init_done = False


def get_free_port():
    """Zoekt een vrije poort om 'Address already in use' errors te voorkomen."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


# ==============================================================================
# TEST 1: Isolatie test van de DictSocketHandler (Inpakken/Uitpakken)
# ==============================================================================

def test_dict_socket_serialization_and_fragmentation():
    """Test de zuivere logica van het inpakken en uitpakken van dicts."""
    handler = DictSocketHandler.__new__(DictSocketHandler)
    handler.rcv_buf = b''

    test_dict_1 = {"cmd": "login", "user": "test", "id": 1}
    test_dict_2 = {"cmd": "data", "payload": [1, 2, 3]}

    packed_1 = handler.send_data_conversion(test_dict_1)
    packed_2 = handler.send_data_conversion(test_dict_2)

    # 1. Fragmentatie simuleren
    result = handler.rcv_data_conversion(packed_1[:3])
    assert len(result) == 0
    assert len(handler.rcv_buf) == 3

    # 2. De rest + een stuk van de volgende
    chunk = packed_1[3:] + packed_2[:10]
    result = handler.rcv_data_conversion(chunk)
    assert len(result) == 1
    assert result[0] == test_dict_1
    assert len(handler.rcv_buf) == 10

    # 3. Het laatste stukje
    result = handler.rcv_data_conversion(packed_2[10:])
    assert len(result) == 1
    assert result[0] == test_dict_2
    assert len(handler.rcv_buf) == 0


# ==============================================================================
# TONICS VOOR INTEGRATIE TESTS
# ==============================================================================

class MockServer(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []
        self.received_count = 0  # <--- Toegevoegd voor de stop_on_probe optimalisatie!
        self.client_connected = False

    def ttse__on_start(self):
        self.net = DictSocketHandler(as_server=True, host='localhost', port=self.port)
        self.to_state('waiting')

    def ttse__on_socket_connected(self, addr):
        self.client_connected = True
        self.to_state('connected')

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)
        self.received_count += 1
        data['echo'] = True
        self.net.ttsc__send_data(data)


class MockClient(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []

    def ttse__on_start(self):
        self.net = DictSocketHandler(as_client=True, host='localhost', port=self.port)
        self.to_state('connecting')

    def ttse__on_socket_connected(self, addr):
        self.to_state('connected')

    def ttsc_connected__send_test(self, payload):
        self.net.ttsc__send_data(payload)

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)


class NetworkTestFormula(ttFormula):
    def __init__(self, port):
        self.port = port
        super().__init__()

    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',
            'tasktonic/log/default': 'stealth',
        }

    def creating_main_catalyst(self):
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.server = MockServer(port=self.port, name="ServerTonic")
        self.client = MockClient(port=self.port, name="ClientTonic")


# ==============================================================================
# TEST 2: Flow & Gedrag (Connectie, Send, Rcv) in de Distiller
# ==============================================================================

def test_socket_connection_flow():
    port = get_free_port()
    app = NetworkTestFormula(port)
    dist = app.distiller

    # --- DEEL 1: Wacht robuust op connectie (AND LOGICA) ---
    # We vertellen de Distiller: Stop pas als de client de state 'connected'
    # heeft, EN de server de interne variabele 'client_connected' op True heeft staan.
    connect_contract = {
        'timeout': 3.0,
        'stop_match_count': 'all',  # AND logica
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

    trace1 = dist.sparkle(contract=connect_contract)

    # Verifieer dat we gestopt zijn wegens het contract en niet de timeout
    assert 'contract_met: 2/2 tonics matched' in trace1['stop_condition']
    assert app.client.get_current_state_name() == 'connected'
    assert app.server.client_connected is True

    # --- DEEL 2: Data sturen en ontvangen ---
    test_payload = {"msg": "Hello TaskTonic"}
    app.client.ttsc__send_test(test_payload)

    # Wacht tot de client de echo binnenkrijgt. Eén match is voldoende.
    echo_contract = {
        'timeout': 3.0,
        'stop_match_count': 1,
        'tonics': {
            'ClientTonic': {
                'till_sparkle_in': ['ttse__on_socket_data']
            }
        }
    }

    trace2 = dist.sparkle(contract=echo_contract)
    assert 'contract_met: 1/1 tonics matched' in trace2['stop_condition']

    # Controleer of de flow 100% goed is gegaan
    assert len(app.server.received_data) == 1
    assert app.server.received_data[0]["msg"] == "Hello TaskTonic"

    assert len(app.client.received_data) == 1
    assert app.client.received_data[0]["msg"] == "Hello TaskTonic"
    assert app.client.received_data[0]["echo"] is True

    dist.finish_distiller()


# ==============================================================================
# TEST 3: Full Speed / Bulk Test (Stress test & Buffering logica)
# ==============================================================================

class BulkSenderClient(MockClient):
    def ttsc_connected__start_bulk(self, amount):
        self.sent_count = amount
        for i in range(amount):
            self.net.ttsc__send_data({"seq": i, "padding": "X" * 1024})
        self.to_state('done_sending')


def test_socket_bulk_speed_and_buffering():
    port = get_free_port()

    class BulkFormula(NetworkTestFormula):
        def creating_starting_tonics(self):
            self.server = MockServer(port=self.port, name="ServerTonic")
            self.client = BulkSenderClient(port=self.port, name="ClientTonic")

    app = BulkFormula(port)
    dist = app.distiller

    # --- DEEL 1: Wacht op connectie (AND LOGICA) ---
    dist.sparkle(contract={
        'timeout': 3.0,
        'stop_match_count': 'all',
        'tonics': {
            'ClientTonic': {'till_state_in': ['connected']},
            'ServerTonic': {'probes': ['client_connected'], 'stop_on_probe': {'client_connected': True}}
        }
    })

    # --- DEEL 2: BULK DATA ---
    # Stuur 5000 flinke dicts tegelijkertijd weg (~5MB)
    TOTAL_MESSAGES = 5000
    app.client.ttsc__start_bulk(TOTAL_MESSAGES)

    # Wacht tot de server exact 5000 berichten heeft verwerkt.
    # Dit voorkomt dat we the Distiller continu laten pollen!
    bulk_contract = {
        'timeout': 5.0,
        'stop_match_count': 1,
        'tonics': {
            'ServerTonic': {
                'probes': ['received_count'],
                'stop_on_probe': {'received_count': TOTAL_MESSAGES}
            }
        }
    }

    trace = dist.sparkle(contract=bulk_contract)
    assert 'contract_met: 1/1 tonics matched' in trace['stop_condition']

    # Final checks
    assert len(app.server.received_data) == TOTAL_MESSAGES
    for i in range(TOTAL_MESSAGES):
        assert app.server.received_data[i]["seq"] == i

    dist.finish_distiller()