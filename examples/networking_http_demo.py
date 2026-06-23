from TaskTonic import ttTonic, ttFormula, ttLog, ttTimerRepeat
from TaskTonic.ttTonicStore.ttNetworking.ttHttpSockets import HttpServerHandler, HttpClientHandler


class SmartHomeHub(ttTonic):
    """
    The server: Constantly listens for incoming HTTP requests (webhooks).
    """

    def ttse__on_start(self):
        self.log("Starting Smart Home Hub (HTTP Webhook Server) on port 8080...")
        # Start the built-in TaskTonic HTTP Server
        self.server = HttpServerHandler(port=8080)
        self.to_state('listening')

    def ttse__on_socket_data(self, data):
        # The HttpServerHandler has already converted the raw bytes into a dictionary
        self.log(f"Hub received Webhook trigger: {data}")
        # Note: The HttpServerHandler automatically sends a '200 OK' response back to the client!

    def ttse__on_socket_finished(self):
        self.log("Client disconnected. Hub ready for the next webhook.")


class SmartButton(ttTonic):
    """
    The client: Simulates a physical button that sends HTTP GET requests to the hub.
    """

    def ttse__on_start(self):
        self.log("Smart Button ready. Pressing automatically every 4 seconds...")
        self.press_count = 0
        # Simulate a button press every 4 seconds
        self.tmr = ttTimerRepeat(seconds=4.0, sparkle_back=self.ttsc__press_button)

    def ttsc__press_button(self, info):
        self.press_count += 1
        self.log(f"Button PRESSED! (Press #{self.press_count}) - Setting up HTTP Client...")

        # Because the HttpClientHandler uses 'Connection: close', the most robust
        # method is to create a new handler for each 'click'.
        self.client = HttpClientHandler(host='127.0.0.1', port=8080)
        self.to_state('connecting')

    def ttse_connecting__on_socket_connected(self, addr):
        self.log(f"Connected to Hub at {addr}. Sending HTTP GET request...")
        path = f"/scene/movie_night?press={self.press_count}"
        self.client.ttsc_connected__get(path=path)
        self.to_state('waiting_for_reply')

    def ttse_waiting_for_reply__on_socket_data(self, data):
        # Here we catch the '200 OK' returned by the Hub
        self.log(f"Hub replied with: {data}")

        # Close the TCP socket safely now that we have our answer
        self.client.ttsc__finish()
        self.to_state('idle')

    def ttse__on_socket_finished(self):
        self.log("HTTP Client socket closed cleanly.")


class LocalWebhookDemoApp(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/project/name': 'IoT Webhook Demo',
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': ttLog.FULL,
        }

    def creating_starting_tonics(self):
        # Start both systems. They run perfectly alongside each other on the same Catalyst.
        SmartHomeHub(name="HomeHub")
        SmartButton(name="LivingRoomButton")


if __name__ == "__main__":
    LocalWebhookDemoApp()
