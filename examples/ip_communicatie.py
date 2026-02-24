import struct

from TaskTonic import ttCatalyst, ttTonic, ttLog, ttSparkleStack
import socket, selectors, errno
import threading, queue, time


'''
Designer Notes: 
The SelectorHandler is designed as a catalyst for both itself and the socket handlers. This ensures 
that all 'sparkles' are executed from the same thread, which is required because Python's selectors 
are not thread-safe by design.

In the sparkling loop, we need to monitor both the catalyst queue and selector events. Since we 
want to avoid polling (busy waiting), a adapted queue is created: MyNotifyingQueue. Putting data now 
also signals a notification channel to trigger a selector event. This wakes up the loop, allowing 
it to process the queue and execute the sparkles.
'''

class SelectorHandler(ttCatalyst):
    _tt_is_service = 'selector_handling_service'
    _tt_root_context = True
    # _tt_force_stealth_logging = True

    def __init__(self, *args, name=None, log_mode=None, **kwargs):
        super().__init__(name, log_mode, dont_start_yet=True)

        self.register_data = {}
        self._queue_filled_notify_channel = None
        self._queue_filled_notify_channel_read = None

        # startup notifier
        self.selector = selectors.DefaultSelector()
        self._queue_filled_notify_channel, self._queue_filled_notify_channel_read = socket.socketpair()
        self._queue_filled_notify_channel.setblocking(False)
        self._queue_filled_notify_channel_read.setblocking(False)
        self.selector.register(self._queue_filled_notify_channel_read, selectors.EVENT_READ,
                               (1, self._handle_queue_filled_notify_channel, None))
        self.start_sparkling()

    def _init_service(self, *args, context=None, **kwargs):
        pass

    def new_catalyst_queue(self):
        class MyNotifyingQueue(queue.SimpleQueue):
            def __init__(self, catalyst, *args, **kwargs):
                super().__init__( *args, **kwargs)
                self.catalyst = catalyst

            def put(self, item):
                super().put(item)
                try:
                    self.catalyst._queue_filled_notify_channel.send(b'1')  # notify: queue filled
                except:
                    pass

        return MyNotifyingQueue(self)

    def sparkle(self):
        """
        The main execution loop of the Catalyst.

        This method continuously pulls work orders (instance, sparkle, args, kwargs)
        from the queue and executes them. It runs until the `self.sparkling` flag
        is set to False.
        """
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True
        sparkles_in_queue = True

        # The loop continues as long as the Catalyst is in a sparkling state.
        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0
            while next_timer_expire == 0.0:
                next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0
            if sparkles_in_queue: next_timer_expire = 0.0
            try:
                events = self.selector.select(timeout=next_timer_expire)
                for key, mask in events:
                    sock = key.fileobj
                    mode, rd_sparkle, wr_sparkle = key.data  # data contains the callback function
                    if mode == 1: # connection rd/wr
                        if mask & selectors.EVENT_READ:
                            try: data = sock.recv(65536)
                            except OSError: data = b''
                            if not data: self.unregister(sock=sock)
                            rd_sparkle(data)
                        if mask & selectors.EVENT_WRITE:
                            wr_sparkle()
                    elif mode == 2: #server accept
                        conn, addr = sock.accept()
                        conn.setblocking(False)
                        rd_sparkle(conn, addr)
            except TimeoutError: pass
            except OSError as e:
                # Op Windows: Check op 'bad file descriptor'
                if getattr(e, 'winerror', 0) == 10038:
                    # Logica om dode sockets op te ruimen
                    pass
                else:
                    raise e
            except Exception: raise

            # handle sparkles if any
            try:
                instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get_nowait()
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                while self.extra_sparkles:
                    instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                    sp_stck.push(instance, sparkle.__name__)
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                    sp_stck.pop()
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                sparkles_in_queue = True
            except queue.Empty:
                sparkles_in_queue = False

        # clean up notifier channel
        self.selector.unregister(self._queue_filled_notify_channel_read)
        self._queue_filled_notify_channel.close()
        self._queue_filled_notify_channel_read.close()

    def _handle_queue_filled_notify_channel(self, data):
        # data read, but has no meaning.
        pass

    def register(self, sock, context, mode=1, mask=None, rd=None, wr=None, rd_sparkle=None, wr_sparkle=None):
        if sock is None: sock = context.comm_socket
        if mask is None:
            mask = 0
            if rd is not None and rd: mask |= selectors.EVENT_READ
            if wr is not None and wr: mask |= selectors.EVENT_WRITE
            if mask == 0: mask = selectors.EVENT_READ
        if rd_sparkle is None: rd_sparkle = context.ttse__on_socket_rd
        if wr_sparkle is None: wr_sparkle = context.ttse__on_socket_wr
        self.register_data[sock] = {'mask': mask, 'data': (mode, rd_sparkle, wr_sparkle)}
        self.selector.register(sock, mask, (mode, rd_sparkle, wr_sparkle))

    def unregister(self, sock=None):
        try: self.selector.unregister(sock)
        except: pass
        try: self.register_data.pop(sock)
        except: pass

    def modify(self, sock, mask=None, rd=None, wr=None):
        if mask is None:
            mask = self.register_data[sock]['mask']
            if rd is not None: mask = mask & ~selectors.EVENT_READ | (selectors.EVENT_READ if rd else 0)
            if wr is not None: mask = mask & ~selectors.EVENT_WRITE | (selectors.EVENT_WRITE if wr else 0)
        if mask == 0:
            if self.register_data[sock]['mask'] != 0:
                self.selector.unregister(sock)
        else:
            if self.register_data[sock]['mask'] == 0:
                self.selector.register(sock, mask, self.register_data[sock]['data'])
            else:
                self.selector.modify(sock, mask, self.register_data[sock]['data'])
        self.register_data[sock]['mask'] = mask


class SocketHandler(ttTonic):
    _tt_force_stealth_logging = True

    def __init__(self, as_server=None, as_client=None, host=None, port=None, **kwargs):
        # Look for service before calling super init and create if not active

        from TaskTonic import ttLedger
        l = ttLedger()
        srv = l.get_service_essence('selector_handling_service')
        if not srv:
            srv = SelectorHandler(log=ttLog.QUIET)

        super().__init__(catalyst=srv.catalyst, **kwargs)

        if as_server is not None and as_client is not None:
            raise ValueError('Make up your mind error: cannot specify both as_server and as_client')
        self.as_server = as_server if as_server is not None else not as_client
        self.server_host = host if host is not None else 'localhost'
        self.server_port = port if port is not None else '5555'
        self.server_addr = f'{host}:{port}'

        self.selector_handler = SelectorHandler()
        self.server_socket = None
        self.comm_socket = None
        self.comm_addr = None
        self.rcv_buf = b''
        self.send_buf = b''
        self.buffering_send = False

    def ttse__on_start(self):
        self.log('init_server' if self.as_server else 'init_client')
        self.to_state('init_server' if self.as_server else 'init_client')
        self.ttsc__start_init()

    def ttse__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status(self.get_active_state())

    def ttsc_init_server__start_init(self):
        self.log(f'Init server: {self.server_addr}')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)  # Accept 1 connection at a time
        self.server_socket.setblocking(False)
        self.to_state('server_wait_for_connection')
        self.selector_handler.register(self.server_socket, self, rd=1, mode=2, rd_sparkle=self.ttse__on_server_rd)

    def ttse_server_wait_for_connection__on_server_rd(self, conn, addr):
        self.selector_handler.unregister(sock=self.server_socket)
        self.server_socket.close()
        self.server_socket = None

        self.comm_socket = conn  # Store the client socket
        self.comm_addr = addr
        self.to_state('connected')
        self.selector_handler.register(self.comm_socket, self, rd=1)

        if self.base and hasattr(self.base, 'ttse__on_socket_connected'):
            self.base.ttse__on_socket_connected(addr)

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
            else: raise e

        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)


    def ttse_client_wait_for_connection__on_socket_wr(self):
        # err = self.connected_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        # if err: raise ConnectionRefusedError(f"Connection failed: {os.strerror(err)}")
        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)

    def ttse_connected__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('connected')
        if hasattr(self.base, 'ttse__on_socket_connected'):
            self.base.ttse__on_socket_connected(self.comm_addr)

    def ttse_connected__on_socket_rd(self, data):
        if data:
            for data in self.rcv_data_conversion(data):
                self.base.ttse__on_socket_data(data)
        else:
            self.comm_socket = None
            self.finish()

    def ttse_connected__on_socket_wr(self):
        # pick up writing if send blocked
        self._send(self.send_buf)

    def ttsc_connected__send_data(self, data):
        bdata = self.send_data_conversion(data)
        if self.buffering_send: self.send_buf += bdata
        else: self._send(bdata)

    def _send(self, bdata):
        try:   sent = self.comm_socket.send(bdata)
        except BlockingIOError: sent = 0

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
        if hasattr(self.base, 'ttse__on_socket_finished'):
            self.base.ttse__on_socket_finished()
            if hasattr(self.base, 'ttse__on_socket_status'):
                self.base.ttse__on_socket_status('finished')
        if self.comm_socket:
            self.selector_handler.unregister(sock=self.comm_socket)
            self.comm_socket.close()
        if self.server_socket:
            self.selector_handler.unregister(sock=self.server_socket)
            self.server_socket.close()

class StrSocketHandler(SocketHandler):
    def send_data_conversion(self, str_data):
        if not isinstance(str_data, str): raise TypeError('Data must be a string')
        return str_data.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        return [bdata.decode('utf-8', errors='replace')]

import pickle
class DictSocketHandler(SocketHandler):
    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, str): raise TypeError('Data must be a dict')
        pdict = pickle.dumps(dict_data)
        return b'' + struct.pack('!I', len(pdict)) + pdict

    def rcv_data_conversion(self, bdata):
        dicts = []
        self.rcv_buf += bdata
        while len(self.rcv_buf) > 4: # start check if rcv_buf at least hast length (4 bytes) and dict data
            plen = struct.unpack('!I', self.rcv_buf[:4])[0]
            if len(self.rcv_buf) < plen+4: break # not enough data, wait for it
            dicts.append(pickle.loads(self.rcv_buf[4:plen]))
            self.rcv_buf = self.rcv_buf[plen+4:]
        return dicts



# --- Usage Example ---
from TaskTonic import ttTonic, ttFormula, ttTimerRepeat, ttTimerSingleShot


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
        self.net = StrSocketHandler(as_client=True, host='localhost', port=9999)
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
        self.net = StrSocketHandler(as_server=True, host='localhost', port=9999)

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