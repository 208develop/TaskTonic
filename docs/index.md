# Welcome to TaskTonic 🧪

<img src="assets/tasktonic-impression.png" align="left" width="350" style="margin-right: 20px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Concept">

**A Refreshing Approach to Python Concurrency.**

TaskTonic is designed to eliminate the headaches of traditional python concurrency. No more wrestling with complex `asyncio` loops, unpredictable threads, or deadlocking locks. 

## Philosophy & Metaphor

The core philosophy is based on the **Tonic**. Think of your running application as a glass of tonic. It comes to life
through **Sparkles**, the **bubbles** rising in a liquid.

* **The Flow:** Code is executed in small, atomic units called *Sparkles*.
* **The Fizz:** When these Sparkles flow continuously, the application "fizzes" with activity. It feels like a single,
  cohesive whole, even though it may be performing multiple logical processes simultaneously.
* **The Rule:** A Sparkle must be short-lived. If one bubble takes too long to rise (blocking code), the flow stops, and
  the fizz goes flat. In practice, this is rarely an issue, as most software processes are reactive chains of short
  events.

<div style="clear: both;"></div>

This architecture allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) without
the race conditions and headaches of traditional multi-threading.

## Use Cases

TaskTonic is ideal for any scenario where you need to orchestrate numerous independent components:

- Responsive User Interfaces: Keep your UI fluid while performing heavy computations in the background.
- IoT & Sensor Networks: Process a continuous stream of events and measurements from thousands of devices.
- Communication Servers: Manage thousands of concurrent connections for chat applications, game servers, or data streams.
- Complex Simulations: Build simulations (e.g., swarm behavior, traffic models) where each entity acts autonomously.
- Asynchronous Data Processing: Create robust data pipelines where information is processed in small, distinct steps.

*...or all of the above, at the same time. That's where the framework's power truly lies.*




---

## Hello World, the TaskTonic way

Ok, Sparkling tonics are fun. This is the reality check. Here is a real example of how simple and structured a TaskTonic application is. Notice how clean the state transitions (`to_state`) and timer events (`on_tm_step`) are handled!

```python
from TaskTonic import *

class HelloWorld(ttTonic):
    def __init__(self, interval=1.5):
        super().__init__()
        self.interval = interval

    def ttse__on_start(self):
        ttTimerRepeat(seconds=self.interval, name='tm_step')
        self.to_state('hello')

    def ttse_hello__on_enter(self):
        self.log('Hello world')

    def ttse_hello__on_tm_step(self, tinfo):
        self.to_state('welcome')

    def ttse_welcome__on_enter(self):
        self.log('Welcome to TaskTonic')

    def ttse_welcome__on_tm_step(self, tinfo):
        self.to_state('ending')

    def ttse_ending__on_tm_step(self, tinfo):
        self.ttsc__finish()

class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'HELLO WORLD'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),
        )

    def creating_starting_tonics(self):
        HelloWorld(1.5)
        # HelloWorld(.2) # you can try a second tonic!!!

if __name__ == '__main__':
    myApp()
```