# TaskTonic/ttTonicStore/ttNetworking/ttSelectorService.py

from TaskTonic import ttCatalyst, ttSparkleStack
import socket
import selectors
import threading
import queue
import time


'''
Designer Note: 
The SelectorHandler is designed as a catalyst for both itself and the socket handlers. This ensures 
that all 'sparkles' are executed from the same thread, which is required because Python's selectors 
are not thread-safe by design.

In the sparkling loop, we need to monitor both the catalyst queue and selector events. Since we 
want to avoid polling (busy waiting), a adapted queue is created: MyNotifyingQueue. Putting data now 
also signals a notification channel to trigger a selector event. This wakes up the loop, allowing 
it to process the queue and execute the sparkles.
'''


class SelectorService(ttCatalyst):
    """
    The central engine for OS-level network I/O.
    This Catalyst blocks on selectors.select() instead of a standard queue,
    making it highly efficient for handling (thousands of) sockets.
    """
    # NEW SERVICE NAME to avoid conflicts with legacy code
    _tt_is_service = 'networking_selector_service'
    _tt_root_context = True

    def __init__(self, *args, name=None, log_mode=None, **kwargs):
        super().__init__(name, log_mode, dont_start_yet=True)

        self.register_data = {}
        self._queue_filled_notify_channel = None
        self._queue_filled_notify_channel_read = None

        # Startup notifier
        self.selector = selectors.DefaultSelector()
        self._queue_filled_notify_channel, self._queue_filled_notify_channel_read = socket.socketpair()
        self._queue_filled_notify_channel.setblocking(False)
        self._queue_filled_notify_channel_read.setblocking(False)

        # Register the notification socket
        self.selector.register(
            self._queue_filled_notify_channel_read,
            selectors.EVENT_READ,
            (1, self._handle_queue_filled_notify_channel, None)
        )
        self.start_sparkling()

    def _init_service(self, *args, context=None, **kwargs):
        pass

    def new_catalyst_queue(self):
        class MyNotifyingQueue(queue.SimpleQueue):
            def __init__(self, catalyst, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.catalyst = catalyst

            def put(self, item):
                super().put(item)
                try:
                    # Wake up the selector loop!
                    self.catalyst._queue_filled_notify_channel.send(b'1')
                except:
                    pass

        return MyNotifyingQueue(self)

    def sparkle(self):
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True
        sparkles_in_queue = True

        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0

            while next_timer_expire == 0.0:
                if self.timers:
                    next_timer_expire = self.timers[0].check_on_expiration(reference)
                else:
                    next_timer_expire = 60.0

            if sparkles_in_queue:
                next_timer_expire = 0.0

            try:
                # Block efficiently at the OS level
                events = self.selector.select(timeout=next_timer_expire)
                for key, mask in events:
                    sock = key.fileobj
                    mode, rd_sparkle, wr_sparkle = key.data

                    if mode == 1:  # Connection read/write (TCP or UDP data)
                        if mask & selectors.EVENT_READ:
                            # Check socket type to determine the correct read method
                            if sock.type == socket.SOCK_DGRAM:
                                try:
                                    # UDP: Read datagram and capture sender address
                                    data, addr = sock.recvfrom(65535)
                                    if data:
                                        # Queue the Sparkle with data AND address
                                        rd_sparkle(data, addr)
                                except OSError:
                                    pass
                            else:
                                try:
                                    # TCP: Read stream data
                                    data = sock.recv(65536)
                                except OSError:
                                    data = b''

                                # An empty byte string in TCP means the connection is closed
                                if not data:
                                    self.unregister(sock=sock)

                                # Queue the Sparkle with just the data
                                rd_sparkle(data)

                        if mask & selectors.EVENT_WRITE:
                            wr_sparkle()

                    elif mode == 2:  # TCP server accept
                        conn, addr = sock.accept()
                        conn.setblocking(False)
                        rd_sparkle(conn, addr)

            except TimeoutError:
                pass
            except OSError as e:
                if getattr(e, 'winerror', 0) == 10038:
                    pass  # Bad file descriptor
                else:
                    raise e
            except Exception:
                raise

            # Process pending TaskTonic Sparkles
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
                sparkles_in_queue = True
            except queue.Empty:
                sparkles_in_queue = False

        # Cleanup
        self.selector.unregister(self._queue_filled_notify_channel_read)
        self._queue_filled_notify_channel.close()
        self._queue_filled_notify_channel_read.close()

    def _handle_queue_filled_notify_channel(self, data):
        pass  # Flush the dummy byte

    def register(self, sock, context, mode=1, mask=None, rd=None, wr=None, rd_sparkle=None, wr_sparkle=None):
        if sock is None: sock = context.comm_socket

        if mask is None:
            mask = 0
            if rd is not None and rd: mask |= selectors.EVENT_READ
            if wr is not None and wr: mask |= selectors.EVENT_WRITE
            if mask == 0: mask = selectors.EVENT_READ

        if rd_sparkle is None:
            defaults_rd = ['ttse__on_socket_rd', 'ttse__on_udp_data', 'ttse__on_tcp_data']
            for default_name in defaults_rd:
                if hasattr(context, default_name):
                    rd_sparkle = getattr(context, default_name)
                    break
            # Fail-fast alleen als we NU direct willen lezen en niets hebben gevonden
            if mask & selectors.EVENT_READ and rd_sparkle is None:
                raise RuntimeError(
                    f"[{context.name}] Selector registration failed: Socket configured for "
                    f"READ events, but no default method found."
                )

        if wr_sparkle is None:
            defaults_wr = ['ttse__on_socket_wr', 'ttse__on_udp_wr', 'ttse__on_tcp_wr']
            for default_name in defaults_wr:
                if hasattr(context, default_name):
                    wr_sparkle = getattr(context, default_name)
                    break
            if mask & selectors.EVENT_WRITE and wr_sparkle is None:
                raise RuntimeError(
                    f"[{context.name}] Selector registration failed: Socket configured for "
                    f"WRITE events, but no default method found."
                )

        self.register_data[sock] = {'mask': mask, 'data': (mode, rd_sparkle, wr_sparkle)}
        self.selector.register(sock, mask, (mode, rd_sparkle, wr_sparkle))

    def unregister(self, sock=None):
        try:
            self.selector.unregister(sock)
        except:
            pass
        try:
            self.register_data.pop(sock)
        except:
            pass

    def modify(self, sock, mask=None, rd=None, wr=None):
        if mask is None:
            mask = self.register_data[sock]['mask']
            if rd is not None:
                mask = mask & ~selectors.EVENT_READ | (selectors.EVENT_READ if rd else 0)
            if wr is not None:
                mask = mask & ~selectors.EVENT_WRITE | (selectors.EVENT_WRITE if wr else 0)

        if mask == 0:
            if self.register_data[sock]['mask'] != 0:
                self.selector.unregister(sock)
        else:
            if self.register_data[sock]['mask'] == 0:
                self.selector.register(sock, mask, self.register_data[sock]['data'])
            else:
                self.selector.modify(sock, mask, self.register_data[sock]['data'])
        self.register_data[sock]['mask'] = mask

    def _ttss__main_catalyst_finished(self):
        pass
