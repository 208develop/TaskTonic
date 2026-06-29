import socket
import errno
import struct
import pickle
from TaskTonic import ttTonic, ttLog, ttTimerSingleShot
from .ttSelectorService import SelectorService


class TcpSocketHandler(ttTonic):
    def __init__(self, as_server=None, as_client=None, host=None, port=None, **kwargs):
        from TaskTonic import ttLedger
        ledger = ttLedger()

        srv = ledger.get_service_essence('networking_selector_service')
        if not srv:
            srv = SelectorService(log_mode=ttLog.QUIET)

        super().__init__(catalyst=srv.catalyst, **kwargs)

        if as_server is not None and as_client is not None:
            raise ValueError('Make up your mind error: cannot specify both as_server and as_client')

        self.as_server = as_server if as_server is not None else not as_client
        self.server_host = host if host is not None else 'localhost'
        self.server_port = port if port is not None else '5555'
        self.server_addr = f'{host}:{port}'

        self.selector_handler = SelectorService()
        self.server_socket = None
        self.comm_socket = None
        self.comm_addr = None
        self.retry = 0
        self.rcv_buf = b''
        self.send_buf = b''
        self.buffering_send = False

    def ttse__on_start(self):
        st_init = 'init_server' if self.as_server else 'init_client'
        self.log(st_init)
        self.to_state(st_init)
        self.ttsc__start_init()

    def ttse__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status(self.get_active_state())

    def ttsc_init_server__start_init(self):
        self.log(f'Init server: {self.server_addr}')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)
        self.to_state('server_wait_for_connection')
        self.selector_handler.register(self.server_socket, self, rd=1, mode=2, rd_sparkle=self.ttse__on_server_rd)

    def ttse_server_wait_for_connection__on_server_rd(self, conn, addr):
        self.selector_handler.unregister(sock=self.server_socket)
        self.server_socket.close()
        self.server_socket = None

        self.comm_socket = conn
        self.comm_addr = addr
        self.to_state('connected')
        self.selector_handler.register(self.comm_socket, self, rd=1)

    def ttsc_init_client__start_init(self):
        self.log(f'Init client: connect to {self.server_addr}')
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_socket.setblocking(False)

        try:
            self.selector_handler.register(self.comm_socket, self, wr=1)
            self.comm_socket.connect((self.server_host, self.server_port))
        except BlockingIOError as e:
            if e.errno == errno.EINPROGRESS or e.errno == errno.WSAEWOULDBLOCK:
                self.to_state('client_wait_for_connection')
                return
            else:
                raise e

        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)

    def ttse_client_wait_for_connection__on_socket_wr(self):
        err = self.comm_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err:
            import os
            self.log(f"Connection failed: {os.strerror(err)}")
            self.selector_handler.unregister(self.comm_socket)
            self.comm_socket.close()
            self.comm_socket = None

            if self.retry > 3:
                self.finish()
            else:
                self.retry += 1
                self.to_state('wait_for_retry')
            return

        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)

    def ttse_wait_for_retry__on_enter(self):
        self.log("Scheduling connection retry in 2 seconds...")
        ttTimerSingleShot(seconds=2, name='tm_retry')

    def ttse_wait_for_retry__on_tm_retry(self, _):
        self.log("Attempting to reconnect to the server...")
        self.to_state('init_client')
        self.ttsc__start_init()

    def ttse_connected__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('connected')
        if hasattr(self.base, 'ttse__on_socket_connected'):
            self.base.ttse__on_socket_connected(self.comm_addr)

    def ttse_connected__on_socket_rd(self, data):
        if data:
            for d in self.rcv_data_conversion(data):
                self.base.ttse__on_socket_data(d)
        else:
            self.comm_socket = None
            if hasattr(self.base, 'ttse__on_socket_status'):
                self.base.ttse__on_socket_status('disconnected')

            if hasattr(self.base, 'ttse__on_disconnected'):
                self.base.ttse__on_disconnected()

            self.finish()

    def ttse_connected__on_socket_wr(self):
        self._send(self.send_buf)

    def ttsc_connected__send_data(self, data):
        bdata = self.send_data_conversion(data)
        if self.buffering_send:
            self.send_buf += bdata
        else:
            self._send(bdata)

    def _send(self, bdata):
        try:
            sent = self.comm_socket.send(bdata)
        except BlockingIOError:
            sent = 0

        if sent == len(bdata):
            self.send_buf = b''
            self.buffering_send = False
            self.selector_handler.modify(self.comm_socket, wr=0)
        else:
            self.send_buf = bdata[sent:]
            self.buffering_send = True
            self.selector_handler.modify(self.comm_socket, wr=1)

    def ttse_connected__on_exit(self):
        self.log(f'Disconnected from {self.comm_addr}')

    def send_data_conversion(self, bdata):
        return bdata

    def rcv_data_conversion(self, bdata):
        return [bdata]

    def ttse__on_finished(self):
        """Cleanup socket resources before allowing the tonic to complete."""
        if hasattr(self.base, 'ttse__on_socket_finished'):
            self.base.ttse__on_socket_finished()

        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('finished')

        if self.comm_socket:
            self.selector_handler.unregister(sock=self.comm_socket)
            self.comm_socket.close()
            self.comm_socket = None

        if self.server_socket:
            self.selector_handler.unregister(sock=self.server_socket)
            self.server_socket.close()
            self.server_socket = None


class TcpStrSocketHandler(TcpSocketHandler):
    def send_data_conversion(self, str_data):
        if not isinstance(str_data, str):
            raise TypeError('Data must be a string')
        return str_data.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        return [bdata.decode('utf-8', errors='replace')]


class TcpDictSocketHandler(TcpSocketHandler):
    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')
        pdict = pickle.dumps(dict_data)
        return b'' + struct.pack('!I', len(pdict)) + pdict

    def rcv_data_conversion(self, bdata):
        dicts = []
        self.rcv_buf += bdata
        while len(self.rcv_buf) > 4:
            plen = struct.unpack('!I', self.rcv_buf[:4])[0]
            if len(self.rcv_buf) < plen + 4:
                break
            dicts.append(pickle.loads(self.rcv_buf[4:plen + 4]))
            self.rcv_buf = self.rcv_buf[plen + 4:]
        return dicts
