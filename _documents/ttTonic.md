# Documentation: The ttTonic Class

This document describes the functionality, syntax, and usage of the refactored `ttTonic` class within the
TaskTonic framework.

---

## 1. Introduction and Core Concepts

The `ttTonic` is the base class for creating active, stateful (if you want) components within a `Catalyst`-driven system.
Its purpose is to break down complex logic into small, manageable steps (**Sparkles**) that are executed
asynchronously via a shared queue.

### Core Concepts

* **Context**: A `tonic` runs in the `context` the controlling `tonic` bound by the `bind` method. 
  The context controls the bound `tonic` by sending commands. Reactions, or events, are send back to inform the
  status or send data. `'Tonics'`, started from the `formula` (from main) don't have a context. **Finishing** a `tonic` will
  result in finishing the whole chain of `tonics` in the context.

* **Catalyst**: The `Catalyst` makes the `Tonic` sparkle. It manages the main execution queue
  for the lifecycle of all connected `Tonic` instances. 
  When a `Tonic` is initialized, it inherits the context `Catalyst`.

* **Catalyst Queue**: A `Tonic` uses the queue provided by its `Catalyst`. When a
  sparkle is called, a "work order" is placed on this shared queue. The `Catalyst` is responsible for
  processing this queue.

* **Sparkle**: A `Sparkle` is a Python method within a `Tonic` class that performs a small, specific task. The
  method's name follows a strict syntax to define its behavior and type.

* **State Machine**: A `Tonic` can function as a state machine. Sparkles can be linked to a specific *state*,
  which changes the `Tonic`'s behavior depending on the active state.

* **Executor Modes**: The `Tonic`'s internal sparkle executor (`_execute_sparkle`) is dynamic. It starts in a
  placeholder state, switches to normal execution mode (`__exec_sparkle`) after initialization, and switches to
  a system-only mode (`__exec_system_sparkle`) during shutdown.

---

## 2. The Lifecycle of a Tonic

A `Tonic` now has a managed lifecycle, from startup to graceful shutdown.

1. **Initialization (`__init__`)**: Create a Tonic by using the bind method to create context. Only the starting 
   Tonics in the formula are started without binding. When the `Tonic` is created, it informs its `Catalyst`, 
   and runs `_sparkle_init()` to discover all its sparkles and build its internal logic.
2. **Startup**: Immediately after initialization, the `ttse__on_start` sparkle is called directly to 
   perform setup logic. The default state can be activated by calling `to_state`.
3. **State startup**: Every time the `state` changes the state `on_enter` sparkle is called, the `on_exit` sparkle is
   called on the next state transition.
3. **Normal Operation**: The `Tonic` is now active. Its `__exec_sparkle` method is used by the `Catalyst` to
   process any work orders from the queue.
4. **Shutdown Request (`finish()`)**: An external entity calls the `finish()` method on the `Tonic` to
   initiate a graceful shutdown.
5. **Finishing Mode**: The `Tonic` enters its shutdown sequence. The executor switches to `__exec_system_sparkle`,
   which ignores all regular sparkles and only processes system-level cleanup sparkles (`_ttss__`).
6. **Termination (`finished()`)**: After all cleanup is done, the `Tonic` calls its `finished()` method to
   notify the `Catalyst` that it has completely terminated.

---

## 3. Sparkle Syntax

The `_sparkle_init` method scans for methods based on the following conventions.

### Sparkle Prefixes

* `ttsc__<command>`
    * **C** = Command. A public command to initiate a task. Places a work order on the `catalyst_queue`.
* `ttse__<event>`
    * **E** = Event. A public method for reacting to an event. Places a work order on the `catalyst_queue`.
* `tts__<sparkle>`
    * **S** = Sparkle. An internal action. When called, it places a work order on the `catalyst_queue`.
* `_tts__<sparkle>`
    * A "private" internal action that also queues a work order.
* `_ttss__<sparkle>`
    * **SS** = System Sparkle. A system-level action. Don't use this for basic functionality, but just for developing
      special TaskTonic features with automated sparkles.
      These are the *only* sparkles that are still executed when the `Tonic` is in its shutdown (`finishing`) mode.

### State-Specific Sparkles

Any of the above prefixes can be combined with a state to make them state-dependent.
Example: `ttsc_waiting__process`.

### Fallback Behavior

When a command is called, the framework searches for an implementation in this order:

1. **Specific**: `ttsc_<current_state>__<command>`
2. **Generic**: `ttsc__<command>` (used if the specific version does not exist)
3. **Nothing**: `_noop` (if neither exists)

### Lifecycle Handlers

These are special, reserved sparkles called automatically by the framework.

* `_ttss__on_start()`: System-level startup hook. Called directly in `__init__`.
* `ttse__on_start()`: User-level startup hook. Called directly in `__init__`.
* `ttse__on_enter()`: A global handler called directly every time the `Tonic` *enters* any state.
* `ttse__on_exit()`: A global handler called directly every time the `Tonic` *exits* any state.
* `ttse__on_finished()`: User-level shutdown hook. Called when `finish()` is initiated.
* `_ttss__on_finished()`: System-level shutdown hook for final cleanup.

---

## 4. Key Methods

* `__init__(self, context, ...)`: Initializes the `Tonic` and binds it to the `Catalyst` provided in the `context`.
* `to_state(self, state)`: Requests a state transition. The change is processed after the current sparkle
  finishes. A special value of `-99` can be passed to immediately stop the state machine.
* `finish(self)`: Initiates the graceful shutdown sequence for the `Tonic`.

---

## 5. Usage Example

This example shows a simple `FileProcessor` tonic that waits for a file, processes it, and then finishes.

```python
# --- Definition ---
class FileProcessor(ttTonic):
    def __init__(self, context, name="FileProcessor"):
        super().__init__(context, name=name)
        self.log("File processor is ready.")
        self.to_state('waiting')
        # internals
        self.filename = None
        self.result = ''

    # --- Lifecycle Handlers ---
    def ttse__on_start(self):
        self.log("Event: Tonic has started.")

    def ttse__on_enter(self):
        self.log(f"GLOBAL: Now entering state '{self.get_current_state_name()}'.")
        
    def ttse__on_finished(self):
        self.log("Event: Tonic has received finish command and is cleaning up.")

    # --- Sparkles ---
    def ttsc_waiting__process_file(self, filename):
        """This command is only available in the 'waiting' state. Start processing by calling ttsc__process_file """
        self.filename = filename
        self.log(f"Starting to process file: {filename}")
        self.to_state('processing')

    def _tts_processing__step(self):
        """ Processing done in the state machine."""
        self.log("...processing step complete...")
        self.result += 'processed '
        self.to_state('finished')
        
    def ttsc_finished__cleanup(self):
        """A command to gracefully shut down the tonic."""
        self.log("Cleanup complete. Finishing the tonic.")
        self.context.ttse__on_file_processed(self.result)  # inform context that job is done en returns data
        self.finish()
    
class DoingSomething(ttTonic):
    def ttse__on_start(self):
        self.processor = self.bind(FileProcessor)
        
    def ttse__on_pressed_button(self):
        self.processor.ttsc__process_file('c:/setting.json')

    def ttse__on_file_processed(self, result):
        self.log(f'Result: {result}')


```

---
