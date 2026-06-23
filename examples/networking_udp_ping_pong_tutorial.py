import json
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot
from TaskTonic.ttTonicStore.ttNetworking import UdpSocketHandler


# =============================================================================
# 1. THE SOCKET HANDLER
# =============================================================================

class JsonUdpSocketHandler(UdpSocketHandler):
    """
    A specific UDP handler that automatically translates Python dictionaries
    into JSON bytes (for sending) and JSON bytes back into dictionaries (for receiving).
    """

    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')

        # Convert dict to a compact JSON string without spaces, then encode to bytes.
        # Adding \r\n is often helpful for strict external parsers.
        json_str = json.dumps(dict_data, separators=(',', ':')) + "\r\n"
        return json_str.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        try:
            # Decode the incoming bytes to a string and parse the JSON
            json_str = bdata.decode('utf-8').strip()
            return json.loads(json_str)
        except Exception as e:
            self.log(f"JSON decode error: {e}")
            return None


# =============================================================================
# 2. THE SERVER TONIC (LISTENER)
# =============================================================================

class UdpEchoServer(ttTonic):
    """
    This Tonic acts as a UDP Server. It binds to a specific port and listens
    continuously in the background. It is entirely stateless.
    """

    def __init__(self, listen_port, **kwargs):
        super().__init__(**kwargs)
        self.listen_port = listen_port

    def ttse__on_start(self):
        self.log(f"Starting UDP Echo Server on port {self.listen_port}...")

        # Instantiate the handler as a server (as_server=True).
        # This binds the socket strictly to the specified port.
        self.udp = JsonUdpSocketHandler(
            host='0.0.0.0',
            port=self.listen_port,
            as_server=True
        )

    def ttse__on_udp_data(self, data, addr):
        """
        This Sparkle is automatically triggered by the UdpSocketHandler
        whenever a valid JSON payload arrives.

        :param data: The decoded JSON dictionary.
        :param addr: A tuple containing the (IP, Port) of the sender.
        """
        self.log(f"Server received from {addr}: {data}")

        # We can immediately send a reply back to the exact address
        # that sent us the message. This is the beauty of connectionless UDP!
        reply_payload = {
            "status": "success",
            "server_message": "I heard you!",
            "echo": data
        }

        self.log(f"Server sending reply back to {addr}...")
        self.udp.ttsc__send_data(reply_payload, addr)


# =============================================================================
# 3. THE CLIENT TONIC (SENDER)
# =============================================================================

class UdpPingClient(ttTonic):
    """
    This Tonic acts as a client. It grabs a random ephemeral port,
    sends a message to the server, waits for the reply, and then finishes.
    """

    def __init__(self, target_port, **kwargs):
        super().__init__(**kwargs)
        self.target_port = target_port

    def ttse__on_start(self):
        self.log("Initializing UDP Client...")

        # Instantiate the handler as a client (as_server=False).
        # The OS will automatically assign it a random available port.
        self.udp = JsonUdpSocketHandler(as_server=False)

        # We give the server a tiny fraction of a second to fully boot up
        # before we start firing packets at it.
        ttTimerSingleShot(seconds=0.5, name='tm_boot_delay')
        self.to_state('booting')

    def ttse_booting__on_tm_boot_delay(self, tinfo):
        self.to_state('sending_ping')

    def ttse_sending_ping__on_enter(self):
        payload = {
            "client_name": "TaskTonic Tutorial Bot",
            "action": "ping"
        }

        target_address = ('127.0.0.1', self.target_port)
        self.log(f"Client sending ping to {target_address}...")

        # Send the data. We target localhost (127.0.0.1) because the server
        # is running in the exact same application on our own machine.
        self.udp.ttsc__send_data(payload, target_address)

        # We wait 2 seconds. If a reply comes in during this time,
        # it will be caught by ttse__on_udp_data.
        ttTimerSingleShot(seconds=2.0, name='tm_finish')

    def ttse__on_udp_data(self, data, addr):
        """
        Catches the reply from the server. Notice this does not need a state
        prefix (like ttse_sending_ping__), meaning it will catch data
        regardless of what state the client is currently in.
        """
        self.log(f"Client received reply from Server {addr}: {data}")

    def ttse_sending_ping__on_tm_finish(self, tinfo):
        self.log("Client sequence complete. Shutting down client.")

        # Finishing the client will automatically clean up its UdpSocketHandler.
        # Note: The server will keep running in the background until the Distiller shuts down!
        self.finish()


# =============================================================================
# 4. THE FORMULA (BOOTSTRAPPER)
# =============================================================================

class UdpTutorialFormula(ttFormula):
    """
    The Formula brings everything together and starts the application.
    """

    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'UDP Ping Pong Tutorial'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', 'full'),
        )

    def creating_starting_tonics(self):
        # Define the port they will use to communicate
        SHARED_PORT = 55555

        # Start the listener first
        UdpEchoServer(listen_port=SHARED_PORT, name="EchoServer")

        # Start the sender
        UdpPingClient(target_port=SHARED_PORT, name="PingClient")


if __name__ == "__main__":
    UdpTutorialFormula()