# TaskTonic Networking (`ttNetworking`)

The `ttNetworking` module provides a robust, non-blocking, asynchronous network stack fully integrated into the TaskTonic framework. It allows you to build highly concurrent network applications—like chat servers, IoT brokers, or webhook listeners—without writing a single line of traditional threading or `asyncio` boilerplate.

---

## 1. The Sockets API

For the standard developer, the networking module exposes simple, state-aware handlers for TCP, UDP, and HTTP protocols. These handlers are native `ttTonic` objects and communicate exclusively via Sparkles.

### TCP Communication (`TcpSocketHandler`)
The TCP handler can act as both a client and a server. It automatically manages connection states, buffering, and background reconnection.

**Example: A Simple TCP Echo Server**
```python
from TaskTonic import ttTonic
from TaskTonic.ttTonicStore.ttNetworking import TcpStrSocketHandler

class EchoServer(ttTonic):
    def ttse__on_start(self):
        self.log("Starting Echo Server on port 5555...")
        self.net = TcpStrSocketHandler(as_server=True, host='0.0.0.0', port=5555)
        self.to_state('listening')

    def ttse__on_socket_connected(self, addr):
        self.log(f"Client connected from {addr}")

    def ttse__on_socket_data(self, data):
        self.log(f"Received: {data}")
        # Echo the data back to the client
        self.net.ttsc__send_data(f"ECHO: {data}")
```

### UDP Communication (`UdpSocketHandler`)
UDP is connectionless and stateless. It is ideal for high-speed, loss-tolerant streams or simple "Ping-Pong" broadcasts.

```python
from TaskTonic import ttTonic
from TaskTonic.ttTonicStore.ttNetworking import UdpDictSocketHandler

class PingClient(ttTonic):
    def ttse__on_start(self):
        self.udp = UdpDictSocketHandler(as_server=False)
        self.to_state('ready')

    def ttse_ready__on_enter(self):
        # Send a JSON dictionary over UDP
        self.udp.ttsc__send_data({"action": "ping"}, ('127.0.0.1', 55555))

    def ttse__on_udp_data(self, data, addr):
        self.log(f"Received reply from {addr}: {data}")
```

### HTTP Webhooks
TaskTonic includes lightweight, asynchronous HTTP handlers designed specifically for IoT webhooks (like Shelly buttons) or quick REST API calls.
* **`HttpServerHandler`**: Listens for incoming GET/POST requests and auto-replies with `200 OK`.
* **`HttpClientHandler`**: Sends asynchronous HTTP requests to endpoints.

---

## 2. Extending Sockets (Serialization & Fragmentation)

Network streams (especially TCP) do not guarantee that your data arrives in neat, complete packages. A 10KB JSON payload might arrive in chunks, or two rapid messages might be glued together.

TaskTonic provides a clean interface to solve this. You do not modify the base `TcpSocketHandler`. Instead, you subclass it and override two specific methods: `send_data_conversion` and `rcv_data_conversion`.

### Example: Building a Dictionary Socket (`TcpDictSocketHandler`)
Here is how you extend a socket to automatically pack and unpack Python dictionaries safely over a TCP stream using `pickle` and a 4-byte length header (to handle fragmentation).

```python
import struct
import pickle
from TaskTonic.ttTonicStore.ttNetworking import TcpSocketHandler

class TcpDictSocketHandler(TcpSocketHandler):
    def send_data_conversion(self, dict_data):
        """Packs a dictionary into bytes with a 4-byte length prefix."""
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')
            
        pdict = pickle.dumps(dict_data)
        # Prefix the payload with its exact length
        return struct.pack('!I', len(pdict)) + pdict

    def rcv_data_conversion(self, bdata):
        """Unpacks the byte stream, resolving TCP fragmentation."""
        dicts = []
        self.rcv_buf += bdata
        
        while len(self.rcv_buf) > 4:
            # Check the expected length of the upcoming payload
            plen = struct.unpack('!I', self.rcv_buf[:4])[0]
            
            if len(self.rcv_buf) < plen + 4:
                # Payload is incomplete (fragmented). Wait for more data.
                break 
                
            # We have a full payload! Extract it and load the dict.
            dicts.append(pickle.loads(self.rcv_buf[4 : plen + 4]))
            
            # Slice the buffer to process the next potential message
            self.rcv_buf = self.rcv_buf[plen + 4 :]
            
        # Return the list of completed dictionaries to the framework
        return dicts
```

---

## 3. Developer Notes: The `SelectorService` Engine

*(This section details the internal mechanics of `ttNetworking`. Standard users do not need to interact with this layer.)*

Under the hood, all socket handlers delegate their raw OS-level operations to the `SelectorService`. This service is a specialized `ttCatalyst` that runs in the background. Its design solves several critical concurrency challenges inherent to Python.

### The Dual-Wait Problem
A standard TaskTonic `ttCatalyst` executes a `while` loop that sleeps efficiently by calling `queue.get(timeout=next_timer)`. It only wakes up when a Sparkle is queued or a timer expires.

However, network sockets require the application to wait for the Operating System (via `selectors.select()`). Python cannot efficiently block a single thread on *both* a Queue and an OS Selector simultaneously without relying on heavy polling (busy-waiting).

### The Dummy Socket Solution
To solve this, the `SelectorService` overrides the core Catalyst loop to block exclusively on the OS `selector`. 
To ensure the Catalyst still processes normal TaskTonic Sparkles, it uses a custom `MyNotifyingQueue`. Whenever a Sparkle is put into this queue, it writes a single byte (`b'1'`) to an internal, hidden dummy socket pair (`_queue_filled_notify_channel`). This instantly wakes up the OS selector, allowing the Catalyst to process the Sparkle queue.

### Atomic Concurrency Benefits
By forcing all network I/O to run inside the *same* Catalyst thread, TaskTonic's uninterruptible Sparkle mechanism applies to network traffic. There are no race conditions between sending data, disconnecting, and receiving data. Locks (`threading.Lock`) are entirely obsolete.

### Level-Triggered Events vs. Edge-Triggered
A crucial architectural decision was made regarding how data is read. OS Selectors in Python are **Level-Triggered** (not Edge-Triggered). This means the OS will constantly scream *"I have data!"* as long as the receive buffer is not empty.

If TaskTonic simply placed a `ttse__on_data_ready` Sparkle on the queue when the selector fired, the selector might fire hundreds of times before the Catalyst actually executes that Sparkle and drains the OS buffer.

**The Solution:** The `SelectorService` reads the data *immediately* inside the active `select()` loop. This instantly drains the OS buffer, silencing the selector. The raw byte data is then passed directly as a parameter into the Sparkle work order (`rd_sparkle(data)`). 

Because the `SelectorService` Catalyst reads the data and executes the Sparkle within the exact same thread, the data can be passed safely by reference without triggering TaskTonic's cross-thread `copy.deepcopy()` overhead. This results in incredibly fast, memory-efficient networking.