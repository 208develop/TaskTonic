# Introduction to TaskTonic

Welcome to TaskTonic! TaskTonic is a Python framework for building asynchronous, event-driven applications. It provides
a structured way to manage parallel processes, state machines, and timed events, allowing you to focus on your
application's logic instead of boilerplate concurrency code.

The core philosophy is "Don't call us, we'll call you." Instead of methods being executed immediately, they are queued
as "sparkles" and processed sequentially by an engine called a Catalyst. This ensures thread safety and a predictable,
orderly execution flow.

## Core Concepts

The framework is built on a few key components:

* **Tonic**: The main building block of your application. A Tonic is a stateful worker object that contains logic for a
  specific task.
* **Sparkle**: A specially named method inside a Tonic that represents a single unit of work. Calling a sparkle does *
  *not** run it immediately; it places it on a queue to be executed later.
* **Catalyst**: The engine of the framework. It pulls sparkles from the queue one by one and executes them. It's what
  makes the Tonics "sparkle."
* **Formula**: The entry point of your application. It's the "recipe" that defines which Tonics to create and how to
  start the Catalyst.

## Getting Started: Your First Tonic

Let's create a simple Tonic that prints a message when it starts and then finishes.

A **Tonic's** behavior is defined by its **sparkles**. Sparkles are identified by a special naming convention. For
example, `ttse__on_start` is an event sparkle that the framework runs automatically when the Tonic is first activated.

**1. Create your Tonic:**

```python
# my_app.py
from TaskTonic import ttTonic, ttFormula

class HelloWorldTonic(ttTonic):
    """A simple Tonic to demonstrate the basics."""

    def ttse__on_start(self):
        """
        This is an event sparkle that runs automatically on startup.
        'ttse' stands for 'Tonic Task Sparkle Event'.
        """
        self.log("Hello from the TaskTonic world!")
        # After our work is done, we tell the framework we are finished.
        self.finish()

    def ttse__on_finished(self):
        """This event sparkle runs automatically just before the Tonic shuts down."""
        self.log("Goodbye!")
```

**2. Create the Formula to launch it:**

The **Formula** tells the framework how to build and start your application. You override `creating_starting_tonics` to
create your initial components.

```python
# my_app.py (continued)

class MySimulation(ttFormula):
    """The application launcher."""
    def creating_starting_tonics(self):
        # Create one instance of our HelloWorldTonic.
        # context=-1 means it has no parent.
        HelloWorldTonic(context=-1)

# --- Main execution block ---
if __name__ == "__main__":
    # This single line sets up and starts the entire application.
    MySimulation()
```

When you run `python my_app.py`, the `MySimulation` formula will create a Catalyst, create your `HelloWorldTonic`, and
the Catalyst will execute its `ttse__on_start` sparkle.

## State Machines Made Easy

Tonics are inherently state machines. You don't need to write complex logic to manage states; it's built into the
sparkle naming convention.

* To define a state, add it to your sparkle's name: `ttsc_state_name__sparkle_name`.
* To change state, use the `self.to_state('new_state_name')` method.
* You can use the `ttse__on_enter` and `ttse__on_exit` event sparkles to run code whenever you enter or leave *any*
  state.

Here is a simple example of a light switch:

```python
from TaskTonic import ttTonic

class LightSwitch(ttTonic):

    def ttse__on_start(self):
        self.to_state('off') # Start in the 'off' state

    def ttse__on_enter(self):
        self.log(f"The light is now {self.get_current_state_name().upper()}")

    # Public command to flip the switch
    def ttsc__flip(self):
        """This is a generic command sparkle, not tied to a state."""
        pass # The state-specific versions below will be used instead.

    def ttsc_off__flip(self):
        """When in the 'off' state, 'flip' moves it to 'on'."""
        self.to_state('on')

    def ttsc_on__flip(self):
        """When in the 'on' state, 'flip' moves it to 'off'."""
        self.to_state('off')
```

## Scheduling Events with Timers

You can easily schedule a sparkle to run after a delay or at a regular interval using Timers.

To create a timer, you `bind` it to your Tonic. When the timer expires, it calls a `sparkle_back` function you provide.

```python
from TaskTonic import ttTonic, ttTimerRepeat

class Heartbeat(ttTonic):
    def ttse__on_start(self):
        self.log("Starting heartbeat...")
        # Create a timer that fires every 2 seconds and calls our 'ttsc__beat' sparkle.
        self.bind(ttTimerRepeat, seconds=2, sparkle_back=self.ttsc__beat)

    def ttsc__beat(self, timer_info):
        """This sparkle is called by the timer."""
        self.log("Lub-dub...")
```

## Parent-Child Context

Tonics exist in a hierarchy. A Tonic can create child Tonics using `self.bind()`.

This creates a powerful relationship: if a parent Tonic is finished, it automatically ensures all of its child Tonics
are also finished. This prevents orphaned processes and makes cleanup automatic.

```python
from TaskTonic import ttTonic, ttTimerSingleShot

class Manager(ttTonic):
    def ttse__on_start(self):
        self.log("Manager starting. Hiring a worker...")
        # Create a WorkerTonic as a child of this Manager.
        self.worker = self.bind(WorkerTonic)

        # After 5 seconds, the manager's job is done.
        self.bind(ttTimerSingleShot, seconds=5, sparkle_back=self.finish)

    def ttse__on_finished(self):
        # When the Manager finishes, its child WorkerTonic will also be stopped automatically.
        self.log("Manager finished. The worker is automatically dismissed.")

class WorkerTonic(ttTonic):
    def ttse__on_start(self):
        self.log("Worker ready for duty!")
