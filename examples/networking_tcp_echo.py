from TaskTonic import ttTonic, ttFormula, ttTimerRepeat, ttTimerSingleShot
from TaskTonic.ttTonicStore.ttNetworking import TcpStrSocketHandler
import time


class ChatClient(ttTonic):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.cnt = None
        self.net = None
        self.bulk_cnt = 0

    def ttse__on_start(self):
        self.log("Client starting delay...")
        ttTimerSingleShot(1, sparkle_back=self.ttse__on_delayed_start)

    def ttse__on_delayed_start(self, info):
        self.log("Starting Client...")
        # Bind Service: IpService is now a Catalyst running in its own thread
        self.net = TcpStrSocketHandler(as_client=True, host='localhost', port=9999)
        self.cnt = 0

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Client Status: {status} - {info}")

    def ttse__on_socket_connected(self, addr):
        self.tmr = ttTimerRepeat(1, name='client_ping_tmr', sparkle_back=self.ttsc__ping)
        self.to_state('ping')

    def ttsc_ping__ping(self, info):
        self.cnt += 1
        self.net.ttsc__send_data(f"Ping {self.cnt}")
        self.log(f"Ping {self.cnt}")

    def ttse_ping__on_socket_data(self, data):
        # This method is called safely by the IpService thread!
        self.log(f"Client received: {data}")
        if 'STOPPED' in data:
            self.to_state('bulk')
            self.tmr.finish()

    def ttse_bulk__on_socket_data(self, data):
        if not hasattr(self, 'start_bulk'): self.start_bulk = time.time()
        self.bulk_cnt += len(data)
        self.log(f"Received: {self.bulk_cnt} bytes total in {(time.time()-self.start_bulk):2.3f} seconds")

    def ttse__on_socket_finished(self):
        self.finish()

class ChatServer(ttTonic):
    def ttse__on_start(self):
        self.log("Starting Server...")
        self.net = TcpStrSocketHandler(as_server=True, host='localhost', port=9999)

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Server Status: {status} - {info}")

    def ttse__on_socket_data(self, data):
        self.log(f"Server got: {data}")
        # Simple echo (broadcasts to all connections of this tonic inInfusion completed this simple impl)
        self.net.ttsc__send_data(f"Echo: {data}")

        if data == 'Ping 4':
            self.net.ttsc__send_data(f" / STOPPED")
            ttTimerSingleShot(1, name='server_wait_for_sending_bulk', sparkle_back=self.ttsc__start_sending_bulk)

    def ttsc__start_sending_bulk(self, info):
        self.ttsc__send_bulk(100)

    def ttsc__send_bulk(self, cnt):
        if cnt == 0:
            ttTimerSingleShot(5, name='tmr_pause_before_finishing', sparkle_back=self.ttse__on_pause_over)
            return

        self.net.ttsc__send_data('1'*1_000_000)
        self.ttsc__send_bulk(cnt-1)

    def ttse__on_pause_over(self, info):
        self.finish()

    def ttse__on_socket_finished(self):
        self.finish()


class NetworkApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', 'full'),
        )

    def creating_starting_tonics(self):
        ChatServer(name="Server")
        # Give server time to bind (conceptually, though select handles async connect fine)
        ChatClient(name="Client")


if __name__ == "__main__":
    NetworkApp()