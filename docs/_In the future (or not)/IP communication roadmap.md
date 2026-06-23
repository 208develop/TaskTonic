# TaskTonic Future Architecture Roadmap: IP, Protocols & Visual Dashboards

This document serves as the architectural vision and blueprint for expanding the TaskTonic framework into network communications (UDP, HTTP, HTTPS, MQTT) and a declarative, vector-based user interface layer.

---

## 1. Core Principles of the Network Layer

All future network expansions will build upon the existing `SelectorHandler` infrastructure. By hooking the underlying native TCP/UDP sockets directly into the selector engine via `EVENT_READ`, TaskTonic handles multi-device networking **synchronously within a single background thread**, completely avoiding thread-safety issues or overhead from external concurrency engines.

---

## 2. UDP Integration (The Immediate Next Step)

UDP (User Datagram Protocol) is essential for high-speed, low-overhead local smart home automation, specifically for components like **WiZ Bulbs** (which listen natively on UDP port 38899).

### Architectural Changes
* **Connectionless:** No `accept()` or `connect()` handshakes are required. The socket simply listens or throws datagrams.
* **No De-fragmentation:** Unlike TCP, UDP delivers packets atomically. The 4-byte framing header and `rcv_buf` reconstruction logic are obsolete; `recvfrom()` returns the full payload immediately.
* **Source Tracking:** Every incoming datagram returns a `(data, addr)` tuple. The sender's address (`addr`) must be tracked to route replies.

### Code Blueprint: `UdpSocketHandler`

```python
import socket
import pickle


class UdpSocketHandler:
    def __init__(self, host, port, as_server=False):
        self.host = host
        self.port = port
        self.as_server = as_server
        
        # SOCK_DGRAM specifies UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        
        if self.as_server:
            self.sock.bind((self.host, self.port))

    def handle_read(self):
        """Called by the SelectorHandler when a UDP packet arrives."""
        try:
            data, addr = self.sock.recvfrom(65535)
            payload = pickle.loads(data)
            return payload, addr
        except Exception:
            return None, None

    def send_data(self, payload, target_addr):
        """Sends an atomic datagram to a specific target address."""
        try:
            data = pickle.dumps(payload)
            self.sock.sendto(data, target_addr)
        except Exception:
            pass
```

---

## 3. HTTP & HTTPS Integration (Shelly Components)

Shelly components expose a powerful local HTTP REST API. Integrating HTTP expands TaskTonic into a web-aware framework.

### HTTP Implementation Strategies
1. **Client Mode (TaskTonic commands Shelly):** TaskTonic sends a quick, standard HTTP GET request to the Shelly IP (e.g., `http://192.168.1.50/relay/0?turn=toggle`).
2. **Server Mode / Webhooks (Shelly commands TaskTonic):** Instead of continuous "long-polling" requests which hog resources, the Shelly is configured via its web UI to trigger an **I/O Action (Webhook)**. When a physical switch is flipped, Shelly fires an instantaneous HTTP GET to TaskTonic's lightweight HTTP Server (e.g., port 8080). TaskTonic parses the URL and immediately maps it to a Sparkle.

---

### Deep Dive: Is HTTPS a Big Step?

**Yes, transitioning from raw HTTP to HTTPS is a significant technical milestone.** While HTTP is just plain text sent over a standard TCP socket, HTTPS injects a mandatory **SSL/TLS cryptographic layer** right between TCP and HTTP.

```
HTTP:  [ Application (Plain Text) ] ----> [ TCP Socket ]
HTTPS: [ Application (Plain Text) ] ----> [ SSL/TLS Encryption ] ----> [ Secure TCP Socket ]
```

#### The Challenges of HTTPS in a Native Socket Framework:
1. **The TLS Handshake:** Before a single byte of data can be read, a complex multi-step cryptographic handshake must occur to exchange keys and verify identities.
2. **Certificate Management:** * **Server Mode:** If TaskTonic acts as an HTTPS server to receive secure webhooks, you **must** supply an SSL certificate (`.crt`) and a private key (`.key`). Local devices will reject self-signed certificates unless you manually force them to trust your custom Root CA.
   * **Client Mode:** If TaskTonic connects to a secure external server, it needs to verify the remote certificate using a local store of trusted authorities.
3. **Socket Wrapping:** In native Python sockets, you cannot just read/write anymore. You must wrap the raw socket using Python's `ssl` module.

#### Impact on `SelectorHandler`:
Fortunately, once an SSL socket finishes its handshake, it can still be registered with the `SelectorHandler` for `EVENT_READ`. However, the wrapping boilerplate introduces extra complexity:

```python
import socket
import ssl

# Example of wrapping a raw socket for HTTPS Server Mode
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(raw_socket, server_side=True)
```

**Conclusion on HTTPS:** For purely local home automation networks (isolated Wi-Fi), raw HTTP is usually preferred due to zero certificate overhead. If external cloud interaction or absolute local encryption is required, the `ssl` module integration must be implemented.

---

## 4. MQTT Integration (The Unified Smart Home Backbone)

MQTT (Message Queuing Telemetry Transport) introduces a lightweight Pub/Sub architecture via a central agent (e.g., a **Mosquitto Broker**).

### Why MQTT is Superior for Smart Homes
* **Decentralized IPs:** TaskTonic no longer needs to keep track of individual Shelly IP addresses or host an HTTP Webhook server. It opens **one permanent TCP connection** to the Mosquitto Broker and subscribes to relevant topics.
* **1:1 Mapping with Store Paths:** MQTT uses a hierarchical slash-separated topic structure that mirrors TaskTonic's Store Paths perfectly.

### Architectural Harmony
Because an MQTT client library (like `paho-mqtt`) allows you to extract its underlying raw TCP file descriptor, you can effortlessly register the Mosquitto connection straight into the `SelectorHandler`. Incoming MQTT payload updates automatically translate directly to targeted Ledger paths:

```python
def on_mqtt_message(client, userdata, message):
    path = message.topic  # e.g., "tasktonic/store/livingroom/switch_1"
    payload = message.payload.decode('utf-8')
    
    ledger = ttLedger.get_instance()
    tonic = ledger.get_tonic_by_path(path)
    
    if tonic is not None:
        # Automatically direct the external network state to the correct internal Tonic
        tonic.ttse__on_external_update(payload)
```

---

## 5. Declarative SVG Dashboards

The future UI layer allows developers to draw beautiful, responsive dashboards using standard vector design software like **Inkscape**, completely bypassing HTML/CSS layout grid nightmares.

```
+------------------+      Sets ID to:       +------------------------+
| Inkscape Drawing |  ===================>  |  "tt_kitchen_light_1"  |
+------------------+                        +------------------------+
                                                        ||
                                                        || (Auto-Maps)
                                                        \/
                                            +------------------------+
                                            |  TaskTonic Store Path: |
                                            |  "kitchen/light_1"     |
                                            +------------------------+
```

### The Workflow Blueprint
1. **Design:** Draw the UI interface visually in Inkscape. Every interactive component (button, bulb, background panel) is given a specific **Object ID** following a naming convention that maps directly to the TaskTonic Store Paths (e.g., an ID of `tt_kitchen_light_1` maps to path `kitchen/light_1`).
2. **Parse:** Upon startup, TaskTonic's lightweight web server uses an XML parser (`xml.etree.ElementTree`) to scan the SVG file, automatically creating data bindings for every element prefixed with `tt_`.
3. **Stream (WebSockets):** The server serves the SVG to any screen or mobile device. A universal, lightweight embedded JavaScript engine handles bidirectional real-time communication over a persistent WebSocket connection:
   * **User Interaction:** Clicking an SVG element in the browser immediately relays a JSON action object back to TaskTonic over the WebSocket, pushing a Sparkle onto the queue.
   * **State Updates:** When an internal Tonic shifts state (e.g., via a UDP or MQTT event), TaskTonic pushes a state message down the WebSocket. The frontend JavaScript instantly locates the corresponding SVG ID and modifies its visual attributes (e.g., changing CSS `fill` colors to yellow) in real-time.

---

## Summary of Protocol Capabilities

| Protocol | Purpose in TaskTonic | Connection Style | Overhead | Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **UDP** | WiZ Bulbs control | Connectionless Datagram | Lowest | Low |
| **HTTP** | Shelly controls & webhooks | Short-lived TCP per request | Medium | Low |
| **HTTPS** | Encrypted webhooks / external APIs | Secure TCP with TLS handshake | High | High (Certificates) |
| **MQTT** | Unified Shelly / Broker fabric | Single permanent TCP connection | Lowest | Low (via library) |
| **WebSockets**| Real-time SVG UI syncing | Single persistent HTTP Upgrade | Low | Medium |