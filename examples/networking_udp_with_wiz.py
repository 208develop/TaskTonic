import json
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot, ttLog

# Import our newly created UDP base class
from TaskTonic.ttTonicStore.ttNetworking import UdpSocketHandler


class WizUdpSocketHandler(UdpSocketHandler):
    """
    A specific UDP handler for JSON payloads, perfect for WiZ bulbs.
    Overrides the conversion methods to translate dicts to JSON bytes and vice versa.
    """

    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')

        # Convert the dictionary to a JSON string, then encode to bytes
        json_str = json.dumps(dict_data, separators=(',', ':'))
        self.log(f"JSON string to send: '{json_str}'")
        return json_str.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        try:
            # Decode bytes to string, then parse the JSON
            json_str = bdata.decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            self.log(f"JSON decode error: {e}")
            return None


class WizTestController(ttTonic):
    """
    The orchestrator Tonic that tests the WiZ bulb.
    It turns the bulb on, waits 3 seconds, turns it off, and finishes.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bulb = None
        self.bulb_port = 38899  # Standard WiZ UDP port

    def ttse__on_start(self):
        self.bulb = self.ledger.formula.at('devices/wiz/#0')
        ip = self.bulb['ip'].v
        bulb = self.bulb['name'].v
        self.log(f"Initializing connection to WiZ bulb '{bulb}' @{ip}")

        # Instantiate the UDP handler as a child of this Tonic
        self.udp = WizUdpSocketHandler()

        # Wait a brief moment to ensure the socket is fully registered
        ttTimerSingleShot(seconds=0.5, name='tm_startup_delay')
        self.to_state('startup_delay')

    def ttse_startup_delay__on_tm_startup_delay(self, tinfo):
        self.to_state('turning_on')

    def ttse_turning_on__on_enter(self):
        self.log("Sending command: Turn ON")

        # WiZ JSON payload to turn the bulb on
        payload = {"method": "setPilot", "params": {"state": True}}
        self.udp.ttsc__send_data(payload, (self.bulb['ip'].v, self.bulb_port))

        # Schedule the next step in 3 seconds (Non-blocking!)
        ttTimerSingleShot(seconds=3.0, name='tm_wait')

    def ttse_turning_on__on_tm_wait(self, tinfo):
        self.to_state('turning_off')

    def ttse_turning_off__on_enter(self):
        self.log("Sending command: Turn OFF")

        # WiZ JSON payload to turn the bulb off
        payload = {"method": "setPilot", "params": {"state": False}}
        self.udp.ttsc__send_data(payload, (self.bulb['ip'].v, self.bulb_port))

        # Wait 1 second to catch any final UDP responses before shutting down
        ttTimerSingleShot(seconds=1.0, name='tm_finish')

    def ttse_turning_off__on_tm_finish(self, tinfo):
        self.log("Test sequence complete. Shutting down.")
        self.finish()

    def ttse__on_udp_data(self, data, addr):
        """
        This event is triggered by the JsonUdpSocketHandler whenever a UDP packet arrives.
        """
        self.log(f"Received response from bulb {addr}: {data}")


class WizTestFormula(ttFormula):
    """
    The Formula to bootstrap the WiZ test application.
    """

    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'WiZ UDP Test'),
            # ('tasktonic/log/to', 'screen'),

            ('tasktonic/log/to', 'ip'),
            ('tasktonic/log/to/target', 'localhost:1767'),

            ('tasktonic/log/default', ttLog.FULL),

            ('devices/wiz/#/name', "LVD-wiz-001"),
            ('devices/wiz/./ip',   "192.168.30.55"), # REPLACE THIS IP WITH THE ACTUAL IP OF YOUR WIZ BULB!
        )

    def creating_starting_tonics(self):
        WizTestController(name="WizTester")


if __name__ == "__main__":
    WizTestFormula()