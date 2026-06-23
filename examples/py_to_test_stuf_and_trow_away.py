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


# import queue
# import time
# from TaskTonic import ttTonic, ttFormula, ttCatalyst, ttLog, ttLedger
#
# """
# ================================================================================
# TaskTonic Architecture Note: Catalyst Queue Optimization
# ================================================================================
#
# What this benchmark does:
# This test evaluates the absolute throughput of the TaskTonic framework's core
# execution loop. It simulates a high-stress environment by firing hundreds of
# thousands of sequential 'sparkles' (atomic work orders) in a continuous chain.
# It measures the total time required for the `ttCatalyst` to process these items
# through its central queue, including the overhead of context switching and
# stack management.
#
# Why this was tested:
# As TaskTonic scales to handle heavy concurrent workloads—such as high-frequency
# IoT sensor streams or complex UI state changes—the latency of the Catalyst's
# internal queue becomes a primary performance bottleneck. The goal was to determine
# if rewriting the core execution loop in C++ was necessary to achieve higher
# throughput, or if native Python optimizations could suffice.
#
# The Result & Architectural Decision:
# This benchmark compares Python's standard `queue.Queue` against `queue.SimpleQueue`.
# The standard `Queue` carries internal locking overhead to support task tracking
# methods like `task_done()` and `join()`. Because the `ttCatalyst` execution
# loop simply relies on continuous `.put()` and `.get()` operations, this extra
# thread-tracking overhead was entirely redundant.
#
# The results proved that `queue.SimpleQueue`—a highly optimized, C-level
# unbounded FIFO queue—processes sparkles significantly faster (yielding a 25%
# to 40% performance increase).
#
# Conclusion:
# The data from this benchmark forced the architectural decision to abandon
# `queue.Queue`. `queue.SimpleQueue` is now the permanent, standard engine for
# all `ttCatalyst` implementations, providing a massive, lock-free performance
# boost without requiring any C++ extensions.
# ================================================================================
# """
#
# class SimpleQueueCatalyst(ttCatalyst):
#     def new_catalyst_queue(self):
#         # Override the queue creation to use the faster SimpleQueue
#         return queue.SimpleQueue()
#
#
# class StdQueueCatalyst(ttCatalyst):
#     def new_catalyst_queue(self):
#         # Explicitly use the standard Queue for comparison
#         return queue.Queue()
#
#
# class BenchTonic(ttTonic):
#     def __init__(self, items=100000, **kwargs):
#         # Prevent double execution due to potential multiple inheritance
#         if getattr(self, '_tt_tonic_init_done', False):
#             return
#
#         self._tt_tonic_init_done = True
#         super().__init__(**kwargs)
#         self.total_items = items
#         self.start_time = 0
#
#     def ttse__on_start(self):
#         self.start_time = time.perf_counter()
#         # Start the chain reaction
#         self.tts__chain(self.total_items)
#
#     def tts__chain(self, count):
#         if count > 0:
#             self.tts__chain(count - 1)
#         else:
#             end_time = time.perf_counter()
#             duration = end_time - self.start_time
#             print(f"Processed {self.total_items:,} sparkles in {duration:.4f} seconds.")
#             print(f"Speed: {self.total_items / duration:,.0f} sparkles/sec")
#             self.finish()
#
#
# def run_benchmark(catalyst_class, items):
#     # Reset the ledger to allow a clean startup for the next formula run
#     ttLedger._instance = None
#     ttLedger._singleton_init_done = False
#
#     class BenchFormula(ttFormula):
#         def creating_formula(self):
#             return (
#                 ('tasktonic/project/name', 'Benchmark'),
#                 # Turn off logging completely to prevent I/O bottlenecks
#                 ('tasktonic/log/to', 'off'),
#                 ('tasktonic/log/default', ttLog.STEALTH),
#             )
#
#         def creating_main_catalyst(self):
#             # Inject the specific catalyst we want to test
#             catalyst_class(name='tt_main_catalyst')
#
#         def creating_starting_tonics(self):
#             BenchTonic(items=items)
#
#     # Start the application
#     BenchFormula()
#
#
# if __name__ == "__main__":
#     items_to_process = 200_000
#     print(f"Benchmarking TaskTonic with {items_to_process:,} sequential sparkles...\n")
#
#     print("Testing with standard queue.Queue...")
#     run_benchmark(StdQueueCatalyst, items_to_process)
#
#     print("\nTesting with queue.SimpleQueue...")
#     run_benchmark(SimpleQueueCatalyst, items_to_process)