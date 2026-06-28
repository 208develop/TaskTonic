from TaskTonic import ttTonic, ttFormula, ttLog, ttTimerSingleShot
# Adjust this import to your exact project structure
from TaskTonic.ttTonicStore.ttNetworking.ttHttpSockets import HttpClientHandler


class ShellyController(ttTonic):
    """
    Controls a local Shelly device via HTTP GET requests.
    Turns it ON, waits 1 second asynchronously, and turns it OFF.
    """

    def ttse__on_start(self):
        self.shelly_ip = '192.168.30.50'

        # Note: If your Shelly is configured as a relay instead of a light,
        # change '/light/0' to '/relay/0'.
        self.api_on = "/light/0?turn=on"
        self.api_off = "/light/0?turn=off"

        self.log(f"Starting Shelly control sequence for {self.shelly_ip}")
        self.ttsc__turn_on()

    # --- PHASE 1: TURN ON ---

    def ttsc__turn_on(self):
        self.log("Initiating ON command...")
        self.client = HttpClientHandler(host=self.shelly_ip, port=80, name="ShellyClientON")
        self.to_state('turning_on')

    def ttse_turning_on__on_socket_connected(self, addr):
        self.log("Connected to Shelly. Sending ON request.")
        self.client.ttsc_connected__get(path=self.api_on)
        self.to_state('waiting_on_reply')

    def ttse_waiting_on_reply__on_socket_data(self, data):
        self.log("Shelly turned ON successfully.")

        # Close the socket so we don't hog OS resources
        self.client.ttsc__finish()

        # Start the asynchronous 1-second delay
        self.to_state('delaying')
        self.log("Waiting exactly 1.0 second...")
        ttTimerSingleShot(seconds=1.0, sparkle_back=self.ttsc__turn_off)

    # --- PHASE 2: TURN OFF ---

    def ttsc__turn_off(self, info=None):
        # This method is called automatically by the timer
        self.log("Timer expired! Initiating OFF command...")
        self.client = HttpClientHandler(host=self.shelly_ip, port=80, name="ShellyClientOFF")
        self.to_state('turning_off')

    def ttse_turning_off__on_socket_connected(self, addr):
        self.log("Connected to Shelly again. Sending OFF request.")
        self.client.ttsc_connected__get(path=self.api_off)
        self.to_state('waiting_off_reply')

    def ttse_waiting_off_reply__on_socket_data(self, data):
        self.log("Shelly turned OFF successfully.")
        self.client.ttsc__finish()
        self.log("Sequence complete. Going to idle.")
        self.to_state('idle')

    def ttse__on_socket_finished(self):
        # Optional: Catch the graceful socket closures just to keep the log clean
        pass


class ShellyDemoApp(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/project/name': 'Shelly Blink Sequence',
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': ttLog.FULL,
        }

    def creating_starting_tonics(self):
        ShellyController(name="LivingRoomShelly")


if __name__ == "__main__":
    ShellyDemoApp()

