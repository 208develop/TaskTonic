# traffic_light_simulation.py

from TaskTonic import *


class TrafficLight(ttTonic):
    """
    A Tonic that simulates a traffic light state machine.
    It cycles through red, green, and yellow states using timers.
    """

    def __init__(self, context, red_duration=5, green_duration=5, yellow_duration=2):
        # Store the duration for each light state
        self.durations = {
            'red': red_duration,
            'green': green_duration,
            'yellow': yellow_duration
        }
        self.timer = None
        super().__init__(context)

    def ttse__on_start(self):
        """
        Event sparkle: Called automatically when the Tonic starts.
        We begin the cycle by transitioning to the 'red' state.
        """
        self.log("Traffic light is starting up...")
        self.to_state('red')
        # self.timer = self.bind(ttTimerPausing, 2, sparkle_back=self.ttsc__change_state)

    def ttse__on_enter(self):
        """
        Event sparkle: Called automatically when entering ANY state.
        This is the perfect place to turn the light 'ON' and start the timer for the state's duration.
        """
        current_state = self.get_current_state_name()
        duration = self.durations.get(current_state, 1)  # Default to 1 sec if not found

        self.log(f"Light is now ON: {current_state.upper()}")

        # Create a single-shot timer that will fire when this state should end.
        # Its callback will trigger the state change.
        self.bind(ttTimerSingleShot, seconds=duration, sparkle_back=self.ttsc__change_state)
        # self.timer.pause_ends()

    def ttse__on_exit(self):
        """
        Event sparkle: Called automatically when leaving ANY state.
        This is where we turn the light 'OFF'.
        """
        current_state = self.get_current_state_name()
        self.log(f"Light is now OFF: {current_state.upper()}")

    # --- State Transition Sparkles ---
    # These are called by the timer when a state's duration is over.

    def ttsc_red__change_state(self, timer_info):
        """Command sparkle: When in 'red' state, the timer expiration triggers a move to 'green'."""
        self.to_state('green')

    def ttsc_green__change_state(self, timer_info):
        """Command sparkle: When in 'green' state, the timer expiration triggers a move to 'yellow'."""
        self.to_state('yellow')

    def ttsc_yellow__change_state(self, timer_info):
        """Command sparkle: When in 'yellow' state, the timer expiration triggers a move back to 'red'."""
        self.to_state('red')  # Loop back to the beginning
        self.finish()

    def ttse__on_finished(self):
        """Event sparkle: Called automatically when the Tonic is finished."""
        self.log("Traffic light is shutting down.")


class TrafficLightSimulation(ttFormula):
    """
    The Formula to set up and launch the traffic light simulation.
    """

    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    # def creating_main_catalyst(self):
    #     pass

    def creating_starting_tonics(self):
        """
        This method is called by the framework to create the initial Tonics.
        We create one instance of our TrafficLight.
        """
        TrafficLight(context=-1, red_duration=5, green_duration=5, yellow_duration=2)


# --- Main execution block ---
if __name__ == "__main__":
    # This creates an instance of our Formula, which automatically
    # sets up the ledger, creates the catalyst, creates our TrafficLight tonic,
    # and starts the main execution loop.
    TrafficLightSimulation()