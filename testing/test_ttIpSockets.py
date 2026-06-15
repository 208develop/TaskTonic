import pytest
import time
import socket
import struct
import pickle
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot, ttLedger
from TaskTonic.ttTonicStore.ttDistiller import ttDistiller
from TaskTonic.ttTonicStore.ttIpSockets import DictSocketHandler, StrSocketHandler


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def reset_ledger():
    """Zorgt voor een schone lei voor elke test."""
    ttLedger._instance = None
    ttLedger._singleton_init_done = False
    yield
    if ttLedger._instance:
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
    """
    Test de zuivere logica van het inpakken en uitpakken van dicts.
    Speciale focus op gefragmenteerde TCP pakketten (halve bytes ontvangen).
    """
    # We bypassen __init__ om te voorkomen dat de TaskTonic ledger start
    handler = DictSocketHandler.__new__(DictSocketHandler)
    handler.rcv_buf = b''

    test_dict_1 = {"cmd": "login", "user": "test", "id": 1}
    test_dict_2 = {"cmd": "data", "payload": [1, 2, 3]}

    # Inpakken
    packed_1 = handler.send_data_conversion(test_dict_1)
    packed_2 = handler.send_data_conversion(test_dict_2)

    # Controleer structuur (4 bytes length header + pickle dump)
    assert len(packed_1) > 4
    length_header = struct.unpack('!I', packed_1[:4])[0]
    assert length_header == len(packed_1) - 4

    # --- Simulatie van Netwerk Fragmentatie ---

    # 1. We ontvangen slechts de eerste 3 bytes van het eerste pakket (header incompleet)
    result = handler.rcv_data_conversion(packed_1[:3])
    assert len(result) == 0  # Nog geen dict beschikbaar
    assert len(handler.rcv_buf) == 3

    # 2. We ontvangen de rest van pakket 1, PLUS de helft van pakket 2
    chunk = packed_1[3:] + packed_2[:10]
    result = handler.rcv_data_conversion(chunk)

    assert len(result) == 1
    assert result[0] == test_dict_1  # Pakket 1 is nu succesvol uit de buffer gehaald!
    assert len(handler.rcv_buf) == 10  # De rest van pakket 2 zit nog in de wachtkamer

    # 3. We ontvangen het laatste stukje van pakket 2
    result = handler.rcv_data_conversion(packed_2[10:])
    assert len(result) == 1
    assert result[0] == test_dict_2
    assert len(handler.rcv_buf) == 0  # Buffer is weer leeg


# ==============================================================================
# TONICS VOOR INTEGRATIE TESTS
# ==============================================================================

class MockServer(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []
        self.client_connected = False

    def ttse__on_start(self):
        self.net = DictSocketHandler(as_server=True, host='localhost', port=self.port)
        self.to_state('waiting')

    def ttse__on_socket_connected(self, addr):
        self.client_connected = True
        self.to_state('connected')

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)
        # Simpele echo terug, we voegen een flag toe
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
    """Test of de Server en Client elkaar vinden, verbinden en data uitwisselen."""
    port = get_free_port()
    app = NetworkTestFormula(port)
    dist = app.distiller

    # 1. Wacht tot de client de status 'connected' bereikt.
    # Omdat de SelectorHandler de socket events afhandelt en dan sparkles
    # terugschiet naar de main thread, pakt de Distiller dit netjes op.
    status = dist.sparkle(timeout=2.0, till_state_in=['connected'], contract={'probes': ['client_connected']})

    assert app.client.get_current_state_name() == 'connected'
    assert app.server.client_connected is True

    # 2. Laat de client data sturen
    test_payload = {"msg": "Hello TaskTonic"}
    app.client.ttsc__send_test(test_payload)

    # 3. Draai de distiller totdat de client zijn eigen data als echo terugkrijgt
    dist.sparkle(timeout=2.0, till_sparkle_in=['ttse__on_socket_data'])

    # Controleer of de server het ontvangen heeft
    assert len(app.server.received_data) == 1
    assert app.server.received_data[0]["msg"] == "Hello TaskTonic"

    # Controleer de echo op de client
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
            # We sturen extreem snel achter elkaar. Dit triggert
            # gegarandeerd BlockingIOError (EAGAIN) in de OS socket
            # waardoor de `buffering_send = True` logica van SocketHandler geactiveerd wordt.
            self.net.ttsc__send_data({"seq": i, "padding": "X" * 1024})
        self.to_state('done_sending')


def test_socket_bulk_speed_and_buffering():
    """
    Test de stabiliteit bij het sturen van gigantische hoeveelheden data.
    Dit forceert de socket buffers om vol te raken, test de 'buffering_send'
    logica in SelectorHandler, en checkt of de volgorde behouden blijft.
    """
    port = get_free_port()

    # Kleine aanpassing van de formule voor deze test
    class BulkFormula(NetworkTestFormula):
        def creating_starting_tonics(self):
            self.server = MockServer(port=self.port, name="ServerTonic")
            self.client = BulkSenderClient(port=self.port, name="ClientTonic")

    app = BulkFormula(port)
    dist = app.distiller

    # Wacht op connectie
    dist.sparkle(timeout=2.0, till_state_in=['connected'])

    # Stuur 5000 flinke dicts tegelijkertijd weg (~5MB aan data direct de non-blocking socket in)
    TOTAL_MESSAGES = 5000
    app.client.ttsc__start_bulk(TOTAL_MESSAGES)

    # We laten de distiller rennen totdat de server alle 5000 berichten heeft ontvangen
    start_time = time.time()

    # Polling met een lichte timeout om de distiller telkens even te laten ademen
    while len(app.server.received_data) < TOTAL_MESSAGES:
        dist.sparkle(timeout=0.1)
        if time.time() - start_time > 5.0:  # Fail-safe
            break

    assert len(app.server.received_data) == TOTAL_MESSAGES

    # Controleer of de TCP volgorde 100% klopt (ondanks fragmentatie en buffering)
    for i in range(TOTAL_MESSAGES):
        assert app.server.received_data[i]["seq"] == i

    # Clean up
    dist.finish_distiller()
