# TaskTonic Framework: Developer Manual

## 1. Introduction

**TaskTonic** is *the* Python framework for realizing concurrency. It allows code to appear as if it is executing
simultaneously. Ideal for scenarios such as:
- TaskTonic is ideal for any scenario where you need to orchestrate numerous independent components:
- Responsive User Interfaces: Keep your UI fluid while performing heavy computations in the background.
- IoT & Sensor Networks: Process a continuous stream of events and measurements from thousands of devices.
- Communication Servers: Manage thousands of concurrent connections for chat applications, game servers, or data
  streams.
- Complex Simulations: Build simulations (e.g., swarm behavior, traffic models) where each entity acts autonomously.
- Asynchronous Data Processing: Create robust data pipelines where information is processed in small, distinct steps.

*...or all of the above, at the same time. That's where the framework's power truly lies.*

### How?
In TaskTonic, this is achieved by breaking down code into small, atomic units that are executed one by one the
framework. Think of them as **sparkles in a tonic**, buzzing with activity. These sparkles are defined within your class
using smart naming conventions. The tonic filters these names and automatically creates the sparkles, making your 
tonic class look clean and tidy.

Also TaskTonic supports you by providing built-in timers, state machines, and clear task hierarchy management.
Additionally, there is a toolbox containing integrations for **PySide6**, smart data storage (`ttStore`), IP
communication, and more. While multithreading is seamlessly supported, it is not strictly necessary to create responsive
applications.

---

## 2. Architecture & Hierarchy

### 2.1 The Foundation: Essence & Ledger

The foundation of TaskTonic is formed by the `ttEssence` class, which, together with the `ttLedger`, handles the
framework's administration.

* **Every task is a subclass of `ttEssence`.**
* **Hierarchy:** The hierarchy is managed here. A `ttEssence` can start a subtask (child) that runs in its own context.
* **Lifecycle:** Terminating a `ttEssence` results in the immediate termination of all its subtasks.

*Note: While `ttEssence` handles structure and hierarchy, it does not yet offer "sparkling."*

### 2.2 The Fun Part: The Tonic

The real magic happens in the next layer: the **`ttTonic`** class. This is where the **sparkles** are added. Within a
`ttTonic`, you can create dynamic code, whether "flat" (sequential) or implemented as a robust State Machine.

### 2.3 The Engine: The Catalyst

The **`ttCatalyst`** is the component that actually makes the system sparkle.

* **Queueing:** When called, sparkles are placed in a queue.
* **Execution:** The Catalyst executes them one by one.

You can work with just the **Main Catalyst** (running in the main thread), but you can also add other Catalysts, each
running in their own thread.

### 2.4 Thread Safety (Concurrency Made Easy)

A crucial feature of TaskTonic is how it handles threading:

1. **Sparkles can be called from *any* thread** (parameters are passed safely).
2. **Sparkles are always executed by the *same* thread** (the one owning the Catalyst).

**Implication:** You never have to think about thread-safe programming *inside* a Tonic, and rarely outside of it.

---

## 3. Quick Start Example

The following example demonstrates the `ttTonic` workflow. Note how `HelloWorld` is a `ttTonic` that chains methods (
sparkles) together.

```python
from TaskTonic import *

# 1. Define the Logic (The Tonic)
class HelloWorld(ttTonic):
    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)

    def ttse__on_start(self):
        """Called automatically by the framework on start."""
        self.tts__hello()

    def tts__hello(self):
        self.log('Hello ')
        self.tts__world()

    def tts__world(self):
        self.log('world, ')
        self.tts__welcome()

    def tts__welcome(self):
        self.log('welcome ')
        self.tts__to()

    def tts__to(self):
        self.log('to ')
        self.tts__tasktonic()

    def tts__tasktonic(self):
        self.log('TaskTonic!')
        self.finish()


# 2. Define the Application Structure (The Formula)
class MyApp(ttFormula):
    def creating_formula(self):
        """Configuration settings."""
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

    def creating_starting_tonics(self):
        """Define which Tonics start immediately."""
        HelloWorld()

# 3. Run
if __name__ == '__main__':
    MyApp()
```

---

## 4. The Tonic in Depth

The `ttTonic` class uses **introspection** to discover its behavior. You do not register callbacks manually; you simply
name your methods according to the Sparkle convention.

### 4.1 Sparkle Naming Convention

The naming structure is: `prefix[_state]__name`.

* **`ttsc__<name>` (Command):** Public command to *request* action (e.g., `ttsc__process`). Puts a job on the queue.
* **`ttse__<name>` (Event):** Public event handler (e.g., `ttse__on_timer`).
* **`tts__<name>` (Internal):** Internal logic, but still executed via the queue.
* **`_ttss__<name>` (System):** Reserved for framework lifecycle (e.g., `_ttss__finish`).

### 4.2 Built-in State Machine

Every Tonic is a state machine. You can transition states using `self.to_state('new_state')`.

**State Routing:**
If you call `ttsc__next()`, the framework looks for a handler in this order:

1. `ttsc_<current_state>__next` (Specific to current state)
2. `ttsc__next` (Generic fallback)
3. `_noop` (Do nothing)

**Hooks:**

* `ttse__on_enter` / `ttse__on_exit`: Called when entering/leaving *any* state.
* `ttse_<state>__on_enter`: Specific handler for entering `<state>`.

---

## 5. Services (The Singleton Pattern)

TaskTonic has a built-in Service mechanism handled by the `ttEssence` metaclass.

### 5.1 Defining and Using a Service

Set the `_tt_is_service` attribute to a unique name. Use `bind` to access it.

* **First Call:** Creates the instance, runs `__init__`, runs `_init_service`.
* **Subsequent Calls:** Returns the *existing* instance, runs `_init_service`.

```python
class DatabaseService(ttTonic):
    _tt_is_service = 'db_service'  # Unique Service Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Runs once per application lifecycle

    def _init_service(self, context, **kwargs):
        # Runs every time a Tonic binds this service
        pass

# Usage in a worker tonic
self.db = self.bind(DatabaseService)
```

---

## 6. Data Store (`ttStore`)

A thread-safe, hierarchical data store service, with notification at data change.

* **Set:** `ds.set('app/config/version', '1.0')`
* **List Append:** `ds.set('users/list[]', 'new_user')`
* **Get:** `val = ds.get('app/config')`
* **Subscribe:** `ds.subscribe('app/config', callback_function)`

---

## 7. Timers (`ttTimer`)

Timers are Essences that trigger a callback (`sparkle_back`) after a duration.

* **`ttTimerSingleShot`**: Fires once.
* **`ttTimerRepeat`**: Fires periodically.

**Default Behavior:**
If no `sparkle_back` is provided, the timer looks for `ttse__on_timer` in the parent Tonic.

```python
# Default callback (calls self.ttse__on_timer)
self.bind(ttTimerSingleShot, 5.0)

def ttse__on_timer(self, info):
    self.log("5 seconds passed")
```

---

## 8. Logging (`ttLogger`)

Logging is controlled via the Formula.

* **STEALTH:** No logging.
* **OFF:** Only lifecycle events.
* **QUIET:** Lifecycle + explicit `self.log()`.
* **FULL:** Logs every Sparkle execution (Trace).

---

## 9. Testing: The Distiller (`ttDistiller`)

The `ttDistiller` is a specialized Catalyst for testing. Instead of running indefinitely, it executes strictly
controlled steps and captures a full trace of sparkles and state changes for analysis.