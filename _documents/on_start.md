# TaskTonic Framework: Developer Manual

## 1. Introduction

**TaskTonic** is a Python framework designed to manage complex, asynchronous applications with ease. It abstracts away
the complexity of threading by using an event-driven, actor-like model.

### The "Alchemist" Philosophy

The framework uses unique terminology to describe its components:

* **Tonic:** The "worker" or agent (your code).
* **Sparkle:** An atomic unit of work (a method).
* **Catalyst:** The engine that makes the Tonics "sparkle" (executes the work).
* **Formula:** The recipe that defines the application structure.

---

## 2. Core Concepts & Architecture

| Component | Class | Description |
| :--- | :--- | :--- |
| **Formula** | `ttFormula` | The entry point. Initializes the `Ledger` and starts the main `Catalyst`. |
| **Tonic** | `ttTonic` | The primary base class for your logic. It is a state machine that emits Sparkles. |
| **Catalyst** | `ttCatalyst` | The execution engine. It owns a thread and a queue. It pulls sparkles and executes them sequentially. |
| **Ledger** | `ttLedger` | A thread-safe Singleton registry that tracks all active Essences (Tonics/Catalysts). |
| **Essence** | `ttEssence` | The base class for both Tonics and Catalysts, handling identity (ID) and hierarchy. |

### Architecture Flow

1. A **Sparkle** (method call) is placed on the `CatalystQueue`.
2. The **Catalyst** pulls the Sparkle from the queue.
3. The Catalyst executes the method on the target **Tonic**.
4. The Tonic may change its internal **State** or bind new child Tonics.

---

## 3. Getting Started

### 3.1 Minimum Application Structure

You need at least one `ttTonic` (your logic) and one `ttFormula` (to start the app).

```python
from TaskTonic import ttTonic, ttFormula

# 1. Define a Tonic
class HelloWorldTonic(ttTonic):
    def ttse__on_start(self):
        """Called automatically after initialization."""
        self.log("Hello World!")
        self.finish()

    def ttse__on_finished(self):
        self.log("Goodbye!")

# 2. Define the Formula
class MyApp(ttFormula):
    def creating_starting_tonics(self):
        # context=-1 means "Top Level" (no parent)
        HelloWorldTonic(context=-1)

# 3. Run
if __name__ == "__main__":
    MyApp()
```

---

## 4. The Tonic (`ttTonic`)

[cite_start]The `ttTonic` class uses **introspection** to discover its behavior[cite: 115]. You do not register
callbacks manually; you simply name your methods according to the Sparkle convention.

### 4.1 Sparkle Naming Convention

The naming structure is: `prefix[_state]__name`.

* **`ttsc__<name>` (Command):** Public command to *request* action (e.g., `ttsc__process`). Puts a job on the queue.
* **`ttse__<name>` (Event):** Public event handler (e.g., `ttse__on_timer`).
* **`tts__<name>` (Internal):** Internal logic, but still executed via the queue.
* **`_ttss__<name>` (System):** Reserved for framework lifecycle (e.g., `_ttss__finish`).

### 4.2 Built-in State Machine

Every Tonic is a state machine. [cite_start]You can transition states using `self.to_state('new_state')`[cite: 144].

**State Routing:**
If you call `ttsc__next()`, the framework looks for a handler in this order:

1. `ttsc_<current_state>__next` (Specific to current state)
2. `ttsc__next` (Generic fallback)
3. `_noop` (Do nothing)

**Hooks:**

* `ttse__on_enter`: Called when entering *any* state.
* `ttse__on_exit`: Called when leaving *any* state.
* `ttse_<state>__on_enter`: Specific handler for entering `<state>`.

**Example: A Traffic Light**
This example demonstrates how to use `on_enter` and `on_exit` to manage resources (turning lamps on/off) and how to use
timers to drive state transitions automatically.

```python
from TaskTonic import ttTonic, ttTimerSingleShot

class TrafficLight(ttTonic):
    def ttse__on_start(self):
        self.log("Traffic Light System Started")
        self.to_state('red')

    # --- Generic Event: Timer Callback ---
    def ttse__next(self, timer_info):
        """
        This event is triggered by the timer. 
        It doesn't need logic; the state-specific overrides handle the routing.
        """
        pass

    # ================= RED STATE =================
    def ttse_red__on_enter(self):
        self.log("(O) RED LAMP ON")
        # Wait 3 seconds, then trigger the 'next' event
        self.bind(ttTimerSingleShot, 3, sparkle_back=self.ttse__next)

    def ttse_red__on_exit(self):
        self.log("( ) RED LAMP OFF")

    def ttse_red__next(self, info):
        self.to_state('green')

    # ================= GREEN STATE =================
    def ttse_green__on_enter(self):
        self.log("(O) GREEN LAMP ON")
        self.bind(ttTimerSingleShot, 3, sparkle_back=self.ttse__next)

    def ttse_green__on_exit(self):
        self.log("( ) GREEN LAMP OFF")

    def ttse_green__next(self, info):
        self.to_state('orange')

    # ================= ORANGE STATE ================
    def ttse_orange__on_enter(self):
        self.log("(O) ORANGE LAMP ON")
        self.bind(ttTimerSingleShot, 1, sparkle_back=self.ttse__next)

    def ttse_orange__on_exit(self):
        self.log("( ) ORANGE LAMP OFF")

    def ttse_orange__next(self, info):
        self.to_state('red')
```

### 4.3 Hierarchy & Binding (`bind`)

Tonics should strictly form a hierarchy.

* [cite_start]**Creation:** Use `self.bind(Class, **kwargs)` instead of `Class(...)`[cite: 69].
* **Effect:** The created Tonic becomes a **child**.
* **Cleanup:** When a parent calls `finish()`, it automatically finishes all children first.

---

## 5. Services (The Singleton Pattern)

[cite_start]TaskTonic has a built-in Service mechanism handled by the `ttEssence` metaclass[cite: 34].

### 5.1 Defining a Service

Set the `_tt_is_service` attribute to a unique name.

```python
class DatabaseService(ttTonic):
    _tt_is_service = 'db_service'  # Unique Service Name

    def __init__(self, srv_conn_str, **kwargs):
        """Runs ONCE when the FIRST instance is created."""
        super().__init__(**kwargs)
        self.conn_str = srv_conn_str

    def _init_service(self, context, ctxt_user, **kwargs):
        """Runs EVERY TIME the service is bound/requested."""
        self.log(f"Access by {ctxt_user}")
```

### 5.2 Using a Service

Use `bind` just like a normal Tonic.

* [cite_start]**First Call:** Creates the instance, runs `__init__`, runs `_init_service`[cite: 44].
* **Subsequent Calls:** Returns the *existing* instance, runs `_init_service`.

```python
# In a Worker Tonic
self.db = self.bind(DatabaseService, 
                    srv_conn_str="db://...",  # Ignored on subsequent calls
                    ctxt_user="Worker1")      # Processed every time
```

---

## 6. DataShare (`ttDataShare`)

A thread-safe, hierarchical data store (like a Registry/Redux).

### Path Syntax

* Standard: `'user/settings/theme'`
* List Index: `'users/list[0]/name'`
* List Append: `'users/list[]'` (Appends a new item).

### Usage

```python
ds = DataShare()

# Set
ds.set('app/config/version', '1.0')
ds.set('app/logs[]', 'started') # Append to list

# Get (Views)
val = ds.get('app/config')                # Clean Dict (View 0, default)
raw = ds.get('app/config', get_value=1)   # Raw internal dict with {'_value': ...}
val = ds.get('app/config', get_value=2)   # Only the direct value

# Subscribe
def callback(path, old, new): print(f"Changed: {path}")
ds.subscribe('app/config', callback)
```

---

## 7. Timers (`ttTimer`)

Timers are Essences that trigger a callback (`sparkle_back`) after a duration. [cite_start]They must be bound to a
Catalyst (which happens automatically when bound to a Tonic)[cite: 187].

### Timer Types

| Class | Description |
| :--- | :--- |
| `ttTimerSingleShot` | Fires once, then finishes. |
| `ttTimerRepeat` | Fires repeatedly every `period` seconds. |
| `ttTimerPausing` | Repeat timer that can be paused and resumed. |

### Default Callback Behavior

[cite_start]If you do **not** provide the `sparkle_back` argument when binding a timer, the framework automatically
looks for a method named **`ttse__on_timer`** in your Tonic[cite: 189].

**Example:**

Note that the callback method uses the `ttse__` prefix. A timer expiration is an **event** that happens to the Tonic.

```python
# Inside a Tonic

# Option A: Explicit callback
self.bind(ttTimerSingleShot, 2.5, sparkle_back=self.ttse__custom_event)

# Option B: Default callback (calls self.ttse__on_timer)
self.bind(ttTimerSingleShot, 5.0)

def ttse__on_timer(self, info):
    """
    Called automatically by Option B.
    'info' contains dictionary with timer id and name.
    """
    self.log("5 seconds passed (Default Handler)")
```

---

## 8. Logging (`ttLogger`)

[cite_start]TaskTonic has a built-in logging facility controlled by the Formula or specific Tonic settings[cite: 199].

### Log Modes

1. **STEALTH:** No logging (Fastest).
2. **OFF:** Logs only lifecycle events (Start/Finish).
3. **QUIET:** Logs lifecycle + explicit `self.log()` calls.
4. **FULL:** Logs everything, including every Sparkle execution (Trace).

### Configuration (in Formula)

```python
return {
    'tasktonic/log/to': 'screen',           # Output destination
    'tasktonic/log/default': ttLog.FULL,    # Default mode
}
```

---

## 9. Testing: The Distiller (`ttDistiller`)

[cite_start]The `ttDistiller` is a specialized Catalyst designed for testing and debugging[cite: 212]. Instead of
running indefinitely, it runs strictly controlled steps and captures a trace.

### Using the Distiller

In your test Formula, replace `ttCatalyst` with `ttDistiller`.

```python
class TestFormula(ttFormula):
    def creating_main_catalyst(self):
        ttDistiller()  # Use Distiller instead of default Catalyst


# In your test script
recipe = TestFormula()
distiller = recipe.ledger.get_essence_by_id(0)

# Run specific test scenarios
status = distiller.sparkle(
    timeout=5,
    till_state_in=['wait_on_timer']  # Run until a specific state is reached
)

# Analyze the trace
for trace in status['sparkle_trace']:
    print(f"{trace['tonic']}.{trace['sparkle']} -> {trace['at_exit']['state']}")
```