# TaskTonic/ttTonicStore/ttNetworking/ttUdpSockets.py

import socket
import pickle
from TaskTonic import ttTonic, ttLog
from .ttSelectorService import SelectorService


class UdpSocketHandler(ttTonic):
    """
    A lightweight, connectionless UDP handler.
    Ideal for fast, local smart home communication (e.g., WiZ Bulbs).
    """

    def __init__(self, host='0.0.0.0', port=0, as_server=False, **kwargs):
        from TaskTonic import ttLedger
        ledger = ttLedger()

        # REQUEST THE SERVICE
        srv = ledger.get_service_essence('networking_selector_service')
        if not srv:
            srv = SelectorService(log_mode=ttLog.QUIET)

        super().__init__(catalyst=srv.catalyst, **kwargs)

        self.host = host
        self.port = port
        self.as_server = as_server
        self.selector_handler = SelectorService()
        self.sock = None

    def ttse__on_start(self):
        self.log(f'Initializing UDP socket on {self.host}:{self.port}')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

        if self.as_server:
            # Bind to a specific port to listen for incoming datagrams
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.log(f'UDP Server listening on port {self.port}')
        else:
            self.sock.bind(('0.0.0.0', 0))
            allocated_port = self.sock.getsockname()[1]
            self.log(f'UDP Client bound to ephemeral port {allocated_port}')

        # Mode 1 means it's a standard Read/Write connection (not an 'accept' server)
        self.selector_handler.register(
            self.sock,
            self,
            rd=1,
            mode=1,
            rd_sparkle=self.ttse__on_udp_receive
        )
        self.to_state('ready')

    def ttse_ready__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('udp_ready')

    def ttse_ready__on_udp_receive(self, data, addr):
        """
        Since the SelectorHandler passes raw bytes, we need to extract
        both the data and the sender's address.
        Note: The standard TCP logic in SelectorHandler only reads data,
        not the address. We need to slightly adjust our approach.
        """
        # Read the full datagram directly from the socket
        try:
            payload = self.rcv_data_conversion(data)

            # Pass the data and the origin address up to the parent Tonic
            if hasattr(self.base, 'ttse__on_udp_data'):
                self.base.ttse__on_udp_data(payload, addr)

        except BlockingIOError:
            pass
        except Exception as e:
            self.log(f"UDP Receive Error: {e}")

    def ttsc_ready__send_data(self, data, target_addr):
        """
        Sends a UDP datagram to a specific address.
        :param data: The payload (dict, str, etc.)
        :param target_addr: Tuple (IP, Port)
        """
        bdata = self.send_data_conversion(data)
        try:
            self.sock.sendto(bdata, target_addr)
        except Exception as e:
            self.log(f"UDP Send Error to {target_addr}: {e}")

    def ttse__on_finished(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('finished')

        if self.sock:
            self.selector_handler.unregister(sock=self.sock)
            self.sock.close()

    # --- Conversion Methods (Override these in subclasses) ---

    def send_data_conversion(self, data):
        """Override to customize serialization (e.g., Pickle, JSON)."""
        return data

    def rcv_data_conversion(self, bdata):
        """Override to customize deserialization."""
        return bdata


class UdpDictSocketHandler(UdpSocketHandler):
    """A UDP handler specifically for transmitting Python dictionaries via Pickle."""

    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')
        return pickle.dumps(dict_data)

    def rcv_data_conversion(self, bdata):
        try:
            return pickle.loads(bdata)
        except Exception as e:
            self.log(f"Pickle decode error: {e}")
            return None