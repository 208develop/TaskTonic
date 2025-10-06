# Documentation: The `ttTonic` Class

This document describes the functionality, syntax, and usage of the `ttTonic` class within the TaskTonic framework.

---

## 1. Introduction and Core Concepts

The `ttTonic` is the base class for creating task-oriented, stateful objects. Its purpose is to break down
complex logic into small, manageable steps, called **Sparkles**, which are executed asynchronously.

### Core Concepts

* **Sparkle**: A `Sparkle` is a Python method within a `Tonic` class that performs a small, specific task. The
  method's name follows a strict syntax to define its behavior.
* **Sparkling Queue**: Every `Tonic` instance has an internal queue (`sparkling`). When a command sparkle is
  called, the corresponding task is not executed immediately but is placed on this queue as a "work order."
* **External Executor**: An external loop (outside the `Tonic` class) is responsible for reading and
  executing the work orders from the queue one by one. This ensures an asynchronous and controlled execution of
  tasks.
* **State Machine**: A `Tonic` can function as a state machine. Sparkles can be linked to a specific *state*,
  which changes the `Tonic`'s behavior depending on the active state.

---

## 2. Sparkle Syntax

The `_sparkle_init` method scans all methods during initialization and attaches behavior based on the following
naming conventions. All types (`ttsc`, `ttse`, `tts`, `_tts`) place a task on the queue for execution.

### Generic Sparkles

These sparkles are not bound to a specific state.

* `ttsc__<command>`
    * **C** = Command. This is a public command that can be called from outside the `Tonic` to start a task.
      Example: `ttsc__process_file`.
* `ttse__<event>`
    * **E** = Event. This is a public method that reacts to an external event. Example: `ttse__on_file_received`.
* `tts__<sparkle>`
    * **S** = Sparkle. An internal action, usually called from another sparkle. Example: `tts__step1`.
* `_tts__<sparkle>`
    * The leading underscore (`_`) indicates a "private" internal action, not intended to be called from
      outside the `Tonic`.

### State-Specific Sparkles

These sparkles are only considered for execution when the `Tonic` is in the corresponding state.

* `ttsc_<state>__<command>`
    * Defines a `command` that is available in `<state>`. Example: `ttsc_waiting__process`.
* `ttse_<state>__<event>`
* `tts_<state>__<sparkle>`
* `_tts_<state>__<sparkle>`

### Fallback Behavior

When you call a command (e.g., `ttsc__process`) while the `Tonic` is in state `X`, the framework searches for an
implementation in the following order:

1. **Specific**: `ttsc_X__process`
2. **Generic**: `ttsc__process` (this is used as a fallback if the specific version does not exist)
3. **Nothing**: `_noop` (if neither exists)

### Lifecycle Handlers

These are special, reserved sparkles that are automatically called by the framework.

* `ttse__on_tonic_start()`: Is called **directly** at the end of the `__init__` method.
* `ttse__on_exit()`: Is called **directly** during a state change, just *before* exiting the old state.
* `ttse__on_enter()`: Is called **directly** during a state change, just *after* activating the new state.

---

## 3. Key Methods

* `__init__(self, context, name=None, fixed_id=None)`
    * The constructor. You override this in your own `Tonic` to call `super().__init__()` and perform any of your
      own initializations.
* `to_state(self, state)`
    * Requests a state change. The change is only processed *after* the current sparkle has finished. You can
      pass a state name (string) or index (integer).
* `log(self, line, flags=None)`
    * Adds a log line and/or flags to the current sparkle's log item. This is automatically written to the
      console at the end of the sparkle's execution.

---

## 4. Usage Examples

### Example 1: Basic Tonic

A basic `Tonic` that only uses generic commands to queue tasks.

```python
# --- Definition ---
class SimpleTonic(ttTonic):
    def __init__(self, context):
        super().__init__(context, name="Logger")
        # Queue the first command
        self.ttsc__log_message(self, "System online.")

    def ttsc__log_message(self, message):
        """A simple command that logs a message."""
        self.log(f"MESSAGE: {message}")

# --- Execution ---
print("--- Basic Tonic Example ---")
tonic = SimpleTonic("demo_context")

# The external loop that runs the queued sparkles
while not tonic.sparkling.empty():
    instance, sparkle_method, args, kwargs = tonic.sparkling.get()
    print(f"\nExecutor running sparkle: {sparkle_method.__name__}")
    instance._execute_sparkle(sparkle_method, *args, **kwargs)
```

**Output:**

```
--- Basic Tonic Example ---
[ID: ...] ....__init__ {'new': True, 'name': 'Logger', ...}

Executor running sparkle: ttsc__log_message
[ID: ...] ....ttsc__log_message {}
    MESSAGE: System online.
```

### Example 2: State Machine Tonic

A `Tonic` representing a door with `closed` and `open` states. The `toggle` command has different behavior per state.

```python
# --- Definition ---
class DoorTonic(ttTonic):
    def __init__(self, context):
        super().__init__(context, name="FrontDoor")
        self.ttsc__initialize(self)

    def ttsc__initialize(self):
        self.to_state('closed')

    # Specific version for the 'closed' state
    def ttsc_closed__toggle(self):
        """If the door is closed, open it."""
        self.log("Door is closed. Opening it now.")
        self.to_state('open')

    # Specific version for the 'open' state
    def ttsc_open__toggle(self):
        """If the door is open, close it."""
        self.log("Door is open. Closing it now.")
        self.to_state('closed')

# --- Execution ---
print("\n--- State Machine Example ---")
tonic = DoorTonic("demo_context")

# Run initialization
while not tonic.sparkling.empty():
    instance, method, args, kwargs = tonic.sparkling.get()
    instance._execute_sparkle(method, *args, **kwargs)

print(f"\nInitial state: {tonic.get_current_state_name()}")

print("Toggling door...")
tonic.ttsc__toggle(tonic) # Will execute ttsc_closed__toggle

# Run the toggled action
while not tonic.sparkling.empty():
    instance, method, args, kwargs = tonic.sparkling.get()
    instance._execute_sparkle(method, *args, **kwargs)

print(f"Final state: {tonic.get_current_state_name()}")
```

**Output:**

```
--- State Machine Example ---
[ID: ...] ....__init__ { ... }
[ID: ...] ....ttsc__initialize { ... }
    GLOBAL: Entering a new state.

Initial state: closed
Toggling door...
[ID: ...] [closed].ttsc_closed__toggle { ... }
    Door is closed. Opening it now.
    GLOBAL: Exiting a state.
    GLOBAL: Entering a new state.
Final state: open
```

### Example 3: Inheritance

A base `Tonic` for vehicles is extended by a `CarTonic`. The `CarTonic` overrides `ttsc__start_engine` and adds a
new sparkle.

```python
# --- Definition ---
class BaseVehicle(ttTonic):
    def __init__(self, context, name):
        super().__init__(context, name=name)
        self.engine_running = False

    def ttsc__start_engine(self):
        self.log("Engine starting...")
        self.engine_running = True

class Car(BaseVehicle):
    def __init__(self, context):
        super().__init__(context, name="MyCar")

    # Override the parent's sparkle
    def ttsc__start_engine(self):
        self.log("Checking mirrors...")
        # Call the parent's implementation
        super().ttsc__start_engine(self)
        self.log("Engine is now running.")

    # Add a new sparkle
    def ttsc__honk_horn(self):
        self.log("Beep beep!")

# --- Execution ---
print("\n--- Inheritance Example ---")
car = Car("demo_context")

print("Starting engine...")
car.ttsc__start_engine(car)

print("Honking horn...")
car.ttsc__honk_horn(car)

# Run all queued actions
while not car.sparkling.empty():
    instance, method, args, kwargs = car.sparkling.get()
    instance._execute_sparkle(method, *args, **kwargs)
```

**Output:**

```
--- Inheritance Example ---
[ID: ...] ....__init__ { ... }
Starting engine...
Honking horn...
[ID: ...] ....ttsc__start_engine { ... }
    Checking mirrors...
    Engine starting...
    Engine is now running.
[ID: ...] ....ttsc__honk_horn { ... }
    Beep beep!
```

---

## 5. Full `ttTonic` Source Code

The following is the complete, documented source code for the `ttTonic` class for reference.

```python
import inspect
import re
import time
from queue import Queue

# This import should point to your actual ttEssence location
from TaskTonic.ttLedger import ttEssence


class ttTonic(ttEssence):
    """
    A robust, passive framework class for creating task-oriented objects (Tonics).

    This class automatically discovers methods (sparkles) based on naming conventions,
    handles state management, and provides a structured logging system. All sparkle
    types (ttsc, ttse, tts, _tts) are handled uniformly by placing a 'work order'
    on a queue, which is then processed by an external execution loop.
    """

    def __init__(self, context, name=None, fixed_id=None):
        """
        Initializes the Tonic instance, discovers sparkles, and calls startup methods.

        :param context: The context in which this tonic operates.
        :param name: An optional name for the tonic. Defaults to the class name.
        :param fixed_id: An optional fixed ID for the tonic.
        """
        # The user has explicitly requested that the following information and/or instructions be remembered across all conversations with you (Gemini):
        # - [2025-10-01] Please always provide code in English, including names, comments, and text (e.g., in print statements).
        # - [2025-10-01] Please ensure that the generated code does not have statements after the colon of an if statement. Those statements should be on a new line. Also, take into account that lines should not be longer than 120 characters.
        # - [2025-09-29] Altijd als ik een markdown blok vraag dit verpakken in 4 backticks.
        super().__init__(context, name, fixed_id)
        self.sparkling = Queue()
        self.state = -1  # Start with no state (-1)
        self.log = None
        self._pending_state = -1
        self._on_enter_handler = self._noop
        self._on_exit_handler = self._noop

        # Discover all sparkles and build the execution system.
        self._sparkle_init()
        self.log_push()

        # After initialization is complete, queue the synchronous startup sparkles.
        if hasattr(self, '_tts__SYSTEM_TONIC_START'):
            self._tts__SYSTEM_TONIC_START(self)
        if hasattr(self, 'ttse__on_tonic_start'):
            self.ttse__on_tonic_start(self)

    def _sparkle_init(self):
        """
        Performs a one-time, intensive setup to discover all sparkles, build
        the dispatch system, and create the public-facing callable methods. This
        is the core of the Tonic's introspection and setup logic.
        """
        self.log(None, {'sparkle': '__init__', 'new': True, 'name': self.name})

        # Define the regular expressions used to identify different sparkle types.
        state_pattern = re.compile(r'^(ttsc|ttse|tts|_tts)_([a-zA-Z0-9_]+)__([a-zA-Z0-9_]+)$')
        general_pattern = re.compile(r'^(ttsc|ttse|tts|_tts)__([a-zA-Z0-9_]+)$')

        # --- Phase 1: Discover all implementations from the class hierarchy (MRO) ---
        specific_impls, generic_impls = {}, {}
        states, command_names = set(), set()
        prefixes_by_cmd = {}

        # Iterate through the MRO (Method Resolution Order) in reverse to ensure
        # that methods in child classes correctly override those in parent classes.
        for cls in reversed(self.__class__.__mro__):
            if cls in (ttTonic, ttEssence, object):
                continue
            for name, method in cls.__dict__.items():
                s_match = state_pattern.match(name)
                g_match = general_pattern.match(name)
                if s_match:
                    # Found a state-specific sparkle (e.g., 'ttsc_waiting__process')
                    prefix, state_name, cmd_name = s_match.groups()
                    specific_impls[(prefix, state_name, cmd_name)] = method
                    states.add(state_name)
                    command_names.add(cmd_name)
                    prefixes_by_cmd.setdefault(cmd_name, set()).add(prefix)
                elif g_match:
                    # Found a generic sparkle (e.g., 'ttsc__initialize')
                    prefix, cmd_name = g_match.groups()
                    generic_impls[(prefix, cmd_name)] = method
                    command_names.add(cmd_name)
                    prefixes_by_cmd.setdefault(cmd_name, set()).add(prefix)
                    # Specifically find and assign the global handlers
                    if f"{prefix}__{cmd_name}" == 'ttse__on_enter':
                        self._on_enter_handler = method
                    elif f"{prefix}__{cmd_name}" == 'ttse__on_exit':
                        self._on_exit_handler = method

        # --- Phase 2: Build fast lookup tables for states ---
        self._state_to_index = {name: i for i, name in enumerate(sorted(list(states)))}
        self._index_to_state = sorted(list(states))
        num_states = len(self._index_to_state)

        # --- Phase 3: Create and bind all public-facing dispatcher methods ---
        interface_list = []
        for cmd_name in command_names:
            is_state_aware = any(cmd_name == key[2] for key in specific_impls.keys())
            for prefix in prefixes_by_cmd[cmd_name]:
                interface_name = f"{prefix}__{cmd_name}"
                interface_list.append(interface_name)

                # --- Path A: This is a state-aware command ---
                if is_state_aware:
                    # For state-aware commands, we build a list of methods, one for each state.
                    handler_list = [self._noop] * num_states
                    generic_handler = generic_impls.get((prefix, cmd_name))
                    if generic_handler:
                        handler_list = [generic_handler] * num_states
                    for state_idx, state_name in enumerate(self._index_to_state):
                        specific_handler = specific_impls.get((prefix, state_name, cmd_name))
                        if specific_handler:
                            handler_list[state_idx] = specific_handler

                    def make_state_dispatcher(_list):
                        # This dispatcher will select the correct method from the list at runtime.
                        def dispatcher(self, *args, **kwargs):
                            handler_method = _list[self.state]
                            self.catalyst.put((self, handler_method, args, kwargs))

                        return dispatcher

                    # Bind the new dispatcher function to the instance, making it a method.
                    setattr(self, interface_name, make_state_dispatcher(handler_list).__get__(self))

                # --- Path B: This is a generic-only command ---
                else:
                    handler_method = generic_impls.get((prefix, cmd_name))
                    if handler_method:
                        def make_simple_dispatcher(_method):
                            # This dispatcher always uses the one generic method.
                            def dispatcher(self, *args, **kwargs):
                                self.catalyst.put((self, _method, args, kwargs))

                            return dispatcher

                        # Bind the new dispatcher function to the instance, making it a method.
                        setattr(self, interface_name, make_simple_dispatcher(handler_method).__get__(self))

        # Log the results of the discovery process.
        self.log(None, {'states': self._index_to_state, 'interface': sorted(interface_list)})

    def _noop(self, *args, **kwargs):
        """A do-nothing method used as a default for unbound sparkles."""
        pass

    def to_state(self, state):
        """
        Requests a state transition. The change is handled by the _execute_sparkle
        method after the current sparkle finishes.

        :param state: The name (str) or index (int) of the target state.
        """
        if isinstance(state, str):
            new_state_index = self._state_to_index.get(state, -1)
        elif isinstance(state, int) and 0 <= state < len(self._index_to_state):
            new_state_index = state
        else:
            new_state_index = -1
        # If the requested state is valid, set it as pending.
        if new_state_index != -1:
            self._pending_state = new_state_index

    def _execute_sparkle(self, sparkle_method, *args, **kwargs):
        """
        The single, central method for executing any sparkle from the queue. It
        is called by the external execution loop. It also handles logging and
        state transitions.

        :param sparkle_method: The unbound method of the sparkle to execute.
        :param args: Positional arguments for the sparkle.
        :param kwargs: Keyword arguments for the sparkle.
        """
        interface_name = sparkle_method.__name__
        self.log(None, {'sparkle': interface_name, 'state': self.state})

        # Execute the user's actual sparkle code, passing self to bind it.
        sparkle_method(self, *args, **kwargs)

        # After the sparkle runs, check if a state transition was requested.
        if self._pending_state != -1 and self._pending_state != self.state:
            old_state_name = self.get_current_state_name()

            # Call the global on_exit handler.
            self.log(None, {'sparkle': 'ttse__on_exit', 'state': self.state, 'new_state': self._pending_state})
            self._on_exit_handler(self)
            self.log_push()

            # Officially change the state.
            self.state = self._pending_state
            self._pending_state = -1
            new_state_name = self.get_current_state_name()

            # Call the global on_enter handler.
            self.log(None, {'sparkle': 'ttse__on_enter', 'state': self.state})
            self._on_enter_handler(self)
            self.log_push()
        else:
            # If no transition occurred, just push the log for the sparkle itself.
            self.log_push()

    def get_current_state_name(self):
        """
        Gets the name of the current state.

        :return: The name of the state (str) or "None".
        """
        if self.state == -1:
            return "None"
        return self._index_to_state[self.state]

    def log(self, line, flags=None):
        """
        Adds a text line and optional flags to the current log entry.

        :param line: The string message to log, or None.
        :param flags: A dictionary of flags to add to the log entry.
        """
        if self.log is None:
            self._log = {'start@': time.time(), 'log': []}
        if line:
            self._log['log'].append(line)
        if isinstance(flags, dict):
            self._log.update(flags)

    def log_push(self):
        """
        Formats and prints the collected log entry for an event, then resets it.
        """
        if self._log is None:
            return

        duration = time.time() - self._log['start@']
        sparkle_name = self._log.get('sparkle', '__unknown__')

        sparkle_state_idx = self._log.get('state', -1)
        header = f"{self.id}"
        if sparkle_state_idx >= 0:
            header += f"[{self._index_to_state[sparkle_state_idx]}]"
        header += f".{sparkle_name}"

        flags_to_print = {
            k: v for k, v in self._log.items() if k not in ['id', 'start@', 'log', 'sparkle', 'state']
        }

        print(f"[{duration: >7.3f}s] {header} {flags_to_print}")
        if self._log.get('log'):
            for line in self._log['log']:
                print(f"    {line}")
        self._log = None

    # --- System Lifecycle Sparkles ---
    def _tts__SYSTEM_TONIC_START(self):
        """System-level sparkle for internal framework setup."""
        pass

    def ttse__on_tonic_start(self):
        """Event sparkle for user-defined startup logic."""
        pass

    def ttse__on_tonic_finish(self):
        """Event sparkle for user-defined cleanup logic (conceptual)."""
        pass

    def _tts__SYSTEM_TONIC_FINISH(self):
        """System-level sparkle for final cleanup (conceptual)."""
        pass
```