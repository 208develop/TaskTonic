# Introduction

# System Prompt: TaskTonic Framework Assistant

You are an expert Python developer specializing in the custom concurrency framework called "TaskTonic". I have provided a comprehensive markdown document containing the complete source code and documentation for this framework. 

Your role is to help me write, refactor, and debug TaskTonic applications based strictly on the provided context.

## 1. Framework Core Concepts
TaskTonic provides concurrency without the complexity of traditional multi-threading or `async/await`. It uses an event-driven, queue-based architecture to guarantee thread-safety via atomic execution.
* **Tonic (`ttTonic`):** The active, stateful worker agent. It does not run code directly but places atomic work orders on a queue.
* **Sparkle:** An atomic, non-interruptible unit of work (a method within a Tonic). 
* **Catalyst (`ttCatalyst`):** The execution engine that sequentially pulls Sparkles from the queue and executes them safely.
* **Formula (`ttFormula`):** The entry point/recipe that configures the application and initializes the first Tonics.
* **State Machine:** Every Tonic has a built-in state machine. Transitions are made via `self.to_state('state_name')`.
* **Services:** Singletons defined by `_tt_is_service`. Initialized once via `__init__`, but `_tt_init_service_base` runs on every access to handle per-client context safely.

## 2. Naming Conventions & Syntax
TaskTonic uses strict introspection to route methods automatically. You must adhere to these prefixes:
* `ttsc__<name>`: Public Command (requests an action).
* `ttse__<name>`: Public Event (reacts to an event).
* `tts__<name>` or `_tts__<name>`: Internal Sparkle.
* `_ttss__<name>`: System Sparkle (lifecycle hooks).
* **State-bound Sparkles:** Format is `prefix_<state>__<name>` (e.g., `ttsc_idle__start`). The framework automatically routes to this if the Tonic is in the target state, otherwise falling back to the generic `ttsc__start`.

## 3. Strict Do's and Don'ts

### Architectural Do's & Don'ts
* **DO NOT block the thread:** Never use `time.sleep()` or heavy blocking `while` loops. This freezes the Catalyst engine and the entire application flow.
* **DO use Timers:** Use `ttTimerSingleShot` or `ttTimerRepeat` for delays and timeouts. Timers start immediately upon instantiation.
* **DO chunk heavy data:** Break long-running CPU tasks into smaller chunks using iterators, re-queuing the next Sparkle (e.g., `self.ttsc__process_next_chunk()`) to keep the engine responsive.
* **DO NOT use standard concurrency features:** Do not use `asyncio`, `await`, or `threading.Lock()`. TaskTonic handles thread-safety natively via the Catalyst queue.
* **DO use `ttStore` for shared state:** Use the `ttStore` and `Item` objects for reactive, hierarchical data sharing between Tonics instead of global variables.

### Code Style Do's & Don'ts
* **DO write all code in English:** This includes variable names, method names, comments, and strings (e.g., in `print` or `self.log()` statements).
* **DO NOT put statements on the same line as an `if` colon:** * *Incorrect:* `if condition: return`
    * *Correct:* ```python
        if condition:
            return
        ```
* **DO keep lines under 120 characters:** Ensure all generated code and comments respect a strict maximum line length of 120 characters.

Analyze the provided documentation carefully before generating code. Ensure all examples and solutions heavily utilize the Sparkle naming conventions, state machines, and proper lifecycle management (`self.finish()`, `ttse__on_start`, etc.).
    

---

# Project Structure

```text
TaskTonic/
    readme.md
    pyproject.toml
    collect_project_content.py
    tasktonic_knowledge_base.md
    mkdocs.yml
    CHANGELOG.md
    TaskTonic/
        __init__.py
        ttLedger.py
        ttTonic.py
        ttCatalyst.py
        ttFormula.py
        ttLiquid.py
        ttTimer.py
        ttLogger.py
        ttSparkleStack.py
        __main__.py
        internals/
            __init__.py
            RWLock.py
            Store.py
            Store - kopie.py
        ttLoggers/
            __init__.py
            ttScreenLogger.py
            ttIpLogger.py
        ttTonicStore/
            ttDistiller.py
            __init__.py
            ttPysideWidget.py
            ttPyside6Ui.py
            ttStore.py
            ttTimerScheduled.py
            ttTkinterUi.py
            ttTkinterWidget.py
            ttNetworking/
                __init__.py
                ttSelectorService.py
                ttTcpSockets.py
                ttUdpSockets.py
                ttHttpSockets.py
    examples/
        main.py
        TrafficLigthSimulationByGemini.py
        py_to_test_stuf_and_trow_away.py
        binding_demo.py
        dut_in_distiller.py
        ip_communicatie.py
        ui_main.py
        demo_data_store.py
        hello_world.py
        demo_scheduled_timers.py
        dut_in_distiller2.py
        queue_bencmark_the_tasktonic_way.py
        ui_tk_main.py
        StoreDemo.py
        networking_udp_with_wiz.py
        networking_udp_ping_pong_tutorial.py
        networking_tcp_echo.py
        https_get_sunset_time.py
        networking_http_demo.py
    testing/
        test_core.py
        conftest.py
        test_distiller.py
        test_store.py
        test_ttTonic.py
        test_ttIpSockets.py
        test_ttNetworking.py
        test_ttNetworking_ttSelectorService.py
        test_ttNetworking_ttTcpSockets.py
        test_ttNetworking_ttUdpSockets.py
        test_ttNetworking_ttHttpSockets.py
    TaskTonic.egg-info/
        dependency_links.txt
        top_level.txt
        SOURCES.txt
    dist/
    build/
        lib/
            TaskTonic/
                __init__.py
                ttLedger.py
                ttTonic.py
                ttCatalyst.py
                ttFormula.py
                ttLiquid.py
                ttTimer.py
                ttLogger.py
                ttSparkleStack.py
                __main__.py
                internals/
                    __init__.py
                    RWLock.py
                    Store.py
                ttLoggers/
                    __init__.py
                    ttScreenLogger.py
                ttTonicStore/
                    ttDistiller.py
                    __init__.py
                    ttPysideWidget.py
                    ttPyside6Ui.py
                    ttStore.py
                    ttTimerScheduled.py
                    ttTkinterUi.py
                    ttTkinterWidget.py
        bdist.win-amd64/
    docs/
        documentation.md
        index.md
        tasting-the-tonic.md
        assets/
        _In the future (or not)/
            IP communication roadmap.md
        CoreConcepts/
            10 - TaskTonic  - The introduction.md
            60 - TaskTonic - Active data store.md
            40 - TaskTonic - Depending on your state.md
            20 - TaskTonic - Sparkling Programming.md
            90 - TaskTonic - Testing in the ttDistiller.md
            30 - TaskTonic - Timers without waiting.md
            70 - TaskTonic - Understanding the ttCatalyst.md
            50 - Tasktonic - At your service.md
        TheToolbox/
            120 - TaskTonic - Networking and Sockets.md
    .github/
        workflows/
            00_publish.yml
            10_webdos.yml
            50_tests.yml
```

---

# File Contents

## `File: readme.md`
# TaskTonic

TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model.

## Philosophy & Metaphor

The core philosophy is based on the **Tonic**. Think of your running application as a glass of tonic. It comes to life
through **Sparkles**, the **bubbles** rising in a liquid.

* **The Flow:** Code is executed in small, atomic units called *Sparkles*.
* **The Fizz:** When these Sparkles flow continuously, the application "fizzes" with activity. It feels like a single,
  cohesive whole, even though it may be performing multiple logical processes simultaneously.
* **The Rule:** A Sparkle must be short-lived. If one bubble takes too long to rise (blocking code), the flow stops, and
  the fizz goes flat. In practice, this is rarely an issue, as most software processes are reactive chains of short
  events.

This architecture allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) without
the race conditions and headaches of traditional multi-threading.

## Use Cases

- TaskTonic is ideal for any scenario where you need to orchestrate numerous independent components:
- Responsive User Interfaces: Keep your UI fluid while performing heavy computations in the background.
- IoT & Sensor Networks: Process a continuous stream of events and measurements from thousands of devices.
- Communication Servers: Manage thousands of concurrent connections for chat applications, game servers, or data streams.
- Complex Simulations: Build simulations (e.g., swarm behavior, traffic models) where each entity acts autonomously.
- Asynchronous Data Processing: Create robust data pipelines where information is processed in small, distinct steps.

*...or all of the above, at the same time. That's where the framework's power truly lies.*

## Documentation

No documentation, no framework. Look into the **\doc** map and read it all.
Or look at https://208develop.github.io/TaskTonic/

## TaskTonic Projects:

- **TaskTonic Visual Logger**: 
  - Visual logger for debugging your TT project. 
  - https://github.com/208develop/tasktonic-visual-logger
 

## `File: pyproject.toml`
```toml
[project]
name = "TaskTonic"
version = "0.2.2"
authors = [
    { name = "Peter", email = "208develop@gmail.com" },
]
description = """ \
TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model.
It allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) \
without the race conditions and headaches of traditional multi-threading. \
"""

readme = "readme.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/208develop/TaskTonic"
Issues = "https://github.com/208develop/TaskTonic/issues"
Documentation = "https://github.com/208develop/TaskTonic/tree/master/_documents"
Changelog = "https://github.com/208develop/TaskTonic/CHANGELOG.md"

[tool.setuptools.packages.find]
include = ["TaskTonic", "TaskTonic.*"]

[tool.pytest.ini_options]
testpaths = ["testing"]


```

## `File: CHANGELOG.md`
# Changelog

## [0.2.0]
🎉 **First Stable Release of TaskTonic (v0.2.0)**

TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model. It allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) without the race conditions and headaches of traditional multi-threading.

### ✨ Key Features in this release:
* **Sparkling Programming:** You figure it out, cheers!!
* **Non-blocking Timers:** Built-in scheduling components (`ttTimerSingleShot`, `ttTimerEveryDay`, etc.) that never freeze your application.
* **Built-in State Machines:** Easy to use, clears up your code.
* **Testing Concurrency:** Yes, really. Look up the `ttDistiller` and find out.
* **UI Integrations:** Optional, ready-to-use wrappers for PySide6 (ready!!) and Tkinter (under construction) (`ttPyside6Ui`, `ttTkinterUi`).
* **Developer Ready:** I hope. It's just out in the open now, please help out. However, it is tested and compatible with `pytest`.

### 🚀 Getting Started
Full documentation and practical use cases can be found in the `_documents` and `examples` directories. 
*(PyPI package installation via `pip install TaskTonic` will be available shortly!)*

## [0.2.1] - 2026-06-01

Refining api after using it in the first project so everything feels like expected 
and redesign of the `Store` for smart central data and state distribution.

### New
- IP logger support, to use with TaskTonic Visual Logger (https://github.com/208develop/tasktonic-visual-logger), for tracking concurrent tasks.

### Changed
- Store and ttStore
   - `ttStore` is a `ttTonic` now, for active store management.
   - Extended subscribing (/room/sensors/*/temp)
   - `StoreLink`, relative path to a `Store` `Item`. You can reach the same `Item` from multiple paths.
   - Some api updates

## [0.2.2] - 2026-06-23
### New
- New networking module with selectorhandler as base. Now supporting tcp / udp / http

### Changed
- ttDistiller
  - Support for multiple tonic test (integrations) with new powerful contracts

## `File: TaskTonic\__init__.py`
```python
from .ttLedger import ttLedger
from .ttSparkleStack import ttSparkleStack
from .ttFormula import ttFormula
from .ttLiquid import ttLiquid
from .ttTonic import ttTonic
from .ttCatalyst import ttCatalyst

from .ttLogger import ttLog
from .ttTimer import ttTimerSingleShot, ttTimerRepeat, ttTimerPausing
```

## `File: TaskTonic\ttLedger.py`
```python
from . import ttLiquid, ttTonic
from .internals.RWLock import RWLock
from .internals.Store import Store

class ttLedger:
    """A thread-safe singleton class that serves as the central registry for all ttEssence instances.

    The Ledger is the authoritative source of truth for the state of the entire
    system. It assigns unique IDs, stores records of all active essences, and
    provides methods to look up essences by ID or name.
    """
    _lock = RWLock()
    _instance = None
    _singleton_init_done = False

    class TonicReservation(object):
        def __init__(self, tid, name):
            self.id = tid
            self.name = name

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock.write_access():
                if cls._instance is None:
                    cls._instance = super().__new__(cls, *args, **kwargs)
                    cls._singleton_init_done = False
        return cls._instance

    def __init__(self):
        if self._singleton_init_done: return
        with self._lock.write_access():
            if self._singleton_init_done: return
            self.tonics = [] # direct acces to liquid instance by id
            self.tonic_by_name = {}
            self.tonic_by_service = {}
            self.formula = Store()
            # init thread data, a data structure depending on active thread.
            self._singleton_init_done = True

    def update_formula(self, formula, val=None):
        """Updates the application's formula

        :param formula: The application definition object, typically a DataShare
                        instance containing configuration.
        :type formula: str, Collection[Tuple[str, Any]] or Dict[str, Any]]
        :param val: used if formula is a string to create a key, val pair
        :type val: any, optional
        """
        self.formula.set(formula, val)

    def make_reservation(self, service_name=None):
        with self._lock.write_access():
            try:
                tid = self.tonics.index(None)
                self.tonics[tid] = self.TonicReservation(tid, None)
            except ValueError:
                tid = len(self.tonics)
                self.tonics.append(self.TonicReservation(tid, None))

            if service_name is not None:
                self.tonic_by_name[service_name] = self.TonicReservation(tid, service_name)
        return tid

    def check_reservation(self, reservation, raise_on_err=False):
        if isinstance(reservation, str):
            reservation = self.tonic_by_name.get(reservation, None)
            if reservation is not None and isinstance(reservation, self.TonicReservation):
                return reservation.id
        elif isinstance(reservation, int) and reservation >= 0:
            if 0 <= reservation < len(self.tonics) \
            and isinstance(self.tonics[reservation], self.TonicReservation):
                return reservation

        if raise_on_err: raise RuntimeError(f'ID "{reservation}" is not a reservation')
        return None

    def register(self, essence, reservation=None):
        """Registers a ttEssence instance and assigns it a unique ID.

        :param essence: The ttEssence instance to be registered.
        :type essence: ttEssence

        :raises TypeError: If `essence` is not a ttEssence instance
        :return: The unique integer ID assigned to the essence.
        :rtype: int
        """
        from TaskTonic.ttLiquid import ttLiquid
        if not isinstance(essence, ttLiquid):
            raise TypeError('essence must be of type ttEssence')

        if reservation is not None:
            ess_id = self.check_reservation(reservation, raise_on_err=True)
            self.tonics[ess_id] = essence
            self.tonic_by_name[essence.name] = essence

        else: # no reservation, find or create space in list
            with self._lock.write_access():
                try:
                    ess_id = self.tonics.index(None)
                    self.tonics[ess_id] = essence
                    self.tonic_by_name[essence.name] = essence
                except ValueError:
                    ess_id = len(self.tonics)
                    self.tonics.append(essence)
                    self.tonic_by_name[essence.name] = essence
        return ess_id

    def unregister(self, liquid):
        """Unregisters a ttEssence instance from the ledger.

        (Note: This method is not yet implemented).

        :param liquid: The ttEssence instance to unregister.
        :type liquid: ttEssence
        """
        from TaskTonic import ttLiquid
        if isinstance(liquid, (ttLiquid, self.TonicReservation)):
            pass
        elif isinstance(liquid, int):

            if liquid == -1 or liquid >= len(self.tonics) or self.tonics[liquid] is None:
                raise RuntimeError(f"Id '{liquid}' not found to unregister")
            liquid = self.tonics[liquid]
        elif isinstance(liquid, str):
            liquid = self.tonic_by_name[liquid]
        else:
            raise TypeError('essence must be of type ttEssence or int or str')

        with self._lock.write_access():
            self.tonics[liquid.id] = None
            self.tonic_by_name.pop(liquid.name, None)
            liquid.id = -1

    def get_id_by_name(self, name):
        """Retrieves the ID of an essence by its registered name.

        :param name: The name of the essence to find.
        :type name: str
        :return: The integer ID of the essence, or -1 if not found.
        :rtype: int
        """
        with self._lock.read_access():
            ess = self.tonic_by_name.get(name, None)
            return ess.id if ess is not None else -1

    def get_tonic_by_name(self, name):
        """Retrieves a ttEssence instance by its registered name.

        :param name: The name of the essence to retrieve.
        :type name: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            return self.tonic_by_name.get(name, None)


    def get_tonic_by_id(self, id):
        """Retrieves a ttEssence instance by its unique ID.

        :param id: The unique integer ID of the essence.
        :type id: int
        :return: The ttEssence instance, or None if the ID is out of bounds.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            if 0 <= id < len(self.tonics): return self.tonics[id]
            return None

    def get_service_essence(self, service):
        """Retrieves a ttEssence instance by its service name.

        :param service: The name of the service of the essence to retrieve.
        :type service: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            return self.tonic_by_name.get(service, None)

    def sdump(self):
        def sdumptonic(t, b, indent):
            s = f'\n{indent}{"F! " if t.finishing else ""} {t.id:02d}[{t.name}] <{t.__class__.__name__}>'
            if hasattr(t, 'tonics_sparkling'): s+=f' cat:{t.tonics_sparkling} '
            if t.finishing: s+=' FINISHING '
            if hasattr(t, 'service_bases'):
                if t.base != b: return s+' SERVICE COPY'
                for sb in t.service_bases:
                    s+=f'\n{indent}  sb: {sb.id:02d}[{sb.name}]'
            for i in t.infusions:
                s += sdumptonic(i, t, ' | '+indent)
            return s

        from .ttTonic import ttTonic
        s = 'Ledger dump'
        for t in self.tonics:
            if isinstance(t, ttTonic):
                if t.base is None:
                    s += sdumptonic(t, None, ' - ')
            elif isinstance(t, self.TonicReservation):
                s += f'\n - {t.id:20d}[{t.name}] <RESERVATION>'

        return s+'\n'
```

## `File: TaskTonic\ttTonic.py`
```python
from sys import prefix

from .ttSparkleStack import ttSparkleStack
from .ttLiquid import ttLiquid
import re, threading, copy


class ttTonic(ttLiquid):
    """
    A robust, passive framework class for creating task-oriented objects (Tonics).

    This class automatically discovers methods (sparkles) based on naming conventions,
    handles state management, and provides a structured logging system. All sparkle
    types (ttsc, ttse, tts, _tts) are handled uniformly by placing a 'work order'
    on a queue, which is then processed by an external execution loop.
    """

    def __init__(self, name=None, log_mode=None, catalyst=None):
        """
        Initializes the Tonic instance, discovers sparkles, and calls startup methods.

        :param context: The context in which this tonic operates.
        :param name: An optional name for the tonic. Defaults to the class name.
        :param fixed_id: An optional fixed ID for the tonic.
        """
        super().__init__(name=name, log_mode=log_mode)
        self.catalyst = catalyst
        # Discover all sparkles and build the execution system.
        self.state = -1  # Start with no state (-1)
        self._pending_state = -1
        self._sparkle_init()

    def _tt_post_init_action(self):
        # Prevent _tt_post_init_action  to runs twice
        # (e.g., due to the complex initialization order in ttPysideWidget
        # involving metaclasses and multiple inheritance).
        if getattr(self, '_post_init_done', False):
            return
        self._post_init_done = True
        # -----------------------
        # bind to catalyst
        if not hasattr(self, 'catalyst_queue'):
            self.catalyst = \
                self.catalyst if self.catalyst is not None \
                else self.base.catalyst if hasattr(self.base, 'catalyst') and self.base.catalyst is not None\
                else self.ledger.get_tonic_by_name('tt_main_catalyst')
            self.catalyst_queue = self.catalyst.catalyst_queue  # copy queue for (a bit) faster acces
            self.log(flags={'catalyst': self.catalyst.name})
            self.catalyst._ttss__add_tonic_to_catalyst(self.id)

        super()._tt_post_init_action()

        # After initialization is completed, queue the synchronous startup sparkles.
        if hasattr(self, '_ttss__on_start'):
            self._ttss__on_start()
        if hasattr(self, 'ttse__on_start'):
            self.ttse__on_start()

        if hasattr(self, '_auto_bind'):
            for auto_bind in self._auto_bind:
                prefix, sparkle, binder = auto_bind
                binder(prefix, sparkle)

    def _get_custom_prefixes(self):
        """
        Hook for syntax extension with new prefixes and the binding method to call
         for binding an event to the sparkle (ea. {'ttqt': self.qt_event_binder}).
        """
        return {}


    def _sparkle_init(self):
        """
        Performs a one-time, intensive setup to discover all sparkles, build
        the dispatch system, and create the public-facing callable methods. This
        is the core of the Tonic's introspection and setup logic.

        Called from the Essence metaclass after completion of __init__
        """

        # Prevent _sparkle_init  to runs twice
        # (e.g., due to the complex initialization order in ttPysideWidget
        # involving metaclasses and multiple inheritance).
        if getattr(self, '_sparkle_init_done', False): return
        self._sparkle_init_done = True

        sp_stck = ttSparkleStack()

        prefix_extension = self._get_custom_prefixes()
        prefixes = ['ttsc', 'ttse', 'tts', '_tts', '_ttss']
        prefixes.extend(prefix_extension.keys())
        prefix_pattern = "|".join(prefixes)

        # Define the regular expressions used to identify different sparkle types.
        # state_pattern = re.compile(f'^({prefix_pattern})_([a-zA-Z0-9_]+)__([a-zA-Z0-9_]+)$')
        # general_pattern = re.compile(f'^({prefix_pattern})__([a-zA-Z0-9_]+)$')
        general_pattern = re.compile(f'^({prefix_pattern})__(.+)$')
        state_pattern = re.compile(f'^({prefix_pattern})_(.+?)__(.+)$')

        # --- Phase 1: Discover all implementations from the class hierarchy (MRO) ---
        state_impls, generic_impls = {}, {}
        states, sparkle_names = set(), set()
        prefixes_by_cmd = {}

        # Iterate through the MRO (Method Resolution Order) in reverse to ensure
        # that methods in child classes correctly override those in parent classes.
        for cls in reversed(self.__class__.__mro__):
            if cls in (ttLiquid, object):
                continue
            for name, method in cls.__dict__.items():
                s_match = state_pattern.match(name)
                g_match = general_pattern.match(name)
                if g_match:
                    # Found a generic sparkle (e.g., 'ttsc__initialize')
                    prefix, sp_name = g_match.groups()
                    generic_impls[(prefix, sp_name)] = method
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)
                elif s_match:
                    # Found a state-specific sparkle (e.g., 'ttsc_waiting__process')
                    prefix, state_name, sp_name = s_match.groups()
                    state_impls[(prefix, state_name, sp_name)] = method
                    states.add(state_name)
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)


        # --- Phase 2: Build fast lookup tables for states ---
        self._state_to_index = {name: i for i, name in enumerate(sorted(list(states)))}
        self._index_to_state = sorted(list(states))
        num_states = len(self._index_to_state)

        # --- Phase 3A: Create fallback methods for state on_enter and on_exit
        if num_states:
            self._direct_execute_ttse__on_enter = self.ttse__on_enter
            self._direct_execute_ttse__on_exit = self.ttse__on_exit
        # --- Phase 3B: Create and bind all public-facing dispatcher methods ---
        sparkle_list = []
        for sp_name in sparkle_names:
            is_state_aware = any(sp_name == key[2] for key in state_impls.keys())
            for prefix in prefixes_by_cmd[sp_name]:
                interface_name = f"{prefix}__{sp_name}"
                sparkle_list.append(interface_name)

                # --- Path A: This is a state-aware command ---
                if is_state_aware:
                    # For state-aware commands, we build a list of methods, one for each state.
                    handler_list = [self._noop] * num_states
                    generic_handler = generic_impls.get((prefix, sp_name))
                    if generic_handler:
                        handler_list = [generic_handler] * num_states
                    for state_idx, state_name in enumerate(self._index_to_state):
                        state_handler = state_impls.get((prefix, state_name, sp_name))
                        if state_handler:
                            handler_list[state_idx] = state_handler

                    def create_put_state_sparkle(_list, _name):
                        # Create a state execution that will select the correct method by state from the list at
                        #  runtime and create the put_state_sparkle to put if on the queue
                        def create_executer():
                            def execute_state_sparkle(self, *args, **kwargs):
                                state_sparkle = _list[self.state]
                                self.log(flags={'state': self.state})
                                state_sparkle(self, *args, **kwargs)
                            execute_state_sparkle.__name__ = _name
                            return execute_state_sparkle

                        def put_state_sparkle(self, *args, **kwargs):
                            if threading.get_ident() != self.catalyst.thread_id:
                                args = tuple((arg if callable(arg) else copy.deepcopy(arg)) for arg in args)
                                kwargs = {key: (value if callable(value) else copy.deepcopy(value))
                                          for key, value in kwargs.items()}
                            self.catalyst_queue.put((self, create_executer(), args, kwargs, sp_stck.get_stack()))
                        return put_state_sparkle

                    # Bind the new put_state_sparkle function to the instance, making it a method.
                    setattr(self, interface_name, create_put_state_sparkle(handler_list, interface_name).__get__(self))

                    # Create direct-execute methods only for 'on_enter' and 'on_exit'
                    if interface_name in ['ttse__on_enter', 'ttse__on_exit']:
                        direct_method_name = f"_direct_execute_{interface_name}"

                        # This factory creates the direct execution method
                        # It needs to capture the handler_list (_list)
                        def create_direct_executor(_list, _name):
                            # This is the exact logic copied from 'execute_state_sparkle'
                            def direct_execute_method(self, *args, **kwargs):
                                state_sparkle = _list[self.state]
                                self.log(flags={'state': self.state})
                                state_sparkle(self, *args, **kwargs)
                            direct_execute_method.__name__ = _name
                            return direct_execute_method

                        # Bind the new direct method to the instance
                        setattr(self,
                                direct_method_name,
                                create_direct_executor(handler_list, interface_name).__get__(self))

                # --- Path B: This is a generic-only command ---
                else:
                    handler_method = generic_impls[(prefix, sp_name)]

                    def create_put_sparkle(_method):
                        # This put_sparkle always uses the one generic method.
                        def put_sparkle(self, *args, **kwargs):
                            if threading.get_ident() != self.catalyst.thread_id:
                                args = tuple((arg if callable(arg) else copy.deepcopy(arg)) for arg in args)
                                kwargs = {key: (value if callable(value) else copy.deepcopy(value))
                                          for key, value in kwargs.items()}
                            self.catalyst_queue.put((self, _method, args, kwargs, sp_stck.get_stack()))
                        return put_sparkle

                    # Bind the new put_sparkle function to the instance, making it a method.
                    setattr(self, interface_name, create_put_sparkle(handler_method).__get__(self))

        # --- Phase 4: Build fast lookup tables for sparkles ---
        self.sparkles = sorted(sparkle_list)

        # --- Phase 5: patch the _execute_sparkle function to normal mode ---
        self._execute_sparkle = self.__exec_sparkle

        # --- Phase 6: prpare for auto binding sparkles for extended syntax
        auto_bind = []
        for sparkle in self.sparkles:
            for prefix, binder in prefix_extension.items():
                if sparkle.startswith(prefix):
                    auto_bind.append((prefix, sparkle, binder))
        if auto_bind: self._auto_bind = auto_bind

        # Log the results of the discovery process.
        self.log(lifecycle={'states': self._index_to_state, 'sparkles': self.sparkles})

    def _noop(self, *args, **kwargs):
        """A do-nothing method used as a default for unbound sparkles."""
        pass

    def to_state(self, state, force_reenter=False):
        """
        Requests a state transition. The change is handled by the _execute_sparkle
        method after the current sparkle finishes.

        :param state: The name (str) or index (int) of the target state. When target == -1, stop machine stops
        :param force_reenter: When True, forces the transition (on_exit and on_enter) even if already in the state.
        """
        if isinstance(state, str):
            to_state = self._state_to_index.get(state, None)
            if to_state is None: return
        elif isinstance(state, int) and 0 <= state < len(self._index_to_state):
            to_state = state
        elif isinstance(state, int) and state == -1:
            to_state = -1
        else:
            return

        if not force_reenter and to_state == self.state: return

        if self.state >= 0:
            self.catalyst._execute_extra_sparkle(self, self._direct_execute_ttse__on_exit)
        if to_state >= 0:
            self.catalyst._execute_extra_sparkle(self, self._ttinternal_state_change_to, to_state)
            self.catalyst._execute_extra_sparkle(self, self._direct_execute_ttse__on_enter)
        else:
            self.catalyst._execute_extra_sparkle(self, self._ttinternal_state_machine_stop)

    def reenter_current_state(self):
        """
        Forces a reentry of the current state by executing on_exit followed by on_enter.
        This is useful for resetting the internal logic of the current state.
        """
        if self.state >= 0:
            self.to_state(self.state, force_reenter=True)

    def _ttinternal_state_change_to(self, state):
        self.log(lifecycle={'phase': 'new_state', 'state': self.state, 'new_state': state})
        self.state = state

    def _ttinternal_state_machine_stop(self):
        self.log(lifecycle={'phase': 'new_state', 'state': self.state, 'new_state': None})
        self.state = -1
        pass

    def get_active_state(self):
        if self.state == -1: return '--'
        return self._index_to_state[self.state]

    def _execute_sparkle(self, sparkle_method, *args, **kwargs):
        """
        The single, central method for executing any sparkle from the queue. It
        is called by the external execution loop. It also handles logging and
        state transitions.

        This is the placeholder. On tonic startup this is replaced by __exec_sparkle, with this functionality.
        On finishing the tonic __exec_system_sparkle which only handles the system calls, and filters out user sparkles

        :param sparkle_method: The unbound method of the sparkle to execute.
        :param args: Positional arguments for the sparkle.
        :param kwargs: Keyword arguments for the sparkle.
        """
        pass

    def __exec_sparkle(self, sparkle_method, *args, **kwargs):
        """
        sparkle execution in running mode
        """
        interface_name = sparkle_method.__name__
        sp_stck = ttSparkleStack()
        self.log(flags={'sparkle': interface_name,
                        'source': f'{sp_stck.source_tonic_name}.{sp_stck.source_sparkle_name}',
                        'source_id': sp_stck.source_tonic_id,
                       },
                 )
        # Execute the user's actual sparkle code, passing self to bind it.
        sparkle_method(self, *args, **kwargs)
        self.log(close_log=True)

    def __exec_system_sparkle(self, sparkle_method, *args, **kwargs):
        """
        sparkle execution in normal mode
        """
        if self.id < 0: return  # Tonic already unregistered (probably old sparkle in queue)

        interface_name = sparkle_method.__name__

        if interface_name.startswith('_ttss') \
        or interface_name in [
            'ttse__on_finished', 'ttse__on_exit',
            'ttse__on_service_base_completed', '_ttinternal_state_machine_stop',
        ]:
            self.__exec_sparkle(sparkle_method, *args, **kwargs)

    def get_current_state_name(self):
        """
        Gets the name of the current state.

        :return: The name of the state (str) or "None".
        """
        if self.state == -1: return "--"
        return self._index_to_state[self.state]

    # standard tonic sparkle
    def ttse__on_start(self): pass
    def ttse__on_finished(self): pass
    def ttse__on_enter(self): pass
    def ttse__on_exit(self): pass

    def ttsc__to_state(self, state, force_reenter=False):
        """External command to safely transition to a new state via the Catalyst queue."""
        self.to_state(state, force_reenter=force_reenter)

    # --- System Lifecycle Sparkles ---
    def _ttss__on_start(self):
        """System-level sparkle for internal framework setup."""
        pass

    def finish(self):
        # Finish on tonic level, will first stop the tonic, and after that finish admin in the essence
        if self.finishing: return
        self.ttsc__finish()

    def ttsc__finish(self):
        if self.finishing: return
        self.log(lifecycle={'phase': 'finishing'})
        calling_tonic = ttSparkleStack().source_tonic

        # check on valid tonic finish
        if calling_tonic in [self.base, self]:
            if hasattr(self, 'service_bases') and calling_tonic in self.service_bases:
                self.service_bases.remove(calling_tonic)

            if self.base:
                self.base._ttss__on_infusion_completed(self)

            # start finishing the tonic
            self.finishing = True
            self._execute_sparkle = self.__exec_system_sparkle # patch the _execute_sparkle function to finish mode
            if self.state != -1: self.to_state(-1)  # stop state machine if active
            self.ttse__on_finished()  # stop tonic (user level)
            self._ttss__on_finished()  # cleanup tonic (system level)


        # check if service finish
        elif hasattr(self, 'service_bases') and calling_tonic in self.service_bases:
            self.service_bases.remove(calling_tonic)
            # notify
            try: getattr(self, 'ttse__on_service_base_removed')(calling_tonic.id, len(self.service_bases))
            except AttributeError: pass
            try: getattr(calling_tonic, f'ttse__on_{self.name}_completed')()
            except AttributeError: pass
            try: getattr(calling_tonic, '_ttss__on_infusion_completed')(self.id)
            except AttributeError: pass

            if len(self.service_bases) <= 0: self.finish()

    def _ttss__on_finished(self):
        """System-level sparkle for final cleanup."""
        #notify and remove service bases left
        try:
            for sb in self.service_bases:
                try: getattr(sb, f'ttse__on_{self.name}_completed')()
                except AttributeError: pass
                try: getattr(sb, '_ttss__on_infusion_completed')(self.id)
                except AttributeError: pass
            self.service_bases.clear()
        except AttributeError: pass

        # finish all infusions
        sp_stck = ttSparkleStack()
        sp_stck.push(self, 'finish')
        for tonic in self.infusions.copy():
            tonic.ttsc__finish()
        sp_stck.pop()
        self.infusions=[]

        # # complete
        # self.catalyst._ttss__remove_tonic_from_catalyst(self.id)
        # self.ledger.unregister(self.id)
        # self.id = -1  # finished

        # finish the Tonic
        # if not self.infusions:
        #     self._ttss__on_completion()
        # else:
        #     sp_stck = ttSparkleStack()
        #     sp_stck.push(self, 'finish')
        #     for tonic in self.infusions.copy():
        #         tonic.ttsc__finish()
        #     sp_stck.pop()

        self._ttss__on_completion()

    def _ttss__on_infusion_completed(self, tonic):
        if tonic in self.infusions:
            self.infusions.remove(tonic)
            # if self.finishing and not self.infusions:
            #     self._ttss__on_completion()

    def _ttss__on_completion(self):
        self.log(lifecycle={'phase': 'finished'})
        self.catalyst._ttss__remove_tonic_from_catalyst(self.id)
        self.ledger.unregister(self.id)
        self.id = -1  # finished


```

## `File: TaskTonic\ttCatalyst.py`
```python
from .ttSparkleStack import ttSparkleStack
from .ttTonic import ttTonic
import queue, threading, time


class ttCatalyst(ttTonic):
    """
    The central executor in the TaskTonic framework, it makes the tonic sparkle. The catalyst itself behaves as
    and can be used as a tonic.

    Only the main catalyst (id==0) is executed from main (from the formula class). It is possible to let all the
    tonic sparkle by one catalyst. However, if a catalyst is created in the tonic chaine, it is launched in its
    own thread.

    A Catalyst is a special type of Tonic that manages the main execution queue
    (the 'catalyst_queue') and controls the lifecycle of other Tonics. It pulls
    'sparkles' from the queue and executes them for the correct tonics
    """

    def __init__(self, name=None, log_mode=None, dont_start_yet=False):
        """
        Initializes the Catalyst and its master queue.

        :param name: An optional name for this Catalyst.
        :param fixed_id: An optional fixed ID for this Catalyst.
        """
        # Initialize the base ttTonic functionality. The Catalyst is also a Tonic.
        super().__init__(name=name, log_mode=log_mode)
        # The master queue that all Tonics managed by this Catalyst will use.
        self.catalyst_queue = self.new_catalyst_queue()
        self.extra_sparkles = []
        self.catalyst = self  # Tonics have to have a catalyst
        # internals
        self.sparkling = False
        self.tonics_sparkling = []
        self.thread_id = -1
        self.timers = []



        if self.id > 0 and not dont_start_yet: # id 0 (main catalyst) will be started in formula
            self.start_sparkling()

    def new_catalyst_queue(self):
        return queue.SimpleQueue()

    def start_sparkling(self):
        """
        Starts the main execution loop of the Catalyst.

        The main Catalyst (id=0) runs its loop in the main thread, blocking
        execution. Other Catalysts will start their loop in a separate thread.
        """
        if self.sparkling: return

        if self.id == 0:
            # If this is the main Catalyst, run its loop in the current thread.
            self.sparkle()
        else:
            # For other Catalysts, spawn a new background thread for the loop or wait when application is starting up
            if self.ledger.formula.get('tasktonic/project/status', 'starting') == 'starting':
                return  # dont startup jet, will be done just before main_catalyst starts sparkling
            threading.Thread(target=self.sparkle).start()

    def sparkle(self):
        """
        The main execution loop of the Catalyst.

        This method continuously pulls work orders (instance, sparkle, args, kwargs)
        from the queue and executes them. It runs until the `self.sparkling` flag
        is set to False.
        """
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True

        # The loop continues as long as the Catalyst is in a sparkling state.
        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0
            while next_timer_expire == 0.0:
                next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60
            try:
                instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get(timeout=next_timer_expire)
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                while self.extra_sparkles:
                    instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                    sp_stck.push(instance, sparkle.__name__)
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                    sp_stck.pop()
            except queue.Empty: pass

    def _execute_extra_sparkle(self, instance, sparkle, *args, **kwargs):
        if hasattr(sparkle, '__func__'): sparkle = sparkle.__func__ # make an unbound method (without self)
        self.extra_sparkles.append((instance, sparkle, args, kwargs))

    def _ttss__add_tonic_to_catalyst(self, tonic_id):
        """
        A system-level sparkle called by a Tonic during its initialization
        to register itself with the Catalyst.

        :param tonic_id: The Tonic id that is starting up.
        """
        if tonic_id not in self.tonics_sparkling:
            self.tonics_sparkling.append(tonic_id)

    def _ttss__remove_tonic_from_catalyst(self, tonic_id):
        """
        A system-level sparkle called by a Tonic when it has completed its
        lifecycle and is shutting down.

        If this is the last active Tonic, the Catalyst will initiate its own
        shutdown sequence.

        :param tonic_id: The Tonic instance that has finished.
        """
        if tonic_id in self.tonics_sparkling:
            self.tonics_sparkling.remove(tonic_id)
        # self.log(f"Tonic {tonic_id} has been removed from Catalyst. (left {self.tonics_sparkling})")

        # If there are no more active tonics, or active tonics used by catalyst, the catalyst's job is done.
        infusion_ids = {i.id for i in self.infusions}
        if set(self.tonics_sparkling).issubset(infusion_ids):
            self.finish()

    def _ttss__main_catalyst_finished(self):
        # Default: Stop when main catalyst is finished. You can override this method for other behavior
        # self.log('Finish catalyst')
        self.finish()

    def _ttss__on_completion(self):
        super()._ttss__on_completion()
        # Setting this flag to False will terminate the sparkle loop.
        self.sparkling = False

```

## `File: TaskTonic\ttFormula.py`
```python
from .ttSparkleStack import ttSparkleStack
from .ttLedger import ttLedger
from .ttCatalyst import ttCatalyst

import time

class ttFormula():
    def __init__(self):

        # 1/ INIT, init parameters ----------------------------------------------------------------------------------
        self.ledger = ttLedger()
        sp_stck = ttSparkleStack()
        from .ttLoggers import ttLogService, ttScreenLogService, ttIpLogService
        from .ttLogger import ttLog
        self.ledger.update_formula((
            # project parameters
            ('tasktonic/project/name', 'tasktonic app'),
            ('tasktonic/project/started@', time.time()),
            ('tasktonic/project/status', 'starting'),

            # default logger is screen, quiet logging
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),

            # set log services
            ('tasktonic/log/service#', 'off'),
            ('tasktonic/log/service./service', ttLogService), # base class, without logging
            ('tasktonic/log/service#', 'screen'),
            ('tasktonic/log/service./service', ttScreenLogService),
            ('tasktonic/log/service./arguments', {}),
            ('tasktonic/log/service#', 'ip'),
            ('tasktonic/log/service./service', ttIpLogService),
            ('tasktonic/log/service./arguments', {}),
        ))

        # 2/ FORMULA, load the user formula -------------------------------------------------------------------------
        app_formula = self.creating_formula()
        if app_formula:
            self.ledger.update_formula(app_formula)

        # make id reservation for main catalyst
        self.ledger.make_reservation(service_name='tt_main_catalyst')

        # 3/ TONIC LOGGER, start the system log function if set -----------------------------------------------------
        log_formula = self.ledger.formula.at('tasktonic/log')
        self._logger = None
        self._log_mode = None
        self._log = None
        log_to = log_formula.get('to', 'off')

        if log_to != 'off':
            from .ttLogger import ttLogService, ttLog
            log_service = None
            services = log_formula.children(prefix='service')
            for service in services:
                if service.v == log_to:
                    s_kwargs = service.get('arguments', {})
                    log_service = service.get('service')(*(), **s_kwargs)  ## startup logger service
                    break
            if log_service is None:
                raise RuntimeError(f'Log to service "{log_to}" not supported.')

        # 4/ CATALYST, start the main catalyst ----------------------------------------------------------------------
        self.creating_main_catalyst()

        main_catalyst = self.ledger.get_tonic_by_name('tt_main_catalyst')
        if not isinstance(main_catalyst, ttCatalyst):
            raise RuntimeError(f'Main catalyst {main_catalyst} in formula is not a ttCatalyst instance')

        # 5/ TONICS, startup the system by creating the starting tonics ---------------------------------------------
        sp_stck.push(self.ledger.get_tonic_by_name('tt_main_catalyst'), '__formula__')
        self.creating_starting_tonics()
        sp_stck.pop()

        # 6/ STARTUP, start created catalysts and them start main catalyst ------------------------------------------
        if not self.ledger.formula.get('tasktonic/testing/dont_start_catalysts', False):

            self.ledger.update_formula('tasktonic/project/status', 'start_catalysts')
            for essence in self.ledger.tonics[1:].copy(): # must be copied, because threads get started and ledger can be changed
                if isinstance(essence, ttCatalyst):
                    essence.start_sparkling()

            self.ledger.update_formula('tasktonic/project/status', 'main_running')
            main_catalyst.start_sparkling()
            self.ledger.update_formula('tasktonic/project/status', 'main_finished')

            # notify unfinished catalysts in ledger records
            for essence in self.ledger.tonics[1:].copy():
                if hasattr(essence, '_ttss__main_catalyst_finished'):
                    essence._ttss__main_catalyst_finished()



    def creating_formula(self):
        return None

    def creating_main_catalyst(self):
        ttCatalyst(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        pass


```

## `File: TaskTonic\ttLiquid.py`
```python
import time
from .ttSparkleStack import ttSparkleStack


class __ttLiquidMeta(type):
    """
    Metaclass for the ttTonic (via TTLiquid)

    This metaclass intercepts the creation of all ttEssence subclasses
    to provide two key functionalities:

    1.  Post-Initialization Hook: It calls an `_init_post_action` method
        on the instance *after* its `__init__` has successfully completed.
    2.  Service (Singleton) Management: It checks for a `service` kwarg
        or a `_tt_is_service` class attribute. If found, it ensures
        that only one instance of that service (identified by its name)
        is ever created. It guarantees that `__init__` and `_init_post_action`
        run only once for the service, but calls `_init_service` on *every* access.
        *BE AWARE*: when creating a new instance of the service in the context of another service,
        the service wil be finished (for everyone) when that context is deleted. It's better to create
        a new instance of the service from your formula.
    """

    def __new__(mcs, name, bases, attrs):
        """
        Intercept class creation to inject the bootstrap logic BEFORE the user's __init__.
        """
        original_init = getattr(super().__new__(mcs, name, bases, attrs), '__init__', None)

        def wrapped_init(self, *args, **kwargs):
            self._bootstrap(*args, **kwargs)
            if original_init:
                original_init(self, *args, **kwargs)

        wrapped_init.__wrapped__ = original_init
        attrs['__init__'] = wrapped_init

        return super().__new__(mcs, name, bases, attrs)


    def __call__(cls, *args, **kwargs):
        """
        Creating the ttEssence.
        - get ledger
        - get base tonic to add to
        - check if this is a service (singleton)
        - create tonic if not service or if first instance of service
        - start
        """
        if not issubclass(cls, ttLiquid):
            raise TypeError(f'Class {cls.__name__} is not a ttLiquid')

        tonic = None

        # GET LEDGER
        from .ttLedger import ttLedger
        ledger = ttLedger()

        # GET BASE
        sp_stck = ttSparkleStack()
        base = sp_stck.get_tonic()

        # CHECK ON SERVICE ESSENCE (singleton) and GET SERVICE IF ALREADY CREATED
        service_name = getattr(cls, '_tt_is_service', None)
        is_service = service_name is not None

        if is_service:
            if len(args) >= 1 and isinstance(args[0], str):
                name = args[0]
                args = args[1:]
            else:
                name = kwargs.get('name', None)
            if name: Warning(f'Name {name} is ignored and changed to service name {service_name}')
            kwargs['name'] = service_name
            tonic = ledger.get_tonic_by_name(service_name) # get existing service or None
            if isinstance(tonic, ledger.TonicReservation): tonic = None

        # CREATE AND INIT TONIC
        if tonic is None:
            tonic = super().__call__(*args, **kwargs)
            if hasattr(tonic, '_tt_sparkle_init'): tonic._tt_sparkle_init()
            tonic._tt_post_init_action()
        else: # existing service
            if base: base._tt_add_infusion(tonic)
            sp_stck.push(tonic, '__init__')

        # HANDLE SERVICE ADMIN
        if is_service and base is not None:
            try: tonic.service_bases.append(base)
            except AttributeError: tonic.service_bases = [base]
            tonic._tt_init_service_base(base, *args, **kwargs)

        sp_stck.pop()

        return tonic

class ttLiquid(metaclass=__ttLiquidMeta):
    """A base class for all active components within the TaskTonic framework.

    Each 'Liquid' represents a distinct, addressable entity with its own
    lifecycle, context (parent), and subjects (children). It automatically
    registers itself with the central ttLedger upon creation to receive a unique ID.
    """

    def _bootstrap(self, *args, **kwargs):
        """
        Setup logic that must run once per instance.
        Safe to call from __new__ OR __init__ (if __new__ was skipped).
        necessary to solve possible metaclass mix issues
        """
        if hasattr(self, 'id'): return

        # GET LEDGER
        from .ttLedger import ttLedger
        ledger = ttLedger()
        cls = self.__class__

        # GET BASE
        sp_stck = ttSparkleStack()
        calling_essence = sp_stck.get_tonic()
        base = None if (getattr(cls, '_tt_base_essence', False) or getattr(cls, '_tt_is_service', None) is not None)\
               else calling_essence

        # CREATE TONIC and INIT ESSENTIALS
        self.ledger = ledger
        self.id = None
        given_name = kwargs.get('name', args[0] if len(args) >= 1 and isinstance(args[0], str) else None)
        if given_name: self.id = ledger.check_reservation(given_name)
        if self.id is None: self.id = ledger.make_reservation()
        self.name = given_name if given_name else  f'{self.id:02d}.{cls.__name__}'
        self.base = base
        self.infusions = []
        self.finishing = False
        ledger.register(self, reservation=self.id)
        if base: base._tt_add_infusion(self)
        elif calling_essence: calling_essence._tt_add_infusion(self)

        # handle essence init as sparkle on stack. popped in meta
        sp_stck.push(self, '__init__')


    def __init__(self, *args, name=None, log_mode=None, **kwargs):
        """
        Initializes a new ttLiquid instance. (after meta and new initialized the TaskTonic basics)

        :param name: An optional name for this essence. If not provided, a name
                     will be generated based on its ID and class name.
        :type name: str, optional
        :param log_mode: The initial logging mode for this essence.
        :type log_mode: ttLog, str, or int, optional
        :param kwargs: Catches any additional keyword arguments, allowing
                       subclasses to accept their own parameters
                       (e.g., `srv_api_key`) without breaking this
                       base class `__init__`.
        """
        if getattr(self, '_tt_liquid_init_done', False): return
        self._tt_liquid_init_done = True
        # first, enable logging
        log_formula = self.ledger.formula.at('tasktonic/log')
        self._logger = None
        self._log_mode = None
        self._log = None
        log_to = log_formula.get('to', 'off')

        # Set logger service and log_mode
        from .ttLogger import ttLogService, ttLog
        if getattr(self, '_tt_force_stealth_logging', False) or log_to == 'off':
            # Essence is forcing stealth mode or no log_to set, so also no logservice needed
            self.set_log_mode(ttLog.STEALTH)
        else:
            if log_mode is None:
                log_mode = \
                    self.base._log_mode if (self.base and self.base._log_mode) \
                    else log_formula.get('default', ttLog.STEALTH) if self.ledger.formula \
                    else ttLog.STEALTH

            if log_mode != ttLog.STEALTH:
                self._logger = ttLogService() # default log service is empty template, the running service is used

            self.set_log_mode(log_mode)

        self.log(lifecycle={
            'phase': 'creation',
            'id': self.id,
            'name': self.name,
            'base': self.base.id if self.base else -1,
            'type': self.__class__.__name__,
        })

    def __str__(self):
        return f'<ID[{self.id:02d}]B[{self.base.id if self.base else -1:02d}] {self.__class__.__name__} {self.name}>'

    def __repr__(self):
        return self.__str__()

    def __deepcopy__(self, memodict={}):
        return self

    def _tt_post_init_action(self):
        """
        A post-initialization hook called by the metaclass.

        This method is guaranteed to run *after* __init__ has completed.
        It is used to init your process (ie. start statemachine) if everything
        is ready.
        """
        self.log(close_log=True)

    def _tt_init_service_base(self, *args, **kwargs):
        """
        A hook called by the metaclass *every time* a service is accessed.

        Subclasses can override this method to capture context-specific
        parameters (from kwargs) each time they are requested.

        Note: For al services the base is already automatically added to the service_bases list

        This method is intentionally a pass-through in the base class.
        """
        pass

    def _tt_add_infusion(self, essence):
        self.infusions.append(essence)

    def finish(self):
        """
        Static finish in one cycle.
         Be aware to use this only within the same thread as the base thread
         and no service cleaning up is done. Also finishing infusions is kept simple,
         no waiting and check on finishing of the infusions.
        """
        if self.finishing or self.id==-1: return
        if self.base:
            if self in self.base.infusions:
                self.base.infusions.remove(self)

            if hasattr(self.base, '_ttss__on_infusion_completed'):
                self.base._ttss__on_infusion_completed(self)
            else:
                if self in self.base.infusions:
                    self.base.infusions.remove(self)


        for liquid in self.infusions.copy():
            liquid.ttsc__finish()

        self.log(lifecycle={'phase': 'finished'})
        self.ledger.unregister(self.id)
        self.id = -1  # finished

    def ttsc__finish(self): self.finish() # make compatible with tonic calls

    # create logger functions for ttLog to overwrite
    def log(self, line=None, flags=None, lifecycle=None,
            lane_color=None, marker=None, probe=None, close_log=False):
        """
        Adds a text line and/or (system) flags to the current log entry.

        A log entry is created on the first call and sent/closed when
        `close_log` is true. This method is a placeholder and will be
        dynamically replaced by `set_log_mode` to point to the correct
        log handler (e.g., `_log_full`, `_log_stealth`).

        Note:
        possible log colors: white, green, blue, orange, pink, purple, cyan or yellow

        :param line: The string message to log (add ##<log color> for coloring log line).
        :param flags: A dictionary of flags to add to the log entry.
        :param lifecycle: A dictionary of framework lifecycle data.
        :param close_log: When true, send the log entry and clear it.
        :param lane_color: Set color of log lane (id) to a log color
        :param marker: Add marker to log (for display and filtering) (add ##<log color> for coloring marker).
        :param probe: Add parameter dict to log to display in the probe list.

        """
        pass

    def _log_full(self, line=None, flags=None, lifecycle=None,
                     lane_color=None, marker=None, probe=None, close_log=False):
        """Internal log handler for the FULL log mode."""
        # if self.id == -1: pass # todo:??

        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}

        if flags: self._log.update(flags)
        if lifecycle: self._log.setdefault('lifecycle', {}).update(lifecycle)
        if lane_color or marker or probe:
            meta = self._log.setdefault('meta', {})
            if lane_color: meta['lane_color'] = lane_color
            if marker:     meta.setdefault('marker', []).append(marker)
            if probe:      meta.setdefault('probe', {}).update(probe)

        if line: self._log['log'].append(line)

        if close_log:
            self._log['duration'] = time.time() - self._log['start@']
            self._log_push(self._log)
            self._log = None

    def _log_quiet(self, line=None, flags=None, lifecycle=None,
                   lane_color=None, marker=None, probe=None, close_log=False):
        """Internal log handler for the QUIET log mode."""
        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}

        if lifecycle: self._log.setdefault('lifecycle', {}).update(lifecycle)
        if flags: self._log.update(flags)
        if lane_color or marker or probe:
            meta = self._log.setdefault('meta', {})
            if lane_color: meta['lane_color'] = lane_color
            if marker:     meta.setdefault('marker', []).append(marker)
            if probe:      meta.setdefault('probe', {}).update(probe)

        if line: self._log['log'].append(line)
        if close_log:
            if self._log['log'] or 'lifecycle' in self._log or 'meta' in self._log:
                self._log_push(self._log)
            self._log = None

    def _log_off(self, line=None, flags=None, lifecycle=None,
                 lane_color=None, marker=None, probe=None, close_log=False):
        """Internal log handler for the OFF log mode (lifecycle only)."""
        if lifecycle:
            if self._log is None: self._log = {'id': self.id, 'start@': time.time()}
            self._log.setdefault('lifecycle', {}).update(lifecycle)
        if close_log and self._log:
            self._log_push(self._log)
            self._log = None

    def _log_stealth(self, line=None, flags=None, lifecycle=None,
                     lane_color=None, marker=None, probe=None, close_log=False):
        """Internal log handler for the STEALTH log mode (does nothing)."""
        pass

    def set_log_mode(self, log_mode):
        """
        Sets the logging function for this essence instance.

        This method "patches" `self.log` to point directly to the
        correct internal log handler (e.g., `_log_full`, `_log_stealth`)
        based on the selected mode for maximum performance.

        Args:
            log_mode (ttLog or str or int): The desired log mode.
        """
        from .ttLogger import ttLog
        log_implementations = [self._log_stealth, self._log_off, self._log_quiet, self._log_full]
        log_mode = ttLog.from_any(log_mode)
        self._log_mode = log_mode
        try:
            self.log = log_implementations[log_mode]
        except IndexError:
            raise NotImplementedError(f"Log mode '{log_mode.name}' is not implemented in ttLiquid.set_log_mode.")


    def _log_push(self, log):
        """
        Internal helper to push the completed log dictionary to the logger.
        Includes a safeguard against a non-existent logger.

        Args:
            log (dict): The log entry to push.
        """
        # Safeguard: Do nothing if no logger is attached
        if self._logger:
            self._logger.put_log(log)

```

## `File: TaskTonic\ttTimer.py`
```python
import time, bisect, re

from TaskTonic.ttTonic import ttTonic
from .ttLiquid import ttLiquid
from .ttSparkleStack import ttSparkleStack


class ttTimer(ttLiquid):
    _tt_force_stealth_logging = True
    """
    Base implementatie of timers. Inherit when you're creating a timer class.
    BE AWARE: Never use to create an instance!!
    """
    TIMER_PATTERN = re.compile(r"(tm|tmr|timer)_|_(tm|tmr|timer)")

    def __init__(self, name=None, sparkle_back=None):
        from TaskTonic.ttLogger import ttLog
        super().__init__(name=name, log_mode=ttLog.QUIET)
        if self.__class__ is ttTimer:
            raise RuntimeError('ttTimer is a base class and not meant to be instantiated')
        self.expire = -1  # -1 -> timer not running

        self.catalyst = self.base.catalyst
        self.sparkle_back = sparkle_back if sparkle_back is not None else self._handle_empty_sparkle_back


    def _handle_empty_sparkle_back(self, info):
        """
        Gets called at expiration when sparkle_back is empty. Checks for the valid callback,
         call that method and set sparkle_back for the next time.
         (this can not be done in __init__ because sparkles of the base may not be initialised yet.)
        """
        if self.name.startswith(f'{self.id:02d}.'):
            # standard named, given by TaskTonic: use generic sparkle_back
            name = ''
        else:
            # user named, use specific sparkle_back
            name = self.name.strip().lower().replace(" ", "_")

        try:
            self.sparkle_back = \
                getattr(self.base, f"ttse__on_{name}",
                getattr(self.base, f"ttse__on_tmr_{name}",
                getattr(self.base, "ttse__on_timer",
                None)))
            self.sparkle_back(info)
        except AttributeError:
            raise AttributeError(f"{self.base} does not have a valid sparkle_back for timers")

    # used to sort timers in the list
    def __lt__(self, other):
        return self.expire < other.expire

    def start(self):
        """
        starts timer
        """
        if self.id == -1: raise RuntimeError(f'Cannot start a finished timer')
        if self.period <= 0:
            self.expire = -1
            return self
        if self.expire == -1:
            self.expire = time.time() + self.period
            bisect.insort(self.catalyst.timers, self)
        else:
            raise RuntimeError(f"Can't start a running timer ({self})")
        return self

    def restart(self):
        """
        Restarts timer
         Can be used for timeout on events. Restart timer at every event, and get notified on set timeout
        """
        if self.id == -1: raise RuntimeError(f'Cannot restart a finished timer')
        self.stop()
        self.start()
        return self

    def stop(self):
        """
        stops timer
        """
        self.expire = -1
        if self in self.catalyst.timers:
            self.catalyst.timers.remove(self)
        return self

    def check_on_expiration(self, reference):
        if reference >= self.expire:
            sp_stck = ttSparkleStack()
            info = {'id': self.id, 'name': self.name}
            sp_stck.push(self, 'expired')
            self.sparkle_back(info)
            sp_stck.pop()
            self.reload_on_expire(reference)
            return 0.0  # ==0, expired
        else:
            return self.expire - reference  # >0, not expired, seconds before expiring returned

    def reload_on_expire(self, reference, info):
        raise Exception('Timer callback_and_reload() must be overridden with proper implementation')

    def _on_completion(self):
        self.stop()
        super()._on_completion()

class _ttPeriodicTimer(ttTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, sparkle_back=None):
        super().__init__(name=name, sparkle_back=sparkle_back)
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        self.start()

    def change_timer(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0):
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        return self

class ttTimerSingleShot(_ttPeriodicTimer):
    def reload_on_expire(self, reference):
        self.catalyst.timers.remove(self)
        self.finish()

class ttTimerRepeat(_ttPeriodicTimer):
    def reload_on_expire(self, reference):
        self.catalyst.timers.remove(self)
        self.expire += self.period
        bisect.insort(self.catalyst.timers, self)

class ttTimerPausing(_ttPeriodicTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, sparkle_back=None, start_paused=False):
        self.paused_at = -1
        super().__init__(seconds=seconds, minutes=minutes, hours=hours, days=days, name=name, sparkle_back=sparkle_back)
        if start_paused: self.pause()

    def reload_on_expire(self, reference):
        self.catalyst.timers.remove(self)
        self.paused_at = self.expire
        self.expire = -1

    def pause(self):
        if self.paused_at != -1: return self
        self.paused_at = time.time()
        if self.expire == -1: return self
        self.catalyst.timers.remove(self)
        return self

    def resume(self):
        if self.paused_at == -1 or self.period == 0: return self
        if self.expire == -1:
            self.expire = time.time() + self.period
        else:
            self.expire += time.time() - self.paused_at
        self.pause_at = -1
        bisect.insort(self.catalyst.timers, self)
        return self


```

## `File: TaskTonic\ttLogger.py`
```python
from .ttCatalyst import ttCatalyst
from .ttLiquid import ttLiquid
import enum

# empty log class, base for all loggers in ttLoggers map
# A logservice allways gets te service name log_service

class ttLogOff(ttLiquid):
    _tt_is_service = 'tt_log_service'
    _tt_force_stealth_logging = True

    def put_log(self, log):
        pass

class ttLogService(ttCatalyst):
    _tt_is_service = 'tt_log_service'
    _tt_base_essence = True
    _tt_force_stealth_logging = True

    def __init__(self, name=None, log_mode=None, dont_start_yet=False):
        super().__init__(name, ttLog.OFF, dont_start_yet)


    def _ttss__main_catalyst_finished(self):
        if set(self.service_bases).issubset(self.infusions):
            self.finish()

    def ttse__on_service_base_completed(self, tonic, srv_left, finish_on_count=0):
        if srv_left == finish_on_count:
            self.finish()
        pass

    def put_log(self, log):
        pass

class ttLog(enum.IntEnum):
    """
    Defines the available logging verbosity levels for an essence.
    """

    def _generate_next_value_(name, start, count, last_values):
        return count  # first enum gets int val 0

    STEALTH = enum.auto()  # No logging at all
    OFF = enum.auto()  # Logs lifecycle, creating and finishing of Essence
    QUIET = enum.auto()  # + Logs sparkles, only if log line is given
    FULL = enum.auto()  # + Logs sparkles, always

    @classmethod
    def from_any(cls, value):
        """
        Converts a string, int, or existing ttLog instance
        into a ttLog member.

        Args:
            value (any): The input to convert (e.g., "QUIET", 2).

        Returns:
            ttLog: The corresponding enum member.

        Raises:
            ValueError: If the string or int does not match a valid member.
            TypeError: If the input type is not convertible.
        """
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                raise ValueError(f"'{value}' is not a valid name for {cls.__name__}")

        if isinstance(value, int):
            try:
                return cls(value)
            except ValueError:
                raise ValueError(f"'{value}' is not a valid value for {cls.__name__}")

        raise TypeError(f"Cannot convert type '{type(value).__name__}' to {cls.__name__}")

```

## `File: TaskTonic\ttSparkleStack.py`
```python
import contextvars
"""
The Sparkle stack is used and maintained bij the TaskTonic Framework.
- The stack keeps track of the active sparkles and the calling sparkles.
- The stack is located in the tread local space, so at every moment the stack is accessed you read the
   values of the active stack and therefore the active catalyst

Stack maintenance by TaskTonic:
- With every catalyst that is started the initial context is set at None, '' (no tasktonic context, no sparkle).
   The instance of the catalyst is copied and the calling sparkle is set to None
- Every time a sparkle is called (and putted in the sparkling queue) the active sparkle is also stored in that queue
   as the source sparkle.
- At execution of a sparkle the active sparkle is pushed on stack as a set of instance, sparkle name. Also de source
   sparkle is set. When executing a sparkle you can refer to that source, ie for returning data.
- Every time a ttEssence, or subclass, is initiated the new instance is pushed with sparkle __init__. This is done in 
   the init of ttEssense so only after you call super().__init__() in your subclass. Popping the stack is done by
   TaskTonic after the whole init sequence is completed.
- Every time the ttFormula is executed, before starting tonics are created, the context main_catalyst, "__formula__"
   is pushed.
- Be aware that the calling sparkle is always the executing sparkle even when nested inits are putted on stack


Note on using:    
 Don't create a parameter self.sparkle_stack in your class! At creating the data of the current thread is locked for 
 that parameter. If a method is called from an other thread self.sparkle_stack refers to the first thread!!
 Always use in your method:
    sp_stck = ttSparkleStack()
    sp_stck.push.....
    sp_stck.get_essence...
    etc
    
    or 
    ttSparkleStack().get_essence... # for single use
    
"""

_sparkle_context: contextvars.ContextVar = contextvars.ContextVar("sparkle_context")
class ttSparkleStack:
    """
    Represents the execution context stack for a single thread.

    It tracks the hierarchy of 'Essences' and 'Sparkles' (methods/actions)
    currently being executed, allowing introspection of the caller.
    """
    def __new__(cls):
        try:
            # 1. get thread instance
            instance = _sparkle_context.get()
            return instance
        except LookupError:
            # 2. init if not existing
            instance = super().__new__(cls)
            instance.catalyst = None
            instance.stack = [(None, "", -1)]
            instance._source = (None, "", -1)
            _sparkle_context.set(instance)
            return instance

    def push(self, essence, sparkle):
        """
        Pushes a new execution frame onto the stack.

        note: also push id for when the tonic finished before requesting the data

        Args:
            essence: The object instance context.
            sparkle (str): The name of the action/method being invoked.
        """
        self.stack.append((essence, sparkle, essence.id))

    def pop(self):
        """Removes the top execution frame from the stack."""
        self.stack.pop()

    def get_stack(self, pos=-1):
        return self.stack[pos]

    def get_tonic(self, pos=-1):
        return self.stack[pos][0]

    def get_tonic_name(self, pos=-1):
        essence = self.stack[pos][0]
        return essence.name if essence else ""

    def get_sparkle_name(self, pos=-1):
        return self.stack[pos][1]

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, src):
        self._source = src if len(src) == 3 else \
            ((src[0], src[0].name, src[0].id) if src[0] is not None else
             (None, "", -1))

    @property
    def source_tonic(self):
        return self.source[0]

    @property
    def source_tonic_name(self):
        return "" if self.source[0] is None else self.source[0].name

    @property
    def source_tonic_id(self):
        return self.source[2]

    @property
    def source_sparkle_name(self):
        return self.source[1]

```

## `File: TaskTonic\__main__.py`
```python
import os

START_CODE = """\
from TaskTonic import *

\"\"\"
Welcome to TaskTonic!

This is Hello World, the TaskTonic way.
Look at it, try it, and read the docs
\"\"\"

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
"""


def generate_starter_file():
    filename = "hello_tasktonic.py"

    print("🍹 Welkom bij TaskTonic!")

    if os.path.exists(filename):
        print(f"⚠️ Je hebt al een '{filename}' in deze map staan.")
        return

    # Maak het bestand aan voor de gebruiker
    with open(filename, "w", encoding="utf-8") as f:
        f.write(START_CODE)

    print(f"✅ We hebben een startbestand voor je klaargezet: {filename}")
    print(f"🚀 Open het bestand in je editor, of test het direct met:")
    print(f"   python {filename}")


if __name__ == "__main__":
    generate_starter_file()
```

## `File: TaskTonic\internals\__init__.py`
```python
from .RWLock import RWLock
# from .DataShare import DataShare
from .Store import Store, Item

```

## `File: TaskTonic\internals\RWLock.py`
```python
"""
Tool lib for private classes
"""
import threading


class RWLock:
    """
    Read/Write lock for accessing admin data with version indicator.
    You can read data, until a (or more) writing requests. Then writing is allowed just after all read operations are
    finished. After the last write operation completes, the lock is released and reading is allowed again.
    Every write will increase self.version checking on version will tell you if your data is old. Version wraps to
    zero after 2^31−1 = 2.147.483.647 operations, so use if version != stored_version!!
    """

    # noinspection PyProtectedMember
    class ReadAccessContext:
        def __init__(self, rw_lock_instance):
            self._rw_lock = rw_lock_instance

        def __enter__(self):
            self._rw_lock._acquire_read()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._rw_lock._release_read()
            return False

    # noinspection PyProtectedMember
    class WriteAccessContext:
        def __init__(self, rw_lock_instance):
            self._rw_lock = rw_lock_instance

        def __enter__(self):
            self._rw_lock._acquire_write()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._rw_lock._release_write()
            return False

    def __init__(self):
        self.version = 0
        self._readers_active = 0
        self._writers_waiting = 0
        self._writing = False
        self._lock = threading.Lock()
        self._can_read = threading.Condition(self._lock)
        self._can_write = threading.Condition(self._lock)

    def read_access(self):
        return self.ReadAccessContext(self)

    def write_access(self):
        return self.WriteAccessContext(self)

    def _acquire_read(self):
        with self._lock:
            while self._writing or self._writers_waiting:
                self._can_read.wait()
            self._readers_active += 1

    def _release_read(self):
        with self._lock:
            self._readers_active -= 1
            if not self._readers_active and self._writers_waiting:
                self._can_write.notify_all()

    def _acquire_write(self):
        with self._lock:
            self._writers_waiting += 1
            while self._readers_active > 0 or self._writing:
                self._can_write.wait()
            self._writers_waiting -= 1
            self._writing = True
            self.version = (self.version + 1) & 0b0111_1111_1111_1111_1111_1111_1111_1111

    def _release_write(self):
        with self._lock:
            self._writing = False
            if self._writers_waiting:
                self._can_write.notify_all()
            else:
                self._can_read.notify_all()

```

## `File: TaskTonic\internals\Store.py`
```python
import threading
import re
import contextlib
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple, Callable, Iterable

# ------------------------------------------------------------------------------
# Type definitions
# ------------------------------------------------------------------------------
PathStr = str
# ChangeEvent: (path, new_value, old_value, source_id)
ChangeEvent = Tuple[str, Any, Any, Optional[str]]
ListenerCallback = Callable[[List[ChangeEvent]], None]
DumpData = Iterable[Tuple[str, Any]]


# ------------------------------------------------------------------------------
# Class: StoreLink (The Smart Proxy Node)
# ------------------------------------------------------------------------------
class StoreLink:
    """
    A smart node that resides inside the Store's storage tree.
    It acts as a proxy to another path and manages its own subscriptions.
    """
    __slots__ = ('store', 'alias_path', 'target_path', 'bubble_events')

    def __init__(self, store: 'Store', alias_path: str, target_path: str, bubble_events: bool = False):
        self.store = store
        self.alias_path = alias_path.strip("/")
        self.target_path = target_path.strip("/")
        self.bubble_events = bubble_events

    def setup(self):
        """Called when the link is inserted into the store."""
        if self.bubble_events:
            self.store.at(self.target_path).subscribe(self._on_target_change, recursive=True, owner=self)

    def teardown(self):
        """Called when this link is removed from the store."""
        if self.bubble_events:
            self.store.unsubscribe(self)

    def _on_target_change(self, events):
        """Routes events from the canonical path to the alias path."""
        for path, new_val, old_val, source_id in events:
            # If the canonical item is destroyed, self-destruct the link
            if new_val is None and path == self.target_path:
                self.store.remove_item(self.alias_path)
                continue

            # Route the event deeper if the change happened in a sub-property
            relative_target = path[len(self.target_path):]
            inject_path = f"{self.alias_path}{relative_target}".strip("/")
            self.store._inject_event(inject_path, new_val, old_val, source_id)

    def __repr__(self):
        return f"<StoreLink(bubble_events={self.bubble_events}) {self.alias_path} -> {self.target_path}>"


# ------------------------------------------------------------------------------
# Class: Item (The Cursor/View)
# ------------------------------------------------------------------------------
class Item:
    """
    Represents a specific cursor/view on a path in the Store.
    Acts like a pointer to a specific location in the data tree.
    """
    __slots__ = ('_store', '_path')

    def __init__(self, store: 'Store', path: PathStr):
        self._store = store
        self._path = path.strip("/")

    @property
    def path(self) -> str:
        """Returns the absolute path of this item."""
        return self._path

    @property
    def v(self) -> Any:
        """
        Property for direct value access.
        Writing to .v ALWAYS sends a notification (notify=True), unless inside a silent group.
        """
        return self._store.get_value(self._path)

    @v.setter
    def v(self, value: Any):
        self._store.set_value(self._path, value, notify=True)

    # --- NAVIGATION HELPERS ---

    @property
    def parent(self) -> 'Item':
        """
        Returns an Item cursor pointing to the direct parent container.
        Example: "users/#0/name" -> "users/#0"
        """
        if "/" not in self._path:
            # Already at root or top-level, return root
            return self._store.at("")

        parent_path, _ = self._path.rsplit("/", 1)
        return self._store.at(parent_path)

    @property
    def list_root(self) -> Optional['Item']:
        """
        Walks up the path tree to find the nearest List Item ancestor.
        Identifies ancestors by the '#' syntax (e.g., '#0', 'user#1').

        Use this when a deep property changes (e.g. 'users/#0/address/street')
        and you need the context of the user record ('users/#0').

        Returns None if no list index is found in the path.
        """
        parts = self._path.split("/")

        # Iterate backwards to find the deepest list index
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            # Check syntax: contains '#' and ends with digit (e.g. "#0" or "name#1")
            if "#" in part and part[-1].isdigit():
                root_path = "/".join(parts[:i + 1])
                return self._store.at(root_path)

        return None

    # --- VALUE ACCESS ---

    def val(self, default: Any = None) -> Any:
        """
        Retrieves the value of THIS item (self).
        Returns 'default' if the value is None or item doesn't exist.
        """
        value = self.v
        return value if value is not None else default

    def get(self, key: str, default: Any = None) -> Any:
        """
        Dictionary-style lookup for CHILDREN.
        Retrieves the value of a child item relative to this item.

        Args:
            key: Relative path/key to the child.
            default: Value to return if child doesn't exist.
        """
        target_path = f"{self._path}/{key}" if self._path else key
        val = self._store.get_value(target_path)
        return val if val is not None else default

    # --- SET LOGIC ---

    def set(self, data: Union[DumpData, str, dict, tuple], value: Any = None, notify: bool = True) -> 'Item':
        """
        Versatile setter method.

        Args:
            data:
                - str: Relative path/key to set 'value' to.
                - dict: Batch update {key: val}.
                - list/tuple: Batch update [(key, val)] OR Value if not pairs.
            value: The value to set (only used if data is a string).
            notify: If False, this update will NOT trigger callbacks (Silent Mode).
        """

        # 1. Dictionary Batch
        if isinstance(data, dict):
            with self._store.group(notify=notify):
                for k, v in data.items():
                    self.set(str(k), v, notify=notify)
            return self

        # 2. List or Tuple Batch (STRUCTURAL UPDATE)
        # We only treat it as a batch if it contains pairs.
        if isinstance(data, (list, tuple)):
            # Check if it looks like a batch of pairs
            is_batch = len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) == 2

            if is_batch:
                with self._store.group(notify=notify):
                    for entry in data:
                        k, v = entry
                        self.set(k, v, notify=notify)
                return self

            # If not a batch of pairs, it falls through to be treated as a VALUE (list assignment)

        # 3. Single Key (String) -> WRITE VALUE
        if isinstance(data, str):
            path_str = data

            # Check for Dynamic Syntax (# or .) which needs parsing
            if "#" in path_str or "." in path_str:
                self._smart_set_path(path_str, value, notify)
            else:
                # Static Path -> Fast Write
                if path_str == "" or path_str == ".":
                    self._store.set_value(self._path, value, notify=notify)
                else:
                    target_path = f"{self._path}/{path_str}" if self._path else path_str
                    self._store.set_value(target_path.strip("/"), value, notify=notify)
            return self

        raise ValueError(f"Invalid arguments for set(). Got type: {type(data)}")

    def _smart_set_path(self, relative_path: str, value: Any, notify: bool):
        """Parses path strings with special characters (#, .)."""
        parts = relative_path.split("/")
        cursor = self

        for i, part in enumerate(parts):
            is_last_part = (i == len(parts) - 1)

            if part == "":
                continue
            elif part == "#":
                cursor = cursor.append(None)
            elif part == ".":
                cursor = self._get_last_list_item(cursor, prefix=None)
            elif part.endswith("#"):
                cursor = cursor.append(part[:-1])
            elif part.endswith("."):
                prefix = part[:-1]
                children_keys = cursor._store.get_children_keys(cursor.path)
                if prefix in children_keys:
                    cursor = cursor.at(prefix)
                    cursor = self._get_last_list_item(cursor, prefix=None)
                else:
                    cursor = self._get_last_list_item(cursor, prefix=prefix)
            else:
                cursor = cursor.at(part)

            if is_last_part:
                cursor._store.set_value(cursor.path, value, notify=notify)
                return

    def _get_last_list_item(self, cursor: 'Item', prefix: str = None) -> 'Item':
        children = cursor._store.get_children_keys(cursor.path)
        if prefix:
            pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
        else:
            pattern = re.compile(r"^#(\d+)$")

        max_idx = -1
        last_key = None
        for key in children:
            match = pattern.match(key)
            if match:
                idx = int(match.group(1))
                if idx > max_idx:
                    max_idx = idx
                    last_key = key
        return cursor.at(last_key) if last_key else cursor

    # --- MANIPULATION ---

    def remove(self, subpath: str = None) -> None:
        """
        Remove Item from store
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        self._store.remove_item(target)

    def pop(self, subpath: str = None) -> Any:
        """
        Remove Item from store and return its value after that
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        val = self._store.get_value(target)
        self._store.remove_item(target)
        return val

    def append(self, prefix: str = None) -> 'Item':
        """
        Creates a new list child item with an auto-incrementing index (e.g. #0, #1).
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item
        """
        return self._store.create_list_item(self._path, prefix)

    def extend(self, data_list: List[Any], prefix: str = None) -> 'Item':
        """
        Appends multiple items to the list.
        :param data_list: list of data to append
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item with created list
        """
        if not isinstance(data_list, list):
            raise ValueError("extend() expects a list")
        for data in data_list:
            new_item = self.append(prefix)
            # If data looks like a batch tuple structure, set it as structure
            is_valid_tuple = isinstance(data, (list, tuple)) and len(data) > 0
            if is_valid_tuple and isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                new_item.set(data)
            else:
                new_item.v = data
        return self

    def set_each(self, subpath: str, value: Any, prefix: str = None) -> 'Item':
        """
        Updates a specific subpath for each child of the current item.
        Filters children by prefix if provided.

        Args:
            subpath: The relative path to update (e.g., "brightness" or "state").
            value: The new value to apply.
            prefix: Optional filter for children (e.g., "lamp").

        Returns:
            The current Item instance for method chaining.
        """
        with self.group():
            for child in self.children(prefix=prefix):
                target_item = child.at(subpath)
                target_item.v = value

        return self

    def link_to(self, target_path: str, bubble_events: bool = False) -> 'Item':
        """
        Creates a StoreLink at the current item's path, pointing to a target path.

        Args:
            target_path: The canonical path this link should point to.
            bubble_events: If True, changes on the target will bubble up this alias path.

        Returns:
            The current Item instance for method chaining.
        """
        link_obj = StoreLink(self._store, self._path, target_path, bubble_events=bubble_events)
        self._store.set_value(self._path, link_obj, notify=True)
        return self

    # --- QUERY ---

    def children(self, prefix: str = None) -> Iterator['Item']:
        """Iterates over children keys."""
        for key in self._store.get_children_keys(self._path):
            if prefix is not None:
                target_start = f"{prefix}#"
                if not key.startswith(target_start):
                    continue
            yield self.at(key)

    @property
    def key(self) -> str:
        """Returns the last segment of the path (e.g., '#0' from 'ui/id/#0')."""
        if not self._path:
            return ""
        return self._path.split('/')[-1]

    def dump(self) -> DumpData:
        return self._store.get_subtree(self._path)

    def dumps(self) -> str:
        data = self.dump()
        lines = [f"Dump of <{self._path or 'ROOT'}>:"]
        if not data:
            lines.append("  (empty)")
        else:
            for key, val in data:
                display_key = key if key else "."
                lines.append(f"  {display_key} = {val}")
        return "\n".join(lines)

    # --- CONTEXT MANAGERS ---

    def group(self, source_id: str = None, notify: bool = True):
        """
        Proxy to the Store's group context manager.
        Allows batching updates directly from an Item instance.
        """
        return self._store.group(source_id=source_id, notify=notify)

    def source(self, source_id: str):
        """
        Proxy to the Store's source context manager.
        """
        return self._store.source(source_id=source_id)

    # --- SUBSCRIBING ---

    def subscribe(self, path_or_callback: Union[str, List[str], ListenerCallback],
                  callback: ListenerCallback = None,
                  ignore_source: str = None, recursive: bool = False,
                  exclude: List[str] = None, extract: List[str] = None,
                  trigger_now: bool = False, owner: object = None) -> 'Item':
        """
        Subscribes to changes on this item or its relative sub-paths.
        """
        # Logic to handle item.subscribe(callback) vs item.subscribe("path", callback)
        if callable(path_or_callback):
            # Case: item.subscribe(callback)
            target_path = self._path
            real_callback = path_or_callback
        else:
            # Case: item.subscribe("subpath", callback) or item.subscribe(["a", "b"], callback)
            real_callback = callback
            if isinstance(path_or_callback, list):
                target_path = [f"{self._path}/{p}".strip("/") for p in path_or_callback]
            else:
                target_path = f"{self._path}/{path_or_callback}".strip("/")

        if real_callback is None:
            raise ValueError("A callback must be provided to subscribe().")

        self._store.subscribe(
            target_path,
            real_callback,
            ignore_source=ignore_source,
            recursive=recursive,
            exclude=exclude,
            extract=extract,
            trigger_now=trigger_now,
            owner=owner  # Pass the owner to the store
        )
        return self

    def unsubscribe(self, target: Union[ListenerCallback, object] = None) -> 'Item':
        """
        Unsubscribe from this item.
        If target is None, it removes all subscriptions where THIS item instance is the owner.
        Otherwise, it removes the specific callback or owner provided.
        """
        if target is None:
            # If no target is given, we assume the user wants to clear
            # everything linked to this item's specific path
            self._store.unsubscribe(self._path)
        else:
            self._store.unsubscribe(target)
        return self

    # --- MAGIC ---

    def at(self, subpath: str) -> 'Item':
        """
        Returns Item at subpath. From there you can access the item directly
        :param subpath: subpath of item
        :return:
        """
        full_path = f"{self._path}/{subpath}" if self._path else subpath
        return self._store.at(full_path)

    def __getitem__(self, key: str) -> 'Item':
        return self.at(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.remove(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._store.get_children_keys(self._path))

    def __repr__(self):
        val = self.v
        return f"<Item '{self._path}': {val}>" if val is not None else f"<Item '{self._path}'>"


# ------------------------------------------------------------------------------
# Class: Store (Base Functionality)
# ------------------------------------------------------------------------------
class Store:
    """
    Thread-safe, hierarchical data store (Functional Core).
    Supports:
    - Pub/Sub with Ancestor Lookup (O(depth) instead of O(subscribers)).
    - Grouped updates (Batching).
    - Silent updates (notify=False) per set or per group.
    - MQTT-style wildcards (* and **)
    - Atomic Snapshots via extraction
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._storage: Dict[str, Dict[str, Any]] = {}
        # Pre-allocate root
        self._storage[""] = {"val": None, "children": set()}
        self._subscribers: Dict[str, List[Dict]] = {}
        # Thread Local Storage for batching contexts
        self._local = threading.local()

    def _resolve_deep_path(self, path: str, visited_links: set = None) -> str:
        """
        Resolves paths segment by segment to support deep writing/reading into StoreLinks.
        Example: 'alias/folder/prop' -> hits link at 'alias/folder' -> returns 'target/device/prop'
        """
        if visited_links is None:
            visited_links = set()

        parts = path.strip("/").split("/")
        current_path = ""

        for i, part in enumerate(parts):
            current_path = f"{current_path}/{part}" if current_path else part

            with self._lock:
                entry = self._storage.get(current_path)

            if entry and isinstance(entry["val"], StoreLink):
                if current_path in visited_links:
                    raise ValueError(f"Circular StoreLink detected at {current_path}")
                visited_links.add(current_path)

                target_base = entry["val"].target_path
                remaining_parts = parts[i + 1:]

                if remaining_parts:
                    rest_of_path = "/".join(remaining_parts)
                    new_full_path = f"{target_base}/{rest_of_path}"
                    return self._resolve_deep_path(new_full_path, visited_links)
                else:
                    return target_base

        return current_path

    # --- Context Managers ---

    @contextlib.contextmanager
    def group(self, source_id: str = None, notify: bool = True):
        """
        Context manager to group multiple changes.
        Args:
            source_id: Optional source tag.
            notify: If False, ALL changes inside are silent (overrides set()).
        """
        # 1. Init Locals
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
        if not hasattr(self._local, "current_source"):
            self._local.current_source = None
        if not hasattr(self._local, "group_notify"):
            self._local.group_notify = True

        # 2. Save previous states
        prev_src = self._local.current_source
        prev_notify = self._local.group_notify

        # 3. Apply new context
        if source_id is not None:
            self._local.current_source = source_id

        # Combine parent silence with current request
        self._local.group_notify = prev_notify and notify

        self._local.batch_stack += 1

        try:
            yield
        finally:
            self._local.batch_stack -= 1

            # 4. Flush only if notifying and root/end of batch
            if self._local.batch_stack == 0 and self._local.group_notify:
                self._flush_notifications()

            # 5. Restore
            if source_id is not None:
                self._local.current_source = prev_src
            self._local.group_notify = prev_notify

    @contextlib.contextmanager
    def source(self, source_id: str):
        with self.group(source_id=source_id):
            yield

    # --- Core Access ---

    def at(self, path: str) -> Item:
        return Item(self, path)

    def set(self, path_or_data: Union[str, DumpData, dict], value: Any = None, notify: bool = True) -> Item:
        return self.at("").set(path_or_data, value, notify=notify)

    def get(self, path: str, default: Any = None) -> Any:
        """Shortcut to retrieve value by absolute path."""
        val = self.get_value(path)
        return val if val is not None else default

    def __getitem__(self, path: str) -> Item:
        return self.at(path)

    def __setitem__(self, path: str, value: Any):
        self.at("").set(path, value)

    def __delitem__(self, path: str):
        self.remove_item(path)

    def subscribe(self, path: Union[str, List[str]], callback: ListenerCallback,
                  ignore_source: str = None, recursive: bool = False,
                  exclude: List[str] = None, extract: List[str] = None,
                  trigger_now: bool = False, owner: object = None) -> Union[int, List[int]]:
        """
        Register a callback.
                recursive: If True, trigger on path and descendants.
        :param exclude: List of absolute sub-paths to ignore (e.g. ['sensor/current']).
        :param extract: List of relative fields to return as a flat dict in new_val.
        :param trigger_now: Immediately fire the callback with current state.
        :param owner: Optional object instance to link this subscription to.
        """

        # If a list of paths is provided, subscribe to each one individually
        if isinstance(path, list):
            for p in path:
                self.subscribe(p, callback, ignore_source, recursive,
                               exclude, extract, trigger_now, owner)
            return

        clean_path = path.strip("/")
        clean_exclude = [e.strip("/") for e in exclude] if exclude else []

        # Determine static prefix for O(1) lookups and compile regex if wildcard is used
        is_wildcard = "*" in clean_path
        static_prefix = clean_path
        pattern = None

        if is_wildcard:
            static_prefix = clean_path.split("*")[0].rstrip("/")

            # Convert MQTT-style to regex safely using a placeholder
            regex_str = clean_path.replace("**", "\0").replace("*", "[^/]+").replace("\0", ".*")
            regex_str = "^" + regex_str

            if not recursive:
                regex_str += "$"
            pattern = re.compile(regex_str)

        with self._lock:
            if static_prefix not in self._subscribers:
                self._subscribers[static_prefix] = []

            # Detect owner if not explicitly provided
            effective_owner = owner
            if effective_owner is None and hasattr(callback, "__self__"):
                effective_owner = callback.__self__

            self._subscribers[static_prefix].append({
                "cb": callback,
                "owner": effective_owner,
                "ignore_source": ignore_source,
                "recursive": recursive,
                "exclude": clean_exclude,
                "extract": extract,
                "pattern": pattern,
                "raw_path": clean_path
            })

        if trigger_now:
            self._trigger_init_event(clean_path, callback, extract, pattern)

    def unsubscribe(self, target: Union[ListenerCallback, object, List[Any]]):
        """
        Remove subscriptions by callback function or class instance (owner).
        """
        if isinstance(target, list):
            for t in target:
                self.unsubscribe(t)
            return

        with self._lock:
            for path in list(self._subscribers.keys()):
                # Filter based on callback or owner
                self._subscribers[path] = [
                    s for s in self._subscribers[path]
                    if s["cb"] != target and s["owner"] != target
                ]

                if not self._subscribers[path]:
                    del self._subscribers[path]

    def _trigger_init_event(self, path: str, callback: ListenerCallback,
                            extract: List[str] = None, pattern: re.Pattern = None):
        """Helper to fire immediate initial state for UI components."""
        events = []

        if pattern:
            # --- WILDCARD INIT ---
            static_prefix = path.split("*")[0].rstrip("/")
            matched_bases = set()

            # Find all existing paths that match the wildcard pattern
            with self._lock:
                for stored_path in self._storage.keys():
                    if stored_path.startswith(static_prefix) and pattern.match(stored_path):
                        base_path = pattern.match(stored_path).group(0)
                        matched_bases.add(base_path)

            if not matched_bases:
                return

            # Build a snapshot for each matched base path
            for base_path in matched_bases:
                if extract:
                    snapshot = {}
                    for field in extract:
                        if field == ".":
                            snapshot["."] = self.get_value(base_path)
                        else:
                            target = f"{base_path}/{field}" if base_path else field
                            snapshot[field] = self.get_value(target)
                    events.append((base_path, snapshot, None, "init"))
                else:
                    events.append((base_path, self.get_value(base_path), None, "init"))
        else:
            # --- STANDARD INIT ---
            current_val = self.get_value(path)

            if extract:
                snapshot = {}
                for field in extract:
                    if field == ".":
                        snapshot["."] = current_val
                    else:
                        target = f"{path}/{field}" if path else field
                        snapshot[field] = self.get_value(target)
                current_val = snapshot

            events.append((path, current_val, None, "init"))

        if events:
            try:
                callback(events)
            except Exception as e:
                print(f"[Store] Init callback error {path}: {e}")

    def dump(self) -> DumpData:
        return self.at("").dump()

    def dumps(self) -> str:
        return self.at("").dumps()

    # --- Implementation Details ---

    def _ensure_node(self, path: str):
        parts = path.split("/")
        current_path = ""
        for i, part in enumerate(parts):
            parent_path = current_path
            if i > 0:
                current_path = f"{current_path}/{part}"
            else:
                current_path = part

            if current_path not in self._storage:
                self._storage[current_path] = {"val": None, "children": set()}
                parent_entry = self._storage.get(parent_path)
                if parent_entry:
                    parent_entry["children"].add(part)

    def set_value(self, path: str, value: Any, notify: bool = True):
        clean_path = path.strip("/")

        with self._lock:
            # If we are directly storing a StoreLink, assign it at the explicit alias path
            if isinstance(value, StoreLink):
                entry = self._storage.get(clean_path)
                old_val = entry["val"] if entry else None
                if isinstance(old_val, StoreLink):
                    old_val.teardown()

                self._ensure_node(clean_path)
                self._storage[clean_path]["val"] = value
                value.setup()

                if notify:
                    self._queue_notification(clean_path, value, old_val)
                return

            # For normal values, resolve the path to support deep writing into links
            resolved_path = self._resolve_deep_path(clean_path)
            entry = self._storage.get(resolved_path)

            if entry:
                old_value = entry["val"]
                entry["val"] = value
            else:
                self._ensure_node(resolved_path)
                entry = self._storage[resolved_path]
                old_value = entry["val"]
                entry["val"] = value

        if notify and old_value != value:
            self._queue_notification(resolved_path, value, old_value)

    def get_value(self, path: str) -> Any:
        resolved_path = self._resolve_deep_path(path.strip("/"))
        with self._lock:
            if resolved_path in self._storage:
                return self._storage[resolved_path]["val"]
            return None

    def remove_item(self, path: str):
        clean_path = path.strip("/")
        if clean_path == "":
            with self._lock:
                self._storage[""]["val"] = None
            return

        with self._lock:
            # Check if the exact path itself is a StoreLink.
            # If it is, we want to remove the link, NOT follow it and delete the target!
            entry = self._storage.get(clean_path)
            if entry and isinstance(entry["val"], StoreLink):
                resolved_path = clean_path
            else:
                resolved_path = self._resolve_deep_path(clean_path)

            if resolved_path not in self._storage:
                return

            old_val = self._storage[resolved_path]["val"]
            if isinstance(old_val, StoreLink):
                old_val.teardown()

            self._queue_notification(resolved_path, None, old_val)
            self._recursive_delete(resolved_path)

            if "/" in resolved_path:
                parent_path, child_key = resolved_path.rsplit("/", 1)
            else:
                parent_path, child_key = "", resolved_path

            if parent_path in self._storage:
                self._storage[parent_path]["children"].discard(child_key)

    def _recursive_delete(self, path: str):
        if path not in self._storage:
            return
        children = list(self._storage[path]["children"])
        for child_key in children:
            child_path = f"{path}/{child_key}"
            if child_path in self._storage:
                old_val = self._storage[child_path]["val"]
                if isinstance(old_val, StoreLink):
                    old_val.teardown()
                self._queue_notification(child_path, None, old_val)
            self._recursive_delete(child_path)

        if path in self._subscribers:
            del self._subscribers[path]
        del self._storage[path]

    def create_list_item(self, base_path: str, prefix: str = None) -> Item:
        clean_path = base_path.strip("/")
        with self._lock:
            if clean_path not in self._storage:
                self._ensure_node(clean_path)

            children = self._storage[clean_path]["children"]
            max_idx = -1

            if prefix:
                pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
            else:
                pattern = re.compile(r"^#(\d+)$")

            for child in children:
                match = pattern.match(child)
                if match:
                    idx = int(match.group(1))
                    if idx > max_idx:
                        max_idx = idx

            new_key = f"{prefix}#{max_idx + 1}" if prefix else f"#{max_idx + 1}"
            new_path = f"{clean_path}/{new_key}" if clean_path else new_key

            self.set_value(new_path, None)
            return self.at(new_path)

    def get_children_keys(self, path: str) -> List[str]:
        resolved_path = self._resolve_deep_path(path.strip("/"))
        with self._lock:
            if resolved_path in self._storage:
                return sorted(list(self._storage[resolved_path]["children"]))
            return []

    def get_subtree(self, base_path: str) -> DumpData:
        clean_base = base_path.strip("/")
        result = []
        with self._lock:
            for path in sorted(self._storage.keys()):
                if clean_base and len(path) < len(clean_base):
                    continue
                if path not in self._storage:
                    continue
                val = self._storage[path]["val"]
                if val is not None:
                    if clean_base == "":
                        is_self = (path == "")
                        is_child = (path != "")
                    else:
                        is_self = (path == clean_base)
                        is_child = path.startswith(clean_base + "/")

                    if is_self or is_child:
                        rel_key = "" if is_self else (path if clean_base == "" else path[len(clean_base) + 1:])
                        # If exporting a StoreLink, format it so it can be restored later
                        if isinstance(val, StoreLink):
                            link_data = {"$link": val.target_path, "bubble_events": val.bubble_events}
                            result.append((rel_key, link_data))
                        else:
                            result.append((rel_key, val))
        return result

    def _queue_notification(self, path: str, new_val: Any, old_val: Any):
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
            self._local.group_notify = True

        # If group is silent, drop event immediately
        if hasattr(self._local, "group_notify") and not self._local.group_notify:
            return

        if not hasattr(self._local, "current_source"):
            self._local.current_source = None

        event = (path, new_val, old_val, self._local.current_source)
        self._local.pending_changes.append(event)

        if self._local.batch_stack == 0:
            self._flush_notifications()

    def _inject_event(self, path: str, new_val: Any, old_val: Any, source_id: str = None):
        """Allows StoreLinks to manually inject events into the current batch sequence."""
        if not hasattr(self._local, "pending_changes"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
            self._local.group_notify = True
            self._local.current_source = None

        if hasattr(self._local, "group_notify") and not self._local.group_notify:
            return

        event = (path, new_val, old_val, source_id)
        self._local.pending_changes.append(event)

        if self._local.batch_stack == 0:
            self._flush_notifications()

    def _flush_notifications(self):
        # OPTIMIZED: Ancestor Lookup Strategy
        if not hasattr(self._local, "pending_changes") or not self._local.pending_changes:
            return

        events = self._local.pending_changes
        self._local.pending_changes = []

        # 1. Identify all relevant paths (the path itself + all ancestors)
        relevant_sub_paths = set()
        for event in events:
            path = event[0]
            relevant_sub_paths.add(path)
            while "/" in path:
                path, _ = path.rsplit("/", 1)
                relevant_sub_paths.add(path)
            if path != "":
                relevant_sub_paths.add("")  # Root always relevant

        # 2. Retrieve only subscribers on those paths (O(1) lookups)
        with self._lock:
            relevant_entries = []
            for sub_path in relevant_sub_paths:
                if sub_path in self._subscribers:
                    relevant_entries.append((sub_path, self._subscribers[sub_path]))

        # 3. Process events per subscriber safely through a clean pipeline
        for sub_path, sub_entries in relevant_entries:
            # Get all events relevant to this base lookup path
            events_in_scope = [e for e in events if e[0] == sub_path or e[0].startswith(sub_path + "/")]

            if not events_in_scope:
                continue

            for entry in sub_entries:
                filtered_events = []

                # --- A. Apply All Filters ---
                for e in events_in_scope:
                    ep = e[0]

                    # 1. Source filter
                    if entry["ignore_source"] is not None and e[3] == entry["ignore_source"]:
                        continue

                    # 2. Wildcard Regex filter
                    pattern = entry.get("pattern")
                    if pattern and not pattern.match(ep):
                        continue

                    # 3. Recursive filter
                    # If not recursive, the path must match exactly.
                    # Wildcards handle non-recursive via a $ at the end of the regex.
                    if not entry["recursive"]:
                        if pattern:
                            pass
                        elif ep != sub_path:
                            continue

                    # 4. Exclude filter
                    if entry["exclude"]:
                        if any(ep == ex or ep.startswith(ex + "/") for ex in entry["exclude"]):
                            continue

                    filtered_events.append(e)

                if not filtered_events:
                    continue

                # --- B. Apply Snapshots (extract) ---
                extract_fields = entry.get("extract")
                if extract_fields:
                    final_events = []
                    seen_bases = set()

                    for e in filtered_events:
                        # Find the correct base path for the snapshot.
                        # Wildcards use the dynamically matched regex segment.
                        if pattern:
                            base_path = pattern.match(e[0]).group(0)
                        else:
                            base_path = sub_path

                        # Deduplicate batch updates for the same snapshot root
                        if base_path in seen_bases:
                            continue
                        seen_bases.add(base_path)

                        # Generate the atomic snapshot
                        snapshot = {}
                        for field in extract_fields:
                            if field == ".":
                                snapshot["."] = self.get_value(base_path)
                            else:
                                target = f"{base_path}/{field}" if base_path else field
                                snapshot[field] = self.get_value(target)

                        final_events.append((base_path, snapshot, e[2], e[3]))
                else:
                    final_events = filtered_events

                # --- C. Emit Callback ---
                try:
                    entry["cb"](final_events)
                except Exception as e:
                    print(f"[Store] Callback error {sub_path}: {e}")

```

## `File: TaskTonic\internals\Store - kopie.py`
```python
import threading
import re
import contextlib
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple, Callable, Iterable

# ------------------------------------------------------------------------------
# Type definitions
# ------------------------------------------------------------------------------
PathStr = str
# ChangeEvent: (path, new_value, old_value, source_id)
ChangeEvent = Tuple[str, Any, Any, Optional[str]]
ListenerCallback = Callable[[List[ChangeEvent]], None]
DumpData = Iterable[Tuple[str, Any]]


# ------------------------------------------------------------------------------
# Class: Item (The Cursor/View)
# ------------------------------------------------------------------------------
class Item:
    """
    Represents a specific cursor/view on a path in the Store.
    Acts like a pointer to a specific location in the data tree.
    """
    __slots__ = ('_store', '_path')

    def __init__(self, store: 'Store', path: PathStr):
        self._store = store
        self._path = path.strip("/")

    @property
    def path(self) -> str:
        """Returns the absolute path of this item."""
        return self._path

    @property
    def v(self) -> Any:
        """
        Property for direct value access.
        Writing to .v ALWAYS sends a notification (notify=True), unless inside a silent group.
        """
        return self._store.get_value(self._path)

    @v.setter
    def v(self, value: Any):
        self._store.set_value(self._path, value, notify=True)

    # --- NAVIGATION HELPERS ---

    @property
    def parent(self) -> 'Item':
        """
        Returns an Item cursor pointing to the direct parent container.
        Example: "users/#0/name" -> "users/#0"
        """
        if "/" not in self._path:
            # Already at root or top-level, return root
            return self._store.at("")

        parent_path, _ = self._path.rsplit("/", 1)
        return self._store.at(parent_path)

    @property
    def list_root(self) -> Optional['Item']:
        """
        Walks up the path tree to find the nearest List Item ancestor.
        Identifies ancestors by the '#' syntax (e.g., '#0', 'user#1').

        Use this when a deep property changes (e.g. 'users/#0/address/street')
        and you need the context of the user record ('users/#0').

        Returns None if no list index is found in the path.
        """
        parts = self._path.split("/")

        # Iterate backwards to find the deepest list index
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            # Check syntax: contains '#' and ends with digit (e.g. "#0" or "name#1")
            if "#" in part and part[-1].isdigit():
                root_path = "/".join(parts[:i + 1])
                return self._store.at(root_path)

        return None

    # --- VALUE ACCESS ---

    def val(self, default: Any = None) -> Any:
        """
        Retrieves the value of THIS item (self).
        Returns 'default' if the value is None or item doesn't exist.
        """
        value = self.v
        return value if value is not None else default

    def get(self, key: str, default: Any = None) -> Any:
        """
        Dictionary-style lookup for CHILDREN.
        Retrieves the value of a child item relative to this item.

        Args:
            key: Relative path/key to the child.
            default: Value to return if child doesn't exist.
        """
        target_path = f"{self._path}/{key}" if self._path else key
        val = self._store.get_value(target_path)
        return val if val is not None else default

    # --- SET LOGIC ---

    def set(self, data: Union[DumpData, str, dict, tuple], value: Any = None, notify: bool = True) -> 'Item':
        """
        Versatile setter method.

        Args:
            data:
                - str: Relative path/key to set 'value' to.
                - dict: Batch update {key: val}.
                - list/tuple: Batch update [(key, val)] OR Value if not pairs.
            value: The value to set (only used if data is a string).
            notify: If False, this update will NOT trigger callbacks (Silent Mode).
        """

        # 1. Dictionary Batch
        if isinstance(data, dict):
            with self._store.group(notify=notify):
                for k, v in data.items():
                    self.set(str(k), v, notify=notify)
            return self

        # 2. List or Tuple Batch (STRUCTURAL UPDATE)
        # We only treat it as a batch if it contains pairs.
        if isinstance(data, (list, tuple)):
            # Check if it looks like a batch of pairs
            is_batch = len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) == 2

            if is_batch:
                with self._store.group(notify=notify):
                    for entry in data:
                        k, v = entry
                        self.set(k, v, notify=notify)
                return self

            # If not a batch of pairs, it falls through to be treated as a VALUE (list assignment)

        # 3. Single Key (String) -> WRITE VALUE
        if isinstance(data, str):
            path_str = data

            # Check for Dynamic Syntax (# or .) which needs parsing
            if "#" in path_str or "." in path_str:
                self._smart_set_path(path_str, value, notify)
            else:
                # Static Path -> Fast Write
                if path_str == "" or path_str == ".":
                    self._store.set_value(self._path, value, notify=notify)
                else:
                    target_path = f"{self._path}/{path_str}" if self._path else path_str
                    self._store.set_value(target_path.strip("/"), value, notify=notify)
            return self

        raise ValueError(f"Invalid arguments for set(). Got type: {type(data)}")

    def _smart_set_path(self, relative_path: str, value: Any, notify: bool):
        """Parses path strings with special characters (#, .)."""
        parts = relative_path.split("/")
        cursor = self

        for i, part in enumerate(parts):
            is_last_part = (i == len(parts) - 1)

            if part == "":
                continue
            elif part == "#":
                cursor = cursor.append(None)
            elif part == ".":
                cursor = self._get_last_list_item(cursor, prefix=None)
            elif part.endswith("#"):
                cursor = cursor.append(part[:-1])
            elif part.endswith("."):
                prefix = part[:-1]
                children_keys = cursor._store.get_children_keys(cursor.path)
                if prefix in children_keys:
                    cursor = cursor.at(prefix)
                    cursor = self._get_last_list_item(cursor, prefix=None)
                else:
                    cursor = self._get_last_list_item(cursor, prefix=prefix)
            else:
                cursor = cursor.at(part)

            if is_last_part:
                cursor._store.set_value(cursor.path, value, notify=notify)
                return

    def _get_last_list_item(self, cursor: 'Item', prefix: str = None) -> 'Item':
        children = cursor._store.get_children_keys(cursor.path)
        if prefix:
            pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
        else:
            pattern = re.compile(r"^#(\d+)$")

        max_idx = -1
        last_key = None
        for key in children:
            match = pattern.match(key)
            if match:
                idx = int(match.group(1))
                if idx > max_idx:
                    max_idx = idx
                    last_key = key
        return cursor.at(last_key) if last_key else cursor

    # --- MANIPULATION ---

    def remove(self, subpath: str = None) -> None:
        """
        Remove Item from store
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        self._store.remove_item(target)

    def pop(self, subpath: str = None) -> Any:
        """
        Remove Item from store and return its value after that
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        val = self._store.get_value(target)
        self._store.remove_item(target)
        return val

    def append(self, prefix: str = None) -> 'Item':
        """
        Creates a new list child item with an auto-incrementing index (e.g. #0, #1).
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item
        """
        return self._store.create_list_item(self._path, prefix)

    def extend(self, data_list: List[Any], prefix: str = None) -> 'Item':
        """
        Appends multiple items to the list.
        :param data_list: list of data to append
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item with created list
        """

        if not isinstance(data_list, list):
            raise ValueError("extend() expects a list")
        for data in data_list:
            new_item = self.append(prefix)
            # If data looks like a batch tuple structure, set it as structure
            # Ensure line length < 120 chars
            is_valid_tuple = isinstance(data, (list, tuple)) and len(data) > 0
            if is_valid_tuple and isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                new_item.set(data)
            else:
                new_item.v = data
        return self

    # --- QUERY ---

    def children(self, prefix: str = None) -> Iterator['Item']:
        """Iterates over children keys."""
        for key in self._store.get_children_keys(self._path):
            if prefix is not None:
                target_start = f"{prefix}#"
                if not key.startswith(target_start):
                    continue
            yield self.at(key)

    @property
    def key(self) -> str:
        """Returns the last segment of the path (e.g., '#0' from 'ui/id/#0')."""
        if not self._path: return ""
        return self._path.split('/')[-1]

    def dump(self) -> DumpData:
        return self._store.get_subtree(self._path)

    def dumps(self) -> str:
        data = self.dump()
        lines = [f"Dump of <{self._path or 'ROOT'}>:"]
        if not data:
            lines.append("  (empty)")
        else:
            for key, val in data:
                display_key = key if key else "."
                lines.append(f"  {display_key} = {val}")
        return "\n".join(lines)

    # --- CONTEXT MANAGERS ---

    def group(self, source_id: str = None, notify: bool = True):
        """
        Proxy to the Store's group context manager.
        Allows batching updates directly from an Item instance.
        """
        return self._store.group(source_id=source_id, notify=notify)

    def source(self, source_id: str):
        """
        Proxy to the Store's source context manager.
        """
        return self._store.source(source_id=source_id)

    # --- SUBSCRIBING ---

    def subscribe(self, path_or_callback: Union[str, List[str], ListenerCallback],
                  callback: ListenerCallback = None,
                  ignore_source: str = None, recursive: bool = False,
                  exclude: List[str] = None, extract: List[str] = None,
                  trigger_now: bool = False, owner: object = None) -> 'Item':
        """
        Subscribes to changes on this item or its relative sub-paths.
        """
        # Logic to handle item.subscribe(callback) vs item.subscribe("path", callback)
        if callable(path_or_callback):
            # Case: item.subscribe(callback)
            target_path = self._path
            real_callback = path_or_callback
        else:
            # Case: item.subscribe("subpath", callback) or item.subscribe(["a", "b"], callback)
            real_callback = callback
            if isinstance(path_or_callback, list):
                target_path = [f"{self._path}/{p}".strip("/") for p in path_or_callback]
            else:
                target_path = f"{self._path}/{path_or_callback}".strip("/")

        if real_callback is None:
            raise ValueError("A callback must be provided to subscribe().")

        self._store.subscribe(
            target_path,
            real_callback,
            ignore_source=ignore_source,
            recursive=recursive,
            exclude=exclude,
            extract=extract,
            trigger_now=trigger_now,
            owner=owner  # Pass the owner to the store
        )
        return self

    def unsubscribe(self, target: Union[ListenerCallback, object] = None) -> 'Item':
        """
        Unsubscribe from this item.
        If target is None, it removes all subscriptions where THIS item instance is the owner.
        Otherwise, it removes the specific callback or owner provided.
        """
        if target is None:
            # If no target is given, we assume the user wants to clear
            # everything linked to this item's specific path
            self._store.unsubscribe(self._path)
        else:
            self._store.unsubscribe(target)
        return self

    # --- MAGIC ---

    def at(self, subpath: str) -> 'Item':
        """
        Returns Item at subpath. From there you can access the item directly
        :param subpath: subpath of item
        :return:
        """
        full_path = f"{self._path}/{subpath}" if self._path else subpath
        return self._store.at(full_path)

    def __getitem__(self, key: str) -> 'Item':
        return self.at(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.remove(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._store.get_children_keys(self._path))

    def __repr__(self):
        val = self.v
        return f"<Item '{self._path}': {val}>" if val is not None else f"<Item '{self._path}'>"


# ------------------------------------------------------------------------------
# Class: Store (Base Functionality)
# ------------------------------------------------------------------------------
class Store:
    """
    Thread-safe, hierarchical data store (Functional Core).
    Supports:
    - Pub/Sub with Ancestor Lookup (O(depth) instead of O(subscribers)).
    - Grouped updates (Batching).
    - Silent updates (notify=False) per set or per group.
    - MQTT-style wildcards (* and **)
    - Atomic Snapshots via extraction
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._storage: Dict[str, Dict[str, Any]] = {}
        # Pre-allocate root
        self._storage[""] = {"val": None, "children": set()}
        self._subscribers: Dict[str, List[Dict]] = {}
        # Thread Local Storage for batching contexts
        self._local = threading.local()

    # --- Context Managers ---

    @contextlib.contextmanager
    def group(self, source_id: str = None, notify: bool = True):
        """
        Context manager to group multiple changes.
        Args:
            source_id: Optional source tag.
            notify: If False, ALL changes inside are silent (overrides set()).
        """
        # 1. Init Locals
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
        if not hasattr(self._local, "current_source"):
            self._local.current_source = None
        if not hasattr(self._local, "group_notify"):
            self._local.group_notify = True

        # 2. Save previous states
        prev_src = self._local.current_source
        prev_notify = self._local.group_notify

        # 3. Apply new context
        if source_id is not None:
            self._local.current_source = source_id

        # Combine parent silence with current request
        self._local.group_notify = prev_notify and notify

        self._local.batch_stack += 1

        try:
            yield
        finally:
            self._local.batch_stack -= 1

            # 4. Flush only if notifying and root/end of batch
            if self._local.batch_stack == 0 and self._local.group_notify:
                self._flush_notifications()

            # 5. Restore
            if source_id is not None:
                self._local.current_source = prev_src
            self._local.group_notify = prev_notify

    @contextlib.contextmanager
    def source(self, source_id: str):
        with self.group(source_id=source_id):
            yield

    # --- Core Access ---

    def at(self, path: str) -> Item:
        return Item(self, path)

    def set(self, path_or_data: Union[str, DumpData, dict], value: Any = None, notify: bool = True) -> Item:
        return self.at("").set(path_or_data, value, notify=notify)

    def get(self, path: str, default: Any = None) -> Any:
        """Shortcut to retrieve value by absolute path."""
        val = self.get_value(path)
        return val if val is not None else default

    def __getitem__(self, path: str) -> Item:
        return self.at(path)

    def __setitem__(self, path: str, value: Any):
        self.at("").set(path, value)

    def __delitem__(self, path: str):
        self.remove_item(path)

    def subscribe(self, path: Union[str, List[str]], callback: ListenerCallback,
                  ignore_source: str = None, recursive: bool = False,
                  exclude: List[str] = None, extract: List[str] = None,
                  trigger_now: bool = False, owner: object = None) -> Union[int, List[int]]:
        """
        Register a callback.
                recursive: If True, trigger on path and descendants.
        :param exclude: List of absolute sub-paths to ignore (e.g. ['sensor/current']).
        :param extract: List of relative fields to return as a flat dict in new_val.
        :param trigger_now: Immediately fire the callback with current state.
        :param owner: Optional object instance to link this subscription to.
        """

        # If a list of paths is provided, subscribe to each one individually
        if isinstance(path, list):
            for p in path:
                self.subscribe(p, callback, ignore_source, recursive,
                               exclude, extract, trigger_now, owner)
            return

        clean_path = path.strip("/")
        clean_exclude = [e.strip("/") for e in exclude] if exclude else []

        # Determine static prefix for O(1) lookups and compile regex if wildcard is used
        is_wildcard = "*" in clean_path
        static_prefix = clean_path
        pattern = None

        if is_wildcard:
            static_prefix = clean_path.split("*")[0].rstrip("/")

            # Convert MQTT-style to regex safely using a placeholder
            regex_str = clean_path.replace("**", "\0").replace("*", "[^/]+").replace("\0", ".*")
            regex_str = "^" + regex_str

            if not recursive:
                regex_str += "$"
            pattern = re.compile(regex_str)

        with self._lock:
            if static_prefix not in self._subscribers:
                self._subscribers[static_prefix] = []

            # Detect owner if not explicitly provided
            effective_owner = owner
            if effective_owner is None and hasattr(callback, "__self__"):
                effective_owner = callback.__self__

            self._subscribers[static_prefix].append({
                "cb": callback,
                "owner": effective_owner,
                "ignore_source": ignore_source,
                "recursive": recursive,
                "exclude": clean_exclude,
                "extract": extract,
                "pattern": pattern,
                "raw_path": clean_path
            })

        if trigger_now:
            self._trigger_init_event(clean_path, callback, extract, pattern)

    def unsubscribe(self, target: Union[ListenerCallback, object, List[Any]]):
        """
        Remove subscriptions by callback function or class instance (owner).
        """
        if isinstance(target, list):
            for t in target:
                self.unsubscribe(t)
            return

        with self._lock:
            for path in list(self._subscribers.keys()):
                # Filter based on callback or owner
                self._subscribers[path] = [
                    s for s in self._subscribers[path]
                    if s["cb"] != target and s["owner"] != target
                ]

                if not self._subscribers[path]:
                    del self._subscribers[path]

    def _trigger_init_event(self, path: str, callback: ListenerCallback,
                            extract: List[str] = None, pattern: re.Pattern = None):
        """Helper to fire immediate initial state for UI components."""
        events = []

        if pattern:
            # --- WILDCARD INIT ---
            static_prefix = path.split("*")[0].rstrip("/")
            matched_bases = set()

            # Find all existing paths that match the wildcard pattern
            with self._lock:
                for stored_path in self._storage.keys():
                    if stored_path.startswith(static_prefix) and pattern.match(stored_path):
                        base_path = pattern.match(stored_path).group(0)
                        matched_bases.add(base_path)

            if not matched_bases:
                return

            # Build a snapshot for each matched base path
            for base_path in matched_bases:
                if extract:
                    snapshot = {}
                    for field in extract:
                        if field == ".":
                            snapshot["."] = self.get_value(base_path)
                        else:
                            target = f"{base_path}/{field}" if base_path else field
                            snapshot[field] = self.get_value(target)
                    events.append((base_path, snapshot, None, "init"))
                else:
                    events.append((base_path, self.get_value(base_path), None, "init"))
        else:
            # --- STANDARD INIT ---
            current_val = self.get_value(path)

            if extract:
                snapshot = {}
                for field in extract:
                    if field == ".":
                        snapshot["."] = current_val
                    else:
                        target = f"{path}/{field}" if path else field
                        snapshot[field] = self.get_value(target)
                current_val = snapshot

            events.append((path, current_val, None, "init"))

        if events:
            try:
                callback(events)
            except Exception as e:
                print(f"[Store] Init callback error {path}: {e}")

    def dump(self) -> DumpData:
        return self.at("").dump()

    def dumps(self) -> str:
        return self.at("").dumps()

    # --- Implementation Details ---

    def _ensure_node(self, path: str):
        parts = path.split("/")
        current_path = ""
        for i, part in enumerate(parts):
            parent_path = current_path
            if i > 0:
                current_path = f"{current_path}/{part}"
            else:
                current_path = part

            if current_path not in self._storage:
                self._storage[current_path] = {"val": None, "children": set()}
                parent_entry = self._storage.get(parent_path)
                if parent_entry:
                    parent_entry["children"].add(part)

    def set_value(self, path: str, value: Any, notify: bool = True):
        # Optimized Fast Path
        with self._lock:
            if path in self._storage:
                entry = self._storage[path]
                old_value = entry["val"]
                entry["val"] = value
            else:
                self._ensure_node(path)
                entry = self._storage[path]
                old_value = entry["val"]
                entry["val"] = value

        if notify and old_value != value:
            self._queue_notification(path, value, old_value)

    def get_value(self, path: str) -> Any:
        with self._lock:
            if path in self._storage:
                return self._storage[path]["val"]
            return None

    def remove_item(self, path: str):
        clean_path = path.strip("/")
        if clean_path == "":
            with self._lock:
                self._storage[""]["val"] = None
            return

        with self._lock:
            if clean_path not in self._storage:
                return
            self._queue_notification(clean_path, None, self._storage[clean_path]["val"])
            self._recursive_delete(clean_path)

            if "/" in clean_path:
                parent_path, child_key = clean_path.rsplit("/", 1)
            else:
                parent_path, child_key = "", clean_path

            if parent_path in self._storage:
                self._storage[parent_path]["children"].discard(child_key)

    def _recursive_delete(self, path: str):
        if path not in self._storage:
            return
        children = list(self._storage[path]["children"])
        for child_key in children:
            child_path = f"{path}/{child_key}"
            if child_path in self._storage:
                self._queue_notification(child_path, None, self._storage[child_path]["val"])
            self._recursive_delete(child_path)

        if path in self._subscribers:
            del self._subscribers[path]
        del self._storage[path]

    def create_list_item(self, base_path: str, prefix: str = None) -> Item:
        clean_path = base_path.strip("/")
        with self._lock:
            if clean_path not in self._storage:
                self._ensure_node(clean_path)

            children = self._storage[clean_path]["children"]
            max_idx = -1

            if prefix:
                pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
            else:
                pattern = re.compile(r"^#(\d+)$")

            for child in children:
                match = pattern.match(child)
                if match:
                    idx = int(match.group(1))
                    if idx > max_idx:
                        max_idx = idx

            new_key = f"{prefix}#{max_idx + 1}" if prefix else f"#{max_idx + 1}"
            new_path = f"{clean_path}/{new_key}" if clean_path else new_key

            self.set_value(new_path, None)
            return self.at(new_path)

    def get_children_keys(self, path: str) -> List[str]:
        clean_path = path.strip("/")
        with self._lock:
            if clean_path in self._storage:
                return sorted(list(self._storage[clean_path]["children"]))
            return []

    def get_subtree(self, base_path: str) -> DumpData:
        clean_base = base_path.strip("/")
        result = []
        with self._lock:
            for path in sorted(self._storage.keys()):
                if clean_base and len(path) < len(clean_base):
                    continue
                if path not in self._storage:
                    continue
                val = self._storage[path]["val"]
                if val is not None:
                    if clean_base == "":
                        is_self = (path == "")
                        is_child = (path != "")
                    else:
                        is_self = (path == clean_base)
                        is_child = path.startswith(clean_base + "/")
                    if is_self or is_child:
                        rel_key = "" if is_self else (path if clean_base == "" else path[len(clean_base) + 1:])
                        result.append((rel_key, val))
        return result

    def _queue_notification(self, path: str, new_val: Any, old_val: Any):
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
            self._local.group_notify = True

        # If group is silent, drop event immediately
        if hasattr(self._local, "group_notify") and not self._local.group_notify:
            return

        if not hasattr(self._local, "current_source"):
            self._local.current_source = None

        event = (path, new_val, old_val, self._local.current_source)
        self._local.pending_changes.append(event)

        if self._local.batch_stack == 0:
            self._flush_notifications()

    def _flush_notifications(self):
        # OPTIMIZED: Ancestor Lookup Strategy
        if not hasattr(self._local, "pending_changes") or not self._local.pending_changes:
            return

        events = self._local.pending_changes
        self._local.pending_changes = []

        # 1. Identify all relevant paths (the path itself + all ancestors)
        relevant_sub_paths = set()
        for event in events:
            path = event[0]
            relevant_sub_paths.add(path)
            while "/" in path:
                path, _ = path.rsplit("/", 1)
                relevant_sub_paths.add(path)
            if path != "":
                relevant_sub_paths.add("")  # Root always relevant

        # 2. Retrieve only subscribers on those paths (O(1) lookups)
        with self._lock:
            relevant_entries = []
            for sub_path in relevant_sub_paths:
                if sub_path in self._subscribers:
                    relevant_entries.append((sub_path, self._subscribers[sub_path]))

        # 3. Process events per subscriber safely through a clean pipeline
        for sub_path, sub_entries in relevant_entries:
            # Get all events relevant to this base lookup path
            events_in_scope = [e for e in events if e[0] == sub_path or e[0].startswith(sub_path + "/")]

            if not events_in_scope:
                continue

            for entry in sub_entries:
                filtered_events = []

                # --- A. Apply All Filters ---
                for e in events_in_scope:
                    ep = e[0]

                    # 1. Source filter
                    if entry["ignore_source"] is not None and e[3] == entry["ignore_source"]:
                        continue

                    # 2. Wildcard Regex filter
                    pattern = entry.get("pattern")
                    if pattern and not pattern.match(ep):
                        continue

                    # 3. Recursive filter
                    # If not recursive, the path must match exactly.
                    # Wildcards handle non-recursive via a $ at the end of the regex.
                    if not entry["recursive"]:
                        if pattern:
                            pass
                        elif ep != sub_path:
                            continue

                    # 4. Exclude filter
                    if entry["exclude"]:
                        if any(ep == ex or ep.startswith(ex + "/") for ex in entry["exclude"]):
                            continue

                    filtered_events.append(e)

                if not filtered_events:
                    continue

                # --- B. Apply Snapshots (extract) ---
                extract_fields = entry.get("extract")
                if extract_fields:
                    final_events = []
                    seen_bases = set()

                    for e in filtered_events:
                        # Find the correct base path for the snapshot.
                        # Wildcards use the dynamically matched regex segment.
                        if pattern:
                            base_path = pattern.match(e[0]).group(0)
                        else:
                            base_path = sub_path

                        # Deduplicate batch updates for the same snapshot root
                        if base_path in seen_bases:
                            continue
                        seen_bases.add(base_path)

                        # Generate the atomic snapshot
                        snapshot = {}
                        for field in extract_fields:
                            if field == ".":
                                snapshot["."] = self.get_value(base_path)
                            else:
                                target = f"{base_path}/{field}" if base_path else field
                                snapshot[field] = self.get_value(target)

                        final_events.append((base_path, snapshot, e[2], e[3]))
                else:
                    final_events = filtered_events

                # --- C. Emit Callback ---
                try:
                    entry["cb"](final_events)
                except Exception as e:
                    print(f"[Store] Callback error {sub_path}: {e}")

```

## `File: TaskTonic\ttLoggers\__init__.py`
```python
from .ttScreenLogger import ttLogService, ttScreenLogService
from .ttIpLogger import ttIpLogService

```

## `File: TaskTonic\ttLoggers\ttScreenLogger.py`
```python
from .. import ttTimerRepeat
from ..ttLogger import ttLogService
import time

class ttScreenLogService(ttLogService):

    def __init__(self, name=None):
        super().__init__(name)
        self.log_records = []
        prj = self.ledger.formula.at('tasktonic/project')
        ts = prj['started@'].v
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        print(f"[{l_time_start}] TaskTonic log for {prj['name'].v}, started at {time.strftime('%H:%M:%S', lt)}")
        print(41 * '-=')
    def _tt_init_service_base(self, base, *args, **kwargs):
        self.log(close_log=True)

    def put_log(self, log):
        self.ttsc__add_log(log)

    def ttse__on_start(self):
        pass

    def ttse__on_finished(self):
        print(41*'-=')
        print('Logging finished')
        print(self.ledger.sdump())

    def ttsc__add_log(self, log):
        """
        Formats and prints the collected log entry for an event, then resets it.
        """
        l_id = log.get('id', -1)
        if l_id < 0:
            raise RuntimeError(f'Error in log entry {log}')

        if log.get('lifecycle',{}).get('phase', '') == 'creation':
            while len(self.log_records) <= l_id:
                self.log_records.append(None)
            self.log_records[l_id] = log.copy()

        sparkle_name = log.get('sparkle', '')
        sparkle_state_idx = log.get('state', -1)

        if sparkle_name == '_ttinternal_state_change_to':
            sparkle_name = f" TO STATE [{self.log_records[l_id]['lifecycle']['states'][log['lifecycle']['new_state']]}]"

        ts = log['start@']
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        header = f"{self.log_records[l_id]['lifecycle']['name']}"
        if sparkle_state_idx >= 0:
            header += f"[{self.log_records[l_id]['lifecycle']['states'][sparkle_state_idx]}]"
        header += f".{sparkle_name}"

        dont_print_flags = ['id', 'start@', 'log', 'sparkle', 'state', 'sparkles', 'states', 'duration']
        flags_to_print = {k: v for k, v in log.items() if k not in dont_print_flags}

        du = log.get('duration',0.0)
        l_du = '' if du <= .15 else f'DURATION: {du:1.3f} sec !!! '

        print(f"[{l_time_start}] {l_id:02d} - {header:.<65} {l_du}{flags_to_print}")
        if l_states := log.get('states'):
            print(f"{16 * ' '}== STATES: |", end='')
            for state in l_states: print(f" {state} |", end='')
            print()
        if l_sparkles := log.get('sparkles'):
            print(f"{16 * ' '}== SPARKLES: |", end='')
            for sparkle in l_sparkles:
                if not sparkle.startswith('_ttss'): print(f" {sparkle} |", end='')
            print()

        if log.get('log'):
            for line in log['log']:
                line = str(line).replace('\n', f"\n{18*' '}")
                print(f"{16 * ' '}- {line}")

```

## `File: TaskTonic\ttLoggers\ttIpLogger.py`
```python
from TaskTonic.ttLogger import ttLogService, ttLog
from TaskTonic.ttTonicStore.ttNetworking import TcpDictSocketHandler

class ttIpLogService(ttLogService):
    """
    Intercepts the real TaskTonic log stream, formats the data,
    and forwards it to the visual LogCenter instead of the terminal.
    """
    _tt_force_stealth_logging = False

    def __init__(self, name=None):
        super().__init__(name=name, log_mode=ttLog.QUIET)
        self.net = None
        self.counter = None

        prj = self.ledger.formula.at('tasktonic/project')
        target = self.ledger.formula.get('tasktonic/log/target', 'localhost:1767')
        self.log_bucket = [{
            'start_new_session': True,
            'project': prj['name'].v,
            'start@': prj['started@'].v,
            'target': target,
            'logger_version': 0,
        }]


    def put_log(self, log):
        self.ttsc__add_log(log)

    def ttse__on_start(self):
        self.counter = 0

        # Start the IP client connecting to our Visual Logger
        target = self.ledger.formula.get('tasktonic/log/to/target', 'localhost:1767')
        target = self.ledger.formula.get('app_data/startup_args/target', target)

        if isinstance(target, int):
            target_host = 'localhost'
            target_port = target
        elif isinstance(target, str):
            s = target.split(':')
            target_host = s[0] if len(s) == 2 else 'localhost'
            target_port = int(s[-1])
        else:
            raise TypeError(f'Logger target [{target}] has wrong type')
        self.net = TcpDictSocketHandler(as_client=True, host=target_host, port=target_port)
        self.log(f'Connecting to log service at {target_host}:{target_port}')
        self.to_state('wait_for_connection')

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Network status changed: {status}")

    def ttse__on_socket_connected(self, addr):
        self.to_state('connected')
        self.log(f"Connected to log service at {addr}")

    def ttsc_wait_for_connection__add_log(self, log):
        self.log_bucket.append(log)

    def ttse_connected__on_enter(self):
        for log in self.log_bucket:
            self.net.ttsc__send_data(log)
        self.log_bucket = []

    def ttsc_connected__add_log(self, log):
        self.net.ttsc__send_data(log)

    def ttse_connected__on_disconnected(self):
        self.to_state('disconnected')
        self.log('Log server disconnected')

    def ttsc_disconnected__add_log(self, log):
        pass

    def ttse__on_service_base_completed(self, tonic, srv_left, _=0):
        super().ttse__on_service_base_completed(tonic, srv_left, finish_on_count=2) # using socket and selector

```

## `File: TaskTonic\ttTonicStore\ttDistiller.py`
```python
from TaskTonic import ttLiquid, ttCatalyst, ttLog, ttSparkleStack
import queue, threading, time, copy


class ttDistiller(ttCatalyst):
    """
    The TaskTonic Test Harness
       The Distiller is the dedicated testing environment for the TaskTonic framework. Where the Catalyst
       is designed for high-speed, real-time production, the Distiller is its analytical counterpart,
       designed for controlled observation and debugging.
    """

    def __init__(self, name='tt_main_catalyst'):
        super().__init__(name=name, log_mode=ttLog.OFF)

    def start_sparkling(self):
        # print('Distiller is setup and ready for testing')
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self

        self.thread_id = threading.get_ident()
        sp_stck.catalyst = self

        self.sparkling = True

    def sparkle(self,
                sparkle_count=None,
                timeout=None,
                till_state_in=None,
                till_sparkle_in=None,
                contract=None):

        status = {}
        sp_stck = ttSparkleStack()
        if self.sparkling:
            if contract is None:
                contract = {}

            def ccheck(item, default, ext=None, force_list=False):
                c = ext if ext is not None else contract.get(item, default)
                if force_list and not isinstance(c, list):
                    c = [c]
                contract[item] = c

            ccheck('timeout', 3600.0, timeout)
            ccheck('till_state_in', [], till_state_in, force_list=True)
            ccheck('till_sparkle_in', [], till_sparkle_in, force_list=True)
            ccheck('probes', [], force_list=True)

            status = {
                'status': 'running',
                'start@': time.time(),
                'sparkle_trace': [],
            }
            ending_at = time.time() + contract['timeout']

            while self.sparkling and not status.get('stop_condition', False):
                reference = time.time()
                next_timer_expire = 0.0
                while next_timer_expire == 0.0:
                    next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0
                if reference + next_timer_expire > ending_at:
                    next_timer_expire = ending_at - reference
                    if next_timer_expire < 0.0:
                        next_timer_expire = 0.0
                try:
                    item = self.catalyst_queue.get(timeout=next_timer_expire)
                    instance, sparkle, args, kwargs, sp_stck.source = item

                    self.execute_with_testlog(instance, sparkle, args, kwargs, status, contract)

                    if sparkle_count:
                        sparkle_count -= 1

                    # State transitions MOGEN NOOIT onderbroken worden!
                    # Drain de extra_sparkles altijd volledig af.
                    while self.extra_sparkles:
                        instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                        self.execute_with_testlog(instance, sparkle, args, kwargs, status, contract)
                        if sparkle_count:
                            sparkle_count -= 1


                except queue.Empty:
                    pass

                if time.time() >= ending_at:
                    status.setdefault('stop_condition', []).append('timeout')
                if sparkle_count is not None and sparkle_count <= 0:
                    status.setdefault('stop_condition', []).append('sparkle_count')

        if not self.sparkling:
            status.update({'status': 'catalyst finished'})
            status.setdefault('stop_condition', []).append('catalyst finished')

        status.update({'end@': time.time()})
        return status

    def execute_with_testlog(self, instance, sparkle, args, kwargs, status, contract):
        def _freeze_value(value):
            """
            Maakt een statische snapshot van een variabele.
            Zorgt ervoor dat dynamische objecten (zoals ttLiquid) worden omgezet
            naar hun huidige string-representatie.
            """
            type_name = type(value).__name__
            if type_name == 'ttLiquid':
                return str(value)

            if isinstance(value, dict):
                return {k: _freeze_value(v) for k, v in value.items()}

            if isinstance(value, (list, tuple)):
                return [_freeze_value(v) for v in value]

            if isinstance(value, (int, float, bool, str, type(None))):
                return value

            if isinstance(value, ttLiquid):
                return value.__str__()

            try:
                return copy.deepcopy(value)
            except:
                return str(value)

        # 1. Determine requested probes (tonic specific OR global fallback)
        tonic_contract = contract.get('tonics', {}).get(instance.name, {})
        requested_probes = tonic_contract.get('probes', contract.get('probes', []))

        sp_stck = ttSparkleStack()

        # 2. Freeze probes BEFORE sparkle execution
        probes_at_enter = {
            p: _freeze_value(getattr(instance, p))
            for p in requested_probes
            if hasattr(instance, p)
        }

        status['sparkle_trace'].append({
            'id': instance.id,
            'tonic': instance.name,
            'sparkle': sparkle.__name__,
            'args': args,
            'kwargs': kwargs,
            'source': sp_stck.source,
            'at_enter': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': probes_at_enter,
            }
        })

        # 3. Execute the Sparkle
        sp_stck.push(instance, sparkle.__name__)
        instance._execute_sparkle(sparkle, *args, **kwargs)
        sp_stck.pop()

        # 4. Freeze probes AFTER sparkle execution
        probes_at_exit = {
            p: _freeze_value(getattr(instance, p))
            for p in requested_probes
            if hasattr(instance, p)
        }

        status['sparkle_trace'][-1].update({
            'at_exit': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': probes_at_exit,
                'sparkling': self.sparkling,
            }
        })

        # 5. Evaluate stop conditions
        just_executed = {
            'tonic': instance.name,
            'sparkle': sparkle.__name__
        }
        self._evaluate_contract(contract, status, just_executed)

    def _evaluate_contract(self, contract, status, just_executed):
        """
        Evaluates both global legacy conditions and the new per-tonic conditions.
        """
        if 'contract_met' in status.get('stop_condition', []):
            return True

        # --- Legacy Global Conditions ---
        if just_executed['sparkle'] in contract.get('till_sparkle_in', []):
            status.setdefault('stop_condition', []).append(f"sparkle_trigger: [{just_executed['sparkle']}]")
            return True

        instance = self.ledger.get_tonic_by_name(just_executed['tonic'])
        if instance and instance.get_current_state_name() in contract.get('till_state_in', []):
            status.setdefault('stop_condition', []).append(f"state_trigger: [{instance.get_current_state_name()}]")
            return True

        # --- New Per-Tonic Advanced Conditions ---
        tonics_dict = contract.get('tonics', {})
        if not tonics_dict:
            return False

        matched_tonics_count = 0
        matched_details = {}  # to store matches

        for tonic_name, rules in tonics_dict.items():
            tonic = self.ledger.get_tonic_by_name(tonic_name)
            if not tonic:
                continue

            match_reasons = []

            # Condition 1: State Match
            if 'till_state_in' in rules:
                current_state = tonic.get_current_state_name()
                if current_state in rules['till_state_in']:
                    match_reasons.append(f"state: '{current_state}'")

            # Condition 2: Sparkle Match
            if 'till_sparkle_in' in rules:
                if tonic_name == just_executed['tonic'] and just_executed['sparkle'] in rules['till_sparkle_in']:
                    match_reasons.append(f"sparkle: '{just_executed['sparkle']}'")

            # Condition 3: Probe Match
            if 'stop_on_probe' in rules:
                for probe_name, expected_val in rules['stop_on_probe'].items():
                    if hasattr(tonic, probe_name) and getattr(tonic, probe_name) == expected_val:
                        match_reasons.append(f"probe: {probe_name} == {expected_val}")

            # If this tonic hit any of its rules, record it
            if match_reasons:
                matched_tonics_count += 1
                matched_details[tonic_name] = match_reasons

        # Determine target count (AND vs OR logic)
        target_count = contract.get('stop_match_count', 1)
        if target_count == 'all':
            target_count = len(tonics_dict)

        # Did we reach the required number of matched tonics?
        if matched_tonics_count >= target_count:
            # 1. Safely add the static flag
            status.setdefault('stop_condition', []).append('contract_met')

            # 2. Add the detailed metadata for the developer/tester
            status['contract_details'] = {
                'match_count': matched_tonics_count,
                'target_count': target_count,
                'matched_tonics': matched_details
            }
            return True

        return False
    def finish_distiller(self, timeout=0.5, contract=None):
        for liq in self.ledger.tonics:
            if isinstance(liq, ttLiquid):
                liq.finish()
            elif isinstance(liq, self.ledger.TonicReservation):
                self.ledger.unregister(liq)

        stat = self.sparkle(timeout=timeout, contract=contract)

        # Forced reset of the ledger to create a new singleton when distiller is restarted.
        self.ledger._instance = None
        self.ledger._singleton_init_done = False
        return stat

    def teardown_test_environment(self):
        """
        Officially tears down the TaskTonic environment for unit testing.
        It finishes the distiller, waits for background threads (like the SelectorService)
        to cleanly exit, and performs a hard reset of the ttLedger Singleton.
        """
        import time
        from TaskTonic import ttLedger

        # 1. Initiate standard shutdown
        self.finish_distiller()

        # 2. Force the Ledger reset and wait for dangling threads
        if ttLedger._instance:
            for t in ttLedger._instance.tonics:
                if t and hasattr(t, 'sparkling') and t.id > 0:
                    start_t = time.time()
                    while t.sparkling and time.time() - start_t < 1.0:
                        time.sleep(0.01)

            # Clear out the administration
            ttLedger._instance.records = []
            ttLedger._instance.tonics = []
            ttLedger._instance.formula = None

        # 3. Destroy the Singleton locks
        ttLedger._instance = None
        ttLedger._singleton_init_done = False

    def stat_print(self, status, filter=None):
        import time
        print('=== Sparkling ==')

        if isinstance(filter, int):
            filter = [filter]
        elif isinstance(filter, list):
            pass
        elif filter is None:
            pass
        else:
            raise TypeError('filter is not None, a number or a list of numbers')

        for t in status.get('sparkle_trace', []):
            if filter is None or t['id'] in filter:
                e = t['at_enter']
                x = t['at_exit']
                ts = e['@']
                te = x['@']
                l_ts = f'{time.strftime("%H%M%S", time.localtime(ts))}.{int((ts - int(ts)) * 1000):03d}'
                l_te = f'{time.strftime("%H%M%S", time.localtime(te))}.{int((te - int(te)) * 1000):03d}'
                l_duration = f'{(te - ts):2.3f}'
                s = t['source']
                src = (s[0].name if s[0] else 'None') + '.' + s[1]

                print(
                    f"{t['id']:03d} - {t['tonic']}.{t['sparkle']} ( {t['args']}, {t['kwargs']} ) <-- {src}\n"
                    f"   at enter                                 at exit\n"
                    f"   {l_ts}                               {l_te}                               < {l_duration}s\n"
                    f"   {e['state']:.<40} {x['state']:.<40} < state"
                )
                pe = e.get('probes', {})
                px = x.get('probes', {})
                p = sorted(set(pe.keys()) | set(px.keys()))
                for key in p:
                    print(f"   {str(pe.get(key, '-')):.<40} {str(px.get(key, '-')):.<40} < {key}")
                print()

        dur = status["end@"] - status["start@"]
        print(f'>> stopped : {status["stop_condition"]}, duration {dur:2.03f}s, Catalyst Status {status["status"]}')
```

## `File: TaskTonic\ttTonicStore\__init__.py`
```python
from .ttDistiller import ttDistiller
from .ttStore import ttStore
from .ttTimerScheduled import (ttTimerEveryYear, ttTimerEveryMonth, ttTimerEveryWeek, ttTimerEveryDay,
                               ttTimerEveryHour, ttTimerEveryMinute)
from .ttIpSockets import SelectorHandler, SocketHandler, StrSocketHandler, DictSocketHandler

# Optional imports for PySide6
try:
    from .ttPyside6Ui import ttPyside6Ui
    from .ttPysideWidget import ttPysideWindow, ttPysideWidget
except ImportError:
    pass

# Optional imports for Tkinter
try:
    from .ttTkinterUi import ttTkinterUi
    from .ttTkinterWidget import ttTkinterFrame
except ImportError:
    pass
```

## `File: TaskTonic\ttTonicStore\ttPysideWidget.py`
```python
import re
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import QObject, Qt

from .. import ttLedger, ttSparkleStack
from ..ttLiquid import __ttLiquidMeta
from ..ttTonic import ttTonic

# Dynamische resolutie van de Qt Metaclass
PySideMeta = type(QObject)


class ttPysideMeta(__ttLiquidMeta, PySideMeta):
    """
    Lost het metaclass conflict op tussen TaskTonic (ttEssence) en PySide6 (QObject).
    """
    pass

class ttPysideMixin:
    """
    Voegt de 'ttqt' functionaliteit toe aan widgets.
    """

    def _get_custom_prefixes(self):
        """
        Hook voor ttTonic. Retourneert onze prefix en de binder methode.
        """
        # We gebruiken de SmartPrefix om compatibel te zijn met de logica in ttTonic
        return {'ttqt': self._bind_qt_event}

    def _bind_qt_event(self, prefix, sparkle_name):
        """
        Deze methode wordt door ttTonic aangeroepen voor elke gevonden 'ttqt' method.
        sparkle_name is de naam van de 'interface method' (bijv. ttqt__btn__clicked)
        die ttTonic al heeft omgezet naar een queue-wrapper.
        """
        # 1. Parse de naam: ttqt__(widget)__(signaal)
        # We halen 'ttqt__' eraf.
        base_name = sparkle_name[6:]  # len('ttqt__') == 6

        # We zoeken de LAATSTE dubbele underscore om widget en signaal te scheiden.
        # Dit staat toe dat widget namen zelf dubbele underscores bevatten (bv. self.main__btn).
        if "__" not in base_name:
            raise RuntimeError(f"Invalid naming for sparkle '{sparkle_name}'. Expected ttqt__widget__signal.")

        w_name, s_name = base_name.rsplit("__", 1)

        # 2. Vind het widget
        if not hasattr(self, w_name):
            # Dit kan gebeuren als de UI nog niet is opgebouwd bij init.
            # Zorg dat setup_ui() wordt aangeroepen vòòr super().__init__().
            raise RuntimeError(f"Widget '{w_name}' not found during binding of '{sparkle_name}'.")

        widget = getattr(self, w_name)

        # 3. Vind het signaal
        if not hasattr(widget, s_name):
            raise RuntimeError(f"Error: Signal '{s_name}' not found on '{w_name}'.")

        signal = getattr(widget, s_name)

        # 4. Haal de wrapper op die ttTonic heeft gemaakt
        # Deze wrapper zet de taak op de queue.
        tonic_wrapper = getattr(self, sparkle_name)

        # 5. Verbinden!
        try:
            signal.connect(tonic_wrapper)
        except Exception as e:
            raise RuntimeError(f"[ttPyside] Failed to connect {sparkle_name}: {e}")


class ttPysideWidget(ttPysideMixin, QWidget, ttTonic, metaclass=ttPysideMeta):
    def __init__(self, parent=None, **kwargs):
        ttTonic.__init__(self, **kwargs)

        qt_parent = parent
        tt_context = ttSparkleStack().get_tonic()
        if qt_parent is None and isinstance(tt_context, QWidget):
            qt_parent = tt_context

        QWidget.__init__(self, qt_parent)
        self.setup_ui()

    def setup_ui(self):
        pass

    def closeEvent(self, event):
        if self.finishing:
            event.accept()
        else:
            event.ignore()
            self.finish()

    def ttse__on_finished(self):
        # self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.close()


class ttPysideWindow(ttPysideMixin, QMainWindow, ttTonic, metaclass=ttPysideMeta):
    def __init__(self, parent=None, **kwargs):
        ttTonic.__init__(self, **kwargs)

        qt_parent = parent
        tt_base = self.base

        if qt_parent is None and isinstance(tt_base, QWidget):
            qt_parent = tt_base

        QMainWindow.__init__(self, qt_parent)

    def closeEvent(self, event):
        if self.finishing:
            event.accept()
        else:
            event.ignore()
            self.ttse__on_close_event()

    def ttse__on_close_event(self):
        self.ttsc__finish()

    def ttse__on_finished(self):
        # self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.close()
```

## `File: TaskTonic\ttTonicStore\ttPyside6Ui.py`
```python
# ttPyside6Ui.py
import sys, queue, time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QEvent, QCoreApplication, QTimer

from .. import ttSparkleStack
from ..ttCatalyst import ttCatalyst
from .ttPysideWidget import ttPysideMeta


class SparkleEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, payload):
        super().__init__(SparkleEvent.EVENT_TYPE)
        self.payload = payload


class PysideQueue(queue.SimpleQueue):
    def __init__(self, catalyst_ui):
        super().__init__()
        self.catalyst_ui = catalyst_ui

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        event = SparkleEvent(item)
        QCoreApplication.postEvent(self.catalyst_ui, event)


class ttPyside6Ui(ttCatalyst, QObject, metaclass=ttPysideMeta):
    def __init__(self, name=None, app_args=None):
        ttCatalyst.__init__(self, name=name)
        QObject.__init__(self)
        if QApplication.instance():
            self.app = QApplication.instance()
        else:
            self.app = QApplication(app_args or sys.argv)

        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.setSingleShot(True)
        self._heartbeat_timer.timeout.connect(self._on_qt_timer_timeout)

    def new_catalyst_queue(self):
        return PysideQueue(catalyst_ui=self)

    def start_sparkling(self):
        if self.id != 0:
            raise RuntimeError(f'{self.__class__.__name__} must be a main catalyst (id==0)')

        self._schedule_next_timer()
        ttSparkleStack().catalyst = self

        self.app.exec()
        super().sparkle()  # finish last TaskTonic calls (if any) after ui ended

    def customEvent(self, event):
        if event.type() == SparkleEvent.EVENT_TYPE:
            sp_stck = ttSparkleStack()
            try:
                item = self.catalyst_queue.get_nowait()
                instance, sparkle, args, kwargs, sp_stck.source = item
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                self._process_extra_sparkles()

            except queue.Empty:
                pass
            except Exception as e:
                raise(f"[ttPyside6Ui] Error: {e}")
            finally:
                self._schedule_next_timer()
            event.accept()
        else:
            super().customEvent(event)

    def _process_extra_sparkles(self):
        sp_stck = ttSparkleStack()
        while self.extra_sparkles:
            payload = self.extra_sparkles.pop(0)
            instance, sparkle, args, kwargs = payload
            sp_stck.push(instance, sparkle.__name__)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

    def _schedule_next_timer(self):
        reference = time.time()
        next_timer_expire = 0.0
        while next_timer_expire == 0.0:
            next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60

        self._heartbeat_timer.stop()
        if next_timer_expire > 0.0:
            ms = max(0, int(next_timer_expire * 1000))
            self._heartbeat_timer.start(ms)

    def _on_qt_timer_timeout(self):
        self._schedule_next_timer()
```

## `File: TaskTonic\ttTonicStore\ttStore.py`
```python
# ------------------------------------------------------------------------------
# Class: ttStore (TaskTonic Service Wrapper)
# ------------------------------------------------------------------------------

from ..ttTonic import ttTonic
from ..internals.Store import Store, Item

class ttStore(ttTonic, Store):
    """
    TaskTonic specific wrapper that integrates Store with the Ledger.
    Defined as a Singleton Service via _tt_is_service.
    """

    # Determines service name in ttEssenceMeta logic
    _tt_is_service = 'store'

    def __init__(self, *args, **kwargs):
        ttTonic.__init__(self, *args, **kwargs)
        Store.__init__(self)

    def _init_service(self, *args, **kwargs):
        """Called every time the service is requested/accessed via ledger."""
        pass

    def ttsc__finish(self):
        super().ttsc__finish()



```

## `File: TaskTonic\ttTonicStore\ttTimerScheduled.py`
```python
import time
import calendar as cal
import bisect
from TaskTonic.ttTimer import ttTimer


def stime(t):
    tm = time.localtime(t)
    return f'{ttTimerScheduled.days[tm.tm_wday + 7]} {tm.tm_year:04d}-{tm.tm_mon:02d}-{tm.tm_mday:02d} ' \
           f'{tm.tm_hour:02}:{tm.tm_min:02}:{tm.tm_sec:02}'


class ttTimerScheduled(ttTimer):
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",

        "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
    ]
    days = [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"
    ]

    def __init__(self, name=None,
                 month=None, week=None, day=None, in_week=None, hour=None, minute=None, second=None,
                 time_str=None, t_units=3, sparkle_back=None):
        super().__init__(name=name, sparkle_back=sparkle_back)
        if month is not None or week is not None:  # year period
            self._month = None
            self._week = None
            if isinstance(month, int):
                if week is not None:
                    raise ValueError(f'Both month and week given')
                if month < 1 or month > 12:
                    raise ValueError(f'Invalid month (1..12) "{month}"')
                self._month = month
            elif isinstance(month, str):
                if week is not None:
                    raise ValueError(f'Both month and week given')
                month = month.strip().lower()
                if month in self.months:
                    self._month = self.months.index(month) % 12 + 1
                else:
                    raise ValueError(f'Invalid day "{month}"')
            elif isinstance(week, int):
                if month is not None:
                    raise ValueError(f'Both month and week given')
                if week < 1 or week > 53:
                    raise ValueError(f'Invalid week (1..53) "{month}"')
                self._week = week

            else:
                raise ValueError(f'Invalid month or week "{month}" - "{week}"')

        if day is not None:
            self._day = None
            self._in_week = None
            if isinstance(day, int):
                self._day = day
                if day < -31 or day > 31:
                    raise ValueError(f'Invalid day (1..31 or -1..-31) "{day}"')
            elif isinstance(day, str):
                day = day.strip().lower()
                if day in self.days:
                    self._day = self.days.index(day) % 7
                    if in_week is None:
                        in_week = 1  # default when day name given
                else:
                    raise ValueError(f'Invalid day "{day}"')
            else:
                raise ValueError(f'Invalid day "{day}"')
            if in_week is not None:
                self._in_week = in_week
                if self._day > 6:
                    raise ValueError(f'Invalid day (0..6 when in_week given) "{day}"')

        if isinstance(hour, int):
            if t_units < 3:
                raise ValueError(f'to many time elements hour:00:00')
            self._hour = hour
            self._minute = 0
            self._second = 0
        elif hour is not None:
            raise ValueError(f'hour must be an integer')

        if isinstance(minute, int):
            if t_units < 2:
                raise ValueError(f'to many time elements minute:00')
            self._minute = minute
            self._second = 0
        elif minute is not None:
            raise ValueError(f'minute must be an integer')

        if isinstance(second, (int, float)):
            self._second = second
        elif second is not None:
            raise ValueError(f'second must be an integer or float')
        if isinstance(time_str, str):
            tu = time_str.split(':')
            try:
                tl = [int(u) for u in tu]
                while len(tl) < t_units:
                    tl.append(0)
                if len(tl) > t_units:
                    raise ValueError(f'to many time elements "{time_str}"')
                if len(tl) == 1:
                    self._second = tl[0]
                elif len(tl) == 2:
                    self._minute, self._second = tl
                elif len(tl) == 3:
                    self._hour, self._minute, self._second = tl

            except ValueError as e:
                raise ValueError(f'Invalid time_str "{e}"')
        elif time_str is not None:
            raise ValueError(f'time_str must be an string')
        self.start()

    def __str__(self):
        s = (self.__class__.__name__[:20]).ljust(21)
        if hasattr(self, "_month") and self._month is not None:
            s += self.months[self._month - 1]
            if hasattr(self, "_in_week") and self._in_week is not None:
                s += f', {self.days[self._day]} {self._in_week}'
            else:
                s += " " + str(self._day)
        elif hasattr(self, "_week") and self._week is not None:
            s += "week " + str(self._week) + ", " + self.days[self._day]
        elif hasattr(self, "_day") and self._day is not None:
            if self._in_week is not None:
                s += f'{self.days[self._day]}{f", {self._in_week}" if self._in_week > 0 else ""}'
            else:
                s += "day " + str(self._day)
        s = s.ljust(45)
        s += f'{self._hour:02}:' if hasattr(self, "_hour") else "   "
        s += f'{self._minute:02}:' if hasattr(self, "_minute") else "   "
        s += f'{self._second:02}' if hasattr(self, "_second") else "  "
        s += f',  expires @ {stime(self.expire) if self.expire >=0 else "-1"}'

        return s

    def reload_on_expire(self, reference_time):
        self.catalyst.timers.remove(self)
        self.next_trigger(reference_time)
        bisect.insort(self.catalyst.timers, self)


    def start(self):
        if self.id == -1: raise RuntimeError(f'Cannot start a finished timer')
        if self.expire == -1:
            self.expire = 0
            n = time.time()
            self.next_trigger(n)
            if self.expire <= n:  # after first time initialisation expire time can buy in the past; recalculate
                self.next_trigger(n)
            bisect.insort(self.catalyst.timers, self)
        else:
            raise RuntimeError(f"Can't start a running timer ({self})")
        return self

    def restart(self):
        if self.expire == -1:
            self.start()

    def next_trigger(self, now):
        raise RuntimeError('next_trigger must be overridden')

    def ts_replace(self, ts, year=None, month=None, day=None, hour=None, minute=None, second=None):
        return time.struct_time((ts.tm_year if year is None else year,
                                 ts.tm_mon if month is None else month,
                                 ts.tm_mday if day is None else day,
                                 ts.tm_hour if hour is None else hour,
                                 ts.tm_min if minute is None else minute,
                                 ts.tm_sec if second is None else second, -1, -1, -1))

    def ts_add_time(self, ts, week=0, day=0, hour=0, minute=0, second=0):
        return time.localtime(time.mktime(ts) + week * 604800 + day * 86400 + hour * 3600 + minute * 60 + second)


class ttTimerEveryYear(ttTimerScheduled):
    def __init__(self, name=None,
                 month=None, week=None, day=None, in_week=None, hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=month, week=week, day=day, in_week=in_week, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        m = 1 if self._month is None else self._month
        if self.expire == 0:
            n = time.localtime(now)
            t = time.struct_time((n.tm_year, m, 1, self._hour, self._minute, self._second, -1, -1, -1))
        else:
            t = time.localtime(
                self.expire +
                (0 if self._month is not None else
                 (((7 * 24 * 3600) if self._week == 1 else 0) - ((14 * 24 * 3600) if self._week >= 52 else 0)))
            )
            t = self.ts_replace(t, year=t.tm_year + 1, month=m, day=1)
        first_day, days_in_month = cal.monthrange(t.tm_year, t.tm_mon)

        if self._month is None:  # by week
            t = self.ts_add_time(t, week=self._week - 1, day=self._day + 3 - (first_day + 3) % 7)
            t = self.ts_replace(t, hour=self._hour, minute=self._minute, second=self._second)

        else:  # by month
            if self._in_week is None:  # day in month
                if self._day > 0:
                    t = self.ts_replace(t, day=min(days_in_month, self._day))
                else:
                    t = self.ts_replace(t, day=max(1, days_in_month + self._day + 1))
            else:  # weekday
                wday_first_in_month = 1 + (7 + self._day - first_day) % 7
                wday_last_in_month = wday_first_in_month + (days_in_month - wday_first_in_month) // 7 * 7
                if self._in_week > 0:
                    t = self.ts_replace(t, day=min(wday_last_in_month, wday_first_in_month + (self._in_week - 1) * 7),
                                        hour=self._hour)
                else:
                    t = self.ts_replace(t, day=max(wday_first_in_month, wday_last_in_month - (-self._in_week - 1) * 7),
                                        hour=self._hour)
        self.expire = time.mktime(t)


class ttTimerEveryMonth(ttTimerScheduled):
    def __init__(self, name=None,
                 day=None, in_week=None, hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=day, in_week=in_week, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire == 0:
            n = time.localtime(now)
            t = time.struct_time((n.tm_year, n.tm_mon, 1, self._hour, self._minute, self._second, -1, -1, -1))
        else:
            t = time.localtime(self.expire + 31 * 86400)  # next month
            t = self.ts_replace(t, day=1, hour=self._hour, minute=self._minute, second=self._second)
        first_day, days_in_month = cal.monthrange(t.tm_year, t.tm_mon)

        if self._in_week is None:  # day in month
            if self._day > 0:
                t = self.ts_replace(t, day=min(days_in_month, self._day))
            else:
                t = self.ts_replace(t, day=max(1, days_in_month + self._day + 1))
        else:  # weekday
            wday_first_in_month = 1 + (7 + self._day - first_day) % 7
            wday_last_in_month = wday_first_in_month + (days_in_month - wday_first_in_month) // 7 * 7
            if self._in_week > 0:
                t = self.ts_replace(t, day=min(wday_last_in_month, wday_first_in_month + (self._in_week - 1) * 7),
                                    hour=self._hour)
            else:
                t = self.ts_replace(t, day=max(wday_first_in_month, wday_last_in_month - (-self._in_week - 1) * 7),
                                    hour=self._hour)

        self.expire = time.mktime(t)


class ttTimerEveryWeek(ttTimerScheduled):
    def __init__(self, name=None,
                 day=None, hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=day, in_week=0, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire = time.mktime(self.ts_replace(time.localtime(self.expire + 604800), hour=self._hour))
        else:
            n = time.localtime(now)
            t = time.localtime(now + (7 + self._day - n.tm_wday) % 7 * 86400)
            t = self.ts_replace(t, hour=self._hour, minute=self._minute, second=self._second)
            self.expire = time.mktime(t)


class ttTimerEveryDay(ttTimerScheduled):
    def __init__(self, name=None,
                 hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=None, in_week=None, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire = time.mktime(self.ts_replace(time.localtime(self.expire + 86400), hour=self._hour))
        else:
            n = time.localtime(now)
            t = self.ts_replace(n, hour=self._hour, minute=self._minute, second=self._second)
            self.expire = time.mktime(t)


class ttTimerEveryHour(ttTimerScheduled):
    def __init__(self, name=None,
                 minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=None, in_week=None, hour=None, minute=minute, second=second,
                         time_str=time_str, t_units=2, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire += 3600
        else:
            self.expire = now // 3600 * 3600 + self._minute * 60 + self._second


class ttTimerEveryMinute(ttTimerScheduled):
    def __init__(self, name=None,
                 second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=None, in_week=None, hour=None, minute=None, second=second,
                         time_str=time_str, t_units=1, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire += 60
        else:
            self.expire = now // 60 * 60 + self._second

```

## `File: TaskTonic\ttTonicStore\ttTkinterUi.py`
```python
import os
import sys

# Re-route the Tcl/Tk libraries to the base Python installation
base_prefix = getattr(sys, "base_prefix", sys.prefix)
os.environ['TCL_LIBRARY'] = os.path.join(base_prefix, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(base_prefix, 'tcl', 'tk8.6')

import tkinter as tk
import queue
import time
from .. import ttSparkleStack
from ..ttCatalyst import ttCatalyst


class TkinterQueue(queue.SimpleQueue):
    def __init__(self, catalyst_ui):
        super().__init__()
        self.catalyst_ui = catalyst_ui
        self.root = catalyst_ui.root

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        # Genereer een thread-safe virtueel event om de mainloop te triggeren
        self.root.event_generate("<<SparkleEvent>>", when="tail")


class ttTkinterUi(ttCatalyst):
    def __init__(self, name=None):
        self.root = tk.Tk()
        super().__init__(name=name)

        # Koppel het virtuele event aan de custom Sparkle verwerker
        self.root.bind("<<SparkleEvent>>", self.customEvent)
        self._timer_id = None

    def new_catalyst_queue(self):
        return TkinterQueue(catalyst_ui=self)

    def start_sparkling(self):
        if self.id != 0:
            raise RuntimeError(f'{self.__class__.__name__} must be a main catalyst (id==0)')

        self._schedule_next_timer()
        ttSparkleStack().catalyst = self

        self.root.mainloop()
        super().sparkle()  # Verwerk overgebleven TaskTonic calls als het scherm sluit

    def customEvent(self, event=None):
        sp_stck = ttSparkleStack()
        try:
            item = self.catalyst_queue.get_nowait()
            instance, sparkle, args, kwargs, sp_stck.source = item
            sp_name = sparkle.__name__

            sp_stck.push(instance, sp_name)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

            sp_stck.source = (instance, sp_name)
            self._process_extra_sparkles()

        except queue.Empty:
            pass
        except Exception as e:
            print(f"[ttTkinterUi] Error: {e}")
        finally:
            self._schedule_next_timer()

    def _process_extra_sparkles(self):
        sp_stck = ttSparkleStack()
        while self.extra_sparkles:
            payload = self.extra_sparkles.pop(0)
            instance, sparkle, args, kwargs = payload
            sp_stck.push(instance, sparkle.__name__)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

    def _schedule_next_timer(self):
        reference = time.time()
        next_timer_expire = 0.0
        while next_timer_expire == 0.0:
            next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0

        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

        if next_timer_expire > 0.0:
            ms = max(0, int(next_timer_expire * 1000))
            if ms > 60000: ms = 60000  # Max 1 minuut wachten als er geen timers zijn
            self._timer_id = self.root.after(ms, self._on_tk_timer_timeout)

    def _on_tk_timer_timeout(self):
        self._schedule_next_timer()

        # TaskTonic/ttTonicStore/ttTkinterUi.py

    def ttse__on_finished(self):
        # Als de Catalyst écht klaar is met z'n queues,
        # sluiten we pas het Tkinter fundament af.
        if self.root:
            try:
                self.root.destroy()
            except tk.TclError:
                pass
        super().ttse__on_finished()
```

## `File: TaskTonic\ttTonicStore\ttTkinterWidget.py`
```python
import tkinter as tk
from .. import ttSparkleStack
from ..ttTonic import ttTonic


class ttTkinterMixin:
    """
    Voegt de 'tttk' functionaliteit toe aan Tkinter widgets.
    """

    def _get_custom_prefixes(self):
        return {'tttk': self._bind_tk_event}

    def _bind_tk_event(self, prefix, sparkle_name):
        # Format: tttk__widget_name__event_or_command
        base_name = sparkle_name[6:]  # Haal 'tttk__' eraf

        if "__" not in base_name:
            raise RuntimeError(f"Invalid naming for sparkle '{sparkle_name}'. Expected tttk__widget__event.")

        w_name, e_name = base_name.rsplit("__", 1)

        if not hasattr(self, w_name):
            raise RuntimeError(f"Widget '{w_name}' not found during binding of '{sparkle_name}'.")

        widget = getattr(self, w_name)
        tonic_wrapper = getattr(self, sparkle_name)

        # Bepaal of het een attribuut 'command' is of een reguliere event binding
        if e_name == "command":
            widget.configure(command=tonic_wrapper)
        else:
            # Bijv. e_name == "<Button-1>" of "<Return>"
            widget.bind(e_name, tonic_wrapper)


class ttTkinterFrame(ttTkinterMixin, tk.Frame, ttTonic):
    def __init__(self, parent=None, **kwargs):
        if getattr(self, '_ui_init_done', False):
            return

        ttTonic.__init__(self, **kwargs)

        tk_parent = parent
        tt_context = ttSparkleStack().get_tonic()

        # Vind de juiste master/parent
        if tk_parent is None and isinstance(tt_context, (tk.Tk, tk.Frame)):
            tk_parent = tt_context
        elif tk_parent is None and hasattr(self.base, 'root'):
            tk_parent = self.base.root

        tk.Frame.__init__(self, tk_parent)
        self.setup_ui()
        self._ui_init_done = True

    def setup_ui(self):
        """Override deze functie om je widgets aan te maken"""
        pass

```

## `File: TaskTonic\ttTonicStore\ttNetworking\__init__.py`
```python
from .ttSelectorService import SelectorService
from .ttTcpSockets import TcpSocketHandler, TcpStrSocketHandler, TcpDictSocketHandler
from .ttUdpSockets import UdpSocketHandler, UdpDictSocketHandler
from .ttHttpSockets import HttpServerHandler, HttpClientHandler


```

## `File: TaskTonic\ttTonicStore\ttNetworking\ttSelectorService.py`
```python
# TaskTonic/ttTonicStore/ttNetworking/ttSelectorService.py

from TaskTonic import ttCatalyst, ttSparkleStack
import socket
import selectors
import threading
import queue
import time


'''
Designer Note: 
The SelectorHandler is designed as a catalyst for both itself and the socket handlers. This ensures 
that all 'sparkles' are executed from the same thread, which is required because Python's selectors 
are not thread-safe by design.

In the sparkling loop, we need to monitor both the catalyst queue and selector events. Since we 
want to avoid polling (busy waiting), a adapted queue is created: MyNotifyingQueue. Putting data now 
also signals a notification channel to trigger a selector event. This wakes up the loop, allowing 
it to process the queue and execute the sparkles.
'''


class SelectorService(ttCatalyst):
    """
    The central engine for OS-level network I/O.
    This Catalyst blocks on selectors.select() instead of a standard queue,
    making it highly efficient for handling (thousands of) sockets.
    """
    # NEW SERVICE NAME to avoid conflicts with legacy code
    _tt_is_service = 'networking_selector_service'
    _tt_root_context = True

    def __init__(self, *args, name=None, log_mode=None, **kwargs):
        super().__init__(name, log_mode, dont_start_yet=True)

        self.register_data = {}
        self._queue_filled_notify_channel = None
        self._queue_filled_notify_channel_read = None

        # Startup notifier
        self.selector = selectors.DefaultSelector()
        self._queue_filled_notify_channel, self._queue_filled_notify_channel_read = socket.socketpair()
        self._queue_filled_notify_channel.setblocking(False)
        self._queue_filled_notify_channel_read.setblocking(False)

        # Register the notification socket
        self.selector.register(
            self._queue_filled_notify_channel_read,
            selectors.EVENT_READ,
            (1, self._handle_queue_filled_notify_channel, None)
        )
        self.start_sparkling()

    def _init_service(self, *args, context=None, **kwargs):
        pass

    def new_catalyst_queue(self):
        class MyNotifyingQueue(queue.SimpleQueue):
            def __init__(self, catalyst, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.catalyst = catalyst

            def put(self, item):
                super().put(item)
                try:
                    # Wake up the selector loop!
                    self.catalyst._queue_filled_notify_channel.send(b'1')
                except:
                    pass

        return MyNotifyingQueue(self)

    def sparkle(self):
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True
        sparkles_in_queue = True

        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0

            while next_timer_expire == 0.0:
                if self.timers:
                    next_timer_expire = self.timers[0].check_on_expiration(reference)
                else:
                    next_timer_expire = 60.0

            if sparkles_in_queue:
                next_timer_expire = 0.0

            try:
                # Block efficiently at the OS level
                events = self.selector.select(timeout=next_timer_expire)
                for key, mask in events:
                    sock = key.fileobj
                    mode, rd_sparkle, wr_sparkle = key.data

                    if mode == 1:  # Connection read/write (TCP or UDP data)
                        if mask & selectors.EVENT_READ:
                            # Check socket type to determine the correct read method
                            if sock.type == socket.SOCK_DGRAM:
                                try:
                                    # UDP: Read datagram and capture sender address
                                    data, addr = sock.recvfrom(65535)
                                    if data:
                                        # Queue the Sparkle with data AND address
                                        rd_sparkle(data, addr)
                                except OSError:
                                    pass
                            else:
                                try:
                                    # TCP: Read stream data
                                    data = sock.recv(65536)
                                except OSError:
                                    data = b''

                                # An empty byte string in TCP means the connection is closed
                                if not data:
                                    self.unregister(sock=sock)

                                # Queue the Sparkle with just the data
                                rd_sparkle(data)

                        if mask & selectors.EVENT_WRITE:
                            wr_sparkle()

                    elif mode == 2:  # TCP server accept
                        conn, addr = sock.accept()
                        conn.setblocking(False)
                        rd_sparkle(conn, addr)

            except TimeoutError:
                pass
            except OSError as e:
                if getattr(e, 'winerror', 0) == 10038:
                    pass  # Bad file descriptor
                else:
                    raise e
            except Exception:
                raise

            # Process pending TaskTonic Sparkles
            try:
                instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get_nowait()
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                while self.extra_sparkles:
                    instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                    sp_stck.push(instance, sparkle.__name__)
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                    sp_stck.pop()
                sparkles_in_queue = True
            except queue.Empty:
                sparkles_in_queue = False

        # Cleanup
        self.selector.unregister(self._queue_filled_notify_channel_read)
        self._queue_filled_notify_channel.close()
        self._queue_filled_notify_channel_read.close()

    def _handle_queue_filled_notify_channel(self, data):
        pass  # Flush the dummy byte

    def register(self, sock, context, mode=1, mask=None, rd=None, wr=None, rd_sparkle=None, wr_sparkle=None):
        if sock is None: sock = context.comm_socket

        if mask is None:
            mask = 0
            if rd is not None and rd: mask |= selectors.EVENT_READ
            if wr is not None and wr: mask |= selectors.EVENT_WRITE
            if mask == 0: mask = selectors.EVENT_READ

        if rd_sparkle is None:
            defaults_rd = ['ttse__on_socket_rd', 'ttse__on_udp_data', 'ttse__on_tcp_data']
            for default_name in defaults_rd:
                if hasattr(context, default_name):
                    rd_sparkle = getattr(context, default_name)
                    break
            # Fail-fast alleen als we NU direct willen lezen en niets hebben gevonden
            if mask & selectors.EVENT_READ and rd_sparkle is None:
                raise RuntimeError(
                    f"[{context.name}] Selector registration failed: Socket configured for "
                    f"READ events, but no default method found."
                )

        if wr_sparkle is None:
            defaults_wr = ['ttse__on_socket_wr', 'ttse__on_udp_wr', 'ttse__on_tcp_wr']
            for default_name in defaults_wr:
                if hasattr(context, default_name):
                    wr_sparkle = getattr(context, default_name)
                    break
            if mask & selectors.EVENT_WRITE and wr_sparkle is None:
                raise RuntimeError(
                    f"[{context.name}] Selector registration failed: Socket configured for "
                    f"WRITE events, but no default method found."
                )

        self.register_data[sock] = {'mask': mask, 'data': (mode, rd_sparkle, wr_sparkle)}
        self.selector.register(sock, mask, (mode, rd_sparkle, wr_sparkle))

    def unregister(self, sock=None):
        try:
            self.selector.unregister(sock)
        except:
            pass
        try:
            self.register_data.pop(sock)
        except:
            pass

    def modify(self, sock, mask=None, rd=None, wr=None):
        if mask is None:
            mask = self.register_data[sock]['mask']
            if rd is not None:
                mask = mask & ~selectors.EVENT_READ | (selectors.EVENT_READ if rd else 0)
            if wr is not None:
                mask = mask & ~selectors.EVENT_WRITE | (selectors.EVENT_WRITE if wr else 0)

        if mask == 0:
            if self.register_data[sock]['mask'] != 0:
                self.selector.unregister(sock)
        else:
            if self.register_data[sock]['mask'] == 0:
                self.selector.register(sock, mask, self.register_data[sock]['data'])
            else:
                self.selector.modify(sock, mask, self.register_data[sock]['data'])
        self.register_data[sock]['mask'] = mask

    def _ttss__main_catalyst_finished(self):
        pass

```

## `File: TaskTonic\ttTonicStore\ttNetworking\ttTcpSockets.py`
```python
# TaskTonic/ttTonicStore/ttNetworking/ttTcpSockets.py

import socket
import errno
import struct
import pickle
from TaskTonic import ttTonic, ttLog, ttTimerSingleShot
from .ttSelectorService import SelectorService


class TcpSocketHandler(ttTonic):
    # Base TCP handler
    def __init__(self, as_server=None, as_client=None, host=None, port=None, **kwargs):
        from TaskTonic import ttLedger
        ledger = ttLedger()

        # REQUEST THE NEW SERVICE
        srv = ledger.get_service_essence('networking_selector_service')
        if not srv:
            srv = SelectorService(log_mode=ttLog.QUIET)

        super().__init__(catalyst=srv.catalyst, **kwargs)

        if as_server is not None and as_client is not None:
            raise ValueError('Make up your mind error: cannot specify both as_server and as_client')

        self.as_server = as_server if as_server is not None else not as_client
        self.server_host = host if host is not None else 'localhost'
        self.server_port = port if port is not None else '5555'
        self.server_addr = f'{host}:{port}'

        self.selector_handler = SelectorService()
        self.server_socket = None
        self.comm_socket = None
        self.comm_addr = None
        self.retry = 0
        self.rcv_buf = b''
        self.send_buf = b''
        self.buffering_send = False

    def ttse__on_start(self):
        st_init = 'init_server' if self.as_server else 'init_client'
        self.log(st_init)
        self.to_state(st_init)
        self.ttsc__start_init()

    def ttse__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status(self.get_active_state())

    def ttsc_init_server__start_init(self):
        self.log(f'Init server: {self.server_addr}')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)
        self.to_state('server_wait_for_connection')
        self.selector_handler.register(self.server_socket, self, rd=1, mode=2, rd_sparkle=self.ttse__on_server_rd)

    def ttse_server_wait_for_connection__on_server_rd(self, conn, addr):
        self.selector_handler.unregister(sock=self.server_socket)
        self.server_socket.close()
        self.server_socket = None

        self.comm_socket = conn
        self.comm_addr = addr
        self.to_state('connected')
        self.selector_handler.register(self.comm_socket, self, rd=1)

    def ttsc_init_client__start_init(self):
        self.log(f'Init client: connect to {self.server_addr}')
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_socket.setblocking(False)

        try:
            self.selector_handler.register(self.comm_socket, self, wr=1)
            self.comm_socket.connect((self.server_host, self.server_port))
        except BlockingIOError as e:
            if e.errno == errno.EINPROGRESS or e.errno == errno.WSAEWOULDBLOCK:
                self.to_state('client_wait_for_connection')
                return
            else:
                raise e

        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)

    def ttse_client_wait_for_connection__on_socket_wr(self):
        err = self.comm_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err:
            import os
            self.log(f"Connection failed: {os.strerror(err)}")
            self.selector_handler.unregister(self.comm_socket)
            self.comm_socket.close()
            self.comm_socket = None

            if self.retry > 3:
                self.finish()
            else:
                self.retry += 1
                self.to_state('wait_for_retry')
            return

        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)

    def ttse_wait_for_retry__on_enter(self):
        self.log("Scheduling connection retry in 2 seconds...")
        ttTimerSingleShot(seconds=2, name='tm_retry')

    def ttse_wait_for_retry__on_tm_retry(self, _):
        self.log("Attempting to reconnect to the server...")
        self.to_state('init_client')
        self.ttsc__start_init()

    def ttse_connected__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('connected')
        if hasattr(self.base, 'ttse__on_socket_connected'):
            self.base.ttse__on_socket_connected(self.comm_addr)

    def ttse_connected__on_socket_rd(self, data):
        if data:
            for d in self.rcv_data_conversion(data):
                self.base.ttse__on_socket_data(d)
        else:
            self.comm_socket = None
            if hasattr(self.base, 'ttse__on_socket_status'):
                self.base.ttse__on_socket_status('disconnected')

            if hasattr(self.base, 'ttse__on_disconnected'):
                self.base.ttse__on_disconnected()

            self.finish()

    def ttse_connected__on_socket_wr(self):
        self._send(self.send_buf)

    def ttsc_connected__send_data(self, data):
        bdata = self.send_data_conversion(data)
        if self.buffering_send:
            self.send_buf += bdata
        else:
            self._send(bdata)

    def _send(self, bdata):
        try:
            sent = self.comm_socket.send(bdata)
        except BlockingIOError:
            sent = 0

        if sent == len(bdata):
            self.send_buf = b''
            self.buffering_send = False
            self.selector_handler.modify(self.comm_socket, wr=0)
        else:
            self.send_buf = bdata[sent:]
            self.buffering_send = True
            self.selector_handler.modify(self.comm_socket, wr=1)

    def ttse_connected__on_exit(self):
        self.log(f'Disconnected from {self.comm_addr}')

    def send_data_conversion(self, bdata):
        return bdata

    def rcv_data_conversion(self, bdata):
        return [bdata]

    def ttse__on_finished(self):
        if hasattr(self.base, 'ttse__on_socket_finished'):
            self.base.ttse__on_socket_finished()
            if hasattr(self.base, 'ttse__on_socket_status'):
                self.base.ttse__on_socket_status('finished')
        if self.comm_socket:
            self.selector_handler.unregister(sock=self.comm_socket)
            self.comm_socket.close()
        if self.server_socket:
            self.selector_handler.unregister(sock=self.server_socket)
            self.server_socket.close()


class TcpStrSocketHandler(TcpSocketHandler):
    def send_data_conversion(self, str_data):
        if not isinstance(str_data, str):
            raise TypeError('Data must be a string')
        return str_data.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        return [bdata.decode('utf-8', errors='replace')]


class TcpDictSocketHandler(TcpSocketHandler):
    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')
        pdict = pickle.dumps(dict_data)
        return b'' + struct.pack('!I', len(pdict)) + pdict

    def rcv_data_conversion(self, bdata):
        dicts = []
        self.rcv_buf += bdata
        while len(self.rcv_buf) > 4:
            plen = struct.unpack('!I', self.rcv_buf[:4])[0]
            if len(self.rcv_buf) < plen + 4:
                break
            dicts.append(pickle.loads(self.rcv_buf[4:plen + 4]))
            self.rcv_buf = self.rcv_buf[plen + 4:]
        return dicts

```

## `File: TaskTonic\ttTonicStore\ttNetworking\ttUdpSockets.py`
```python
# TaskTonic/ttTonicStore/ttNetworking/ttUdpSockets.py

import socket
import pickle
from TaskTonic import ttTonic, ttLog
from .ttSelectorService import SelectorService


class UdpSocketHandler(ttTonic):
    """
    A lightweight, connectionless UDP handler.
    Ideal for fast, local smart home communication (e.g., WiZ Bulbs).
    """

    def __init__(self, host='0.0.0.0', port=0, as_server=False, **kwargs):
        from TaskTonic import ttLedger
        ledger = ttLedger()

        # REQUEST THE SERVICE
        srv = ledger.get_service_essence('networking_selector_service')
        if not srv:
            srv = SelectorService(log_mode=ttLog.QUIET)

        super().__init__(catalyst=srv.catalyst, **kwargs)

        self.host = host
        self.port = port
        self.as_server = as_server
        self.selector_handler = SelectorService()
        self.sock = None

    def ttse__on_start(self):
        self.log(f'Initializing UDP socket on {self.host}:{self.port}')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

        if self.as_server:
            # Bind to a specific port to listen for incoming datagrams
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.log(f'UDP Server listening on port {self.port}')
        else:
            self.sock.bind(('0.0.0.0', 0))
            allocated_port = self.sock.getsockname()[1]
            self.log(f'UDP Client bound to ephemeral port {allocated_port}')

        # Mode 1 means it's a standard Read/Write connection (not an 'accept' server)
        self.selector_handler.register(
            self.sock,
            self,
            rd=1,
            mode=1,
            rd_sparkle=self.ttse__on_udp_receive
        )
        self.to_state('ready')

    def ttse_ready__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('udp_ready')

    def ttse_ready__on_udp_receive(self, data, addr):
        """
        Since the SelectorHandler passes raw bytes, we need to extract
        both the data and the sender's address.
        Note: The standard TCP logic in SelectorHandler only reads data,
        not the address. We need to slightly adjust our approach.
        """
        # Read the full datagram directly from the socket
        try:
            payload = self.rcv_data_conversion(data)

            # Pass the data and the origin address up to the parent Tonic
            if hasattr(self.base, 'ttse__on_udp_data'):
                self.base.ttse__on_udp_data(payload, addr)

        except BlockingIOError:
            pass
        except Exception as e:
            self.log(f"UDP Receive Error: {e}")

    def ttsc_ready__send_data(self, data, target_addr):
        """
        Sends a UDP datagram to a specific address.
        :param data: The payload (dict, str, etc.)
        :param target_addr: Tuple (IP, Port)
        """
        bdata = self.send_data_conversion(data)
        try:
            self.sock.sendto(bdata, target_addr)
        except Exception as e:
            self.log(f"UDP Send Error to {target_addr}: {e}")

    def ttse__on_finished(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('finished')

        if self.sock:
            self.selector_handler.unregister(sock=self.sock)
            self.sock.close()

    # --- Conversion Methods (Override these in subclasses) ---

    def send_data_conversion(self, data):
        """Override to customize serialization (e.g., Pickle, JSON)."""
        return data

    def rcv_data_conversion(self, bdata):
        """Override to customize deserialization."""
        return bdata


class UdpDictSocketHandler(UdpSocketHandler):
    """A UDP handler specifically for transmitting Python dictionaries via Pickle."""

    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')
        return pickle.dumps(dict_data)

    def rcv_data_conversion(self, bdata):
        try:
            return pickle.loads(bdata)
        except Exception as e:
            self.log(f"Pickle decode error: {e}")
            return None
```

## `File: TaskTonic\ttTonicStore\ttNetworking\ttHttpSockets.py`
```python
# TaskTonic/ttTonicStore/ttNetworking/ttHttpSockets.py

from .ttTcpSockets import TcpSocketHandler


class HttpServerHandler(TcpSocketHandler):
    """
    A lightweight, asynchronous HTTP server designed to receive
    webhooks from local IoT devices (like Shelly buttons or relays).
    """

    def __init__(self, port=8080, **kwargs):
        super().__init__(as_server=True, host='0.0.0.0', port=port, **kwargs)
        self.request_buffer = b''

    def rcv_data_conversion(self, bdata):
        """
        Parses the raw incoming TCP stream to extract the HTTP request line.
        """
        self.request_buffer += bdata

        # Check if the HTTP headers are complete (identified by a double CRLF)
        if b'\r\n\r\n' in self.request_buffer:
            headers_raw, body = self.request_buffer.split(b'\r\n\r\n', 1)

            # Decode the headers safely
            header_text = headers_raw.decode('utf-8', errors='ignore')
            header_lines = header_text.split('\r\n')

            # The first line is the Request Line (e.g., "GET /relay/0?turn=on HTTP/1.1")
            request_line = header_lines[0]
            parts = request_line.split(' ')

            if len(parts) >= 2:
                method = parts[0]
                url = parts[1]

                # Send a standard HTTP 200 OK back to the device to close the transaction
                response = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
                self._send(response)

                # Reset the buffer for the next incoming request
                self.request_buffer = b''

                # Return the parsed data as a dictionary
                return [{'method': method, 'url': url}]

        return []

class HttpClientHandler(TcpSocketHandler):
    """
    A lightweight, asynchronous HTTP client designed to send quick
    commands to local IoT devices.
    """

    def __init__(self, host, port=80, **kwargs):
        super().__init__(as_client=True, host=host, port=port, **kwargs)
        self.target_host = host
        # self.response_buffer = b''

    def ttsc_connected__get(self, path="/"):
        request = f"GET {path} HTTP/1.1\r\nHost: {self.target_host}\r\nConnection: close\r\n\r\n"
        self.ttsc__send_data(request.encode('utf-8'))

    def rcv_data_conversion(self, bdata):
        return [{'body': bdata.decode('utf-8', errors='ignore')}]

        self.response_buffer += bdata

        # Nu zoeken we veilig in de gecombineerde buffer
        if b'\r\n\r\n' in self.response_buffer:
            headers, body = self.response_buffer.split(b'\r\n\r\n', 1)
            res = [{'body': body.decode('utf-8', errors='ignore')}]
            self.response_buffer = b''  # Reset na succes
            return res

        return []
```

## `File: examples\main.py`
```python
from TaskTonic import *
from TaskTonic.ttLoggers import ttScreenLogService


class MyService(ttTonic):
    _tt_is_service = "my_service"
    _tt_base_essence = True

class MyProcess(ttTonic):
    def __init__(self, dup_at=0):
        super().__init__()
        self.dup_at = dup_at

    def ttse__on_start(self):
        self.log('Started')
        self.srv = MyService()
        self._tts__process(0)

    def _tts__process(self, count):
        count += 1
        self.log(f'Processing {count}')
        if count == 10:
            self.finish()
            pass
        else:
            if count == self.dup_at:
                self.log('duplicate')
                MyProcess(dup_at=0)
            self._tts__process(count)

    def ttse__on_finished(self):
        self.log('Finished')
        s = self.ledger.sdump()
        self.log(s)



class MyMachine(ttTonic):
    def ttse__on_start(self):
        self.srv = MyService()
        self.to_state('init')
        self.step_tmr = ttTimerRepeat(.5, name='stepper', sparkle_back=self.ttsc__step)
        self.disp_tmr = ttTimerRepeat(1, name='display', sparkle_back=self.ttsc__disp)

    def _ttss__main_catalyst_finished(self):
        pass # compleets catalyst after main catalyst stopped

    def ttsc__disp(self, timer_info):
        self.log(f'Called by: {ttSparkleStack().source}')

    def ttse__on_enter(self):
        self.log(f'Entering state {self.get_current_state_name()}')

    def ttse__on_exit(self):
        self.log(f'Exiting state {self.get_current_state_name()}')

    def ttsc_init__step(self, timer_info):
        self.log(f'timer info: {timer_info}')
        self.to_state('s1')

    def ttsc_s1__step(self, timer_info):
        self.to_state('s2')
    def ttsc_s2__step(self, timer_info):
        self.to_state('s3')
    def ttsc_s3__step(self, timer_info):
        self.log('Logging in state 4')
        self.to_state('s4')
    def ttsc_s4__step(self, timer_info):
        self.step_tmr.stop()
        self.finish()

    def ttse__on_finished(self):
        self.log('Finished')

class myMixDrink(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'DEMO PROJECT'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        p=MyProcess(dup_at=3)
        m=MyMachine()#log_mode='quiet')
#
if __name__ == "__main__":
    myMixDrink()

```

## `File: examples\TrafficLigthSimulationByGemini.py`
```python
# traffic_light_simulation.py

from TaskTonic import *


class TrafficLight(ttTonic):
    """
    A Tonic that simulates a traffic light state machine.
    It cycles through red, green, and yellow states using timers.
    """

    def __init__(self, red_duration=5, green_duration=5, yellow_duration=2):
        # Store the duration for each light state
        self.durations = {
            'red': red_duration,
            'green': green_duration,
            'yellow': yellow_duration
        }
        self.timer = None
        super().__init__()

    def ttse__on_start(self):
        """
        Event sparkle: Called automatically when the Tonic starts.
        We begin the cycle by transitioning to the 'red' state.
        """
        self.log("Traffic light is starting up...")
        self.to_state('red')
        # self.timer = ttTimerPausing(2, sparkle_back=self.ttsc__change_state)

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
        ttTimerSingleShot(seconds=duration, sparkle_back=self.ttsc__change_state)


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
        TrafficLight(red_duration=5, green_duration=5, yellow_duration=2)


# --- Main execution block ---
if __name__ == "__main__":
    # This creates an instance of our Formula, which automatically
    # sets up the ledger, creates the catalyst, creates our TrafficLight tonic,
    # and starts the main execution loop.
    TrafficLightSimulation()
```

## `File: examples\py_to_test_stuf_and_trow_away.py`
```python
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
```

## `File: examples\binding_demo.py`
```python
from TaskTonic import *
import json


class E(ttLiquid):
    pass

class T(ttTonic):
    def ttse__on_start(self):
        S()
        pass

    def ttsc__bindings_in_row(self, cnt):
        self.log(f'Create {cnt} bindings as row')
        t =T()
        self.log(self.infusions)
        cnt -= 1
        if cnt > 0:
            t.ttsc__bindings_in_row(cnt)

class S(ttTonic):
    _tt_is_service = 'demo_service'
    pass

class Demo(ttTonic):
    def log_ledger(self):
        self.log('== LEDGER ==')
        self.log(json.dumps(self.ledger.records, indent=4))

    def ttse__on_start(self):
        S()
        self.log('== Binding at Tonic level ==')
        self.ttsc__4bindings_in_self()

    def ttsc__4bindings_in_self(self):
        self.log('Create 4 bindings in self')
        for i in range(4):
            T()
        self.log(self.infusions)
        self.ttsc__bindings_in_row(4)

    def ttsc__bindings_in_row(self, cnt):
        self.log(f'Create {cnt} bindings as row')
        t = T()
        t.ttsc__bindings_in_row(cnt-1)
        self.log(self.infusions)
        ttTimerSingleShot(1, sparkle_back=self.ttsc__finish_demo)
        self.log(self.infusions)

    def ttsc__finish_demo(self, timer_info):
        self.log('Finishing demo tonic')
        self.finish()

class MyTonics(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'Binding demo'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

    def creating_starting_tonics(self):
        S()  # starting service
        Demo()

def print_ledger(l):
    print('== LEDGER ==')
    print(json.dumps(l.records, indent=4))



# print('== Binding at Essence level ==')
# l=ttLedger()
# l.update_formula('tasktonic/project/name', 'Binding demo')
#
# e = E()
# print_ledger(l)
#
# print('Create 4 bindings in e')
# for i in range(4):
#
#     e.bind(E)
# print_ledger(l)
# print(e.bindings)
#
# print('Create 4 bindings as row ')
# t = e
# for i in range(4):
#     t = t.bind(E)
# print_ledger(l)
# print(e.bindings)
#
# print('Finish e')
# e.finish()
# print_ledger(l)
# print(e.bindings)


# reset ledger singleton, forcing clean startup
ttLedger._instance = None
ttLedger._singleton_init_done = False

MyTonics()


```

## `File: examples\dut_in_distiller.py`
```python
from TaskTonic import *
from TaskTonic.ttTonicStore import ttDistiller
import json, time

class DUT(ttTonic):
    def ttse__on_start(self):
        self.log('DUT started')
        self.to_state('init')

    def ttse__on_finished(self):
        self.log('DUT finished')

    def ttse__on_enter(self):
        self.log('generic state enter')

    def ttse_init__on_enter(self):
        self.to_state('paused')

    def ttsc_paused__start_timer(self):
        ttTimerSingleShot(seconds=2)
        self.to_state('wait_on_timer')

    def ttse_wait_on_timer__on_timer(self, info):
        self.to_state('paused')

class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        self.dist = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.dut = DUT(name='TonicUnderTest')

recipe = TestRecipe()
distiller = recipe.dist
dut = recipe.dut

print(dut._index_to_state)
print(dut.sparkles)

distiller.stat_print(distiller.sparkle( timeout=5, till_state_in='paused'), dut.id)

print('start timer')
dut.ttsc__start_timer()

distiller.stat_print(distiller.sparkle( timeout=5, till_state_in='wait_on_timer'), dut.id)
distiller.stat_print(distiller.sparkle( timeout=5, till_sparkle_in='ttse__on_timer'), dut.id)
distiller.stat_print(distiller.sparkle( timeout=3))

print('finishing')
distiller.stat_print(distiller.finish_distiller(), 2)

```

## `File: examples\ip_communicatie.py`
```python
import struct

from TaskTonic import ttCatalyst, ttTonic, ttLog, ttSparkleStack
import socket, selectors, errno
import threading, queue, time


'''
Designer Notes: 
The SelectorHandler is designed as a catalyst for both itself and the socket handlers. This ensures 
that all 'sparkles' are executed from the same thread, which is required because Python's selectors 
are not thread-safe by design.

In the sparkling loop, we need to monitor both the catalyst queue and selector events. Since we 
want to avoid polling (busy waiting), a adapted queue is created: MyNotifyingQueue. Putting data now 
also signals a notification channel to trigger a selector event. This wakes up the loop, allowing 
it to process the queue and execute the sparkles.
'''

class SelectorHandler(ttCatalyst):
    _tt_is_service = 'selector_handling_service'
    _tt_root_context = True
    # _tt_force_stealth_logging = True

    def __init__(self, *args, name=None, log_mode=None, **kwargs):
        super().__init__(name, log_mode, dont_start_yet=True)

        self.register_data = {}
        self._queue_filled_notify_channel = None
        self._queue_filled_notify_channel_read = None

        # startup notifier
        self.selector = selectors.DefaultSelector()
        self._queue_filled_notify_channel, self._queue_filled_notify_channel_read = socket.socketpair()
        self._queue_filled_notify_channel.setblocking(False)
        self._queue_filled_notify_channel_read.setblocking(False)
        self.selector.register(self._queue_filled_notify_channel_read, selectors.EVENT_READ,
                               (1, self._handle_queue_filled_notify_channel, None))
        self.start_sparkling()

    def _init_service(self, *args, context=None, **kwargs):
        pass

    def new_catalyst_queue(self):
        class MyNotifyingQueue(queue.SimpleQueue):
            def __init__(self, catalyst, *args, **kwargs):
                super().__init__( *args, **kwargs)
                self.catalyst = catalyst

            def put(self, item):
                super().put(item)
                try:
                    self.catalyst._queue_filled_notify_channel.send(b'1')  # notify: queue filled
                except:
                    pass

        return MyNotifyingQueue(self)

    def sparkle(self):
        """
        The main execution loop of the Catalyst.

        This method continuously pulls work orders (instance, sparkle, args, kwargs)
        from the queue and executes them. It runs until the `self.sparkling` flag
        is set to False.
        """
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True
        sparkles_in_queue = True

        # The loop continues as long as the Catalyst is in a sparkling state.
        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0
            while next_timer_expire == 0.0:
                next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0
            if sparkles_in_queue: next_timer_expire = 0.0
            try:
                events = self.selector.select(timeout=next_timer_expire)
                for key, mask in events:
                    sock = key.fileobj
                    mode, rd_sparkle, wr_sparkle = key.data  # data contains the callback function
                    if mode == 1: # connection rd/wr
                        if mask & selectors.EVENT_READ:
                            try: data = sock.recv(65536)
                            except OSError: data = b''
                            if not data: self.unregister(sock=sock)
                            rd_sparkle(data)
                        if mask & selectors.EVENT_WRITE:
                            wr_sparkle()
                    elif mode == 2: #server accept
                        conn, addr = sock.accept()
                        conn.setblocking(False)
                        rd_sparkle(conn, addr)
            except TimeoutError: pass
            except OSError as e:
                # Op Windows: Check op 'bad file descriptor'
                if getattr(e, 'winerror', 0) == 10038:
                    # Logica om dode sockets op te ruimen
                    pass
                else:
                    raise e
            except Exception: raise

            # handle sparkles if any
            try:
                instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get_nowait()
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                while self.extra_sparkles:
                    instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                    sp_stck.push(instance, sparkle.__name__)
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                    sp_stck.pop()
                sparkles_in_queue = True
            except queue.Empty:
                sparkles_in_queue = False

        # clean up notifier channel
        self.selector.unregister(self._queue_filled_notify_channel_read)
        self._queue_filled_notify_channel.close()
        self._queue_filled_notify_channel_read.close()

    def _handle_queue_filled_notify_channel(self, data):
        # data read, but has no meaning.
        pass

    def register(self, sock, context, mode=1, mask=None, rd=None, wr=None, rd_sparkle=None, wr_sparkle=None):
        if sock is None: sock = context.comm_socket
        if mask is None:
            mask = 0
            if rd is not None and rd: mask |= selectors.EVENT_READ
            if wr is not None and wr: mask |= selectors.EVENT_WRITE
            if mask == 0: mask = selectors.EVENT_READ
        if rd_sparkle is None: rd_sparkle = context.ttse__on_socket_rd
        if wr_sparkle is None: wr_sparkle = context.ttse__on_socket_wr
        self.register_data[sock] = {'mask': mask, 'data': (mode, rd_sparkle, wr_sparkle)}
        self.selector.register(sock, mask, (mode, rd_sparkle, wr_sparkle))

    def unregister(self, sock=None):
        try: self.selector.unregister(sock)
        except: pass
        try: self.register_data.pop(sock)
        except: pass

    def modify(self, sock, mask=None, rd=None, wr=None):
        if mask is None:
            mask = self.register_data[sock]['mask']
            if rd is not None: mask = mask & ~selectors.EVENT_READ | (selectors.EVENT_READ if rd else 0)
            if wr is not None: mask = mask & ~selectors.EVENT_WRITE | (selectors.EVENT_WRITE if wr else 0)
        if mask == 0:
            if self.register_data[sock]['mask'] != 0:
                self.selector.unregister(sock)
        else:
            if self.register_data[sock]['mask'] == 0:
                self.selector.register(sock, mask, self.register_data[sock]['data'])
            else:
                self.selector.modify(sock, mask, self.register_data[sock]['data'])
        self.register_data[sock]['mask'] = mask


class SocketHandler(ttTonic):
    _tt_force_stealth_logging = True

    def __init__(self, as_server=None, as_client=None, host=None, port=None, **kwargs):
        # Look for service before calling super init and create if not active

        from TaskTonic import ttLedger
        l = ttLedger()
        srv = l.get_service_essence('selector_handling_service')
        if not srv:
            srv = SelectorHandler(log=ttLog.QUIET)

        super().__init__(catalyst=srv.catalyst, **kwargs)

        if as_server is not None and as_client is not None:
            raise ValueError('Make up your mind error: cannot specify both as_server and as_client')
        self.as_server = as_server if as_server is not None else not as_client
        self.server_host = host if host is not None else 'localhost'
        self.server_port = port if port is not None else '5555'
        self.server_addr = f'{host}:{port}'

        self.selector_handler = SelectorHandler()
        self.server_socket = None
        self.comm_socket = None
        self.comm_addr = None
        self.rcv_buf = b''
        self.send_buf = b''
        self.buffering_send = False

    def ttse__on_start(self):
        self.log('init_server' if self.as_server else 'init_client')
        self.to_state('init_server' if self.as_server else 'init_client')
        self.ttsc__start_init()

    def ttse__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status(self.get_active_state())

    def ttsc_init_server__start_init(self):
        self.log(f'Init server: {self.server_addr}')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)  # Accept 1 connection at a time
        self.server_socket.setblocking(False)
        self.to_state('server_wait_for_connection')
        self.selector_handler.register(self.server_socket, self, rd=1, mode=2, rd_sparkle=self.ttse__on_server_rd)

    def ttse_server_wait_for_connection__on_server_rd(self, conn, addr):
        self.selector_handler.unregister(sock=self.server_socket)
        self.server_socket.close()
        self.server_socket = None

        self.comm_socket = conn  # Store the client socket
        self.comm_addr = addr
        self.to_state('connected')
        self.selector_handler.register(self.comm_socket, self, rd=1)

        if self.base and hasattr(self.base, 'ttse__on_socket_connected'):
            self.base.ttse__on_socket_connected(addr)

    def ttsc_init_client__start_init(self):
        self.log(f'Init client: connect to {self.server_addr}')
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_socket.setblocking(False)

        try:
            self.selector_handler.register(self.comm_socket, self, wr=1)
            self.comm_socket.connect((self.server_host, self.server_port))
        except BlockingIOError as e:
            if e.errno == errno.EINPROGRESS or e.errno == errno.WSAEWOULDBLOCK:
                self.to_state('client_wait_for_connection')
                return
            else: raise e

        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)


    def ttse_client_wait_for_connection__on_socket_wr(self):
        # err = self.connected_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        # if err: raise ConnectionRefusedError(f"Connection failed: {os.strerror(err)}")
        self.comm_addr = f'{self.server_host}:{self.server_port}'
        self.to_state('connected')
        self.selector_handler.modify(self.comm_socket, rd=1, wr=0)

    def ttse_connected__on_enter(self):
        if hasattr(self.base, 'ttse__on_socket_status'):
            self.base.ttse__on_socket_status('connected')
        if hasattr(self.base, 'ttse__on_socket_connected'):
            self.base.ttse__on_socket_connected(self.comm_addr)

    def ttse_connected__on_socket_rd(self, data):
        if data:
            for data in self.rcv_data_conversion(data):
                self.base.ttse__on_socket_data(data)
        else:
            self.comm_socket = None
            self.finish()

    def ttse_connected__on_socket_wr(self):
        # pick up writing if send blocked
        self._send(self.send_buf)

    def ttsc_connected__send_data(self, data):
        bdata = self.send_data_conversion(data)
        if self.buffering_send: self.send_buf += bdata
        else: self._send(bdata)

    def _send(self, bdata):
        try:   sent = self.comm_socket.send(bdata)
        except BlockingIOError: sent = 0

        if sent == len(bdata):
            self.send_buf = b''
            self.buffering_send = False
            self.selector_handler.modify(self.comm_socket, wr=0)
        else:
            self.send_buf = bdata[sent:]
            self.buffering_send = True
            self.selector_handler.modify(self.comm_socket, wr=1)

    def ttse_connected__on_exit(self):
        self.log(f'Disconnected from {self.comm_addr}')

    def send_data_conversion(self, bdata):
        return bdata

    def rcv_data_conversion(self, bdata):
        return [bdata]

    def ttse__on_finished(self):
        if hasattr(self.base, 'ttse__on_socket_finished'):
            self.base.ttse__on_socket_finished()
            if hasattr(self.base, 'ttse__on_socket_status'):
                self.base.ttse__on_socket_status('finished')
        if self.comm_socket:
            self.selector_handler.unregister(sock=self.comm_socket)
            self.comm_socket.close()
        if self.server_socket:
            self.selector_handler.unregister(sock=self.server_socket)
            self.server_socket.close()

class StrSocketHandler(SocketHandler):
    def send_data_conversion(self, str_data):
        if not isinstance(str_data, str): raise TypeError('Data must be a string')
        return str_data.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        return [bdata.decode('utf-8', errors='replace')]

import pickle
class DictSocketHandler(SocketHandler):
    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, str): raise TypeError('Data must be a dict')
        pdict = pickle.dumps(dict_data)
        return b'' + struct.pack('!I', len(pdict)) + pdict

    def rcv_data_conversion(self, bdata):
        dicts = []
        self.rcv_buf += bdata
        while len(self.rcv_buf) > 4: # start check if rcv_buf at least hast length (4 bytes) and dict data
            plen = struct.unpack('!I', self.rcv_buf[:4])[0]
            if len(self.rcv_buf) < plen+4: break # not enough data, wait for it
            dicts.append(pickle.loads(self.rcv_buf[4:plen]))
            self.rcv_buf = self.rcv_buf[plen+4:]
        return dicts



# --- Usage Example ---
from TaskTonic import ttTonic, ttFormula, ttTimerRepeat, ttTimerSingleShot


class ChatClient(ttTonic):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.cnt = None
        self.net = None
        self.bulk_cnt = 0

    def ttse__on_start(self):
        self.log("Client starting delay...")
        ttTimerSingleShot(1, sparkle_back=self.ttse__on_delayed_start)

    def ttse__on_delayed_start(self, info):
        self.log("Starting Client...")
        # Bind Service: IpService is now a Catalyst running in its own thread
        self.net = StrSocketHandler(as_client=True, host='localhost', port=9999)
        self.cnt = 0

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Client Status: {status} - {info}")

    def ttse__on_socket_connected(self, addr):
        self.tmr = ttTimerRepeat(1, name='client_ping_tmr', sparkle_back=self.ttsc__ping)
        self.to_state('ping')

    def ttsc_ping__ping(self, info):
        self.cnt += 1
        self.net.ttsc__send_data(f"Ping {self.cnt}")
        self.log(f"Ping {self.cnt}")

    def ttse_ping__on_socket_data(self, data):
        # This method is called safely by the IpService thread!
        self.log(f"Client received: {data}")
        if 'STOPPED' in data:
            self.to_state('bulk')
            self.tmr.finish()

    def ttse_bulk__on_socket_data(self, data):
        if not hasattr(self, 'start_bulk'): self.start_bulk = time.time()
        self.bulk_cnt += len(data)
        self.log(f"Received: {self.bulk_cnt} bytes total in {(time.time()-self.start_bulk):2.3f} seconds")

    def ttse__on_socket_finished(self):
        self.finish()

class ChatServer(ttTonic):
    def ttse__on_start(self):
        self.log("Starting Server...")
        self.net = StrSocketHandler(as_server=True, host='localhost', port=9999)

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Server Status: {status} - {info}")

    def ttse__on_socket_data(self, data):
        self.log(f"Server got: {data}")
        # Simple echo (broadcasts to all connections of this tonic inInfusion completed this simple impl)
        self.net.ttsc__send_data(f"Echo: {data}")

        if data == 'Ping 4':
            self.net.ttsc__send_data(f" / STOPPED")
            ttTimerSingleShot(1, name='server_wait_for_sending_bulk', sparkle_back=self.ttsc__start_sending_bulk)

    def ttsc__start_sending_bulk(self, info):
        self.ttsc__send_bulk(100)

    def ttsc__send_bulk(self, cnt):
        if cnt == 0:
            ttTimerSingleShot(5, name='tmr_pause_before_finishing', sparkle_back=self.ttse__on_pause_over)
            return

        self.net.ttsc__send_data('1'*1_000_000)
        self.ttsc__send_bulk(cnt-1)

    def ttse__on_pause_over(self, info):
        self.finish()

    def ttse__on_socket_finished(self):
        self.finish()


class NetworkApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', 'full'),
        )

    def creating_starting_tonics(self):
        ChatServer(name="Server")
        # Give server time to bind (conceptually, though select handles async connect fine)
        ChatClient(name="Client")


if __name__ == "__main__":
    NetworkApp()
```

## `File: examples\ui_main.py`
```python
import sys
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt

from TaskTonic import *
from TaskTonic.ttTonicStore import ttPyside6Ui, ttPysideWindow, ttPysideWidget


class TrafficLightWidget(ttPysideWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tm_next = None

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl = QLabel("INIT")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("font-size: 30px; font-weight: bold; padding: 20px; background: #333; color: white;")
        self.layout.addWidget(self.lbl)

        # Widget naam: btn_next
        self.btn_next = QPushButton("Next State")
        self.layout.addWidget(self.btn_next)

    # --- Lifecycle ---

    def ttse__on_start(self):
        self.to_state('red')
        self.tm_next = ttTimerPausing(name='tm_next').pause()

    # --- State Machine Event Handling ---

    # Syntax: ttqt_<state>__<widget>__<signal>
    # TaskTonic maakt hiervan automatisch één wrapper 'ttqt__btn_next__clicked'
    # en zorgt dat de juiste methode wordt aangeroepen op basis van de state.

    def set_color(self, color):
        self.lbl.setText(color.upper())
        colors = {'red': '#f00', 'green': '#0f0', 'yellow': '#ff0', 'off': '#222'}
        self.lbl.setStyleSheet(f"font-size: 30px; padding: 20px; background: {colors.get(color)}; color: black;")

    def ttse_red__on_enter(self):
        self.log('COLOR RED')
        self.set_color('red')

    def ttqt_red__btn_next__clicked(self):
        self.to_state('green')

    def ttse_green__on_enter(self):
        self.log('COLOR GREEN')
        self.set_color('green')
        self.tm_next.change_timer(seconds=5).resume()

    def ttqt_green__btn_next__clicked(self):
        self.log("Klik in GROEN -> ga naar GEEL")
        self.to_state('yellow')

    def ttse_green__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('yellow')

    def ttse_yellow__on_enter(self):
        self.log('COLOR YELLOW')
        self.set_color('yellow')
        self.tm_next.change_timer(seconds=2.5).resume()

    def ttqt_yellow__btn_next__clicked(self):
        self.log("Klik in GEEL -> ga naar ROOD")
        self.to_state('red')

    def ttse_yellow__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('red')

    def ttse__on_exit(self):
        # for all states:
        self.tm_next.pause()
        self.log('COLOR OFF')
        self.set_color('off')

    # def ttqt__btn_next__released(self):
    #     self.log('button released')
    #
    # def ttqt_red__btn_next__pressed(self):
    #     self.log('button pressed in state red')

class MainWindow(ttPysideWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("TaskTonic + PySide6 Pluggable Syntax")
        self.resize(300, 250)

        self.light = TrafficLightWidget()
        self.setCentralWidget(self.light)

    def ttse__on_start(self):
        self.show()


class TrafficFormula(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttPyside6Ui(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        MainWindow()


if __name__ == "__main__":
    TrafficFormula()
```

## `File: examples\demo_data_store.py`
```python
from TaskTonic import *
from TaskTonic.ttTonicStore import ttStore
import random


class OperatorInterface(ttTonic):

    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.twin = DigitalTwin()

    def ttse__on_start(self):
        self.twin.subscribe("sensors", self.ttse__on_sensor_update)
        ttTimerSingleShot(5, name='parm_update')
        ttTimerSingleShot(10, name='end_program')


    def ttse__on_sensor_update(self, updates):
        for path, new, old, source in updates:
            sensor = self.twin.at(path).list_root
            self.log(f"UPDATE OF SENSOR {sensor.v}: {sensor['value'].v:.3f}{sensor.get('unit', '')}")

    def ttse__on_parm_update(self, tmr):
        self.twin['parameters/update_freq'] = .5

    def ttse__on_end_program(self, tmr):
        self.finish()
        self.catalyst.finish() # stop application

class MyProcess(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.twin = DigitalTwin()
        self.temp_sens = self.twin.at('sensors/#0')
        self.utmr = None

    def ttse__on_start(self):
        self.twin.subscribe("parameters", self.ttse__on_param_update)
        self.utmr = ttTimerRepeat(seconds=self.twin.get('parameters/update_freq', 5),
                                  name='update_timer')

    def ttse__on_param_update(self, updates):
        for path, new, old, source in updates:
            if path == 'parameters/update_freq':
                self.utmr.change_timer(seconds=new).restart()

    def ttse__on_update_timer(self, tmr):
        self.temp_sens['value'].v += random.uniform(-2, 2)
        # self.log('temp update')


class DigitalTwin(ttStore):
    _tt_is_service = "digital_twin"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _tt_post_init_action(self):
        super()._tt_post_init_action()
        with self.group(notify=False):
            self.set((
                ('parameters/update_freq', 2),
                ('parameters/temp_limit', 10),
                ('sensors/#', 'temp'),
                ('sensors/./value', 15.0),
                ('sensors/./unit', '℃'),
                ('sensors/./high_alarm', False),
                ('sensors/#', 'humidity'),
                ('sensors/./value', -1),
            ))
        self.log(f"Digital Twin is initialized\n{self.dumps()}")


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

    def creating_starting_tonics(self):
        DigitalTwin()
        OperatorInterface()
        MyProcess()




if __name__ == '__main__':
    myApp()
```

## `File: examples\hello_world.py`
```python
from TaskTonic import *

class HelloWorld(ttTonic):
    def __init__(self, name=None, log_mode=None):
        super().__init__(name, log_mode)

    def ttse__on_start(self):
        ttTimerRepeat(seconds=1.5, name='tm_step')
        self.to_state('hello')

    def ttse_hello__on_enter(self):
        self.log('Hello world')

    def ttse_hello__on_tm_step(self, tinfo):
        self.to_state('welcome')

    def ttse_welcome__on_enter(self):
        self.log('Welcome to TaskTonic')

    def ttse_welcome__on_tm_step(self, tinfo):
        self.to_state('ending')

    def ttse_welcome__on_tm_step(self, tinfo):
        self.ttsc__finish()


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        HelloWorld()


if __name__ == '__main__':
    myApp()

```

## `File: examples\demo_scheduled_timers.py`
```python
from TaskTonic import *
from TaskTonic.ttTonicStore.ttTimerScheduled import *

class TimTst(ttTonic):
    def __init__(self, **kwargs):
        super(TimTst, self).__init__(**kwargs)

    def ttse__on_start(self):
        tr = [
            ttTimerEveryYear(month=2, day=3, hour=10),
            ttTimerEveryYear(month="august", day=-1, hour=10),
            ttTimerEveryYear(month="august", day=2, hour=10),
            ttTimerEveryYear(month="february", day="monday", in_week=-1, time_str="9:56:45"),
            ttTimerEveryYear(month="september", day="saturday", in_week=-1, time_str="8:00:00"),
            ttTimerEveryYear(week=1, day="tuesday", hour=8),
            ttTimerEveryYear(week=3, day=6, hour=6),
            ttTimerEveryYear(week=52, day=6, time_str="23:59:59"),
            ttTimerEveryYear(month="december", day=-1, time_str="23:59:59"),

            ttTimerEveryMonth(day="wednesday", in_week=1, hour=10),
            ttTimerEveryMonth(day="wednesday", in_week=2, hour=10),
            ttTimerEveryMonth(day="wednesday", in_week=-1, hour=10),
            ttTimerEveryMonth(day="wednesday", in_week=-6, hour=10),
            ttTimerEveryMonth(day="tuesday", in_week=5, hour=10),
            ttTimerEveryMonth(day="tuesday", in_week=6, hour=10),
            ttTimerEveryMonth(day="monday", in_week=-1, hour=19),
            ttTimerEveryMonth(day=27, time_str="13:00:00"),
            ttTimerEveryMonth(day=-1, time_str="13:00:00"),
            ttTimerEveryMonth(day=-10, time_str="13:00:00"),

            ttTimerEveryWeek(day=0, time_str="23:59:59"),
            ttTimerEveryWeek(day="Tuesday", time_str="23:59:00"),
            ttTimerEveryWeek(day="wednesday", hour=1),
            ttTimerEveryWeek(day="friday", hour=2),
            ttTimerEveryWeek(day="saturday", hour=23),

            ttTimerEveryDay(hour=0),
            ttTimerEveryDay(hour=5),
            ttTimerEveryDay(hour=12),
            ttTimerEveryDay(hour=19),

            ttTimerEveryHour(time_str="59:59", name='tm_start_backup'),

            ttTimerEveryMinute(second=0),
            ttTimerEveryMinute(second=15),
            ttTimerEveryMinute(second=30.8),
            ttTimerEveryMinute(second=45)
        ]

        for t in tr:
            self.log(str(t))

    def ttse__on_timer(self, tinfo):
        self.log(f'{tinfo} >> {self.ledger.get_tonic_by_name(tinfo["name"])}')


class myMixDrink(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'DEMO PROJECT'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),
        )

    def creating_starting_tonics(self):
        TimTst()

myMixDrink()

```

## `File: examples\dut_in_distiller2.py`
```python
from TaskTonic import *
from TaskTonic.ttTonicStore import ttDistiller


class MyTonic(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)

    def ttse__on_start(self):
        self.log(self.ledger.sdump())
        ttTimerSingleShot(name='tm_finish', seconds=.5)
        ttTimerSingleShot(name='tm_new', seconds=.2)
        self.log(self.ledger.sdump())

    def ttse__on_tm_finish(self, tinfo):
        self.log(self.ledger.sdump())
        self.finish()

    def ttse__on_tm_new(self, tinfo):
        MyTonic()
        pass

    def ttse__on_finished(self):
        self.log(self.ledger.sdump())


class App(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'TEST PROJECT'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        self.main = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.dut = MyTonic()


app = App()
distiller = app.main
dut = app.dut

distiller.stat_print(distiller.sparkle(timeout=5, contract={'probes': ['tonics_sparkling', 'infusions', 'finishing']}))
print(ttLedger().sdump())

```

## `File: examples\queue_bencmark_the_tasktonic_way.py`
```python
import queue
import time
from TaskTonic import ttTonic, ttFormula, ttCatalyst, ttLog, ttLedger

"""
================================================================================
TaskTonic Architecture Note: Catalyst Queue Optimization
================================================================================

What this benchmark does:
This test evaluates the absolute throughput of the TaskTonic framework's core 
execution loop. It simulates a high-stress environment by firing hundreds of 
thousands of sequential 'sparkles' (atomic work orders) in a continuous chain. 
It measures the total time required for the `ttCatalyst` to process these items 
through its central queue, including the overhead of context switching and 
stack management.

Why this was tested:
As TaskTonic scales to handle heavy concurrent workloads—such as high-frequency 
IoT sensor streams or complex UI state changes—the latency of the Catalyst's 
internal queue becomes a primary performance bottleneck. The goal was to determine 
if rewriting the core execution loop in C++ was necessary to achieve higher 
throughput, or if native Python optimizations could suffice.

The Result & Architectural Decision:
This benchmark compares Python's standard `queue.Queue` against `queue.SimpleQueue`.
The standard `Queue` carries internal locking overhead to support task tracking 
methods like `task_done()` and `join()`. Because the `ttCatalyst` execution 
loop simply relies on continuous `.put()` and `.get()` operations, this extra 
thread-tracking overhead was entirely redundant.

The results proved that `queue.SimpleQueue`—a highly optimized, C-level 
unbounded FIFO queue—processes sparkles significantly faster (yielding a 25% 
to 40% performance increase). 

Conclusion:
The data from this benchmark forced the architectural decision to abandon 
`queue.Queue`. `queue.SimpleQueue` is now the permanent, standard engine for 
all `ttCatalyst` implementations, providing a massive, lock-free performance 
boost without requiring any C++ extensions.
================================================================================
"""


class SimpleQueueCatalyst(ttCatalyst):
    def new_catalyst_queue(self):
        # Override the queue creation to use the faster SimpleQueue
        return queue.SimpleQueue()


class StdQueueCatalyst(ttCatalyst):
    def new_catalyst_queue(self):
        # Explicitly use the standard Queue for comparison
        return queue.Queue()


class BenchTonic(ttTonic):
    def __init__(self, items=100000, **kwargs):
        # Prevent double execution due to potential multiple inheritance
        if getattr(self, '_tt_tonic_init_done', False):
            return

        self._tt_tonic_init_done = True
        super().__init__(**kwargs)
        self.total_items = items
        self.start_time = 0

    def ttse__on_start(self):
        self.start_time = time.perf_counter()
        # Start the chain reaction
        self.tts__chain(self.total_items)

    def tts__chain(self, count):
        if count > 0:
            self.tts__chain(count - 1)
        else:
            end_time = time.perf_counter()
            duration = end_time - self.start_time
            print(f"Processed {self.total_items:,} sparkles in {duration:.4f} seconds.")
            print(f"Speed: {self.total_items / duration:,.0f} sparkles/sec")
            self.finish()


def run_benchmark(catalyst_class, items):
    # Reset the ledger to allow a clean startup for the next formula run
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

    class BenchFormula(ttFormula):
        def creating_formula(self):
            return (
                ('tasktonic/project/name', 'Benchmark'),
                # Turn off logging completely to prevent I/O bottlenecks
                ('tasktonic/log/to', 'off'),
                ('tasktonic/log/default', ttLog.STEALTH),
            )

        def creating_main_catalyst(self):
            # Inject the specific catalyst we want to test
            catalyst_class(name='tt_main_catalyst')

        def creating_starting_tonics(self):
            BenchTonic(items=items)

    # Start the application
    BenchFormula()


if __name__ == "__main__":
    items_to_process = 200_000
    print(f"Benchmarking TaskTonic with {items_to_process:,} sequential sparkles...\n")

    print("Testing with standard queue.Queue...")
    run_benchmark(StdQueueCatalyst, items_to_process)

    print("\nTesting with queue.SimpleQueue...")
    run_benchmark(SimpleQueueCatalyst, items_to_process)
```

## `File: examples\ui_tk_main.py`
```python
import tkinter as tk

from TaskTonic import *
from TaskTonic.ttTonicStore import ttTkinterUi, ttTkinterFrame

class TrafficLightWidget(ttTkinterFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tm_next = None

    def setup_ui(self):
        # We gebruiken pack in plaats van QVBoxLayout
        self.lbl = tk.Label(self, text="INIT", font=("Arial", 30, "bold"), width=10, bg="#333", fg="white")
        self.lbl.pack(pady=20)

        # Widget naam: btn_next
        self.btn_next = tk.Button(self, text="Next State", font=("Arial", 14))
        self.btn_next.pack(pady=10)

    # --- Lifecycle ---

    def ttse__on_start(self):
        self.to_state('red')
        self.tm_next = ttTimerPausing(name='tm_next').pause()

    # --- State Machine Event Handling ---

    def set_color(self, color):
        colors = {'red': '#f00', 'green': '#0f0', 'yellow': '#ff0', 'off': '#222'}
        self.lbl.config(text=color.upper(), bg=colors.get(color, '#222'), fg="black")

    def ttse_red__on_enter(self):
        self.log('COLOR RED')
        self.set_color('red')

    # Tkinter syntax voor het 'command' attribuut van een button
    def tttk_red__btn_next__command(self):
        self.to_state('green')

    def ttse_green__on_enter(self):
        self.log('COLOR GREEN')
        self.set_color('green')
        self.tm_next.change_timer(seconds=5).resume()

    def tttk_green__btn_next__command(self):
        self.log("Klik in GROEN -> ga naar GEEL")
        self.to_state('yellow')

    def ttse_green__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('yellow')

    def ttse_yellow__on_enter(self):
        self.log('COLOR YELLOW')
        self.set_color('yellow')
        self.tm_next.change_timer(seconds=2.5).resume()

    def tttk_yellow__btn_next__command(self):
        self.log("Klik in GEEL -> ga naar ROOD")
        self.to_state('red')

    def ttse_yellow__on_tm_next(self, tinfo):
        self.log('Timeout on status')
        self.to_state('red')

    def ttse__on_exit(self):
        self.tm_next.pause()
        self.log('COLOR OFF')
        self.set_color('off')


class MainWindow(ttTonic):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # In Tkinter is het root window al aangemaakt door de Catalyst
        self.root = self.base.root
        self.root.title("TaskTonic + Tkinter Pluggable Syntax")
        self.root.geometry("300x250")

        # Voeg de TrafficLightWidget toe aan het hoofdscherm
        self.light = TrafficLightWidget(parent=self.root)
        self.light.pack(expand=True, fill=tk.BOTH)

    def ttse__on_start(self):
        # We vangen het sluiten van het venster af om TaskTonic netjes af te sluiten
        self.root.protocol("WM_DELETE_WINDOW", self.ttsc__finish)

    def ttse__on_finished(self):
        # Als de MainWindow tonic klaar is, sluiten we Tkinter netjes af
        self.root.destroy()


class TrafficFormula(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttTkinterUi(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        MainWindow()


if __name__ == "__main__":
    TrafficFormula()
```

## `File: examples\StoreDemo.py`
```python
from rfc3986.validators import host_is_valid

from TaskTonic.internals import Store

s = Store()

s['test'] = 1

s['list/#'] = 'name1' # list root
s['list/./a'] = 1
s['list/./b'] = 2

s['list1/#/name'] = 'name2'
s['list1/./a'] = 1
s['list1/./b'] = 2

i = s['list2'].append()
i.v = 'name3'
i['a'] = 1
i['b'] = 2

i = s['list2'].append()
i.v = 'name4'
i['a'] = 3
ii = i['b/c']
ii.v = 4

s['list2'].append().v = 'name5'

print(i)
l = s.at('list/#')
l['l'] = 10

_session = s.at('session')
store_session = _session.append()
store_session['s'] = 's1'

print("s:"+s.dumps())

print("i:"+i.dumps())
print("i.list_root:"+i.list_root.dumps())
print("i.parent:"+i.parent.dumps())

print("ii:"+ii.dumps())
print("ii.list_root:"+ii.list_root.dumps())
print("ii.list:"+ii.list_root.parent.dumps())

d = i.list_root.pop()
print(f"d: {d}")
print(s.dumps())



i = s['list3'].append()
i['name'].v = 'name31'
i['a'] = 3
ii = i['b/c']
ii.v = 4
i = s['list3'].append()
i['name'].v = 'name32'
i['a'] = 5
ii = i['b/c']
ii.v = 6

print("i:" + i.dumps())
print("i.list_root:" + i.list_root.dumps())
print("i.parent:" + i.parent.dumps())

print("ii:" + ii.dumps())
print("ii.list_root:" + ii.list_root.dumps())
print("ii.list:" + ii.list_root.parent.dumps())

print(s.dumps())
p = i.pop()
print(p)
print(s.dumps())

c = s.get_children_keys(path='')
print(c)
c = s.get_children_keys(path='list2')
print(c)

ic = s['list2'].children()
for c in ic:
    print(c)
    print(c.dumps())

print (s.dump())
```

## `File: examples\networking_udp_with_wiz.py`
```python
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
```

## `File: examples\networking_udp_ping_pong_tutorial.py`
```python
import json
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot
from TaskTonic.ttTonicStore.ttNetworking import UdpSocketHandler


# =============================================================================
# 1. THE SOCKET HANDLER
# =============================================================================

class JsonUdpSocketHandler(UdpSocketHandler):
    """
    A specific UDP handler that automatically translates Python dictionaries
    into JSON bytes (for sending) and JSON bytes back into dictionaries (for receiving).
    """

    def send_data_conversion(self, dict_data):
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')

        # Convert dict to a compact JSON string without spaces, then encode to bytes.
        # Adding \r\n is often helpful for strict external parsers.
        json_str = json.dumps(dict_data, separators=(',', ':')) + "\r\n"
        return json_str.encode('utf-8')

    def rcv_data_conversion(self, bdata):
        try:
            # Decode the incoming bytes to a string and parse the JSON
            json_str = bdata.decode('utf-8').strip()
            return json.loads(json_str)
        except Exception as e:
            self.log(f"JSON decode error: {e}")
            return None


# =============================================================================
# 2. THE SERVER TONIC (LISTENER)
# =============================================================================

class UdpEchoServer(ttTonic):
    """
    This Tonic acts as a UDP Server. It binds to a specific port and listens
    continuously in the background. It is entirely stateless.
    """

    def __init__(self, listen_port, **kwargs):
        super().__init__(**kwargs)
        self.listen_port = listen_port

    def ttse__on_start(self):
        self.log(f"Starting UDP Echo Server on port {self.listen_port}...")

        # Instantiate the handler as a server (as_server=True).
        # This binds the socket strictly to the specified port.
        self.udp = JsonUdpSocketHandler(
            host='0.0.0.0',
            port=self.listen_port,
            as_server=True
        )

    def ttse__on_udp_data(self, data, addr):
        """
        This Sparkle is automatically triggered by the UdpSocketHandler
        whenever a valid JSON payload arrives.

        :param data: The decoded JSON dictionary.
        :param addr: A tuple containing the (IP, Port) of the sender.
        """
        self.log(f"Server received from {addr}: {data}")

        # We can immediately send a reply back to the exact address
        # that sent us the message. This is the beauty of connectionless UDP!
        reply_payload = {
            "status": "success",
            "server_message": "I heard you!",
            "echo": data
        }

        self.log(f"Server sending reply back to {addr}...")
        self.udp.ttsc__send_data(reply_payload, addr)


# =============================================================================
# 3. THE CLIENT TONIC (SENDER)
# =============================================================================

class UdpPingClient(ttTonic):
    """
    This Tonic acts as a client. It grabs a random ephemeral port,
    sends a message to the server, waits for the reply, and then finishes.
    """

    def __init__(self, target_port, **kwargs):
        super().__init__(**kwargs)
        self.target_port = target_port

    def ttse__on_start(self):
        self.log("Initializing UDP Client...")

        # Instantiate the handler as a client (as_server=False).
        # The OS will automatically assign it a random available port.
        self.udp = JsonUdpSocketHandler(as_server=False)

        # We give the server a tiny fraction of a second to fully boot up
        # before we start firing packets at it.
        ttTimerSingleShot(seconds=0.5, name='tm_boot_delay')
        self.to_state('booting')

    def ttse_booting__on_tm_boot_delay(self, tinfo):
        self.to_state('sending_ping')

    def ttse_sending_ping__on_enter(self):
        payload = {
            "client_name": "TaskTonic Tutorial Bot",
            "action": "ping"
        }

        target_address = ('127.0.0.1', self.target_port)
        self.log(f"Client sending ping to {target_address}...")

        # Send the data. We target localhost (127.0.0.1) because the server
        # is running in the exact same application on our own machine.
        self.udp.ttsc__send_data(payload, target_address)

        # We wait 2 seconds. If a reply comes in during this time,
        # it will be caught by ttse__on_udp_data.
        ttTimerSingleShot(seconds=2.0, name='tm_finish')

    def ttse__on_udp_data(self, data, addr):
        """
        Catches the reply from the server. Notice this does not need a state
        prefix (like ttse_sending_ping__), meaning it will catch data
        regardless of what state the client is currently in.
        """
        self.log(f"Client received reply from Server {addr}: {data}")

    def ttse_sending_ping__on_tm_finish(self, tinfo):
        self.log("Client sequence complete. Shutting down client.")

        # Finishing the client will automatically clean up its UdpSocketHandler.
        # Note: The server will keep running in the background until the Distiller shuts down!
        self.finish()


# =============================================================================
# 4. THE FORMULA (BOOTSTRAPPER)
# =============================================================================

class UdpTutorialFormula(ttFormula):
    """
    The Formula brings everything together and starts the application.
    """

    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'UDP Ping Pong Tutorial'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', 'full'),
        )

    def creating_starting_tonics(self):
        # Define the port they will use to communicate
        SHARED_PORT = 55555

        # Start the listener first
        UdpEchoServer(listen_port=SHARED_PORT, name="EchoServer")

        # Start the sender
        UdpPingClient(target_port=SHARED_PORT, name="PingClient")


if __name__ == "__main__":
    UdpTutorialFormula()
```

## `File: examples\networking_tcp_echo.py`
```python
from TaskTonic import ttTonic, ttFormula, ttTimerRepeat, ttTimerSingleShot
from TaskTonic.ttTonicStore.ttNetworking import TcpStrSocketHandler
import time


class ChatClient(ttTonic):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.cnt = None
        self.net = None
        self.bulk_cnt = 0

    def ttse__on_start(self):
        self.log("Client starting delay...")
        ttTimerSingleShot(1, sparkle_back=self.ttse__on_delayed_start)

    def ttse__on_delayed_start(self, info):
        self.log("Starting Client...")
        # Bind Service: IpService is now a Catalyst running in its own thread
        self.net = TcpStrSocketHandler(as_client=True, host='localhost', port=9999)
        self.cnt = 0

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Client Status: {status} - {info}")

    def ttse__on_socket_connected(self, addr):
        self.tmr = ttTimerRepeat(1, name='client_ping_tmr', sparkle_back=self.ttsc__ping)
        self.to_state('ping')

    def ttsc_ping__ping(self, info):
        self.cnt += 1
        self.net.ttsc__send_data(f"Ping {self.cnt}")
        self.log(f"Ping {self.cnt}")

    def ttse_ping__on_socket_data(self, data):
        # This method is called safely by the IpService thread!
        self.log(f"Client received: {data}")
        if 'STOPPED' in data:
            self.to_state('bulk')
            self.tmr.finish()

    def ttse_bulk__on_socket_data(self, data):
        if not hasattr(self, 'start_bulk'): self.start_bulk = time.time()
        self.bulk_cnt += len(data)
        self.log(f"Received: {self.bulk_cnt} bytes total in {(time.time()-self.start_bulk):2.3f} seconds")

    def ttse__on_socket_finished(self):
        self.finish()

class ChatServer(ttTonic):
    def ttse__on_start(self):
        self.log("Starting Server...")
        self.net = TcpStrSocketHandler(as_server=True, host='localhost', port=9999)

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Server Status: {status} - {info}")

    def ttse__on_socket_data(self, data):
        self.log(f"Server got: {data}")
        # Simple echo (broadcasts to all connections of this tonic inInfusion completed this simple impl)
        self.net.ttsc__send_data(f"Echo: {data}")

        if data == 'Ping 4':
            self.net.ttsc__send_data(f" / STOPPED")
            ttTimerSingleShot(1, name='server_wait_for_sending_bulk', sparkle_back=self.ttsc__start_sending_bulk)

    def ttsc__start_sending_bulk(self, info):
        self.ttsc__send_bulk(100)

    def ttsc__send_bulk(self, cnt):
        if cnt == 0:
            ttTimerSingleShot(5, name='tmr_pause_before_finishing', sparkle_back=self.ttse__on_pause_over)
            return

        self.net.ttsc__send_data('1'*1_000_000)
        self.ttsc__send_bulk(cnt-1)

    def ttse__on_pause_over(self, info):
        self.finish()

    def ttse__on_socket_finished(self):
        self.finish()


class NetworkApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', 'full'),
        )

    def creating_starting_tonics(self):
        ChatServer(name="Server")
        # Give server time to bind (conceptually, though select handles async connect fine)
        ChatClient(name="Client")


if __name__ == "__main__":
    NetworkApp()
```

## `File: examples\https_get_sunset_time.py`
```python
import json
import urllib.request
from TaskTonic import ttTonic, ttCatalyst, ttFormula, ttLog
from TaskTonic.ttTonicStore import ttTimerEveryDay


'''
Demo fetching the sunset en rise time from https://api.sunrise-sunset.org

I doesn't use the networking module because of https
I implements u call from urllib in a separate catalyst that prevents the
main catalyst from blocking in a time consuming operation (you see time DURATION warning in the logs!!)
'''


class ApiWorker(ttCatalyst):
    """
    A dedicated worker catalyst for blocking API calls.
    This prevents the main UI or application from freezing during the HTTPS request.
    """

    def ttsc__fetch_sun_times(self, lat, lng):
        self.log("Fetching data from API (blocking thread...)")
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=0"

        try:
            # Create a Request object and spoof a standard browser User-Agent
            # to prevent getting a 403 Forbidden error from the API's bot protection.
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )

            # Pass the Request object to urlopen instead of the raw url string
            with urllib.request.urlopen(req, timeout=5.0) as response:
                response_text = response.read().decode('utf-8')
                data = json.loads(response_text)

                if data.get("status") == "OK":
                    self.base.ttse__on_sun_data_received(data['results'])
                else:
                    self.base.ttse__on_api_error(data.get("status"))

        except Exception as e:
            self.base.ttse__on_api_error(str(e))


class SunTracker(ttTonic):
    """
    The main Tonic that orchestrates the daily updates and stores the state.
    """

    def ttse__on_start(self):
        # Coordinates for Den Haag (The Hague)
        self.lat = 52.0705
        self.lng = 4.3007

        # Spawn the dedicated worker for safe HTTPS requests
        self.worker = ApiWorker(name="HttpsWorker")

        # Schedule the update to run every day at 01:00 AM
        ttTimerEveryDay(hour=1, name='daily_fetch')

        # Fetch immediately on startup
        self.ttsc__update_now()

    def ttsc__update_now(self):
        self.to_state('fetching')
        self.worker.ttsc__fetch_sun_times(self.lat, self.lng)

    def ttse_fetching__on_sun_data_received(self, results):
        self.to_state('idle')

        sunrise = results.get('sunrise')
        sunset = results.get('sunset')

        self.log(f"Sunrise in Den Haag: {sunrise}")
        self.log(f"Sunset in Den Haag: {sunset}")

        # Store the data centrally so other Tonics or the UI can react to it
        if self.ledger.formula:
            with self.ledger.formula.group():
                self.ledger.formula.set('weather/den_haag/sunrise', sunrise)
                self.ledger.formula.set('weather/den_haag/sunset', sunset)

    def ttse_fetching__on_api_error(self, error_msg):
        self.to_state('idle')
        self.log(f"Failed to fetch sun data: {error_msg}")

    def ttse_idle__on_tm_daily_fetch(self, info):
        self.log("Daily timer fired, fetching new sun times...")
        self.ttsc__update_now()


class WeatherApp(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/project/name': 'Weather Fetcher',
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': ttLog.FULL,
        }

    def creating_starting_tonics(self):
        SunTracker(name="SunTracker")


if __name__ == "__main__":
    WeatherApp()
```

## `File: examples\networking_http_demo.py`
```python
from TaskTonic import ttTonic, ttFormula, ttLog, ttTimerRepeat
from TaskTonic.ttTonicStore.ttNetworking.ttHttpSockets import HttpServerHandler, HttpClientHandler


class SmartHomeHub(ttTonic):
    """
    The server: Constantly listens for incoming HTTP requests (webhooks).
    """

    def ttse__on_start(self):
        self.log("Starting Smart Home Hub (HTTP Webhook Server) on port 8080...")
        # Start the built-in TaskTonic HTTP Server
        self.server = HttpServerHandler(port=8080)
        self.to_state('listening')

    def ttse__on_socket_data(self, data):
        # The HttpServerHandler has already converted the raw bytes into a dictionary
        self.log(f"Hub received Webhook trigger: {data}")
        # Note: The HttpServerHandler automatically sends a '200 OK' response back to the client!

    def ttse__on_socket_finished(self):
        self.log("Client disconnected. Hub ready for the next webhook.")


class SmartButton(ttTonic):
    """
    The client: Simulates a physical button that sends HTTP GET requests to the hub.
    """

    def ttse__on_start(self):
        self.log("Smart Button ready. Pressing automatically every 4 seconds...")
        self.press_count = 0
        # Simulate a button press every 4 seconds
        self.tmr = ttTimerRepeat(seconds=4.0, sparkle_back=self.ttsc__press_button)

    def ttsc__press_button(self, info):
        self.press_count += 1
        self.log(f"Button PRESSED! (Press #{self.press_count}) - Setting up HTTP Client...")

        # Because the HttpClientHandler uses 'Connection: close', the most robust
        # method is to create a new handler for each 'click'.
        self.client = HttpClientHandler(host='127.0.0.1', port=8080)
        self.to_state('connecting')

    def ttse_connecting__on_socket_connected(self, addr):
        self.log(f"Connected to Hub at {addr}. Sending HTTP GET request...")
        path = f"/scene/movie_night?press={self.press_count}"
        self.client.ttsc_connected__get(path=path)
        self.to_state('waiting_for_reply')

    def ttse_waiting_for_reply__on_socket_data(self, data):
        # Here we catch the '200 OK' returned by the Hub
        self.log(f"Hub replied with: {data}")

        # Close the TCP socket safely now that we have our answer
        self.client.ttsc__finish()
        self.to_state('idle')

    def ttse__on_socket_finished(self):
        self.log("HTTP Client socket closed cleanly.")


class LocalWebhookDemoApp(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/project/name': 'IoT Webhook Demo',
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': ttLog.FULL,
        }

    def creating_starting_tonics(self):
        # Start both systems. They run perfectly alongside each other on the same Catalyst.
        SmartHomeHub(name="HomeHub")
        SmartButton(name="LivingRoomButton")


if __name__ == "__main__":
    LocalWebhookDemoApp()

```

## `File: testing\test_core.py`
```python
# test_core.py
import pytest
from TaskTonic import ttLiquid, ttFormula


# --- Mock Classes ---
class SimpleLiquid(ttLiquid):
    def __init__(self, create_child=False, **kwargs):
        super().__init__(**kwargs)
        self.se = SimpleLiquid() if create_child else None

    def get_child_essence(self):
            return self.se

class LiquidWithService(ttLiquid):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.srv = MockService()


class MockService(ttLiquid):
    _tt_is_service = "MySingletonService"
    _tt_base_essence = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_count = 1
        self.access_count = 0

    def _tt_init_service_base(self, base, **kwargs):
        self.access_count += 1


class CoreFormula(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/testing/dont_start_catalysts', True),
            ('tasktonic/log/to', 'off'),
            ('tasktonic/log/default', 'stealth'),
        )

    def creating_starting_tonics(self):
        pass


# --- Tests ---

def test_ledger_registration():
    """Test of essences correct een ID krijgen en in de ledger komen."""
    f = CoreFormula()

    # check creating of main catalyst
    main_catalyst = f.ledger.get_tonic_by_name('tt_main_catalyst')
    assert main_catalyst.id == 0
    assert main_catalyst.name == 'tt_main_catalyst'
    assert main_catalyst.base is None

    t1 = SimpleLiquid(name="Ess1")
    assert t1.id == 1
    assert t1.name == "Ess1"


    t2 = SimpleLiquid(name="Ess2")
    assert t2.id == 2
    assert t2.name == "Ess2"

    assert t1.id != t2.id

    # Check ledger lookup
    retrieved = f.ledger.get_tonic_by_name("Ess1")
    assert retrieved == t1


def test_parent_child_binding():
    """Test parent-child relaties en automatische cleanup."""
    f = CoreFormula()
    parent = SimpleLiquid(create_child=True)

    # get the bound child
    child = parent.get_child_essence()

    assert child.base == parent
    assert child in parent.infusions

    # Finish parent -> must also finish child
    parent.finish()

    # both must be 'finished' (id -1 after unregister)
    assert parent.id == -1
    assert child.id == -1

#
# def test_service_singleton():
#     """Test of een Service echt maar 1x wordt aangemaakt."""
#     f = CoreFormula()
#
#     assert f.ledger.get_service_essence('MySingletonService') is None
#
#     # create service from context -1
#     srv = MockService()
#
#     assert f.ledger.get_service_essence('MySingletonService') == srv
#     assert srv.name == 'MySingletonService'
#     assert srv.id == 1
#     assert srv.init_count == 1
#     assert srv.access_count == 1
#
#     # first client, using the service
#     client_a = LiquidWithService(name='client_a')
#     first_id = client_a.srv.id
#     assert srv in client_a.infusions
#     assert srv.init_count == 1
#     assert srv.access_count == 2
#     assert len(srv.service_bases) == 2 # serv is also included
#
#     # second client, using the service
#     client_b = LiquidWithService(name='client_b')
#     assert srv in client_b.infusions
#     assert srv.init_count == 1
#     assert srv.access_count == 3
#     assert len(srv.service_bases) == 3
#
#     # check services
#     assert client_a.srv is client_b.srv
#     assert client_b.srv.id == first_id
#     assert set(srv.service_bases) == {None, client_a, client_b}
#
#     # finish essence that uses the service
#     client_a.finish()
#     assert set(srv.service_bases) == {None, client_b}
#     assert client_a.id == -1
#     assert srv.id == 1 # stil active
#
#     # finish essence that uses the service
#     client_b.finish()
#     assert set(srv.service_bases) == {None, }
#     assert client_b.id == -1
#     assert srv.id == 1  # stil active
#
#     # finish service
#     srv.finish()
#     assert srv.id == -1  # last base finished -> service finished
#





```

## `File: testing\conftest.py`
```python
# conftest.py
import pytest
from TaskTonic import ttLedger


@pytest.fixture(autouse=True)
def reset_ledger():
    """
    Reset de Singleton Ledger voor en na elke test.
    Dit voorkomt dat IDs oplopen en essences uit vorige tests blijven hangen.
    """
    # Setup: Zorg dat we schoon beginnen
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

    yield

    # Teardown: Ruim op na de test
    if ttLedger._instance:
        # Forceer een clear van de interne lijsten indien nodig
        ttLedger._instance.records = []
        ttLedger._instance.tonics = []
        ttLedger._instance.formula = None

    ttLedger._instance = None
    ttLedger._singleton_init_done = False
```

## `File: testing\test_distiller.py`
```python
import pytest
import time
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot, ttLedger
from TaskTonic.ttTonicStore.ttDistiller import ttDistiller


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def reset_ledger():
    """Zorgt voor een schone lei voor elke test en wacht op background threads."""
    ttLedger._instance = None
    ttLedger._singleton_init_done = False

    yield

    if ttLedger._instance:
        for t in ttLedger._instance.tonics:
            if t and hasattr(t, 'sparkling') and t.id > 0:
                start_t = time.time()
                while t.sparkling and time.time() - start_t < 1.0:
                    time.sleep(0.01)

        ttLedger._instance.records = []
        ttLedger._instance.tonics = []
        ttLedger._instance.formula = None

    ttLedger._instance = None
    ttLedger._singleton_init_done = False


# ==============================================================================
# TONICS VOOR TESTS
# ==============================================================================

class DUT(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.tm = None
        self.cycle_count = 0  # Toegevoegd voor de stop_on_probe test

    def ttse__on_start(self):
        self.to_state('init')

    def ttse_init__on_enter(self):
        self.to_state('paused')

    def ttsc_paused__start_timer(self, delay=2.0):
        # Start een timer, variabel gemaakt voor de OR-logica test
        self.tm = ttTimerSingleShot(seconds=delay)
        self.to_state('wait_on_timer')

    def ttse_wait_on_timer__on_timer(self, info):
        # Wordt aangeroepen als de timer afloopt
        self.cycle_count += 1
        self.to_state('finished_cycle')

    def ttse_finished_cycle__on_enter(self):
        pass  # empty state

    def ttsc__dut_finish(self):
        self.ttsc__finish()


class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',  # Geen output tijdens tests
            'tasktonic/log/default': 'stealth',
        }

    def creating_main_catalyst(self):
        # We gebruiken de Distiller in plaats van de standaard Catalyst
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        DUT(name="MyDevice")


# ==============================================================================
# TEST 1: BACKWARDS COMPATIBILITY (Legacy Syntax)
# ==============================================================================

def test_dut_flow_with_timer():
    recipe = TestRecipe()
    ledger = recipe.ledger
    distiller = recipe.distiller
    dut = ledger.get_tonic_by_name("MyDevice")

    assert isinstance(distiller, ttDistiller)
    assert dut is not None
    assert set(dut._index_to_state) == {'init', 'paused', 'wait_on_timer', 'finished_cycle'}

    # STAP 1: Oude platte syntax
    status = distiller.sparkle(timeout=1.0, till_state_in=['paused'])
    assert 'state_trigger: [paused]' in status.get('stop_condition', [])
    assert dut.get_current_state_name() == 'paused'

    # STAP 2: Vuur handmatig een commando af
    dut.ttsc__start_timer(delay=2.0)
    status = distiller.sparkle(timeout=1.0, till_state_in=['wait_on_timer'])
    assert dut.get_current_state_name() == 'wait_on_timer'

    # STAP 3: Wacht op de timer via de oude global sparkle_in check
    status = distiller.sparkle(timeout=5.0, till_sparkle_in=['ttse__on_timer'])
    assert 'sparkle_trigger: [ttse__on_timer]' in status.get('stop_condition', [])
    assert dut.get_current_state_name() == 'finished_cycle'

    # Finish
    dut.ttsc__dut_finish()
    status = distiller.sparkle(timeout=0.5)
    assert 'catalyst finished' in status['stop_condition']

    distiller.finish_distiller()


# ==============================================================================
# TEST 2: ADVANCED CONTRACTS (Multi-Tonic, AND/OR logic, Probes)
# ==============================================================================

class MultiDeviceRecipe(TestRecipe):
    def creating_starting_tonics(self):
        # We spawnen er nu TWEE om AND/OR logica te testen
        DUT(name="Device_Fast")
        DUT(name="Device_Slow")


def test_advanced_distiller_contracts():
    recipe = MultiDeviceRecipe()
    ledger = recipe.ledger
    distiller = recipe.distiller
    dev_fast = ledger.get_tonic_by_name("Device_Fast")
    dev_slow = ledger.get_tonic_by_name("Device_Slow")

    # --- DEEL 1: De 'AND' Conditie (stop_match_count: 'all') ---
    # We wachten expliciet tot BEIDE devices gepauzeerd zijn
    trace1 = distiller.sparkle(contract={
        'timeout': 2.0,
        'stop_match_count': 'all',
        'tonics': {
            'Device_Fast': {'till_state_in': ['paused']},
            'Device_Slow': {'till_state_in': ['paused']}
        }
    })

    assert 'contract_met' in trace1['stop_condition']
    assert trace1['contract_details']['match_count'] == 2
    assert trace1['contract_details']['target_count'] == 2
    assert trace1['contract_details']['matched_tonics'] ==  {'Device_Fast': ["state: 'paused'"], 'Device_Slow': ["state: 'paused'"]}

    assert dev_fast.get_current_state_name() == 'paused'
    assert dev_slow.get_current_state_name() == 'paused'

    # --- DEEL 2: De 'OR' Conditie met Probes (stop_match_count: 1) ---
    # We geven ze ongelijke timers
    dev_fast.ttsc__start_timer(delay=0.5)
    dev_slow.ttsc__start_timer(delay=2.5)

    # We vertellen de Distiller te stoppen zodra de ALLEREERSTE Tonic klaar is.
    # We checken dit puur op basis van de interne variabele via 'stop_on_probe'.
    trace2 = distiller.sparkle(contract={
        'timeout': 5.0,
        'stop_match_count': 1,  # Stop als er 1 matcht!
        'tonics': {
            'Device_Fast': {
                'probes': ['cycle_count'],
                'stop_on_probe': {'cycle_count': 1}
            },
            'Device_Slow': {
                'probes': ['cycle_count'],
                'stop_on_probe': {'cycle_count': 1}
            }
        }
    })

    assert 'contract_met' in trace2['stop_condition']

    # Omdat Device_Fast een timer van 0.5 had, moet deze klaar zijn
    assert dev_fast.cycle_count == 1
    assert dev_fast.get_current_state_name() == 'finished_cycle'

    # Device_Slow is trager en moet nog steeds wachten
    assert dev_slow.cycle_count == 0
    assert dev_slow.get_current_state_name() == 'wait_on_timer'

    # --- DEEL 3: Wacht op de trage ---
    trace3=distiller.sparkle(contract={
        'timeout': 5.0,
        'stop_match_count': 1,
        'tonics': {
            'Device_Slow': {'till_state_in': ['finished_cycle']}
        }
    })

    assert 'contract_met' in trace2['stop_condition']
    assert dev_slow.cycle_count == 1

    # Cleanup
    dev_fast.ttsc__dut_finish()
    dev_slow.ttsc__dut_finish()
    distiller.finish_distiller()
```

## `File: testing\test_store.py`
```python
import pytest
import threading
import time
from typing import List, Tuple, Any

# Adjust the import below to match your actual project structure
# from TaskTonic.ttTonicStore import Store, Item, ttStore
# For this example, assuming they are available in the context:
from TaskTonic.ttTonicStore import ttStore
from TaskTonic.internals.Store import Store, Item


# ======================================================================================================================
# PART 1: Core Data & Structure Tests (Store & Item)
# ======================================================================================================================
class TestStoreCore:
    """
    Tests for the foundational Store and Item classes.
    Focuses on path manipulation, data retrieval, syntax support, and hierarchical navigation.
    """

    @pytest.fixture
    def store(self):
        """
        Fixture to provide a clean Store instance for every test method.
        """
        return Store()

    def test_basic_set_and_get(self, store):
        """
        Test simple key-value setting and retrieval using absolute paths.
        """
        store.set([
            ('config/version', '1.0.0'),
            ('config/debug', True)
        ])

        assert store.get('config/version') == '1.0.0'
        assert store.get('config/debug') is True
        # Test default value for missing key
        assert store.get('config/missing', 'default') == 'default'

    def test_iterable_types_in_set(self, store):
        """
        Test that .set() accepts both lists and tuples (Iterable check).
        This validates the fix for the PyCharm warning/static analysis.
        """
        # Case 1: List of tuples (Standard)
        store.set([('a', 1)])
        assert store.get('a') == 1

        # Case 2: Tuple of tuples (The specific requested fix)
        # This ensures ((k,v), (k,v)) is valid runtime syntax
        store.set((
            ('b', 2),
            ('c', 3)
        ))
        assert store.get('b') == 2
        assert store.get('c') == 3

    def test_children_filtering(self, store):
        """
        Test the .children() iterator with and without prefix filtering.
        Verifies that:
        - No argument returns ALL children (lists and properties).
        - prefix='' returns only standard list items (created with '#').
        - prefix='name' returns only specific list items (created with 'name#').
        """
        # Define complex data structure as requested
        data = [
            ('sensors/#', 'temp_sensor_1'),  # Creates index 0 (e.g., sensors/#0)
            ('sensors/./unit', 'C'),
            ('sensors/./val', 25.5),

            ('sensors/#', 'hum_sensor'),  # Creates index 1 (e.g., sensors/#1)
            ('sensors/./unit', '%'),
            ('sensors/./val', 60),

            ('sensors/extra', 33),  # A standard property (not a list item)

            ('sensors/sens#', 'temp_sensor_2'),  # Creates named list index 0 (e.g., sensors/sens#0)
            ('sensors/sens./unit', 'C'),
            ('sensors/sens./val', 25.5),
        ]
        store.set(data)

        # 1. Test .children() WITHOUT arguments -> Should return EVERYTHING (4 items)
        # Expected keys: #0, #1, extra, sens#0
        sensors_node = store.at('sensors')
        all_children = list(sensors_node.children())

        assert len(all_children) == 4

        # Verify that 'extra' is among them
        # We look for the item where the value is 33
        has_extra = any(item.v == 33 for item in all_children)
        assert has_extra is True

        # 2. Test .children(prefix='') -> Should return only standard list items (2 items)
        # Expected: #0 (temp_sensor_1) and #1 (hum_sensor)
        # It should EXCLUDE 'extra' and 'sens#0'
        standard_list_items = list(sensors_node.children(prefix=''))

        assert len(standard_list_items) == 2
        assert standard_list_items[0].v == 'temp_sensor_1'
        assert standard_list_items[1].v == 'hum_sensor'

        # 3. Test .children(prefix='sens') -> Should return only 'sens#' items (1 item)
        # Expected: sens#0 (temp_sensor_2)
        sens_list_items = list(sensors_node.children(prefix='sens'))

        assert len(sens_list_items) == 1
        assert sens_list_items[0].v == 'temp_sensor_2'
        assert sens_list_items[0]['unit'].v == 'C'

    def test_item_navigation_and_value(self, store):
        """
        Test the Item object (cursor) functionality: .v property and navigation via [].
        """
        store.set([('machine/settings/speed', 100)])

        # Get an Item pointer
        speed_item = store.at('machine/settings/speed')

        assert isinstance(speed_item, Item)
        assert speed_item.v == 100

        # Change value via Item
        speed_item.v = 150
        assert store.get('machine/settings/speed') == 150

    def test_item_parent_navigation(self, store):
        """
        Test navigating up the tree using .parent.

        This test covers two scenarios:
        1. Hierarchy where every level has an explicit value.
        2. Hierarchy where intermediate levels are just containers (value is None),
           verified by checking their children.
        """
        # --- Scenario 1: Explicit values at every level ---
        store.set([
            ('grandparent', 100),
            ('grandparent/parent', 200),
            ('grandparent/parent/child', 300)
        ])

        item_child = store.at('grandparent/parent/child')
        item_parent = item_child.parent
        item_gp = item_parent.parent

        # Verify values to ensure .parent returned the correct node
        assert item_child.v == 300
        assert item_parent.v == 200
        assert item_gp.v == 100

        # Verify that root parent is None (or handles gracefully)
        # Assuming 'grandparent' is at root level:
        assert item_gp.parent is None or item_gp.parent.path == ''

        # --- Scenario 2: Container nodes (folders without values) ---
        store.set([
            ('folder/doc_a', 'content_a'),
            ('folder/doc_b', 'content_b')
        ])

        item_doc_a = store.at('folder/doc_a')
        item_folder = item_doc_a.parent

        # The folder itself was never assigned a value, so it should be None
        assert item_folder.v is None

        # However, it acts as a parent container, so we verify via children()
        # We expect 'doc_a' and 'doc_b' to be children of 'folder'
        folder_contents = list(item_folder.children())

        assert len(folder_contents) == 2

        # Extract values from children to verify content
        child_values = [child.v for child in folder_contents]
        assert 'content_a' in child_values
        assert 'content_b' in child_values

    def test_item_list_root(self, store):
        """
        Test .list_root functionality.
        This should find the list item itself, even when deep inside that item's properties.
        """
        store.set([
            ('users/#', 'alice'),
            ('users/./profile/age', 30)
        ])

        # We are deep inside the structure: users -> #0 -> profile -> age
        age_item = store.at('users/#0/profile/age')

        # list_root should return the item at 'users/#0'
        root_item = age_item.list_root

        assert root_item.v == 'alice'

    def test_dict_set_input(self, store):
        """
        Test that .set() also handles standard dictionaries correctly.
        """
        store.set({
            'direct/path': 123,
            'another/path': 'abc'
        })
        assert store.get('direct/path') == 123

    def test_complex_nested_updates(self, store):
        """
        Test updating an existing structure without wiping siblings.
        """
        # Initial setup
        store.set([
            ('grp/a', 1),
            ('grp/b', 2)
        ])

        # Update only 'a'
        store.set([('grp/a', 99)])

        assert store.get('grp/a') == 99
        assert store.get('grp/b') == 2  # Should still exist


# ======================================================================================================================
# PART 2: Advanced ttStore Features (Events, Locking, Concurrency)
# ======================================================================================================================

class MockStore(ttStore):
    """
    Minimal subclass of ttStore to test service functionalities in isolation.
    """
    _tt_is_service = "mock_store"

class TestTTStoreFeatures:
    """
    Tests for ttStore specific features: Subscriptions, Event Callbacks, and Thread Safety.
    """

    @pytest.fixture
    def store(self):
        # return MockStore()
        return Store()

    def test_subscribe_and_callback(self, store):
        """
        Test if subscribers receive the correct updates.
        """
        received_updates = []

        def on_update(updates):
            # updates is expected to be a list of tuples: (path, new, old, source)
            received_updates.extend(updates)

        # Subscribe to the 'sensors' path
        store.subscribe('sensors', on_update, recursive=True)

        # Perform a set action inside a group
        with store.group():
            store.set([
                ('sensors/temp', 20),
                ('other/param', 5)  # Should NOT trigger the callback
            ])

        # Assertions
        # 1. We expect only 1 update (for sensors/temp), not for other/param
        assert len(received_updates) == 1

        path, new_val, old_val, source = received_updates[0]
        assert path == 'sensors/temp'
        assert new_val == 20

    def test_wildcard_subscription(self, store):
        """
        Test if subscribing to a parent path catches changes in children.
        """
        updates_received = 0

        def callback(updates):
            nonlocal updates_received
            updates_received += len(updates)

        store.subscribe('config', callback, recursive=True)

        with store.group():
            store.set([
                ('config/a', 1),
                ('config/nested/b', 2),  # Should also trigger 'config' (no recursive set)
                ('config/nested', 3),
                ('outside', 4)
            ])

        assert updates_received == 3

    def test_multithreading_locking_integrity(self, store):
        """
        STRESS TEST: Thread Safety.

        Scenario: 10 threads running simultaneously.
        Each thread appends 100 items to the SAME list in the store ('logs/#').

        Expected Result: The list 'logs' must contain exactly 1000 items.
        Failure Mode: Race conditions cause items to be overwritten or RuntimeErrors.
        """
        num_threads = 10
        items_per_thread = 100
        total_expected = num_threads * items_per_thread

        def worker(thread_id):
            for i in range(items_per_thread):
                # Using '#' syntax forces a read-modify-write operation (get len, add item).
                # This requires robust locking inside the Store implementation.
                store.set([
                    ('logs/#', f"t{thread_id}-{i}"),
                    ('logs/./val', i)
                ])
                # Tiny sleep to encourage context switching to provoke race conditions
                time.sleep(0.0001)

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Check results
        # We cannot use store.get('logs') as it returns None for containers.
        # Instead, we use .children() to count the created items.
        logs_container = store.at('logs')
        all_logs = list(logs_container.children())

        assert len(all_logs) == total_expected, \
            f"Race condition detected! Expected {total_expected} items, found {len(all_logs)}."

        # Optional: Verify data integrity of the last item
        # This confirms that the values were stored correctly associated with the list items
        last_item = all_logs[-1]
        assert 't' in str(last_item.v)
        assert isinstance(last_item['val'].v, int)

    def test_read_write_concurrency(self, store):
        """
        Test stability when one thread reads continuously while another writes continuously.
        Ensures no RuntimeError (dictionary changed size during iteration) occurs.
        """
        stop_event = threading.Event()

        def writer():
            idx = 0
            while not stop_event.is_set():
                store.set([('status/heartbeat', idx)])
                idx += 1
                time.sleep(0.001)

        def reader():
            reads = 0
            while not stop_event.is_set():
                val = store.get('status/heartbeat')
                reads += 1
                time.sleep(0.001)
            return reads

        w_thread = threading.Thread(target=writer)
        r_thread = threading.Thread(target=reader)

        w_thread.start()
        r_thread.start()

        # Let them run concurrently for 1 second
        time.sleep(1)

        stop_event.set()
        w_thread.join()
        r_thread.join()

        # If we reached here without an exception, the test passed.
        assert store.get('status/heartbeat') > 0


class TestStoreNewFeatures:
    """
    Tests for the newly added advanced subscription features:
    - MQTT-style wildcards (* and **)
    - Atomic Snapshots (extract)
    - Self-reference in Snapshots (.)
    - Immediate Initialization (trigger_now)
    - Subscribing via Items
    """

    @pytest.fixture
    def store(self):
        return Store()

    def test_wildcard_single_level(self, store):
        """
        Test the single-level wildcard (*).
        It should match exactly one path segment.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Subscribe to any view under ui/
        store.subscribe("ui/*/view", callback)

        with store.group():
            store.set("ui/dashboard/view", "active")  # Should match
            store.set("ui/settings/view", "hidden")  # Should match
            store.set("ui/dashboard/other", 123)  # Should NOT match (wrong suffix)
            store.set("backend/dashboard/view", 1)  # Should NOT match (wrong prefix)

        assert len(events) == 2

        paths = [e[0] for e in events]
        assert "ui/dashboard/view" in paths
        assert "ui/settings/view" in paths

    def test_wildcard_recursive_level(self, store):
        """
        Test the recursive wildcard (**).
        It should match across multiple path segments.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.subscribe("system/**/status", callback)

        with store.group():
            # Should match (one level deep)
            store.set("system/network/status", "ok")
            # Should match (two levels deep)
            store.set("system/cpu/core_1/status", "high")
            # Should NOT match (doesn't end with status)
            store.set("system/cpu/core_1/usage", 99)

        assert len(events) == 2

        paths = [e[0] for e in events]
        assert "system/network/status" in paths
        assert "system/cpu/core_1/status" in paths

    def test_atomic_snapshots_with_extract_and_self(self, store):
        """
        Test extracting specific fields into a flat dictionary,
        including the self-reference (.).
        """
        events = []

        def callback(e):
            events.extend(e)

        # Initial state setup
        store.set([
            ("sensor/temp", 25.0),
            ("sensor/temp/unit", "Celsius"),
            ("sensor/temp/battery", 80)
        ])

        # Subscribe to the temp sensor, but only extract the value itself and the unit
        # We explicitly exclude battery by not listing it
        store.subscribe(
            "sensor/temp",
            callback,
            extract=[".", "unit"],
            recursive=False
        )

        # Trigger a change on the base path
        store.set("sensor/temp", 26.5)

        assert len(events) == 1

        path, snapshot, old_val, source = events[0]
        assert path == "sensor/temp"

        # Verify the snapshot dictionary
        assert isinstance(snapshot, dict)
        assert snapshot["."] == 26.5
        assert snapshot["unit"] == "Celsius"

        # Verify unrequested fields are not in the snapshot
        assert "battery" not in snapshot

    def test_trigger_now(self, store):
        """
        Test if trigger_now=True immediately fires the callback with the current state.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set("app/ready", True)

        # Subscribe with trigger_now, it should fire immediately during the function call
        store.subscribe("app/ready", callback, trigger_now=True)

        assert len(events) == 1

        path, val, old_val, source = events[0]
        assert path == "app/ready"
        assert val is True
        assert old_val is None
        assert source == "init"

    def test_trigger_now_with_extract(self, store):
        """
        Test if trigger_now=True works correctly in combination with extract snapshots.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set([
            ("ui/button", "submit"),
            ("ui/button/color", "blue")
        ])

        # This should immediately return a snapshot of the current state
        store.subscribe("ui/button", callback, extract=[".", "color"], trigger_now=True)

        assert len(events) == 1

        path, snapshot, old_val, source = events[0]
        assert path == "ui/button"
        assert snapshot["."] == "submit"
        assert snapshot["color"] == "blue"

    def test_item_subscribe(self, store):
        """
        Test if subscribing directly via an Item object works identically
        to calling subscribe on the store.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Get the cursor
        btn_item = store.at("ui/dialog/btn_ok")

        # Subscribe via the item
        btn_item.subscribe(callback)

        # Trigger an update using the item's .v setter
        btn_item.v = "clicked"

        assert len(events) == 1
        assert events[0][0] == "ui/dialog/btn_ok"
        assert events[0][1] == "clicked"

    def test_wildcard_combined_with_snapshot(self, store):
        """
        Test combining single-level wildcards (*) with atomic snapshots (extract).
        Scenario: A list of UI parameters where modifying any ID triggers a snapshot
        of that specific ID's properties (color and active state).
        """
        events = []

        def callback(e):
            events.extend(e)

        # 1. Initial setup: Two UI buttons with their own state
        store.set([
            ("ui/items/btn_save/color", "blue"),
            ("ui/items/btn_save/active", True),
            ("ui/items/btn_cancel/color", "red"),
            ("ui/items/btn_cancel/active", False)
        ])

        # 2. Subscribe to ANY item under ui/items/
        # We want to extract 'color' and 'active' relative to the matched item.
        store.subscribe(
            "ui/items/*",
            callback,
            extract=["color", "active"],
            recursive=True
        )

        # 3. Action: Modify the color of btn_cancel
        store.set("ui/items/btn_cancel/color", "grey")

        # 4. Assertions for the first action
        assert len(events) == 1

        path, snapshot, old_val, source = events[0]

        # It should trigger exactly on the modified item's root path
        assert path == "ui/items/btn_cancel"

        # The snapshot must contain the new color, AND the unchanged active state
        assert isinstance(snapshot, dict)
        assert snapshot["color"] == "grey"
        assert snapshot["active"] is False

        # 5. Action: Modify the other button
        events.clear()
        store.set("ui/items/btn_save/active", False)

        # 6. Assertions for the second action
        assert len(events) == 1
        assert events[0][0] == "ui/items/btn_save"
        assert events[0][1]["color"] == "blue"  # Fetched the unchanged color
        assert events[0][1]["active"] is False  # The newly set active state

    def test_trigger_now_basic_value(self, store):
        """
        Test of trigger_now direct de huidige state afvuurt als een 'init' event.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Zet een initiële waarde in de store
        store.set("system/status", "online")

        # Abonneer met trigger_now=True
        store.subscribe("system/status", callback, trigger_now=True)

        # De callback moet onmiddellijk afgevuurd zijn, zonder dat er een nieuwe set() is gedaan
        assert len(events) == 1

        path, val, old_val, source = events[0]
        assert path == "system/status"
        assert val == "online"
        assert old_val is None  # Bij een init is er conceptueel geen old_val
        assert source == "init"  # Dit bewijst dat het door de trigger_now logica komt

    def test_trigger_now_empty_path(self, store):
        """
        Test of trigger_now netjes omgaat met paden waar nog geen data in zit.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Abonneer op een pad dat nog niet bestaat
        store.subscribe("ghost/path", callback, trigger_now=True)

        assert len(events) == 1

        path, val, old_val, source = events[0]
        assert path == "ghost/path"
        assert val is None  # Moet veilig None teruggeven
        assert source == "init"

    def test_trigger_now_with_extract_snapshot(self, store):
        """
        Test of trigger_now correct een atomische snapshot (dictionary) opbouwt
        als dit gecombineerd wordt met de extract parameter.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Zet een complexe structuur op
        store.set([
            ("ui/widget_1", "active"),
            ("ui/widget_1/color", "blue"),
            ("ui/widget_1/size", 100),
            ("ui/widget_1/hidden", False)
        ])

        # Abonneer met zowel trigger_now als extract
        store.subscribe(
            "ui/widget_1",
            callback,
            extract=[".", "color", "size"],
            trigger_now=True
        )

        assert len(events) == 1

        path, snapshot, old_val, source = events[0]

        assert path == "ui/widget_1"
        assert source == "init"

        # Verifieer dat de snapshot een correct opgebouwde dictionary is
        assert isinstance(snapshot, dict)
        assert snapshot["."] == "active"
        assert snapshot["color"] == "blue"
        assert snapshot["size"] == 100

        # Het veld 'hidden' mag niet in de snapshot zitten, want het zat niet in de extract lijst
        assert "hidden" not in snapshot

    def test_trigger_now_with_wildcard_and_snapshot(self, store):
        """
        Test if trigger_now correctly fetches a list of items using a wildcard,
        builds snapshots for ALL existing matches, and returns them in one initial batch.
        Crucial for initial UI rendering of lists.
        """
        events = []

        def callback(e):
            events.extend(e)

        # 1. Pre-fill the store with multiple items
        store.set([
            ("ui/list/item_1/color", "red"),
            ("ui/list/item_1/active", True),
            ("ui/list/item_2/color", "blue"),
            ("ui/list/item_2/active", False),
            ("ui/other_stuff/color", "green")  # Should be ignored
        ])

        # 2. Subscribe with trigger_now, wildcard, AND extract
        store.subscribe(
            "ui/list/*",
            callback,
            extract=["color", "active"],
            recursive=True,
            trigger_now=True
        )

        # 3. Assertions
        assert len(events) == 2

        # Extract paths and snapshots for easy checking
        results = {e[0]: e[1] for e in events}

        assert "ui/list/item_1" in results
        assert "ui/list/item_2" in results

        assert results["ui/list/item_1"]["color"] == "red"
        assert results["ui/list/item_1"]["active"] is True

        assert results["ui/list/item_2"]["color"] == "blue"
        assert results["ui/list/item_2"]["active"] is False

    def test_unsubscribe_by_instance(self, store):
        """Test if unsubscribing via an instance (owner) removes all linked callbacks."""

        class MockWidget:
            def __init__(self):
                self.count = 0

            def on_change(self, events):
                self.count += 1

        widget = MockWidget()
        # Automatically detects 'widget' as owner because on_change is a bound method
        store.subscribe("ui/theme", widget.on_change)

        # Update 1: Should trigger
        store.set("ui/theme", "dark")
        assert widget.count == 1

        # Unsubscribe using the instance
        store.unsubscribe(widget)

        # Update 2: Should NOT trigger
        store.set("ui/theme", "light")
        assert widget.count == 1

    def test_unsubscribe_lambda_with_owner(self, store):
        """Test if a lambda linked to an owner is correctly removed."""
        results = []

        class Owner: pass

        my_owner = Owner()

        # Subscribe a lambda and manually link it to my_owner
        store.subscribe("data/val", lambda e: results.append(e), owner=my_owner)

        # Update 1: Should trigger
        store.set("data/val", 100)
        assert len(results) == 1

        # Unsubscribe the owner
        store.unsubscribe(my_owner)

        # Update 2: Should NOT trigger
        store.set("data/val", 200)
        assert len(results) == 1

    def test_unsubscribe_by_callback_function(self, store):
        """Test if unsubscribing via the function itself works."""
        self.call_count = 0

        def my_callback(events):
            self.call_count += 1

        store.subscribe("system/status", my_callback)

        store.set("system/status", "online")
        assert self.call_count == 1

        # Unsubscribe using the function reference
        store.unsubscribe(my_callback)

        store.set("system/status", "offline")
        assert self.call_count == 1

    def test_item_unsubscribe_all_on_path(self, store):
        """Test if item.unsubscribe() without args clears the entire path."""
        count_a = 0
        count_b = 0

        def cb_a(e): nonlocal count_a; count_a += 1

        def cb_b(e): nonlocal count_b; count_b += 1

        item = store.at("ui/sidebar")
        item.subscribe(cb_a, owner=self) # use owner, because internal function, no class method
        item.subscribe(cb_b, owner=self)

        item.v = "open"
        assert count_a == 1
        assert count_b == 1

        # Remove ALL listeners for this path
        item.unsubscribe(self)

        item.v = "closed"
        assert count_a == 1
        assert count_b == 1


# ======================================================================================================================
# PART 3: Proxy Nodes (StoreLink) & Batch Iteration (set_each)
# ======================================================================================================================

class TestStoreLinkAndSetEach:
    """
    Tests for the StoreLink proxy pattern (aliasing) via the .link_to() method
    and the set_each batching method.
    """

    @pytest.fixture
    def store(self):
        """Fixture to provide a clean Store instance for every test method."""
        return Store()

    def test_storelink_passive_read_write(self, store):
        """
        Test if a passive link (bubble_events=False) correctly redirects basic reads
        and writes to the canonical target path.
        """
        # 1. Setup canonical data
        store.set("devices/lamp_1", {"state": "off", "brightness": 0})

        # 2. Create a passive link via Item method
        store.at("house/living/main_light").link_to("devices/lamp_1", bubble_events=False)

        # 3. Test reading via alias
        alias_item = store.at("house/living/main_light")
        assert alias_item.v["state"] == "off"

        # 4. Test writing via alias
        alias_item.set("brightness", 100)

        # 5. Verify the canonical path was updated
        assert store.get("devices/lamp_1/brightness") == 100

    def test_storelink_deep_path_resolution(self, store):
        """
        Test if the Store correctly resolves paths segment by segment when
        writing to or reading from a sub-property of a link.
        """
        store.set("devices/thermostat_1/temperature", 21.5)

        store.at("rooms/kitchen/climate").link_to("devices/thermostat_1", bubble_events=False)

        # Access deep property through the link
        deep_item = store.at("rooms/kitchen/climate/temperature")
        assert deep_item.v == 21.5

        # Modify deep property through the link
        deep_item.v = 22.0

        # Verify the physical device was updated
        assert store.get("devices/thermostat_1/temperature") == 22.0

    def test_storelink_active_event_bubbling(self, store):
        """
        Test if an active link (bubble_events=True) intercepts changes from the canonical path
        and injects an event into its own alias path so subscribers are notified.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set("devices/sensor_1/motion", False)

        store.at("security/zones/front_door").link_to("devices/sensor_1", bubble_events=True)

        # Subscribe to the alias path sub-property
        store.subscribe("security/zones/front_door/motion", callback)

        # Change the canonical path
        store.set("devices/sensor_1/motion", True)

        # The active link should have injected an event for the alias
        assert len(events) == 1
        path, new_val, old_val, source = events[0]
        assert path == "security/zones/front_door/motion"
        assert new_val is True

    def test_storelink_cascading_delete(self, store):
        """
        Test if deleting a canonical item automatically destroys the link
        and propagates a 'None' event to alias subscribers.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set("system/users/u1", {"name": "Alice"})

        store.at("ui/current_user").link_to("system/users/u1", bubble_events=True)
        store.subscribe("ui/current_user", callback)

        # Remove canonical item
        store.remove_item("system/users/u1")

        # Link should be destroyed and None propagated to alias
        assert store.get("ui/current_user") is None

        # Check the events. One should be the removal of the alias.
        removal_events = [e for e in events if e[0] == "ui/current_user" and e[1] is None]
        assert len(removal_events) == 1

    def test_storelink_circular_prevention(self, store):
        """
        Test if the deep path resolution catches circular links and raises
        a ValueError to prevent infinite recursion/loops.
        """
        store.at("folder_a").link_to("folder_b")
        store.at("folder_b").link_to("folder_a")

        with pytest.raises(ValueError) as excinfo:
            store.get("folder_a/prop")

        assert "Circular StoreLink detected" in str(excinfo.value)

    def test_storelink_dump_format(self, store):
        """
        Test if links are serialized correctly during a store dump,
        allowing them to be restored later.
        """
        store.set("devices/dummy", 123)
        store.at("alias/dummy").link_to("devices/dummy", bubble_events=True)

        dump_data = dict(store.dump())

        assert dump_data["devices/dummy"] == 123

        alias_dump = dump_data["alias/dummy"]
        assert isinstance(alias_dump, dict)
        assert alias_dump["$link"] == "devices/dummy"
        assert alias_dump["bubble_events"] is True

    def test_item_set_each_with_prefix(self, store):
        """
        Test the set_each method with a prefix filter.
        It should update matching children and ignore others.
        """
        store.set([
            ("room/lamp#0/brightness", 0),
            ("room/lamp#1/brightness", 0),
            ("room/fan#0/speed", 0)
        ])

        room = store.at("room")

        # Use set_each with a prefix to target only lamps
        room.set_each("brightness", 100, prefix="lamp")

        assert store.get("room/lamp#0/brightness") == 100
        assert store.get("room/lamp#1/brightness") == 100

        # Fan should remain unaffected and not have a brightness property
        assert store.get("room/fan#0/speed") == 0
        assert store.get("room/fan#0/brightness") is None

    def test_item_set_each_without_prefix(self, store):
        """
        Test the set_each method without a prefix filter.
        It should update all immediate children.
        """
        store.set([
            ("ui/widgets/#/disabled", False),
            ("ui/widgets/#/disabled", False),
            ("ui/widgets/#/disabled", False)
        ])

        assert store.get("ui/widgets/#0/disabled") is False
        assert store.get("ui/widgets/#1/disabled") is False
        assert store.get("ui/widgets/#2/disabled") is False

        widgets = store.at("ui/widgets")

        # Apply to all children
        widgets.set_each("disabled", True)

        assert store.get("ui/widgets/#0/disabled") is True
        assert store.get("ui/widgets/#1/disabled") is True
        assert store.get("ui/widgets/#2/disabled") is True

    def test_set_each_through_storelink(self, store):
        """
        Complex scenario: Test if set_each works correctly when the children
        it iterates over are actually links pointing elsewhere.
        """
        store.set("devices/l1/power", "off")
        store.set("devices/l2/power", "off")

        store.at("house/lamps/l1").link_to("devices/l1")
        store.at("house/lamps/l2").link_to("devices/l2")

        # Perform set_each on the alias folder
        store.at("house/lamps").set_each("power", "on")

        # Check if canonical devices were updated via deep resolution
        assert store.get("devices/l1/power") == "on"
        assert store.get("devices/l2/power") == "on"


# ======================================================================================================================
# PART 4: Event Routing Scenarios
# ======================================================================================================================

class TestEventRoutingScenarios:

    @pytest.fixture
    def store(self):
        return Store()

    def test_event_routing_passive_link(self, store):
        """
        Scenario 1: Passive Link (bubble_events=False)
        Proves that a physical change ONLY bubbles up the physical tree,
        and leaves the alias tree completely silent (no event storms).
        """
        store.set("devices/l1/power", "off")
        store.at("house/lamps/l1").link_to("devices/l1", bubble_events=False)

        device_events = []
        house_events = []

        store.subscribe("devices", lambda e: device_events.extend(e), recursive=True, owner=self)
        store.subscribe("house/lamps", lambda e: house_events.extend(e), recursive=True, owner=self)

        store.set("devices/l1/power", "on")

        assert len(device_events) == 1, "The physical tree should receive the event."
        assert device_events[0][0] == "devices/l1/power"

        assert len(house_events) == 0, "A passive link should NOT bubble events to its alias tree."

    def test_event_routing_active_link(self, store):
        """
        Scenario 2: Active Link (bubble_events=True)
        Proves that a physical change bubbles up the physical tree,
        AND is actively injected into the alias tree so context-listeners are notified.
        """
        store.set("devices/motion_1/detected", False)
        store.at("house/living/motion").link_to("devices/motion_1", bubble_events=True)

        device_events = []
        house_events = []

        store.subscribe("devices", lambda e: device_events.extend(e), recursive=True, owner=self)
        store.subscribe("house/living", lambda e: house_events.extend(e), recursive=True, owner=self)

        store.set("devices/motion_1/detected", True)

        assert len(device_events) == 1, "The physical tree should receive the event."
        assert device_events[0][0] == "devices/motion_1/detected"

        assert len(house_events) == 1, "An active link MUST bubble events to its alias tree."
        assert house_events[0][0] == "house/living/motion/detected"
        assert house_events[0][1] is True

    def test_wildcard_combined_with_active_storelink(self, store):
        """
        Scenario 3: Wildcards over Active Links
        Proves that a wildcard subscription on an alias folder correctly catches
        injected events from multiple active StoreLinks inside that folder.
        """
        # 1. Setup physical devices
        store["devices/sw_1/state"] = "off"
        store["devices/sw_2/state"] = "off"
        store["devices/sensor/temp"] = 20   # Unrelated device

        # 2. Setup the functional room layout with active links
        # We explicitly want to hear about changes to these switches in this room
        store.at("house/living/switches/main").link_to("devices/sw_1", bubble_events=True)
        store.at("house/living/switches/reading").link_to("devices/sw_2", bubble_events=True)

        events_caught = []

        def callback(e):
            events_caught.extend(e)

        # 3. Subscribe to ALL switches in the living room
        # Using recursive=True so we also catch the '/state' sub-property
        store.subscribe("house/living/switches/*", callback, recursive=True, owner=self)

        # 4. Trigger changes on the physical devices
        store.set("devices/sw_1/state", "on")
        store.set("devices/sensor/temp", 21)  # Should NOT trigger the wildcard
        store.set("devices/sw_2/state", "on")

        # 5. Assertions
        # We expect exactly 2 events (the two switches). The temp sensor is ignored.
        assert len(events_caught) == 2, "Wildcard should have caught exactly 2 injected alias events."

        # Verify the paths were correctly translated to the alias paths
        paths_caught = [e[0] for e in events_caught]
        assert "house/living/switches/main/state" in paths_caught
        assert "house/living/switches/reading/state" in paths_caught

        # Verify the values
        assert events_caught[0][1] == "on"
        assert events_caught[1][1] == "on"
```

## `File: testing\test_ttTonic.py`
```python
import pytest
import threading
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller


# --- Definition of a child Tonic to test infusions ---
class MockInfusion(ttTonic):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.is_finished = False

    def ttse__on_start(self):
        self.is_running = True
        self.is_finished = False

    def ttse__on_finished(self):
        self.is_running = False
        self.is_finished = True


# --- Definition of the Device Under Test (DUT) ---
class StateMachineTestTonic(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.action_log = []
        self.received_list_id = None
        self.child = None

    # --- TEST INTERFACE --------------------------------------------------------
    def ttsc__reenter_current_state(self):
        self.reenter_current_state()
    def ttsc__start_up_infusion(self):
        self.child = MockInfusion()
    # ---------------------------------------------------------------------------

    def ttse__on_start(self):
        self.action_log.append("on_start")
        self.to_state('idle')

    def ttse__on_finished(self):
        self.action_log.append("on_finished")

    def ttsc__test_state(self, state):
        self.to_state(state)

    # --- State Machine Handlers ---
    def ttse_idle__on_enter(self):
        self.action_log.append("enter_idle")

    def ttse_idle__on_exit(self):
        self.action_log.append("exit_idle")

    def ttse_active__on_enter(self):
        self.action_log.append("enter_active")

    def ttse_active__on_exit(self):
        self.action_log.append("exit_active")

    # --- Sparkles with Parameters ---
    def ttsc__receive_data(self, data_list, data_dict):
        self.action_log.append("receive_data")
        self.received_list_id = id(data_list)

    # --- State-bound Sparkles ---
    def ttsc_active__process_task(self):
        self.action_log.append("process_active")

    def ttsc__process_task(self):
        self.action_log.append("process_default")

    def ttsc__dut_finish(self):
        self.ttsc__finish()


# --- Definition of the Test Formula ---
class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        StateMachineTestTonic(name="TestDevice")


# --- Pytest Fixtures ---
@pytest.fixture
def setup_distiller():
    """Fixture to set up and tear down the Distiller and DUT for each test."""
    recipe = TestRecipe()
    ledger = recipe.ledger
    distiller = ledger.get_tonic_by_name('tt_main_catalyst')
    dut = ledger.get_tonic_by_name("TestDevice")

    yield distiller, dut

    # Teardown
    distiller.finish_distiller()


# --- Test Cases ---
def test_thread_safety_and_parameter_copying(setup_distiller):
    distiller, dut = setup_distiller

    # Wait for the device to reach the idle state
    distiller.sparkle(timeout=1.0, till_state_in=['idle'])
    assert "enter_idle" in dut.action_log

    original_list = [9, 8, 7]
    original_dict = {"status": "testing"}
    original_list_id = id(original_list)

    # Simulate an external event coming from a different thread (e.g. UI or Network)
    def background_worker():
        dut.ttsc__receive_data(original_list, original_dict)

    thread = threading.Thread(target=background_worker)
    thread.start()
    thread.join()

    # Wait for the catalyst to process the specific sparkle
    distiller.sparkle(timeout=1.0, till_sparkle_in=['ttsc__receive_data'])

    assert "receive_data" in dut.action_log

    if dut.received_list_id == original_list_id:
        pytest.fail("Mutable parameters were not copied across threads!")


def test_state_machine_transitions(setup_distiller):
    distiller, dut = setup_distiller

    # INIT
    status = distiller.sparkle(timeout=1.0, till_state_in=['idle'])
    assert 'state_trigger: [idle]' in status.get('stop_condition', [])
    dut.action_log.clear()


    # STAP 1: Normal transition to 'active'
    dut.ttsc__to_state('active')
    status = distiller.sparkle(timeout=1.0, till_state_in=['active'])

    assert 'state_trigger: [active]' in status.get('stop_condition', [])
    assert "exit_idle" in dut.action_log
    assert "enter_active" in dut.action_log

    dut.action_log.clear()

    # STAP 2: Idempotent transition (should do nothing)
    dut.ttsc__to_state('active')
    distiller.sparkle(timeout=0.2)  # Process queue, no trigger expected

    assert "exit_active" not in dut.action_log
    assert "enter_active" not in dut.action_log

    # STAP 3: Forced re-entry of the current state
    dut.ttsc__reenter_current_state()
    # Or explicitly: dut.to_state('active', force_reenter=True)
    distiller.sparkle(timeout=0.2)

    assert "exit_active" in dut.action_log
    assert "enter_active" in dut.action_log


def test_state_bound_sparkles(setup_distiller):
    distiller, dut = setup_distiller

    distiller.sparkle(timeout=1.0, till_state_in=['idle'])

    # Calling process_task in 'idle' should hit the default handler
    dut.ttsc__process_task()
    distiller.sparkle(timeout=0.5)

    assert "process_default" in dut.action_log
    assert "process_active" not in dut.action_log

    dut.action_log.clear()

    # Move to 'active' state
    dut.ttsc__to_state('active')
    distiller.sparkle(timeout=1.0, till_state_in=['active'])

    # Calling process_task in 'active' should hit the state-bound handler
    dut.ttsc__process_task()
    distiller.sparkle(timeout=0.5, till_sparkle_in=['ttsc_active__process_task'])

    assert "process_active" in dut.action_log
    assert "process_default" not in dut.action_log


def test_cleanup_infusions_on_finish(setup_distiller):
    distiller, dut = setup_distiller

    dut.ttsc__start_up_infusion()
    distiller.sparkle(timeout=0.5)

    child_tonic = distiller.ledger.get_tonic_by_name('02.MockInfusion')

    assert child_tonic is not None

    if not child_tonic.is_running:
        pytest.fail("Child infusion did not start.")

    # Finish the parent DUT
    dut.ttsc__dut_finish()

    # Wait until the catalyst runs out of things to do or the DUT finishes
    distiller.sparkle(timeout=1.0)

    if not child_tonic.is_finished:
        pytest.fail("Child infusion was not finished when the parent finished.")


```

## `File: testing\test_ttIpSockets.py`
```python
# this test is replaced by tests:
#   test_ttNetworking_ttSelectorService
#   test_ttNetworking_ttTcpSockets,
#   test_ttNetworking_ttUdpSockets,
#   test_ttNetworking_ttHttpSockets,
#
```

## `File: testing\test_ttNetworking.py`
```python
# this test is replaced by tests:
#   test_ttNetworking_ttSelectorService
#   test_ttNetworking_ttTcpSockets,
#   test_ttNetworking_ttUdpSockets,
#   test_ttNetworking_ttHttpSockets,
#
```

## `File: testing\test_ttNetworking_ttSelectorService.py`
```python
import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttIpSockets import SelectorHandler


class DummySocketTonic(ttTonic):
    """
    A simple Tonic to test if the SelectorService can register sockets
    without crashing or causing infinite loops.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dummy_sock = None
        self.selector = None

    def _tt_post_init_action(self):
        from TaskTonic import ttLedger
        ledger = ttLedger()

        self.selector = ledger.get_service_essence('selector_handling_service')
        if not self.selector:
            self.selector = SelectorHandler()

        super()._tt_post_init_action()

    def ttse__on_start(self):
        self.dummy_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dummy_sock.setblocking(False)

        self.selector.register(
            sock=self.dummy_sock,
            context=self,
            rd_sparkle=self.ttse__on_dummy_data,
            wr_sparkle=self.ttse__on_dummy_data
        )
        # GEEN to_state('waiting') of nep variabelen meer nodig!

    def ttse__on_dummy_data(self, data=None):
        pass

    def ttse__on_finished(self):
        if self.dummy_sock and self.selector:
            self.selector.unregister(sock=self.dummy_sock)
            self.dummy_sock.close()


class EngineTestFormula(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'off'),
            ('tasktonic/log/default', 'stealth')
        )

    def creating_main_catalyst(self):
        ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.dummy = DummySocketTonic(name="DummyTonic")


def test_selector_service_registration():
    """
    Validates that the base OS-level engine boots up and accepts socket registrations.
    """
    app = EngineTestFormula()
    dist = app.ledger.get_tonic_by_name('tt_main_catalyst')

    dist.start_sparkling()

    # Jouw geniale inzicht: Wacht gewoon tot de opstart-sparkle klaar is!
    contract = {
        'timeout': 2.0,
        'stop_match_count': 1,
        'tonics': {
            'DummyTonic': {
                'till_sparkle_in': ['ttse__on_start']
            }
        }
    }

    try:
        trace = dist.sparkle(contract=contract)
        assert 'contract_met' in trace['stop_condition']
    finally:
        dist.finish_distiller()

```

## `File: testing\test_ttNetworking_ttTcpSockets.py`
```python
import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import TcpDictSocketHandler


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TcpMockServer(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []
        self.client_connected = False

    def ttse__on_start(self):
        self.net = TcpDictSocketHandler(as_server=True, host='127.0.0.1', port=self.port)
        self.to_state('waiting')

    def ttse__on_socket_connected(self, addr):
        self.client_connected = True
        self.to_state('connected')

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)
        data['echo'] = True
        self.net.ttsc__send_data(data)


class TcpMockClient(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = []

    def ttse__on_start(self):
        self.net = TcpDictSocketHandler(as_client=True, host='127.0.0.1', port=self.port)
        self.to_state('connecting')

    def ttse__on_socket_connected(self, addr):
        self.to_state('connected')

    def ttsc_connected__send_test(self, payload):
        self.net.ttsc__send_data(payload)

    def ttse__on_socket_data(self, data):
        self.received_data.append(data)


class TcpTestFormula(ttFormula):
    def __init__(self, port):
        self.port = port
        super().__init__()

    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'off'),
        )

    def creating_main_catalyst(self):
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.server = TcpMockServer(port=self.port, name="ServerTonic")
        self.client = TcpMockClient(port=self.port, name="ClientTonic")


def test_tcp_socket_flow():
    """Tests the connection, transmission, and teardown of a TCP stream."""
    port = get_free_port()
    app = TcpTestFormula(port)
    dist = app.distiller

    # 1. Wait for connection
    connect_contract = {
        'timeout': 3.0,
        'stop_match_count': 'all',
        'tonics': {
            'ClientTonic': {
                'till_state_in': ['connected']
            },
            'ServerTonic': {
                'probes': ['client_connected'],
                'stop_on_probe': {'client_connected': True}
            }
        }
    }

    dist.sparkle(contract=connect_contract)

    assert app.client.get_current_state_name() == 'connected'
    assert app.server.client_connected is True

    # 2. Send and receive data
    app.client.ttsc_connected__send_test({"msg": "Hello"})

    echo_contract = {
        'timeout': 3.0,
        'stop_match_count': 1,
        'tonics': {
            'ClientTonic': {
                'till_sparkle_in': ['ttse__on_socket_data']
            }
        }
    }

    dist.sparkle(contract=echo_contract)

    assert len(app.server.received_data) == 1
    assert app.server.received_data[0]["msg"] == "Hello"
    assert app.client.received_data[0]["echo"] is True

    dist.teardown_test_environment()

```

## `File: testing\test_ttNetworking_ttUdpSockets.py`
```python
import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import UdpDictSocketHandler


def get_free_port():
    """Finds a free port to prevent 'Address already in use' errors."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class UdpEchoServer(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_data = None

    def ttse__on_start(self):
        self.udp = UdpDictSocketHandler(host='127.0.0.1', port=self.port, as_server=True)

    def ttse__on_udp_data(self, data, addr):
        self.received_data = data
        data['echo'] = True
        self.udp.ttsc__send_data(data, addr)


class UdpPingClient(ttTonic):
    def __init__(self, target_port, **kwargs):
        super().__init__(**kwargs)
        self.target_port = target_port
        self.received_reply = None

    def ttse__on_start(self):
        self.udp = UdpDictSocketHandler(as_server=False)
        self.to_state('sending')

    def ttse_sending__on_enter(self):
        payload = {"action": "ping"}
        self.udp.ttsc__send_data(payload, ('127.0.0.1', self.target_port))

    def ttse__on_udp_data(self, data, addr):
        self.received_reply = data


class UdpTestFormula(ttFormula):
    def __init__(self, port):
        self.port = port
        super().__init__()

    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'off'),
        )

    def creating_main_catalyst(self):
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.server = UdpEchoServer(port=self.port, name="Server")
        self.client = UdpPingClient(target_port=self.port, name="Client")


def test_udp_ping_pong():
    """Tests if a UDP client can successfully ping a server and receive an echo."""
    port = get_free_port()
    app = UdpTestFormula(port)
    dist = app.distiller

    contract = {
        'timeout': 2.0,
        'stop_match_count': 1,
        'tonics': {
            'Client': {
                'till_sparkle_in': ['ttse__on_udp_data']
            }
        }
    }

    trace = dist.sparkle(contract=contract)

    assert 'contract_met' in trace['stop_condition']
    assert app.server.received_data['action'] == 'ping'
    assert app.client.received_reply['echo'] is True

    dist.teardown_test_environment()

```

## `File: testing\test_ttNetworking_ttHttpSockets.py`
```python
import socket
from TaskTonic import ttTonic, ttFormula
from TaskTonic.ttTonicStore import ttDistiller
from TaskTonic.ttTonicStore.ttNetworking import HttpServerHandler, HttpClientHandler


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class WebhookServerTonic(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_webhook = None

    def ttse__on_start(self):
        self.server = HttpServerHandler(port=self.port)

    def ttse__on_socket_data(self, request_data):
        self.received_webhook = request_data


class WebhookClientTonic(ttTonic):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.received_response = None

    def ttse__on_start(self):
        self.client = HttpClientHandler(host='127.0.0.1', port=self.port)
        # self.to_state('connecting')

    def ttse__on_socket_connected(self, addr):
        # Fire the HTTP GET request as soon as the TCP connection is established
        self.client.ttsc_connected__get(path="/test_webhook")

    def ttse__on_socket_data(self, response_data):
        self.received_response = response_data


class HttpTestFormula(ttFormula):
    def __init__(self, port):
        self.port = port
        super().__init__()

    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'off'),
        )

    def creating_main_catalyst(self):
        self.distiller = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.server = WebhookServerTonic(port=self.port, name="Server")
        self.client = WebhookClientTonic(port=self.port, name="Client")


def test_http_webhook_flow():
    """Tests if the HTTP Server can receive a GET request and send a 200 OK back."""
    port = get_free_port()
    app = HttpTestFormula(port)
    dist = app.distiller

    # Wait until BOTH tonics have received their data
    contract = {
        'timeout': 3.0,
        'stop_match_count': 'all',
        'tonics': {
            # 'Server': {
            #     'till_sparkle_in': ['ttse__on_socket_data']
            # },
            'Client': {
                'till_sparkle_in': ['ttse__on_socket_data']
            }
        }
    }

    trace = dist.sparkle(contract=contract)

    assert 'contract_met' in trace['stop_condition']
    assert app.server.received_webhook['url'] == '/test_webhook'
    assert '200 OK' in app.client.received_response['body']

    dist.teardown_test_environment()

```

## `File: TaskTonic.egg-info\dependency_links.txt`
```text


```

## `File: TaskTonic.egg-info\top_level.txt`
```text
TaskTonic

```

## `File: TaskTonic.egg-info\SOURCES.txt`
```text
LICENSE
pyproject.toml
readme.md
TaskTonic/__init__.py
TaskTonic/__main__.py
TaskTonic/ttCatalyst.py
TaskTonic/ttFormula.py
TaskTonic/ttLedger.py
TaskTonic/ttLiquid.py
TaskTonic/ttLogger.py
TaskTonic/ttSparkleStack.py
TaskTonic/ttTimer.py
TaskTonic/ttTonic.py
TaskTonic.egg-info/PKG-INFO
TaskTonic.egg-info/SOURCES.txt
TaskTonic.egg-info/dependency_links.txt
TaskTonic.egg-info/top_level.txt
TaskTonic/internals/RWLock.py
TaskTonic/internals/Store.py
TaskTonic/internals/__init__.py
TaskTonic/ttLoggers/__init__.py
TaskTonic/ttLoggers/ttScreenLogger.py
TaskTonic/ttTonicStore/__init__.py
TaskTonic/ttTonicStore/ttDistiller.py
TaskTonic/ttTonicStore/ttPyside6Ui.py
TaskTonic/ttTonicStore/ttPysideWidget.py
TaskTonic/ttTonicStore/ttStore.py
TaskTonic/ttTonicStore/ttTimerScheduled.py
TaskTonic/ttTonicStore/ttTkinterUi.py
TaskTonic/ttTonicStore/ttTkinterWidget.py
```

## `File: build\lib\TaskTonic\__init__.py`
```python
from .ttLedger import ttLedger
from .ttSparkleStack import ttSparkleStack
from .ttFormula import ttFormula
from .ttLiquid import ttLiquid
from .ttTonic import ttTonic
from .ttCatalyst import ttCatalyst

from .ttLogger import ttLog
from .ttTimer import ttTimerSingleShot, ttTimerRepeat, ttTimerPausing
```

## `File: build\lib\TaskTonic\ttLedger.py`
```python
from . import ttLiquid, ttTonic
from .internals.RWLock import RWLock
from .internals.Store import Store

class ttLedger:
    """A thread-safe singleton class that serves as the central registry for all ttEssence instances.

    The Ledger is the authoritative source of truth for the state of the entire
    system. It assigns unique IDs, stores records of all active essences, and
    provides methods to look up essences by ID or name.
    """
    _lock = RWLock()
    _instance = None
    _singleton_init_done = False

    class TonicReservation(object):
        def __init__(self, tid, name):
            self.id = tid
            self.name = name

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock.write_access():
                if cls._instance is None:
                    cls._instance = super().__new__(cls, *args, **kwargs)
                    cls._singleton_init_done = False
        return cls._instance

    def __init__(self):
        if self._singleton_init_done: return
        with self._lock.write_access():
            if self._singleton_init_done: return
            self.tonics = [] # direct acces to liquid instance by id
            self.tonic_by_name = {}
            self.tonic_by_service = {}
            self.formula = Store()
            # init thread data, a data structure depending on active thread.
            self._singleton_init_done = True

    def update_formula(self, formula, val=None):
        """Updates the application's formula

        :param formula: The application definition object, typically a DataShare
                        instance containing configuration.
        :type formula: str, Collection[Tuple[str, Any]] or Dict[str, Any]]
        :param val: used if formula is a string to create a key, val pair
        :type val: any, optional
        """
        self.formula.set(formula, val)

    def make_reservation(self, service_name=None):
        with self._lock.write_access():
            try:
                tid = self.tonics.index(None)
                self.tonics[tid] = self.TonicReservation(tid, None)
            except ValueError:
                tid = len(self.tonics)
                self.tonics.append(self.TonicReservation(tid, None))

            if service_name is not None:
                self.tonic_by_name[service_name] = self.TonicReservation(tid, service_name)
        return tid

    def check_reservation(self, reservation, raise_on_err=False):
        if isinstance(reservation, str):
            reservation = self.tonic_by_name.get(reservation, None)
            if reservation is not None and isinstance(reservation, self.TonicReservation):
                return reservation.id
        elif isinstance(reservation, int) and reservation >= 0:
            if 0 <= reservation < len(self.tonics) \
            and isinstance(self.tonics[reservation], self.TonicReservation):
                return reservation

        if raise_on_err: raise RuntimeError(f'ID "{reservation}" is not a reservation')
        return None

    def register(self, essence, reservation=None):
        """Registers a ttEssence instance and assigns it a unique ID.

        :param essence: The ttEssence instance to be registered.
        :type essence: ttEssence

        :raises TypeError: If `essence` is not a ttEssence instance
        :return: The unique integer ID assigned to the essence.
        :rtype: int
        """
        from TaskTonic.ttLiquid import ttLiquid
        if not isinstance(essence, ttLiquid):
            raise TypeError('essence must be of type ttEssence')

        if reservation is not None:
            ess_id = self.check_reservation(reservation, raise_on_err=True)
            self.tonics[ess_id] = essence
            self.tonic_by_name[essence.name] = essence

        else: # no reservation, find or create space in list
            with self._lock.write_access():
                try:
                    ess_id = self.tonics.index(None)
                    self.tonics[ess_id] = essence
                    self.tonic_by_name[essence.name] = essence
                except ValueError:
                    ess_id = len(self.tonics)
                    self.tonics.append(essence)
                    self.tonic_by_name[essence.name] = essence
        return ess_id

    def unregister(self, liquid):
        """Unregisters a ttEssence instance from the ledger.

        (Note: This method is not yet implemented).

        :param liquid: The ttEssence instance to unregister.
        :type liquid: ttEssence
        """
        from TaskTonic import ttLiquid
        if isinstance(liquid, (ttLiquid, self.TonicReservation)):
            pass
        elif isinstance(liquid, int):

            if liquid == -1 or liquid >= len(self.tonics) or self.tonics[liquid] is None:
                raise RuntimeError(f"Id '{liquid}' not found to unregister")
            liquid = self.tonics[liquid]
        elif isinstance(liquid, str):
            liquid = self.tonic_by_name[liquid]
        else:
            raise TypeError('essence must be of type ttEssence or int or str')

        with self._lock.write_access():
            self.tonics[liquid.id] = None
            self.tonic_by_name.pop(liquid.name, None)
            liquid.id = -1

    def get_id_by_name(self, name):
        """Retrieves the ID of an essence by its registered name.

        :param name: The name of the essence to find.
        :type name: str
        :return: The integer ID of the essence, or -1 if not found.
        :rtype: int
        """
        with self._lock.read_access():
            ess = self.tonic_by_name.get(name, None)
            return ess.id if ess is not None else -1

    def get_tonic_by_name(self, name):
        """Retrieves a ttEssence instance by its registered name.

        :param name: The name of the essence to retrieve.
        :type name: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            return self.tonic_by_name.get(name, None)


    def get_tonic_by_id(self, id):
        """Retrieves a ttEssence instance by its unique ID.

        :param id: The unique integer ID of the essence.
        :type id: int
        :return: The ttEssence instance, or None if the ID is out of bounds.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            if 0 <= id < len(self.tonics): return self.tonics[id]
            return None

    def get_service_essence(self, service):
        """Retrieves a ttEssence instance by its service name.

        :param service: The name of the service of the essence to retrieve.
        :type service: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            return self.tonic_by_name.get(service, None)

    def sdump(self):
        def sdumptonic(t, b, indent):
            s = f'\n{indent}{"F! " if t.finishing else ""} {t.id:02d}[{t.name}] <{t.__class__.__name__}>'
            if hasattr(t, 'tonics_sparkling'): s+=f' cat:{t.tonics_sparkling} '
            if t.finishing: s+=' FINISHING '
            if hasattr(t, 'service_bases'):
                if t.base != b: return s+' SERVICE COPY'
                for sb in t.service_bases:
                    s+=f'\n{indent}  sb: {sb.id:02d}[{sb.name}]'
            for i in t.infusions:
                s += sdumptonic(i, t, ' | '+indent)
            return s

        from .ttTonic import ttTonic
        s = 'Ledger dump'
        for t in self.tonics:
            if isinstance(t, ttTonic):
                if t.base is None:
                    s += sdumptonic(t, None, ' - ')
            elif isinstance(t, self.TonicReservation):
                s += f'\n - {t.id:20d}[{t.name}] <RESERVATION>'

        return s+'\n'
```

## `File: build\lib\TaskTonic\ttTonic.py`
```python
from sys import prefix

from .ttSparkleStack import ttSparkleStack
from .ttLiquid import ttLiquid
import re, threading, copy


class ttTonic(ttLiquid):
    """
    A robust, passive framework class for creating task-oriented objects (Tonics).

    This class automatically discovers methods (sparkles) based on naming conventions,
    handles state management, and provides a structured logging system. All sparkle
    types (ttsc, ttse, tts, _tts) are handled uniformly by placing a 'work order'
    on a queue, which is then processed by an external execution loop.
    """

    def __init__(self, name=None, log_mode=None, catalyst=None):
        """
        Initializes the Tonic instance, discovers sparkles, and calls startup methods.

        :param context: The context in which this tonic operates.
        :param name: An optional name for the tonic. Defaults to the class name.
        :param fixed_id: An optional fixed ID for the tonic.
        """
        super().__init__(name=name, log_mode=log_mode)
        self.catalyst = catalyst
        # Discover all sparkles and build the execution system.
        self.state = -1  # Start with no state (-1)
        self._pending_state = -1
        self._sparkle_init()

    def _tt_post_init_action(self):
        # Prevent _tt_post_init_action  to runs twice
        # (e.g., due to the complex initialization order in ttPysideWidget
        # involving metaclasses and multiple inheritance).
        if getattr(self, '_post_init_done', False):
            return
        self._post_init_done = True
        # -----------------------
        # bind to catalyst
        if not hasattr(self, 'catalyst_queue'):
            self.catalyst = \
                self.catalyst if self.catalyst is not None \
                else self.base.catalyst if hasattr(self.base, 'catalyst') and self.base.catalyst is not None\
                else self.ledger.get_tonic_by_name('tt_main_catalyst')
            self.catalyst_queue = self.catalyst.catalyst_queue  # copy queue for (a bit) faster acces
            self.log(flags={'catalyst': self.catalyst.name})
            self.catalyst._ttss__add_tonic_to_catalyst(self.id)

        super()._tt_post_init_action()

        # After initialization is completed, queue the synchronous startup sparkles.
        if hasattr(self, '_ttss__on_start'):
            self._ttss__on_start()
        if hasattr(self, 'ttse__on_start'):
            self.ttse__on_start()

        if hasattr(self, '_auto_bind'):
            for auto_bind in self._auto_bind:
                prefix, sparkle, binder = auto_bind
                binder(prefix, sparkle)

    def _get_custom_prefixes(self):
        """
        Hook for syntax extension with new prefixes and the binding method to call
         for binding an event to the sparkle (ea. {'ttqt': self.qt_event_binder}).
        """
        return {}


    def _sparkle_init(self):
        """
        Performs a one-time, intensive setup to discover all sparkles, build
        the dispatch system, and create the public-facing callable methods. This
        is the core of the Tonic's introspection and setup logic.

        Called from the Essence metaclass after completion of __init__
        """

        # Prevent _sparkle_init  to runs twice
        # (e.g., due to the complex initialization order in ttPysideWidget
        # involving metaclasses and multiple inheritance).
        if getattr(self, '_sparkle_init_done', False): return
        self._sparkle_init_done = True

        sp_stck = ttSparkleStack()

        prefix_extension = self._get_custom_prefixes()
        prefixes = ['ttsc', 'ttse', 'tts', '_tts', '_ttss']
        prefixes.extend(prefix_extension.keys())
        prefix_pattern = "|".join(prefixes)

        # Define the regular expressions used to identify different sparkle types.
        # state_pattern = re.compile(f'^({prefix_pattern})_([a-zA-Z0-9_]+)__([a-zA-Z0-9_]+)$')
        # general_pattern = re.compile(f'^({prefix_pattern})__([a-zA-Z0-9_]+)$')
        general_pattern = re.compile(f'^({prefix_pattern})__(.+)$')
        state_pattern = re.compile(f'^({prefix_pattern})_(.+?)__(.+)$')

        # --- Phase 1: Discover all implementations from the class hierarchy (MRO) ---
        state_impls, generic_impls = {}, {}
        states, sparkle_names = set(), set()
        prefixes_by_cmd = {}

        # Iterate through the MRO (Method Resolution Order) in reverse to ensure
        # that methods in child classes correctly override those in parent classes.
        for cls in reversed(self.__class__.__mro__):
            if cls in (ttLiquid, object):
                continue
            for name, method in cls.__dict__.items():
                s_match = state_pattern.match(name)
                g_match = general_pattern.match(name)
                if g_match:
                    # Found a generic sparkle (e.g., 'ttsc__initialize')
                    prefix, sp_name = g_match.groups()
                    generic_impls[(prefix, sp_name)] = method
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)
                elif s_match:
                    # Found a state-specific sparkle (e.g., 'ttsc_waiting__process')
                    prefix, state_name, sp_name = s_match.groups()
                    state_impls[(prefix, state_name, sp_name)] = method
                    states.add(state_name)
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)


        # --- Phase 2: Build fast lookup tables for states ---
        self._state_to_index = {name: i for i, name in enumerate(sorted(list(states)))}
        self._index_to_state = sorted(list(states))
        num_states = len(self._index_to_state)

        # --- Phase 3A: Create fallback methods for state on_enter and on_exit
        if num_states:
            self._direct_execute_ttse__on_enter = self.ttse__on_enter
            self._direct_execute_ttse__on_exit = self.ttse__on_exit
        # --- Phase 3B: Create and bind all public-facing dispatcher methods ---
        sparkle_list = []
        for sp_name in sparkle_names:
            is_state_aware = any(sp_name == key[2] for key in state_impls.keys())
            for prefix in prefixes_by_cmd[sp_name]:
                interface_name = f"{prefix}__{sp_name}"
                sparkle_list.append(interface_name)

                # --- Path A: This is a state-aware command ---
                if is_state_aware:
                    # For state-aware commands, we build a list of methods, one for each state.
                    handler_list = [self._noop] * num_states
                    generic_handler = generic_impls.get((prefix, sp_name))
                    if generic_handler:
                        handler_list = [generic_handler] * num_states
                    for state_idx, state_name in enumerate(self._index_to_state):
                        state_handler = state_impls.get((prefix, state_name, sp_name))
                        if state_handler:
                            handler_list[state_idx] = state_handler

                    def create_put_state_sparkle(_list, _name):
                        # Create a state execution that will select the correct method by state from the list at
                        #  runtime and create the put_state_sparkle to put if on the queue
                        def create_executer():
                            def execute_state_sparkle(self, *args, **kwargs):
                                state_sparkle = _list[self.state]
                                self.log(flags={'state': self.state})
                                state_sparkle(self, *args, **kwargs)
                            execute_state_sparkle.__name__ = _name
                            return execute_state_sparkle

                        def put_state_sparkle(self, *args, **kwargs):
                            if threading.get_ident() != self.catalyst.thread_id:
                                args = tuple((arg if callable(arg) else copy.deepcopy(arg)) for arg in args)
                                kwargs = {key: (value if callable(value) else copy.deepcopy(value))
                                          for key, value in kwargs.items()}
                            self.catalyst_queue.put((self, create_executer(), args, kwargs, sp_stck.get_stack()))
                        return put_state_sparkle

                    # Bind the new put_state_sparkle function to the instance, making it a method.
                    setattr(self, interface_name, create_put_state_sparkle(handler_list, interface_name).__get__(self))

                    # Create direct-execute methods only for 'on_enter' and 'on_exit'
                    if interface_name in ['ttse__on_enter', 'ttse__on_exit']:
                        direct_method_name = f"_direct_execute_{interface_name}"

                        # This factory creates the direct execution method
                        # It needs to capture the handler_list (_list)
                        def create_direct_executor(_list, _name):
                            # This is the exact logic copied from 'execute_state_sparkle'
                            def direct_execute_method(self, *args, **kwargs):
                                state_sparkle = _list[self.state]
                                self.log(flags={'state': self.state})
                                state_sparkle(self, *args, **kwargs)
                            direct_execute_method.__name__ = _name
                            return direct_execute_method

                        # Bind the new direct method to the instance
                        setattr(self,
                                direct_method_name,
                                create_direct_executor(handler_list, interface_name).__get__(self))

                # --- Path B: This is a generic-only command ---
                else:
                    handler_method = generic_impls[(prefix, sp_name)]

                    def create_put_sparkle(_method):
                        # This put_sparkle always uses the one generic method.
                        def put_sparkle(self, *args, **kwargs):
                            if threading.get_ident() != self.catalyst.thread_id:
                                args = tuple((arg if callable(arg) else copy.deepcopy(arg)) for arg in args)
                                kwargs = {key: (value if callable(value) else copy.deepcopy(value))
                                          for key, value in kwargs.items()}
                            self.catalyst_queue.put((self, _method, args, kwargs, sp_stck.get_stack()))
                        return put_sparkle

                    # Bind the new put_sparkle function to the instance, making it a method.
                    setattr(self, interface_name, create_put_sparkle(handler_method).__get__(self))

        # --- Phase 4: Build fast lookup tables for sparkles ---
        self.sparkles = sorted(sparkle_list)

        # --- Phase 5: patch the _execute_sparkle function to normal mode ---
        self._execute_sparkle = self.__exec_sparkle

        # --- Phase 6: prpare for auto binding sparkles for extended syntax
        auto_bind = []
        for sparkle in self.sparkles:
            for prefix, binder in prefix_extension.items():
                if sparkle.startswith(prefix):
                    auto_bind.append((prefix, sparkle, binder))
        if auto_bind: self._auto_bind = auto_bind

        # Log the results of the discovery process.
        self.log(system_flags={'states': self._index_to_state, 'sparkles': self.sparkles})

    def _noop(self, *args, **kwargs):
        """A do-nothing method used as a default for unbound sparkles."""
        pass

    def to_state(self, state, no_change_on_eq=False):
        """
        Requests a state transition. The change is handled by the _execute_sparkle
        method after the current sparkle finishes.

        :param state: The name (str) or index (int) of the target state. When target == -1, stop machine stops
        :param no_change_on_eq: When False (default) state exit wil be executed on a change to the same state, on True not
        """
        to_state = -1  # no action
        if isinstance(state, str):
            to_state = self._state_to_index.get(state, None)
            if to_state is None: return
        elif isinstance(state, int) and 0 <= state < len(self._index_to_state):
            to_state = state
        elif isinstance(state, int) and state == -1:
            to_state = -1
        else:
            return

        if no_change_on_eq and to_state == self.state: return

        if self.state >= 0:
            self.catalyst._execute_extra_sparkle(self, self._direct_execute_ttse__on_exit)
        if to_state >= 0:
            self.catalyst._execute_extra_sparkle(self, self._ttinternal_state_change_to, to_state)
            self.catalyst._execute_extra_sparkle(self, self._direct_execute_ttse__on_enter)
        else:
            self.catalyst._execute_extra_sparkle(self, self._ttinternal_state_machine_stop)

    def _ttinternal_state_change_to(self, state):
        self.log(system_flags={'state': self.state, 'new_state': state})
        self.state = state

    def _ttinternal_state_machine_stop(self):
        self.log(system_flags={'state': self.state, 'new_state': None})
        self.state = -1
        pass

    def get_active_state(self):
        if self.state == -1: return '--'
        return self._index_to_state[self.state]

    def _execute_sparkle(self, sparkle_method, *args, **kwargs):
        """
        The single, central method for executing any sparkle from the queue. It
        is called by the external execution loop. It also handles logging and
        state transitions.

        This is the placeholder. On tonic startup this is replaced by __exec_sparkle, with this functionality.
        On finishing the tonic __exec_system_sparkle which only handles the system calls, and filters out user sparkles

        :param sparkle_method: The unbound method of the sparkle to execute.
        :param args: Positional arguments for the sparkle.
        :param kwargs: Keyword arguments for the sparkle.
        """
        pass

    def __exec_sparkle(self, sparkle_method, *args, **kwargs):
        """
        sparkle execution in running mode
        """
        interface_name = sparkle_method.__name__
        sp_stck = ttSparkleStack()
        self.log(flags={'sparkle': interface_name,
                        'source': f'{sp_stck.source_tonic_name}.{sp_stck.source_sparkle_name}'})
        # Execute the user's actual sparkle code, passing self to bind it.
        sparkle_method(self, *args, **kwargs)
        self.log(close_log=True)

    def __exec_system_sparkle(self, sparkle_method, *args, **kwargs):
        """
        sparkle execution in normal mode
        """
        if self.id < 0: return  # Tonic already unregistered (probably old sparkle in queue)

        interface_name = sparkle_method.__name__

        if interface_name.startswith('_ttss') \
        or interface_name in [
            'ttse__on_finished', 'ttse__on_exit',
            'ttse__on_service_base_completed', '_ttinternal_state_machine_stop',
        ]:
            self.__exec_sparkle(sparkle_method, *args, **kwargs)

    def get_current_state_name(self):
        """
        Gets the name of the current state.

        :return: The name of the state (str) or "None".
        """
        if self.state == -1: return "--"
        return self._index_to_state[self.state]

    # standard tonic sparkle
    def ttse__on_start(self): pass
    def ttse__on_finished(self): pass
    def ttse__on_enter(self): pass
    def ttse__on_exit(self): pass

    # --- System Lifecycle Sparkles ---
    def _ttss__on_start(self):
        """System-level sparkle for internal framework setup."""
        pass

    def finish(self):
        # Finish on tonic level, will first stop the tonic, and after that finish admin in the essence
        if self.finishing: return
        self.ttsc__finish()

    def ttsc__finish(self):
        if self.finishing: return

        calling_tonic = ttSparkleStack().source_tonic

        # check on valid tonic finish
        if calling_tonic in [self.base, self]:
            if hasattr(self, 'service_bases') and calling_tonic in self.service_bases:
                self.service_bases.remove(calling_tonic)

            if self.base:
                self.base._ttss__on_infusion_completed(self)

            # start finishing the tonic
            self.finishing = True
            self._execute_sparkle = self.__exec_system_sparkle # patch the _execute_sparkle function to finish mode
            if self.state != -1: self.to_state(-1)  # stop state machine if active
            self.ttse__on_finished()  # stop tonic (user level)
            self._ttss__on_finished()  # cleanup tonic (system level)


        # check if service finish
        elif hasattr(self, 'service_bases') and calling_tonic in self.service_bases:
            self.service_bases.remove(calling_tonic)
            # notify
            try: getattr(self, 'ttse__on_service_base_removed')(calling_tonic.id, len(self.service_bases))
            except AttributeError: pass
            try: getattr(calling_tonic, f'ttse__on_{self.name}_completed')()
            except AttributeError: pass
            try: getattr(calling_tonic, '_ttss__on_infusion_completed')(self.id)
            except AttributeError: pass

            if len(self.service_bases) <= 0: self.finish()

    def _ttss__on_finished(self):
        """System-level sparkle for final cleanup."""
        #notify and remove service bases left
        try:
            for sb in self.service_bases:
                try: getattr(sb, f'ttse__on_{self.name}_completed')()
                except AttributeError: pass
                try: getattr(sb, '_ttss__on_infusion_completed')(self.id)
                except AttributeError: pass
            self.service_bases.clear()
        except AttributeError: pass

        # finish all infusions
        sp_stck = ttSparkleStack()
        sp_stck.push(self, 'finish')
        for tonic in self.infusions.copy():
            tonic.ttsc__finish()
        sp_stck.pop()
        self.infusions=[]

        # # complete
        # self.catalyst._ttss__remove_tonic_from_catalyst(self.id)
        # self.ledger.unregister(self.id)
        # self.id = -1  # finished

        # finish the Tonic
        # if not self.infusions:
        #     self._ttss__on_completion()
        # else:
        #     sp_stck = ttSparkleStack()
        #     sp_stck.push(self, 'finish')
        #     for tonic in self.infusions.copy():
        #         tonic.ttsc__finish()
        #     sp_stck.pop()

        self._ttss__on_completion()

    def _ttss__on_infusion_completed(self, tonic):
        if tonic in self.infusions:
            self.infusions.remove(tonic)
            # if self.finishing and not self.infusions:
            #     self._ttss__on_completion()

    def _ttss__on_completion(self):
        self.catalyst._ttss__remove_tonic_from_catalyst(self.id)
        self.ledger.unregister(self.id)
        self.id = -1  # finished


```

## `File: build\lib\TaskTonic\ttCatalyst.py`
```python
from .ttSparkleStack import ttSparkleStack
from .ttTonic import ttTonic
import queue, threading, time


class ttCatalyst(ttTonic):
    """
    The central executor in the TaskTonic framework, it makes the tonic sparkle. The catalyst itself behaves as
    and can be used as a tonic.

    Only the main catalyst (id==0) is executed from main (from the formula class). It is possible to let all the
    tonic sparkle by one catalyst. However, if a catalyst is created in the tonic chaine, it is launched in its
    own thread.

    A Catalyst is a special type of Tonic that manages the main execution queue
    (the 'catalyst_queue') and controls the lifecycle of other Tonics. It pulls
    'sparkles' from the queue and executes them for the correct tonics
    """

    def __init__(self, name=None, log_mode=None, dont_start_yet=False):
        """
        Initializes the Catalyst and its master queue.

        :param name: An optional name for this Catalyst.
        :param fixed_id: An optional fixed ID for this Catalyst.
        """
        # Initialize the base ttTonic functionality. The Catalyst is also a Tonic.
        super().__init__(name=name, log_mode=log_mode)
        # The master queue that all Tonics managed by this Catalyst will use.
        self.catalyst_queue = self.new_catalyst_queue()
        self.extra_sparkles = []
        self.catalyst = self  # Tonics have to have a catalyst
        # internals
        self.sparkling = False
        self.tonics_sparkling = []
        self.thread_id = -1
        self.timers = []



        if self.id > 0 and not dont_start_yet: # id 0 (main catalyst) will be started in formula
            self.start_sparkling()

    def new_catalyst_queue(self):
        return queue.SimpleQueue()

    def start_sparkling(self):
        """
        Starts the main execution loop of the Catalyst.

        The main Catalyst (id=0) runs its loop in the main thread, blocking
        execution. Other Catalysts will start their loop in a separate thread.
        """
        if self.sparkling: return

        if self.id == 0:
            # If this is the main Catalyst, run its loop in the current thread.
            self.sparkle()
        else:
            # For other Catalysts, spawn a new background thread for the loop or wait when application is starting up
            if self.ledger.formula.get('tasktonic/project/status', 'starting') == 'starting':
                return  # dont startup jet, will be done just before main_catalyst starts sparkling
            threading.Thread(target=self.sparkle).start()

    def sparkle(self):
        """
        The main execution loop of the Catalyst.

        This method continuously pulls work orders (instance, sparkle, args, kwargs)
        from the queue and executes them. It runs until the `self.sparkling` flag
        is set to False.
        """
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True

        # The loop continues as long as the Catalyst is in a sparkling state.
        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0
            while next_timer_expire == 0.0:
                next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60
            try:
                instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get(timeout=next_timer_expire)
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                while self.extra_sparkles:
                    instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                    sp_stck.push(instance, sparkle.__name__)
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                    sp_stck.pop()
            except queue.Empty: pass

    def _execute_extra_sparkle(self, instance, sparkle, *args, **kwargs):
        if hasattr(sparkle, '__func__'): sparkle = sparkle.__func__ # make an unbound method (without self)
        self.extra_sparkles.append((instance, sparkle, args, kwargs))

    def _ttss__add_tonic_to_catalyst(self, tonic_id):
        """
        A system-level sparkle called by a Tonic during its initialization
        to register itself with the Catalyst.

        :param tonic_id: The Tonic id that is starting up.
        """
        if tonic_id not in self.tonics_sparkling:
            self.tonics_sparkling.append(tonic_id)

    def _ttss__remove_tonic_from_catalyst(self, tonic_id):
        """
        A system-level sparkle called by a Tonic when it has completed its
        lifecycle and is shutting down.

        If this is the last active Tonic, the Catalyst will initiate its own
        shutdown sequence.

        :param tonic_id: The Tonic instance that has finished.
        """
        if tonic_id in self.tonics_sparkling:
            self.tonics_sparkling.remove(tonic_id)
        self.log(f"Tonic {tonic_id} has been removed from Catalyst. (left {self.tonics_sparkling})")

        # If there are no more active tonics, or active tonics used by catalyst, the catalyst's job is done.
        infusion_ids = {i.id for i in self.infusions}
        if set(self.tonics_sparkling).issubset(infusion_ids):
            self.finish()

    def _ttss__main_catalyst_finished(self):
        # Default: Stop when main catalyst is finished. You can override this method for other behavior
        self.log('Finish catalyst')
        self.finish()

    def _ttss__on_completion(self):
        super()._ttss__on_completion()
        # Setting this flag to False will terminate the sparkle loop.
        self.sparkling = False

```

## `File: build\lib\TaskTonic\ttFormula.py`
```python
from .ttSparkleStack import ttSparkleStack
from .ttLedger import ttLedger
from .ttCatalyst import ttCatalyst

import time

class ttFormula():
    def __init__(self):

        # 1/ INIT, init parameters ----------------------------------------------------------------------------------
        self.ledger = ttLedger()
        sp_stck = ttSparkleStack()

        from .ttLoggers.ttScreenLogger import ttLogService, ttScreenLogService
        from .ttLogger import ttLog
        self.ledger.update_formula((
            # project parameters
            ('tasktonic/project/name', 'tasktonic app'),
            ('tasktonic/project/started@', time.time()),
            ('tasktonic/project/status', 'starting'),

            # default logger is screen, quiet logging
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),

            # set log services
            ('tasktonic/log/service#', 'off'),
            ('tasktonic/log/service./service', ttLogService), # base class, without logging
            ('tasktonic/log/service#', 'screen'),
            ('tasktonic/log/service./service', ttScreenLogService),
            ('tasktonic/log/service./arguments', {}),
        ))

        # 2/ FORMULA, load the user formula -------------------------------------------------------------------------
        app_formula = self.creating_formula()
        if app_formula:
            self.ledger.update_formula(app_formula)

        # make id reservation for main catalyst
        self.ledger.make_reservation(service_name='tt_main_catalyst')

        # 3/ TONIC LOGGER, start the system log function if set -----------------------------------------------------
        log_formula = self.ledger.formula.at('tasktonic/log')
        self._logger = None
        self._log_mode = None
        self._log = None
        log_to = log_formula.get('to', 'off')

        if log_to != 'off':
            from .ttLogger import ttLogService, ttLog
            log_service = None
            services = log_formula.children(prefix='service')
            for service in services:
                if service.v == log_to:
                    s_kwargs = service.get('arguments', {})
                    log_service = service.get('service')(*(), **s_kwargs)  ## startup logger service
                    break
            if log_service is None:
                raise RuntimeError(f'Log to service "{log_to}" not supported.')

        # 4/ CATALYST, start the main catalyst ----------------------------------------------------------------------
        self.creating_main_catalyst()

        main_catalyst = self.ledger.get_tonic_by_name('tt_main_catalyst')
        if not isinstance(main_catalyst, ttCatalyst):
            raise RuntimeError(f'Main catalyst {main_catalyst} in formula is not a ttCatalyst instance')

        # 5/ TONICS, startup the system by creating the starting tonics ---------------------------------------------
        sp_stck.push(self.ledger.get_tonic_by_name('tt_main_catalyst'), '__formula__')
        self.creating_starting_tonics()
        sp_stck.pop()

        # 6/ STARTUP, start created catalysts and them start main catalyst ------------------------------------------
        if not self.ledger.formula.get('tasktonic/testing/dont_start_catalysts', False):

            self.ledger.update_formula('tasktonic/project/status', 'start_catalysts')
            for essence in self.ledger.tonics[1:].copy(): # must be copied, because threads get started and ledger can be changed
                if isinstance(essence, ttCatalyst):
                    essence.start_sparkling()

            self.ledger.update_formula('tasktonic/project/status', 'main_running')
            main_catalyst.start_sparkling()
            self.ledger.update_formula('tasktonic/project/status', 'main_finished')

            # notify unfinished catalysts in ledger records
            for essence in self.ledger.tonics[1:].copy():
                if hasattr(essence, '_ttss__main_catalyst_finished'):
                    essence._ttss__main_catalyst_finished()



    def creating_formula(self):
        return None

    def creating_main_catalyst(self):
        ttCatalyst(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        pass


```

## `File: build\lib\TaskTonic\ttLiquid.py`
```python
import time
from .ttSparkleStack import ttSparkleStack


class __ttLiquidMeta(type):
    """
    Metaclass for the ttTonic (via TTLiquid)

    This metaclass intercepts the creation of all ttEssence subclasses
    to provide two key functionalities:

    1.  Post-Initialization Hook: It calls an `_init_post_action` method
        on the instance *after* its `__init__` has successfully completed.
    2.  Service (Singleton) Management: It checks for a `service` kwarg
        or a `_tt_is_service` class attribute. If found, it ensures
        that only one instance of that service (identified by its name)
        is ever created. It guarantees that `__init__` and `_init_post_action`
        run only once for the service, but calls `_init_service` on *every* access.
        *BE AWARE*: when creating a new instance of the service in the context of another service,
        the service wil be finished (for everyone) when that context is deleted. It's better to create
        a new instance of the service from your formula.
    """

    def __new__(mcs, name, bases, attrs):
        """
        Intercept class creation to inject the bootstrap logic BEFORE the user's __init__.
        """
        original_init = getattr(super().__new__(mcs, name, bases, attrs), '__init__', None)

        def wrapped_init(self, *args, **kwargs):
            self._bootstrap(*args, **kwargs)
            if original_init:
                original_init(self, *args, **kwargs)

        wrapped_init.__wrapped__ = original_init
        attrs['__init__'] = wrapped_init

        return super().__new__(mcs, name, bases, attrs)


    def __call__(cls, *args, **kwargs):
        """
        Creating the ttEssence.
        - get ledger
        - get base tonic to add to
        - check if this is a service (singleton)
        - create tonic if not service or if first instance of service
        - start
        """
        if not issubclass(cls, ttLiquid):
            raise TypeError(f'Class {cls.__name__} is not a ttLiquid')

        tonic = None

        # GET LEDGER
        from .ttLedger import ttLedger
        ledger = ttLedger()

        # GET BASE
        sp_stck = ttSparkleStack()
        base = sp_stck.get_tonic()

        # CHECK ON SERVICE ESSENCE (singleton) and GET SERVICE IF ALREADY CREATED
        service_name = getattr(cls, '_tt_is_service', None)
        is_service = service_name is not None

        if is_service:
            if len(args) >= 1:
                name = args[0]
                args = args[1:]
            else:
                name = kwargs.get('name', None)
            if name: Warning(f'Name {name} is ignored and changed to service name {service_name}')
            kwargs['name'] = service_name
            tonic = ledger.get_tonic_by_name(service_name) # get existing service or None
            if isinstance(tonic, ledger.TonicReservation): tonic = None

        # CREATE AND INIT TONIC
        if tonic is None:
            tonic = super().__call__(*args, **kwargs)
            if hasattr(tonic, '_tt_sparkle_init'): tonic._tt_sparkle_init()
            tonic._tt_post_init_action()
        else: # existing service
            if base: base._tt_add_infusion(tonic)
            sp_stck.push(tonic, '__init__')

        # HANDLE SERVICE ADMIN
        if is_service and base is not None:
            try: tonic.service_bases.append(base)
            except AttributeError: tonic.service_bases = [base]
            tonic._tt_init_service_base(base, *args, **kwargs)

        sp_stck.pop()

        return tonic

class ttLiquid(metaclass=__ttLiquidMeta):
    """A base class for all active components within the TaskTonic framework.

    Each 'Liquid' represents a distinct, addressable entity with its own
    lifecycle, context (parent), and subjects (children). It automatically
    registers itself with the central ttLedger upon creation to receive a unique ID.
    """

    def _bootstrap(self, *args, **kwargs):
        """
        Setup logic that must run once per instance.
        Safe to call from __new__ OR __init__ (if __new__ was skipped).
        necessary to solve possible metaclass mix issues
        """
        if hasattr(self, 'id'): return

        # GET LEDGER
        from .ttLedger import ttLedger
        ledger = ttLedger()
        cls = self.__class__

        # GET BASE
        sp_stck = ttSparkleStack()
        calling_essence = sp_stck.get_tonic()
        base = None if (getattr(cls, '_tt_base_essence', False) or getattr(cls, '_tt_is_service', None) is not None)\
               else calling_essence

        # CREATE TONIC and INIT ESSENTIALS
        self.ledger = ledger
        self.id = None
        given_name = kwargs.get('name', args[0] if len(args) >= 1 else None)
        if given_name: self.id = ledger.check_reservation(given_name)
        if self.id is None: self.id = ledger.make_reservation()
        self.name = given_name if given_name else  f'{self.id:02d}.{cls.__name__}'
        self.base = base
        self.infusions = []
        self.finishing = False
        ledger.register(self, reservation=self.id)
        if base: base._tt_add_infusion(self)
        elif calling_essence: calling_essence._tt_add_infusion(self)

        # handle essence init as sparkle on stack. popped in meta
        sp_stck.push(self, '__init__')


    def __init__(self, *args, name=None, log_mode=None, **kwargs):
        """
        Initializes a new ttLiquid instance. (after meta and new initialized the TaskTonic basics)

        :param name: An optional name for this essence. If not provided, a name
                     will be generated based on its ID and class name.
        :type name: str, optional
        :param log_mode: The initial logging mode for this essence.
        :type log_mode: ttLog, str, or int, optional
        :param kwargs: Catches any additional keyword arguments, allowing
                       subclasses to accept their own parameters
                       (e.g., `srv_api_key`) without breaking this
                       base class `__init__`.
        """
        if getattr(self, '_tt_liquid_init_done', False): return
        self._tt_liquid_init_done = True
        # first, enable logging
        log_formula = self.ledger.formula.at('tasktonic/log')
        self._logger = None
        self._log_mode = None
        self._log = None
        log_to = log_formula.get('to', 'off')

        # Set logger service and log_mode
        from .ttLogger import ttLogService, ttLog
        if getattr(self, '_tt_force_stealth_logging', False) or log_to == 'off':
            # Essence is forcing stealth mode or no log_to set, so also no logservice needed
            self.set_log_mode(ttLog.STEALTH)
        else:
            if log_mode is None:
                log_mode = \
                    self.base._log_mode if (self.base and self.base._log_mode) \
                    else log_formula.get('default', ttLog.STEALTH) if self.ledger.formula \
                    else ttLog.STEALTH

            if log_mode != ttLog.STEALTH:
                self._logger = ttLogService() # default log service is empty template, the running service is used

            self.set_log_mode(log_mode)

        self.log(system_flags={
            'created': True,
            'id': self.id,
            'name': self.name,
            'base': self.base.id if self.base else -1,
            'type': self.__class__.__name__,
        })

    def __str__(self):
        return f'<ID[{self.id:02d}]B[{self.base.id if self.base else -1:02d}] {self.__class__.__name__} {self.name}>'

    def __repr__(self):
        return self.__str__()

    def __deepcopy__(self, memodict={}):
        return self

    def _tt_post_init_action(self):
        """
        A post-initialization hook called by the metaclass.

        This method is guaranteed to run *after* __init__ has completed.
        It is used to init your process (ie. start statemachine) if everything
        is ready.
        """
        self.log(close_log=True)

    def _tt_init_service_base(self, *args, **kwargs):
        """
        A hook called by the metaclass *every time* a service is accessed.

        Subclasses can override this method to capture context-specific
        parameters (from kwargs) each time they are requested.

        Note: For al services the base is already automatically added to the service_bases list

        This method is intentionally a pass-through in the base class.
        """
        pass

    def _tt_add_infusion(self, essence):
        self.infusions.append(essence)

    def finish(self):
        """
        Static finish in one cycle.
         Be aware to use this only within the same thread as the base thread
         and no service cleaning up is done. Also finishing infusions is kept simple,
         no waiting and check on finishing of the infusions.
        """
        if self.finishing or self.id==-1: return
        if self.base:
            if self in self.base.infusions:
                self.base.infusions.remove(self)

            if hasattr(self.base, '_ttss__on_infusion_completed'):
                self.base._ttss__on_infusion_completed(self)
            else:
                if self in self.base.infusions:
                    self.base.infusions.remove(self)


        for liquid in self.infusions.copy():
            liquid.ttsc__finish()

        self.ledger.unregister(self.id)
        self.id = -1  # finished

    def ttsc__finish(self): self.finish() # make compatible with tonic calls

    # create logger functions for ttLog to overwrite
    def log(self, line=None, flags=None, system_flags=None, close_log=False):
        """
        Adds a text line and/or (system) flags to the current log entry.

        A log entry is created on the first call and sent/closed when
        `close_log` is true. This method is a placeholder and will be
        dynamically replaced by `set_log_mode` to point to the correct
        log handler (e.g., `_log_full`, `_log_stealth`).

        :param line: The string message to log.
        :param flags: A dictionary of flags to add to the log entry.
        :param system_flags: A dictionary of system flags to add.
        :param close_log: When true, send the log entry and clear it.
        """
        pass

    def _log_full(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the FULL log mode."""
        if self.id == -1:
            pass # todo:??
        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault(lifecycle, {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            self._log['duration'] = time.time() - self._log['start@']
            self._log_push(self._log)
            self._log = None

    def _log_quiet(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the QUIET log mode."""
        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault(lifecycle, {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            if 'log' in self._log or lifecycle in self._log:
                self._log_push(self._log)
            self._log = None

    def _log_off(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the OFF log mode (lifecycle only)."""
        if system_flags:
            if self._log is None: self._log = {'id': self.id, 'start@': time.time()}
            self._log.setdefault(lifecycle, {}).update(system_flags)
        if close_log and self._log:
            self._log_push(self._log)
            self._log = None

    def _log_stealth(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the STEALTH log mode (does nothing)."""
        pass

    def set_log_mode(self, log_mode):
        """
        Sets the logging function for this essence instance.

        This method "patches" `self.log` to point directly to the
        correct internal log handler (e.g., `_log_full`, `_log_stealth`)
        based on the selected mode for maximum performance.

        Args:
            log_mode (ttLog or str or int): The desired log mode.
        """
        from .ttLogger import ttLog
        log_implementations = [self._log_stealth, self._log_off, self._log_quiet, self._log_full]
        log_mode = ttLog.from_any(log_mode)
        self._log_mode = log_mode
        try:
            self.log = log_implementations[log_mode]
        except IndexError:
            raise NotImplementedError(f"Log mode '{log_mode.name}' is not implemented in ttLiquid.set_log_mode.")


    def _log_push(self, log):
        """
        Internal helper to push the completed log dictionary to the logger.
        Includes a safeguard against a non-existent logger.

        Args:
            log (dict): The log entry to push.
        """
        # Safeguard: Do nothing if no logger is attached
        if self._logger:
            self._logger.put_log(log)

```

## `File: build\lib\TaskTonic\ttTimer.py`
```python
import time, bisect, re

from TaskTonic.ttTonic import ttTonic
from .ttLiquid import ttLiquid
from .ttSparkleStack import ttSparkleStack


class ttTimer(ttLiquid):
    _tt_force_stealth_logging = True
    """
    Base implementatie of timers. Inherit when you're creating a timer class.
    BE AWARE: Never use to create an instance!!
    """
    TIMER_PATTERN = re.compile(r"(tm|tmr|timer)_|_(tm|tmr|timer)")

    def __init__(self, name=None, sparkle_back=None):
        from TaskTonic.ttLogger import ttLog
        super().__init__(name=name, log_mode=ttLog.QUIET)
        if self.__class__ is ttTimer:
            raise RuntimeError('ttTimer is a base class and not meant to be instantiated')
        self.expire = -1  # -1 -> timer not running

        self.catalyst = self.base.catalyst
        self.sparkle_back = sparkle_back if sparkle_back is not None else self._handle_empty_sparkle_back


    def _handle_empty_sparkle_back(self, info):
        """
        Gets called at expiration when sparkle_back is empty. Checks for the valid callback,
         call that method and set sparkle_back for the next time.
         (this can not be done in __init__ because sparkles of the base may not be initialised yet.)
        """
        if self.name.startswith(f'{self.id:02d}.'):
            # standard named, given by TaskTonic: use generic sparkle_back
            name = ''
        else:
            # user named, use specific sparkle_back
            name = self.name.strip().lower().replace(" ", "_")

        try:
            self.sparkle_back = \
                getattr(self.base, f"ttse__on_{name}",
                getattr(self.base, f"ttse__on_tmr_{name}",
                getattr(self.base, "ttse__on_timer",
                None)))
            self.sparkle_back(info)
        except AttributeError:
            raise AttributeError(f"{self.base} does not have a valid sparkle_back for timers")

    # used to sort timers in the list
    def __lt__(self, other):
        return self.expire < other.expire

    def start(self):
        """
        starts timer
        """
        if self.id == -1: raise RuntimeError(f'Cannot start a finished timer')
        if self.period <= 0:
            self.expire = -1
            return self
        if self.expire == -1:
            self.expire = time.time() + self.period
            bisect.insort(self.catalyst.timers, self)
        else:
            raise RuntimeError(f"Can't start a running timer ({self})")
        return self

    def restart(self):
        """
        Restarts timer
         Can be used for timeout on events. Restart timer at every event, and get notified on set timeout
        """
        if self.id == -1: raise RuntimeError(f'Cannot restart a finished timer')
        self.stop()
        self.start()
        return self

    def stop(self):
        """
        stops timer
        """
        self.expire = -1
        if self in self.catalyst.timers:
            self.catalyst.timers.remove(self)
        return self

    def check_on_expiration(self, reference):
        if reference >= self.expire:
            sp_stck = ttSparkleStack()
            info = {'id': self.id, 'name': self.name}
            sp_stck.push(self, 'expired')
            self.sparkle_back(info)
            sp_stck.pop()
            self.reload_on_expire(reference)
            return 0.0  # ==0, expired
        else:
            return self.expire - reference  # >0, not expired, seconds before expiring returned

    def reload_on_expire(self, reference, info):
        raise Exception('Timer callback_and_reload() must be overridden with proper implementation')

    def _on_completion(self):
        self.stop()
        super()._on_completion()

class _ttPeriodicTimer(ttTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, sparkle_back=None):
        super().__init__(name=name, sparkle_back=sparkle_back)
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        self.start()

    def change_timer(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0):
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        return self

class ttTimerSingleShot(_ttPeriodicTimer):
    def reload_on_expire(self, reference):
        self.catalyst.timers.remove(self)
        self.finish()

class ttTimerRepeat(_ttPeriodicTimer):
    def reload_on_expire(self, reference):
        self.catalyst.timers.remove(self)
        self.expire += self.period
        bisect.insort(self.catalyst.timers, self)

class ttTimerPausing(_ttPeriodicTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, sparkle_back=None, start_paused=False):
        self.paused_at = -1
        super().__init__(seconds=seconds, minutes=minutes, hours=hours, days=days, name=name, sparkle_back=sparkle_back)
        if start_paused: self.pause()

    def reload_on_expire(self, reference):
        self.catalyst.timers.remove(self)
        self.paused_at = self.expire
        self.expire = -1

    def pause(self):
        if self.paused_at != -1: return self
        self.paused_at = time.time()
        if self.expire == -1: return self
        self.catalyst.timers.remove(self)
        return self

    def resume(self):
        if self.paused_at == -1 or self.period == 0: return self
        if self.expire == -1:
            self.expire = time.time() + self.period
        else:
            self.expire += time.time() - self.paused_at
        self.pause_at = -1
        bisect.insort(self.catalyst.timers, self)
        return self


```

## `File: build\lib\TaskTonic\ttLogger.py`
```python
from .ttCatalyst import ttCatalyst
from .ttLiquid import ttLiquid
import enum

# empty log class, base for all loggers in ttLoggers map
# A logservice allways gets te service name log_service

class ttLogOff(ttLiquid):
    _tt_is_service = 'tt_log_service'
    _tt_force_stealth_logging = True

    def put_log(self, log):
        pass

class ttLogService(ttCatalyst):
    _tt_is_service = 'tt_log_service'
    _tt_base_essence = True
    _tt_force_stealth_logging = True

    def __init__(self, name=None, log_mode=None, dont_start_yet=False):
        super().__init__(name, ttLog.OFF, dont_start_yet)


    def _ttss__main_catalyst_finished(self):
        if set(self.service_bases).issubset(self.infusions):
            self.finish()

    def ttse__on_service_base_completed(self, tonic, srv_left):
        if srv_left == 0:
            self.finish()
        pass

    def put_log(self, log):
        pass

class ttLog(enum.IntEnum):
    """
    Defines the available logging verbosity levels for an essence.
    """

    def _generate_next_value_(name, start, count, last_values):
        return count  # first enum gets int val 0

    STEALTH = enum.auto()  # No logging at all
    OFF = enum.auto()  # Logs lifecycle, creating and finishing of Essence
    QUIET = enum.auto()  # + Logs sparkles, only if log line is given
    FULL = enum.auto()  # + Logs sparkles, always

    @classmethod
    def from_any(cls, value):
        """
        Converts a string, int, or existing ttLog instance
        into a ttLog member.

        Args:
            value (any): The input to convert (e.g., "QUIET", 2).

        Returns:
            ttLog: The corresponding enum member.

        Raises:
            ValueError: If the string or int does not match a valid member.
            TypeError: If the input type is not convertible.
        """
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                raise ValueError(f"'{value}' is not a valid name for {cls.__name__}")

        if isinstance(value, int):
            try:
                return cls(value)
            except ValueError:
                raise ValueError(f"'{value}' is not a valid value for {cls.__name__}")

        raise TypeError(f"Cannot convert type '{type(value).__name__}' to {cls.__name__}")

```

## `File: build\lib\TaskTonic\ttSparkleStack.py`
```python
import contextvars
"""
The Sparkle stack is used and maintained bij the TaskTonic Framework.
- The stack keeps track of the active sparkles and the calling sparkles.
- The stack is located in the tread local space, so at every moment the stack is accessed you read the
   values of the active stack and therefore the active catalyst

Stack maintenance by TaskTonic:
- With every catalyst that is started the initial context is set at None, '' (no tasktonic context, no sparkle).
   The instance of the catalyst is copied and the calling sparkle is set to None
- Every time a sparkle is called (and putted in the sparkling queue) the active sparkle is also stored in that queue
   as the source sparkle.
- At execution of a sparkle the active sparkle is pushed on stack as a set of instance, sparkle name. Also de source
   sparkle is set. When executing a sparkle you can refer to that source, ie for returning data.
- Every time a ttEssence, or subclass, is initiated the new instance is pushed with sparkle __init__. This is done in 
   the init of ttEssense so only after you call super().__init__() in your subclass. Popping the stack is done by
   TaskTonic after the whole init sequence is completed.
- Every time the ttFormula is executed, before starting tonics are created, the context main_catalyst, "__formula__"
   is pushed.
- Be aware that the calling sparkle is always the executing sparkle even when nested inits are putted on stack


Note on using:    
 Don't create a parameter self.sparkle_stack in your class! At creating the data of the current thread is locked for 
 that parameter. If a method is called from an other thread self.sparkle_stack refers to the first thread!!
 Always use in your method:
    sp_stck = ttSparkleStack()
    sp_stck.push.....
    sp_stck.get_essence...
    etc
    
    or 
    ttSparkleStack().get_essence... # for single use
    
"""

_sparkle_context: contextvars.ContextVar = contextvars.ContextVar("sparkle_context")
class ttSparkleStack:
    """
    Represents the execution context stack for a single thread.

    It tracks the hierarchy of 'Essences' and 'Sparkles' (methods/actions)
    currently being executed, allowing introspection of the caller.
    """
    def __new__(cls):
        try:
            # 1. get thread instance
            instance = _sparkle_context.get()
            return instance
        except LookupError:
            # 2. init if not existing
            instance = super().__new__(cls)
            instance.catalyst = None
            instance.stack = [(None, "")]
            instance.source = (None, "")
            _sparkle_context.set(instance)
            return instance

    def push(self, essence, sparkle):
        """
        Pushes a new execution frame onto the stack.

        Args:
            essence: The object instance context.
            sparkle (str): The name of the action/method being invoked.
        """
        self.stack.append((essence, sparkle))

    def pop(self):
        """Removes the top execution frame from the stack."""
        self.stack.pop()

    def get_stack(self, pos=-1):
        return self.stack[pos]

    def get_tonic(self, pos=-1):
        return self.stack[pos][0]

    def get_tonic_name(self, pos=-1):
        essence = self.stack[pos][0]
        return essence.name if essence else ""

    def get_sparkle_name(self, pos=-1):
        return self.stack[pos][1]

    @property
    def source_tonic(self):
        return self.source[0]

    @property
    def source_tonic_name(self):
        return "" if self.source[0] is None else self.source[0].name

    @property
    def source_sparkle_name(self):
        return self.source[1]

```

## `File: build\lib\TaskTonic\__main__.py`
```python
import os

START_CODE = """\
from TaskTonic import *

\"\"\"
Welcome to TaskTonic!

This is Hello World, the TaskTonic way.
Look at it, try it, and read the docs
\"\"\"

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
"""


def generate_starter_file():
    filename = "hello_tasktonic.py"

    print("🍹 Welkom bij TaskTonic!")

    if os.path.exists(filename):
        print(f"⚠️ Je hebt al een '{filename}' in deze map staan.")
        return

    # Maak het bestand aan voor de gebruiker
    with open(filename, "w", encoding="utf-8") as f:
        f.write(START_CODE)

    print(f"✅ We hebben een startbestand voor je klaargezet: {filename}")
    print(f"🚀 Open het bestand in je editor, of test het direct met:")
    print(f"   python {filename}")


if __name__ == "__main__":
    generate_starter_file()
```

## `File: build\lib\TaskTonic\internals\__init__.py`
```python
from .RWLock import RWLock
# from .DataShare import DataShare
from .Store import Store, Item

```

## `File: build\lib\TaskTonic\internals\RWLock.py`
```python
"""
Tool lib for private classes
"""
import threading


class RWLock:
    """
    Read/Write lock for accessing admin data with version indicator.
    You can read data, until a (or more) writing requests. Then writing is allowed just after all read operations are
    finished. After the last write operation completes, the lock is released and reading is allowed again.
    Every write will increase self.version checking on version will tell you if your data is old. Version wraps to
    zero after 2^31−1 = 2.147.483.647 operations, so use if version != stored_version!!
    """

    # noinspection PyProtectedMember
    class ReadAccessContext:
        def __init__(self, rw_lock_instance):
            self._rw_lock = rw_lock_instance

        def __enter__(self):
            self._rw_lock._acquire_read()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._rw_lock._release_read()
            return False

    # noinspection PyProtectedMember
    class WriteAccessContext:
        def __init__(self, rw_lock_instance):
            self._rw_lock = rw_lock_instance

        def __enter__(self):
            self._rw_lock._acquire_write()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._rw_lock._release_write()
            return False

    def __init__(self):
        self.version = 0
        self._readers_active = 0
        self._writers_waiting = 0
        self._writing = False
        self._lock = threading.Lock()
        self._can_read = threading.Condition(self._lock)
        self._can_write = threading.Condition(self._lock)

    def read_access(self):
        return self.ReadAccessContext(self)

    def write_access(self):
        return self.WriteAccessContext(self)

    def _acquire_read(self):
        with self._lock:
            while self._writing or self._writers_waiting:
                self._can_read.wait()
            self._readers_active += 1

    def _release_read(self):
        with self._lock:
            self._readers_active -= 1
            if not self._readers_active and self._writers_waiting:
                self._can_write.notify_all()

    def _acquire_write(self):
        with self._lock:
            self._writers_waiting += 1
            while self._readers_active > 0 or self._writing:
                self._can_write.wait()
            self._writers_waiting -= 1
            self._writing = True
            self.version = (self.version + 1) & 0b0111_1111_1111_1111_1111_1111_1111_1111

    def _release_write(self):
        with self._lock:
            self._writing = False
            if self._writers_waiting:
                self._can_write.notify_all()
            else:
                self._can_read.notify_all()

```

## `File: build\lib\TaskTonic\internals\Store.py`
```python
import threading
import re
import contextlib
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple, Callable, Iterable

# ------------------------------------------------------------------------------
# Type definitions
# ------------------------------------------------------------------------------
PathStr = str
# ChangeEvent: (path, new_value, old_value, source_id)
ChangeEvent = Tuple[str, Any, Any, Optional[str]]
ListenerCallback = Callable[[List[ChangeEvent]], None]
DumpData = Iterable[Tuple[str, Any]]


# ------------------------------------------------------------------------------
# Class: Item (The Cursor/View)
# ------------------------------------------------------------------------------
class Item:
    """
    Represents a specific cursor/view on a path in the Store.
    Acts like a pointer to a specific location in the data tree.
    """
    __slots__ = ('_store', '_path')

    def __init__(self, store: 'Store', path: PathStr):
        self._store = store
        self._path = path.strip("/")

    @property
    def path(self) -> str:
        """Returns the absolute path of this item."""
        return self._path

    @property
    def v(self) -> Any:
        """
        Property for direct value access.
        Writing to .v ALWAYS sends a notification (notify=True), unless inside a silent group.
        """
        return self._store.get_value(self._path)

    @v.setter
    def v(self, value: Any):
        self._store.set_value(self._path, value, notify=True)

    # --- NAVIGATION HELPERS ---

    @property
    def parent(self) -> 'Item':
        """
        Returns an Item cursor pointing to the direct parent container.
        Example: "users/#0/name" -> "users/#0"
        """
        if "/" not in self._path:
            # Already at root or top-level, return root
            return self._store.at("")

        parent_path, _ = self._path.rsplit("/", 1)
        return self._store.at(parent_path)

    @property
    def list_root(self) -> Optional['Item']:
        """
        Walks up the path tree to find the nearest List Item ancestor.
        Identifies ancestors by the '#' syntax (e.g., '#0', 'user#1').

        Use this when a deep property changes (e.g. 'users/#0/address/street')
        and you need the context of the user record ('users/#0').

        Returns None if no list index is found in the path.
        """
        parts = self._path.split("/")

        # Iterate backwards to find the deepest list index
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            # Check syntax: contains '#' and ends with digit (e.g. "#0" or "name#1")
            if "#" in part and part[-1].isdigit():
                root_path = "/".join(parts[:i + 1])
                return self._store.at(root_path)

        return None

    # --- VALUE ACCESS ---

    def val(self, default: Any = None) -> Any:
        """
        Retrieves the value of THIS item (self).
        Returns 'default' if the value is None or item doesn't exist.
        """
        value = self.v
        return value if value is not None else default

    def get(self, key: str, default: Any = None) -> Any:
        """
        Dictionary-style lookup for CHILDREN.
        Retrieves the value of a child item relative to this item.

        Args:
            key: Relative path/key to the child.
            default: Value to return if child doesn't exist.
        """
        target_path = f"{self._path}/{key}" if self._path else key
        val = self._store.get_value(target_path)
        return val if val is not None else default

    # --- SET LOGIC ---

    def set(self, data: Union[DumpData, str, dict, tuple], value: Any = None, notify: bool = True) -> 'Item':
        """
        Versatile setter method.

        Args:
            data:
                - str: Relative path/key to set 'value' to.
                - dict: Batch update {key: val}.
                - list/tuple: Batch update [(key, val)] OR Value if not pairs.
            value: The value to set (only used if data is a string).
            notify: If False, this update will NOT trigger callbacks (Silent Mode).
        """

        # 1. Dictionary Batch
        if isinstance(data, dict):
            with self._store.group(notify=notify):
                for k, v in data.items():
                    self.set(str(k), v, notify=notify)
            return self

        # 2. List or Tuple Batch (STRUCTURAL UPDATE)
        # We only treat it as a batch if it contains pairs.
        if isinstance(data, (list, tuple)):
            # Check if it looks like a batch of pairs
            is_batch = len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) == 2

            if is_batch:
                with self._store.group(notify=notify):
                    for entry in data:
                        k, v = entry
                        self.set(k, v, notify=notify)
                return self

            # If not a batch of pairs, it falls through to be treated as a VALUE (list assignment)

        # 3. Single Key (String) -> WRITE VALUE
        if isinstance(data, str):
            path_str = data

            # Check for Dynamic Syntax (# or .) which needs parsing
            if "#" in path_str or "." in path_str:
                self._smart_set_path(path_str, value, notify)
            else:
                # Static Path -> Fast Write
                if path_str == "" or path_str == ".":
                    self._store.set_value(self._path, value, notify=notify)
                else:
                    target_path = f"{self._path}/{path_str}" if self._path else path_str
                    self._store.set_value(target_path.strip("/"), value, notify=notify)
            return self

        raise ValueError(f"Invalid arguments for set(). Got type: {type(data)}")

    def _smart_set_path(self, relative_path: str, value: Any, notify: bool):
        """Parses path strings with special characters (#, .)."""
        parts = relative_path.split("/")
        cursor = self

        for i, part in enumerate(parts):
            is_last_part = (i == len(parts) - 1)

            if part == "":
                continue
            elif part == "#":
                cursor = cursor.append(None)
            elif part == ".":
                cursor = self._get_last_list_item(cursor, prefix=None)
            elif part.endswith("#"):
                cursor = cursor.append(part[:-1])
            elif part.endswith("."):
                prefix = part[:-1]
                children_keys = cursor._store.get_children_keys(cursor.path)
                if prefix in children_keys:
                    cursor = cursor.at(prefix)
                    cursor = self._get_last_list_item(cursor, prefix=None)
                else:
                    cursor = self._get_last_list_item(cursor, prefix=prefix)
            else:
                cursor = cursor.at(part)

            if is_last_part:
                cursor._store.set_value(cursor.path, value, notify=notify)
                return

    def _get_last_list_item(self, cursor: 'Item', prefix: str = None) -> 'Item':
        children = cursor._store.get_children_keys(cursor.path)
        if prefix:
            pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
        else:
            pattern = re.compile(r"^#(\d+)$")

        max_idx = -1
        last_key = None
        for key in children:
            match = pattern.match(key)
            if match:
                idx = int(match.group(1))
                if idx > max_idx:
                    max_idx = idx
                    last_key = key
        return cursor.at(last_key) if last_key else cursor

    # --- MANIPULATION ---

    def remove(self, subpath: str = None) -> None:
        """
        Remove Item from store
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        self._store.remove_item(target)

    def pop(self, subpath: str = None) -> Any:
        """
        Remove Item from store and return its value after that
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        val = self._store.get_value(target)
        self._store.remove_item(target)
        return val

    def append(self, prefix: str = None) -> 'Item':
        """
        Creates a new list child item with an auto-incrementing index (e.g. #0, #1).
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item
        """
        return self._store.create_list_item(self._path, prefix)

    def extend(self, data_list: List[Any], prefix: str = None) -> 'Item':
        """
        Appends multiple items to the list.
        :param data_list: ???
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item with created list
        """

        if not isinstance(data_list, list):
            raise ValueError("extend() expects a list")
        for data in data_list:
            new_item = self.append(prefix)
            # If data looks like a batch tuple structure, set it as structure
            if isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)) and len(
                    data[0]) == 2:
                new_item.set(data)
            else:
                new_item.v = data
        return self

    # --- QUERY ---

    def children(self, prefix: str = None) -> Iterator['Item']:
        """Iterates over children keys."""
        for key in self._store.get_children_keys(self._path):
            if prefix is not None:
                target_start = f"{prefix}#"
                if not key.startswith(target_start):
                    continue
            yield self.at(key)

    def dump(self) -> DumpData:
        return self._store.get_subtree(self._path)

    def dumps(self) -> str:
        data = self.dump()
        lines = [f"Dump of <{self._path or 'ROOT'}>:"]
        if not data:
            lines.append("  (empty)")
        else:
            for key, val in data:
                display_key = key if key else "."
                lines.append(f"  {display_key} = {val}")
        return "\n".join(lines)

    # --- MAGIC ---

    def at(self, subpath: str) -> 'Item':
        """
        Returns Item at subpath. From there you can acces the item directly
        :param subpath: subpath of item
        :return:
        """
        full_path = f"{self._path}/{subpath}" if self._path else subpath
        return self._store.at(full_path)

    def __getitem__(self, key: str) -> 'Item':
        return self.at(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.remove(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._store.get_children_keys(self._path))

    def __repr__(self):
        val = self.v
        return f"<Item '{self._path}': {val}>" if val is not None else f"<Item '{self._path}'>"


# ------------------------------------------------------------------------------
# Class: Store (Base Functionality)
# ------------------------------------------------------------------------------
class Store:
    """
    Thread-safe, hierarchical data store (Functional Core).
    Supports:
    - Pub/Sub with Ancestor Lookup (O(depth) instead of O(subscribers)).
    - Grouped updates (Batching).
    - Silent updates (notify=False) per set or per group.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._storage: Dict[str, Dict[str, Any]] = {}
        # Pre-allocate root
        self._storage[""] = {"val": None, "children": set()}
        self._subscribers: Dict[str, List[Dict]] = {}
        # Thread Local Storage for batching contexts
        self._local = threading.local()

    # --- Context Managers ---

    @contextlib.contextmanager
    def group(self, source_id: str = None, notify: bool = True):
        """
        Context manager to group multiple changes.
        Args:
            source_id: Optional source tag.
            notify: If False, ALL changes inside are silent (overrides set()).
        """
        # 1. Init Locals
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
        if not hasattr(self._local, "current_source"):
            self._local.current_source = None
        if not hasattr(self._local, "group_notify"):
            self._local.group_notify = True

            # 2. Save previous states
        prev_src = self._local.current_source
        prev_notify = self._local.group_notify

        # 3. Apply new context
        if source_id is not None:
            self._local.current_source = source_id

        # Combine parent silence with current request
        self._local.group_notify = prev_notify and notify

        self._local.batch_stack += 1

        try:
            yield
        finally:
            self._local.batch_stack -= 1

            # 4. Flush only if notifying and root/end of batch
            if self._local.batch_stack == 0 and self._local.group_notify:
                self._flush_notifications()

            # 5. Restore
            if source_id is not None:
                self._local.current_source = prev_src
            self._local.group_notify = prev_notify

    @contextlib.contextmanager
    def source(self, source_id: str):
        with self.group(source_id=source_id):
            yield

    # --- Core Access ---

    def at(self, path: str) -> Item:
        return Item(self, path)

    def set(self, path_or_data: Union[str, DumpData, dict], value: Any = None, notify: bool = True) -> Item:
        return self.at("").set(path_or_data, value, notify=notify)

    def get(self, path: str, default: Any = None) -> Any:
        """Shortcut to retrieve value by absolute path."""
        val = self.get_value(path)
        return val if val is not None else default

    def __getitem__(self, path: str) -> Item:
        return self.at(path)

    def __setitem__(self, path: str, value: Any):
        self.at("").set(path, value)

    def __delitem__(self, path: str):
        self.remove_item(path)

    def subscribe(self, path: str, callback: ListenerCallback, ignore_source: str = None, recursive: bool = True,
                  exclude: List[str] = None):
        """
        Register a callback.
        recursive: If True, trigger on path and descendants.
        exclude: List of absolute sub-paths to ignore (e.g. ['sensor/current']).
        """
        clean_path = path.strip("/")
        clean_exclude = [e.strip("/") for e in exclude] if exclude else []

        with self._lock:
            if clean_path not in self._subscribers:
                self._subscribers[clean_path] = []

            self._subscribers[clean_path].append({
                "cb": callback,
                "ignore_source": ignore_source,
                "recursive": recursive,
                "exclude": clean_exclude
            })

    def dump(self) -> DumpData:
        return self.at("").dump()

    def dumps(self) -> str:
        return self.at("").dumps()

    # --- Implementation Details ---

    def _ensure_node(self, path: str):
        parts = path.split("/")
        current_path = ""
        for i, part in enumerate(parts):
            parent_path = current_path
            if i > 0:
                current_path = f"{current_path}/{part}"
            else:
                current_path = part

            if current_path not in self._storage:
                self._storage[current_path] = {"val": None, "children": set()}
                parent_entry = self._storage.get(parent_path)
                if parent_entry: parent_entry["children"].add(part)

    def set_value(self, path: str, value: Any, notify: bool = True):
        # Optimized Fast Path
        with self._lock:
            if path in self._storage:
                entry = self._storage[path]
                old_value = entry["val"]
                entry["val"] = value
            else:
                self._ensure_node(path)
                entry = self._storage[path]
                old_value = entry["val"]
                entry["val"] = value

        if notify and old_value != value:
            self._queue_notification(path, value, old_value)

    def get_value(self, path: str) -> Any:
        with self._lock:
            if path in self._storage:
                return self._storage[path]["val"]
            return None

    def remove_item(self, path: str):
        clean_path = path.strip("/")
        if clean_path == "":
            with self._lock: self._storage[""]["val"] = None
            return

        with self._lock:
            if clean_path not in self._storage: return
            self._queue_notification(clean_path, None, self._storage[clean_path]["val"])
            self._recursive_delete(clean_path)

            if "/" in clean_path:
                parent_path, child_key = clean_path.rsplit("/", 1)
            else:
                parent_path, child_key = "", clean_path

            if parent_path in self._storage:
                self._storage[parent_path]["children"].discard(child_key)

    def _recursive_delete(self, path: str):
        if path not in self._storage: return
        children = list(self._storage[path]["children"])
        for child_key in children:
            child_path = f"{path}/{child_key}"
            if child_path in self._storage:
                self._queue_notification(child_path, None, self._storage[child_path]["val"])
            self._recursive_delete(child_path)

        if path in self._subscribers: del self._subscribers[path]
        del self._storage[path]

    def create_list_item(self, base_path: str, prefix: str = None) -> Item:
        clean_path = base_path.strip("/")
        with self._lock:
            if clean_path not in self._storage:
                self._ensure_node(clean_path)

            children = self._storage[clean_path]["children"]
            max_idx = -1

            if prefix:
                pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
            else:
                pattern = re.compile(r"^#(\d+)$")

            for child in children:
                match = pattern.match(child)
                if match:
                    idx = int(match.group(1))
                    if idx > max_idx: max_idx = idx

            new_key = f"{prefix}#{max_idx + 1}" if prefix else f"#{max_idx + 1}"
            new_path = f"{clean_path}/{new_key}" if clean_path else new_key

            self.set_value(new_path, None)
            return self.at(new_path)

    def get_children_keys(self, path: str) -> List[str]:
        clean_path = path.strip("/")
        with self._lock:
            if clean_path in self._storage:
                return sorted(list(self._storage[clean_path]["children"]))
            return []

    def get_subtree(self, base_path: str) -> DumpData:
        clean_base = base_path.strip("/")
        result = []
        with self._lock:
            for path in sorted(self._storage.keys()):
                if clean_base and len(path) < len(clean_base): continue
                if path not in self._storage: continue
                val = self._storage[path]["val"]
                if val is not None:
                    if clean_base == "":
                        is_self = (path == "")
                        is_child = (path != "")
                    else:
                        is_self = (path == clean_base)
                        is_child = path.startswith(clean_base + "/")
                    if is_self or is_child:
                        rel_key = "" if is_self else (path if clean_base == "" else path[len(clean_base) + 1:])
                        result.append((rel_key, val))
        return result

    def _queue_notification(self, path: str, new_val: Any, old_val: Any):
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
            self._local.group_notify = True

            # If group is silent, drop event immediately
        if hasattr(self._local, "group_notify") and not self._local.group_notify:
            return

        if not hasattr(self._local, "current_source"):
            self._local.current_source = None

        event = (path, new_val, old_val, self._local.current_source)
        self._local.pending_changes.append(event)

        if self._local.batch_stack == 0:
            self._flush_notifications()

    def _flush_notifications(self):
        # OPTIMIZED: Ancestor Lookup Strategy
        if not hasattr(self._local, "pending_changes") or not self._local.pending_changes: return
        events = self._local.pending_changes
        self._local.pending_changes = []

        # 1. Identify all relevant paths (the path itself + all ancestors)
        relevant_sub_paths = set()
        for event in events:
            path = event[0]
            relevant_sub_paths.add(path)
            while "/" in path:
                path, _ = path.rsplit("/", 1)
                relevant_sub_paths.add(path)
            if path != "":
                relevant_sub_paths.add("")  # Root always relevant

        # 2. Retrieve only subscribers on those paths (O(1) lookups)
        with self._lock:
            relevant_entries = []
            for sub_path in relevant_sub_paths:
                if sub_path in self._subscribers:
                    relevant_entries.append((sub_path, self._subscribers[sub_path]))

        # 3. Process events against this filtered subset of subscribers
        for sub_path, sub_entries in relevant_entries:
            relevant_events = []
            for event in events:
                evt_path = event[0]
                # Match logic:
                if evt_path == sub_path:
                    relevant_events.append(event)
                elif evt_path.startswith(sub_path + "/"):
                    relevant_events.append(event)

            if relevant_events:
                for entry in sub_entries:
                    # A. Recursive Filter
                    is_recursive = entry["recursive"]

                    if not is_recursive:
                        events_for_sub = [e for e in relevant_events if e[0] == sub_path]
                    else:
                        events_for_sub = relevant_events

                    # B. Exclude Filter (Subtree pruning)
                    exclusions = entry["exclude"]
                    if exclusions and events_for_sub:
                        filtered_events = []
                        for e in events_for_sub:
                            ep = e[0]
                            is_excluded = False
                            for ex in exclusions:
                                if ep == ex or ep.startswith(ex + "/"):
                                    is_excluded = True
                                    break
                            if not is_excluded:
                                filtered_events.append(e)
                        events_for_sub = filtered_events

                    # C. Source Filter
                    ignore = entry["ignore_source"]
                    filtered = [e for e in events_for_sub if ignore is None or e[3] != ignore]
                    if filtered:
                        try:
                            entry["cb"](filtered)
                        except Exception as e:
                            print(f"[Store] Callback error {sub_path}: {e}")


```

## `File: build\lib\TaskTonic\ttLoggers\__init__.py`
```python
from .ttScreenLogger import ttLogService, ttScreenLogService
```

## `File: build\lib\TaskTonic\ttLoggers\ttScreenLogger.py`
```python
from .. import ttTimerRepeat
from ..ttLogger import ttLogService
import time

class ttScreenLogService(ttLogService):

    def __init__(self, name=None):
        super().__init__(name)
        self.log_records = []
        prj = self.ledger.formula.at('tasktonic/project')
        ts = prj['started@'].v
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        print(f"[{l_time_start}] TaskTonic log for {prj['name'].v}, started at {time.strftime('%H:%M:%S', lt)}")
        print(41 * '-=')
    def _tt_init_service_base(self, base, *args, **kwargs):
        self.log(close_log=True)

    def put_log(self, log):
        self.ttsc__add_log(log)

    def ttse__on_start(self):
        pass

    def ttse__on_finished(self):
        print(41*'-=')
        print('Logging finished')
        print(self.ledger.sdump())

    def ttsc__add_log(self, log):
        """
        Formats and prints the collected log entry for an event, then resets it.
        """
        l_id = log.get('id', -1)
        if l_id < 0:
            raise RuntimeError(f'Error in log entry {log}')

        if log.get(lifecycle,{}).get('created', False):

            while len(self.log_records) <= l_id:
                self.log_records.append(None)
            self.log_records[l_id] = log.copy()

        sparkle_name = log.get('sparkle', '')
        sparkle_state_idx = log.get('state', -1)

        if sparkle_name == '_ttinternal_state_change_to':
            sparkle_name = f" TO STATE [{self.log_records[l_id][lifecycle]['states'][log[lifecycle]['new_state']]}]"

        ts = log['start@']
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        header = f"{self.log_records[l_id][lifecycle]['name']}"
        if sparkle_state_idx >= 0:
            header += f"[{self.log_records[l_id][lifecycle]['states'][sparkle_state_idx]}]"
        header += f".{sparkle_name}"

        dont_print_flags = ['id', 'start@', 'log', 'sparkle', 'state', 'sparkles', 'states', 'duration']
        flags_to_print = {k: v for k, v in log.items() if k not in dont_print_flags}

        du = log.get('duration',0.0)
        l_du = '' if du <= .15 else f'DURATION: {du:1.3f} sec !!! '

        print(f"[{l_time_start}] {l_id:02d} - {header:.<65} {l_du}{flags_to_print}")
        if l_states := log.get('states'):
            print(f"{16 * ' '}== STATES: |", end='')
            for state in l_states: print(f" {state} |", end='')
            print()
        if l_sparkles := log.get('sparkles'):
            print(f"{16 * ' '}== SPARKLES: |", end='')
            for sparkle in l_sparkles:
                if not sparkle.startswith('_ttss'): print(f" {sparkle} |", end='')
            print()

        if log.get('log'):
            for line in log['log']:
                line = str(line).replace('\n', f"\n{18*' '}")
                print(f"{16 * ' '}- {line}")

```

## `File: build\lib\TaskTonic\ttTonicStore\ttDistiller.py`
```python
from TaskTonic import ttLiquid, ttCatalyst, ttLog, ttSparkleStack
import queue, threading, time, copy


class ttDistiller(ttCatalyst):
    """
    The TaskTonic Test Harness
       The Distiller is the dedicated testing environment for the TaskTonic framework. Where the Catalyst
       is designed for high-speed, real-time production, the Distiller is its analytical counterpart,
       designed for controlled observation and debugging.
    """

    def __init__(self, name='tt_main_catalyst'):
        super().__init__(name=name, log_mode=ttLog.OFF)

    def start_sparkling(self):
        # print('Distiller is setup and ready for testing')
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self

        self.thread_id = threading.get_ident()
        sp_stck.catalyst = self

        self.sparkling = True

    def sparkle(self,
                sparkle_count=None,
                timeout=None,
                till_state_in=None,
                till_sparkle_in=None,
                contract=None):

        status={}
        sp_stck = ttSparkleStack()
        if self.sparkling:
            if contract is None: contract = {}

            def ccheck(item, default, ext=None, force_list=False):
                c = ext if ext else contract.get(item, default)
                if force_list and not isinstance(c, list): c=[c]
                contract[item] = c

            ccheck('timeout', 3600, timeout)
            ccheck('till_state_in', [], till_state_in, force_list=True)
            ccheck('till_sparkle_in', [], till_sparkle_in, force_list=True)
            ccheck('probes', [], force_list=True)

            status = {
                'status': 'running',
                'start@': time.time(),
                'sparkle_trace': [],
            }
            ending_at = time.time() + contract['timeout']

            while self.sparkling and not status.get('stop_condition', False):
                reference = time.time()
                next_timer_expire = 0.0
                while next_timer_expire == 0.0:
                    next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60
                if reference+next_timer_expire > ending_at:
                    next_timer_expire = ending_at - reference
                    if next_timer_expire < 0.0: next_timer_expire = 0.0
                try:
                    instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get(timeout=next_timer_expire)
                    sp_name = sparkle.__name__
                    self.execute_with_testlog(instance, sparkle, args, kwargs, status, contract)
                    if sparkle_count: sparkle_count -= 1
                    while self.extra_sparkles:
                        instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                        self.execute_with_testlog(instance, sparkle, args, kwargs,
                                                  status, contract)
                        if sparkle_count: sparkle_count -= 1
                except queue.Empty:
                    pass

                if time.time() >= ending_at:
                    status.setdefault('stop_condition', []).append('timeout')
                if (sparkle_count is not None and sparkle_count <= 0):
                    status.setdefault('stop_condition', []).append('sparkle_count')

        if not self.sparkling:
            status.update({'status': 'catalyst finished'})
            status.setdefault('stop_condition', []).append('catalyst finished')
        status.update({'end@': time.time()})

        return status

    def execute_with_testlog(self, instance, sparkle, args, kwargs, status, contract):
        def _freeze_value(value):
            """
            Maakt een statische snapshot van een variabele.
            Zorgt ervoor dat dynamische objecten (zoals ttLiquid) worden omgezet
            naar hun huidige string-representatie.
            """
            # 1. Specifieke types die we direct als string willen vastleggen
            # Check op type naam is veiliger tegen circulaire imports dan isinstance
            type_name = type(value).__name__
            if type_name == 'ttLiquid':
                return str(value)

            # 2. Dictionaries recursief doorlopen
            if isinstance(value, dict):
                return {k: _freeze_value(v) for k, v in value.items()}

            # 3. Lists en Tuples recursief doorlopen
            if isinstance(value, (list, tuple)):
                return [_freeze_value(v) for v in value]

            # 4. Primitives (int, float, bool, str, None) mogen door
            if isinstance(value, (int, float, bool, str, type(None))):
                return value

            # 5. ttLiquid
            if isinstance(value, ttLiquid):
                return value.__str__()

            # 6. Fallback: probeer deepcopy, anders string representatie
            try:
                return copy.deepcopy(value)
            except:
                return str(value)

        sp_stck = ttSparkleStack()
        status['sparkle_trace'].append({
            'id': instance.id,
            'tonic': instance.name,
            'sparkle': sparkle.__name__,
            'args': args,
            'kwargs': kwargs,
            'source': sp_stck.source,
            'at_enter': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': {
                    p: _freeze_value(getattr(instance, p))
                    for p in contract.get('probes', [])
                    if hasattr(instance, p)
                },
            }
        })
        sp_stck.push(instance, sparkle.__name__)
        instance._execute_sparkle(sparkle, *args, **kwargs)
        sp_stck.pop()
        status['sparkle_trace'][-1].update({
            'at_exit': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': {
                    p: _freeze_value(getattr(instance, p))
                    for p in contract.get('probes', [])
                    if hasattr(instance, p)
                },
                'sparkling': self.sparkling,
            }
        })
        if sparkle.__name__ in contract['till_sparkle_in']:
            status.setdefault('stop_condition', []).append(f'sparkle_trigger: [{sparkle.__name__}]')
        if instance.get_current_state_name() in contract['till_state_in']:
            status.setdefault('stop_condition', []).append(f'state_trigger: [{instance.get_current_state_name()}]')


    def finish_distiller(self, timeout=.5, contract=None):
        for liq in self.ledger.tonics:
            if isinstance(liq, ttLiquid): liq.finish()
            elif isinstance(liq, self.ledger.TonicReservation): self.ledger.unregister(liq)
        stat = self.sparkle(timeout=timeout, contract=contract)
        #todo: reset ledger
        return stat

    def stat_print(self, status, filter=None):
        import time
        print('=== Sparkling ==')

        if isinstance(filter, int):
            filter = [filter]
        elif isinstance(filter, list):
            pass
        elif filter is None:
            pass
        else:
            raise TypeError('filter is not None, a number or a list of numbers')

        for t in status.get('sparkle_trace', []):
            if filter is None or t['id'] in filter:
                e = t['at_enter']
                x = t['at_exit']
                ts = e['@']
                te = x['@']
                l_ts = f'{time.strftime("%H%M%S", time.localtime(ts))}.{int((ts - int(ts)) * 1000):03d}'
                l_te = f'{time.strftime("%H%M%S", time.localtime(te))}.{int((te - int(te)) * 1000):03d}'
                l_duration = f'{(te - ts):2.3f}'
                s = t['source']
                src = (s[0].name if s[0] else 'None') + '.' + s[1]

                print(
                    f"{t['id']:03d} - {t['tonic']}.{t['sparkle']} ( {t['args']}, {t['kwargs']} ) <-- {src}\n"
                    f"   at enter                                 at exit\n"
                    f"   {l_ts}                               {l_te}                               < {l_duration}s\n"
                    f"   {e['state']:.<40} {x['state']:.<40} < state"
                )
                pe = e.get('probes', {})
                px = x.get('probes', {})
                p = sorted(set(pe.keys()) | set(px.keys()))
                for key in p:
                    print(f"   {str(pe.get(key, '-')):.<40} {str(px.get(key, '-')):.<40} < {key}")
                print()
        print(
            f'>> stopped : {status["stop_condition"]}, duration {(status["end@"] - status["start@"]):2.03f}s, Catalyst Status {status["status"]}')

```

## `File: build\lib\TaskTonic\ttTonicStore\__init__.py`
```python
from .ttDistiller import ttDistiller
from .ttStore import ttStore
from .ttTimerScheduled import (ttTimerEveryYear, ttTimerEveryMonth, ttTimerEveryWeek, ttTimerEveryDay,
                               ttTimerEveryHour, ttTimerEveryMinute)

# Optional imports for PySide6
try:
    from .ttPyside6Ui import ttPyside6Ui
    from .ttPysideWidget import ttPysideWindow, ttPysideWidget
except ImportError:
    pass

# Optional imports for Tkinter
try:
    from .ttTkinterUi import ttTkinterUi
    from .ttTkinterWidget import ttTkinterFrame
except ImportError:
    pass
```

## `File: build\lib\TaskTonic\ttTonicStore\ttPysideWidget.py`
```python
import re
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import QObject, Qt

from .. import ttLedger, ttSparkleStack
from ..ttLiquid import __ttLiquidMeta
from ..ttTonic import ttTonic

# Dynamische resolutie van de Qt Metaclass
PySideMeta = type(QObject)


class ttPysideMeta(__ttLiquidMeta, PySideMeta):
    """
    Lost het metaclass conflict op tussen TaskTonic (ttEssence) en PySide6 (QObject).
    """
    pass

class ttPysideMixin:
    """
    Voegt de 'ttqt' functionaliteit toe aan widgets.
    """

    def _get_custom_prefixes(self):
        """
        Hook voor ttTonic. Retourneert onze prefix en de binder methode.
        """
        # We gebruiken de SmartPrefix om compatibel te zijn met de logica in ttTonic
        return {'ttqt': self._bind_qt_event}

    def _bind_qt_event(self, prefix, sparkle_name):
        """
        Deze methode wordt door ttTonic aangeroepen voor elke gevonden 'ttqt' method.
        sparkle_name is de naam van de 'interface method' (bijv. ttqt__btn__clicked)
        die ttTonic al heeft omgezet naar een queue-wrapper.
        """
        # 1. Parse de naam: ttqt__(widget)__(signaal)
        # We halen 'ttqt__' eraf.
        base_name = sparkle_name[6:]  # len('ttqt__') == 6

        # We zoeken de LAATSTE dubbele underscore om widget en signaal te scheiden.
        # Dit staat toe dat widget namen zelf dubbele underscores bevatten (bv. self.main__btn).
        if "__" not in base_name:
            raise RuntimeError(f"Invalid naming for sparkle '{sparkle_name}'. Expected ttqt__widget__signal.")

        w_name, s_name = base_name.rsplit("__", 1)

        # 2. Vind het widget
        if not hasattr(self, w_name):
            # Dit kan gebeuren als de UI nog niet is opgebouwd bij init.
            # Zorg dat setup_ui() wordt aangeroepen vòòr super().__init__().
            raise RuntimeError(f"Widget '{w_name}' not found during binding of '{sparkle_name}'.")

        widget = getattr(self, w_name)

        # 3. Vind het signaal
        if not hasattr(widget, s_name):
            raise RuntimeError(f"Error: Signal '{s_name}' not found on '{w_name}'.")

        signal = getattr(widget, s_name)

        # 4. Haal de wrapper op die ttTonic heeft gemaakt
        # Deze wrapper zet de taak op de queue.
        tonic_wrapper = getattr(self, sparkle_name)

        # 5. Verbinden!
        try:
            signal.connect(tonic_wrapper)
        except Exception as e:
            raise RuntimeError(f"[ttPyside] Failed to connect {sparkle_name}: {e}")


class ttPysideWidget(ttPysideMixin, QWidget, ttTonic, metaclass=ttPysideMeta):
    def __init__(self, parent=None, **kwargs):
        ttTonic.__init__(self, **kwargs)

        qt_parent = parent
        tt_context = ttSparkleStack().get_tonic()
        if qt_parent is None and isinstance(tt_context, QWidget):
            qt_parent = tt_context

        QWidget.__init__(self, qt_parent)
        self.setup_ui()

    def setup_ui(self):
        pass

    def closeEvent(self, event):
        if self.finishing:
            event.accept()
        else:
            event.ignore()
            self.finish()

    def ttse__on_finished(self):
        # self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.close()


class ttPysideWindow(ttPysideMixin, QMainWindow, ttTonic, metaclass=ttPysideMeta):
    def __init__(self, parent=None, **kwargs):
        ttTonic.__init__(self, **kwargs)

        qt_parent = parent
        tt_base = self.base

        if qt_parent is None and isinstance(tt_base, QWidget):
            qt_parent = tt_base

        QMainWindow.__init__(self, qt_parent)

    def closeEvent(self, event):
        if self.finishing:
            event.accept()
        else:
            event.ignore()
            self.ttse__on_close_event()

    def ttse__on_close_event(self):
        self.ttsc__finish()

    def ttse__on_finished(self):
        # self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.close()
```

## `File: build\lib\TaskTonic\ttTonicStore\ttPyside6Ui.py`
```python
# ttPyside6Ui.py
import sys, queue, time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QEvent, QCoreApplication, QTimer

from .. import ttSparkleStack
from ..ttCatalyst import ttCatalyst
from .ttPysideWidget import ttPysideMeta


class SparkleEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, payload):
        super().__init__(SparkleEvent.EVENT_TYPE)
        self.payload = payload


class PysideQueue(queue.SimpleQueue):
    def __init__(self, catalyst_ui):
        super().__init__()
        self.catalyst_ui = catalyst_ui

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        event = SparkleEvent(item)
        QCoreApplication.postEvent(self.catalyst_ui, event)


class ttPyside6Ui(ttCatalyst, QObject, metaclass=ttPysideMeta):
    def __init__(self, name=None, app_args=None):
        ttCatalyst.__init__(self, name=name)
        QObject.__init__(self)
        if QApplication.instance():
            self.app = QApplication.instance()
        else:
            self.app = QApplication(app_args or sys.argv)

        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.setSingleShot(True)
        self._heartbeat_timer.timeout.connect(self._on_qt_timer_timeout)

    def new_catalyst_queue(self):
        return PysideQueue(catalyst_ui=self)

    def start_sparkling(self):
        if self.id != 0:
            raise RuntimeError(f'{self.__class__.__name__} must be a main catalyst (id==0)')

        self._schedule_next_timer()
        ttSparkleStack().catalyst = self

        self.app.exec()
        super().sparkle()  # finish last TaskTonic calls (if any) after ui ended

    def customEvent(self, event):
        if event.type() == SparkleEvent.EVENT_TYPE:
            sp_stck = ttSparkleStack()
            try:
                item = self.catalyst_queue.get_nowait()
                instance, sparkle, args, kwargs, sp_stck.source = item
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                self._process_extra_sparkles()

            except queue.Empty:
                pass
            except Exception as e:
                raise(f"[ttPyside6Ui] Error: {e}")
            finally:
                self._schedule_next_timer()
            event.accept()
        else:
            super().customEvent(event)

    def _process_extra_sparkles(self):
        sp_stck = ttSparkleStack()
        while self.extra_sparkles:
            payload = self.extra_sparkles.pop(0)
            instance, sparkle, args, kwargs = payload
            sp_stck.push(instance, sparkle.__name__)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

    def _schedule_next_timer(self):
        reference = time.time()
        next_timer_expire = 0.0
        while next_timer_expire == 0.0:
            next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60

        self._heartbeat_timer.stop()
        if next_timer_expire > 0.0:
            ms = max(0, int(next_timer_expire * 1000))
            self._heartbeat_timer.start(ms)

    def _on_qt_timer_timeout(self):
        self._schedule_next_timer()
```

## `File: build\lib\TaskTonic\ttTonicStore\ttStore.py`
```python
# ------------------------------------------------------------------------------
# Class: ttStore (TaskTonic Service Wrapper)
# ------------------------------------------------------------------------------
from ..ttLiquid import ttLiquid
from ..internals.Store import Store, Item

class ttStore(ttLiquid, Store):
    """
    TaskTonic specific wrapper that integrates Store with the Ledger.
    Defined as a Singleton Service via _tt_is_service.
    """

    # Determines service name in ttEssenceMeta logic
    _tt_is_service = 'store'

    def __init__(self, *args, **kwargs):
        # 1. Init ttEssence (Registers in Ledger)
        # Note: ttEssenceMeta ensures this runs only once for the singleton
        ttLiquid.__init__(self, *args, **kwargs)

        # 2. Init Store (Setup locks and storage)
        Store.__init__(self)

    def _init_service(self, *args, **kwargs):
        """Called every time the service is requested/accessed via ledger."""
        pass
```

## `File: build\lib\TaskTonic\ttTonicStore\ttTimerScheduled.py`
```python
import time
import calendar as cal
import bisect
from TaskTonic.ttTimer import ttTimer


def stime(t):
    tm = time.localtime(t)
    return f'{ttTimerScheduled.days[tm.tm_wday + 7]} {tm.tm_year:04d}-{tm.tm_mon:02d}-{tm.tm_mday:02d} ' \
           f'{tm.tm_hour:02}:{tm.tm_min:02}:{tm.tm_sec:02}'


class ttTimerScheduled(ttTimer):
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",

        "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
    ]
    days = [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"
    ]

    def __init__(self, name=None,
                 month=None, week=None, day=None, in_week=None, hour=None, minute=None, second=None,
                 time_str=None, t_units=3, sparkle_back=None):
        super().__init__(name=name, sparkle_back=sparkle_back)
        if month is not None or week is not None:  # year period
            self._month = None
            self._week = None
            if isinstance(month, int):
                if week is not None:
                    raise ValueError(f'Both month and week given')
                if month < 1 or month > 12:
                    raise ValueError(f'Invalid month (1..12) "{month}"')
                self._month = month
            elif isinstance(month, str):
                if week is not None:
                    raise ValueError(f'Both month and week given')
                month = month.strip().lower()
                if month in self.months:
                    self._month = self.months.index(month) % 12 + 1
                else:
                    raise ValueError(f'Invalid day "{month}"')
            elif isinstance(week, int):
                if month is not None:
                    raise ValueError(f'Both month and week given')
                if week < 1 or week > 53:
                    raise ValueError(f'Invalid week (1..53) "{month}"')
                self._week = week

            else:
                raise ValueError(f'Invalid month or week "{month}" - "{week}"')

        if day is not None:
            self._day = None
            self._in_week = None
            if isinstance(day, int):
                self._day = day
                if day < -31 or day > 31:
                    raise ValueError(f'Invalid day (1..31 or -1..-31) "{day}"')
            elif isinstance(day, str):
                day = day.strip().lower()
                if day in self.days:
                    self._day = self.days.index(day) % 7
                    if in_week is None:
                        in_week = 1  # default when day name given
                else:
                    raise ValueError(f'Invalid day "{day}"')
            else:
                raise ValueError(f'Invalid day "{day}"')
            if in_week is not None:
                self._in_week = in_week
                if self._day > 6:
                    raise ValueError(f'Invalid day (0..6 when in_week given) "{day}"')

        if isinstance(hour, int):
            if t_units < 3:
                raise ValueError(f'to many time elements hour:00:00')
            self._hour = hour
            self._minute = 0
            self._second = 0
        elif hour is not None:
            raise ValueError(f'hour must be an integer')

        if isinstance(minute, int):
            if t_units < 2:
                raise ValueError(f'to many time elements minute:00')
            self._minute = minute
            self._second = 0
        elif minute is not None:
            raise ValueError(f'minute must be an integer')

        if isinstance(second, (int, float)):
            self._second = second
        elif second is not None:
            raise ValueError(f'second must be an integer or float')
        if isinstance(time_str, str):
            tu = time_str.split(':')
            try:
                tl = [int(u) for u in tu]
                while len(tl) < t_units:
                    tl.append(0)
                if len(tl) > t_units:
                    raise ValueError(f'to many time elements "{time_str}"')
                if len(tl) == 1:
                    self._second = tl[0]
                elif len(tl) == 2:
                    self._minute, self._second = tl
                elif len(tl) == 3:
                    self._hour, self._minute, self._second = tl

            except ValueError as e:
                raise ValueError(f'Invalid time_str "{e}"')
        elif time_str is not None:
            raise ValueError(f'time_str must be an string')
        self.start()

    def __str__(self):
        s = (self.__class__.__name__[:20]).ljust(21)
        if hasattr(self, "_month") and self._month is not None:
            s += self.months[self._month - 1]
            if hasattr(self, "_in_week") and self._in_week is not None:
                s += f', {self.days[self._day]} {self._in_week}'
            else:
                s += " " + str(self._day)
        elif hasattr(self, "_week") and self._week is not None:
            s += "week " + str(self._week) + ", " + self.days[self._day]
        elif hasattr(self, "_day") and self._day is not None:
            if self._in_week is not None:
                s += f'{self.days[self._day]}{f", {self._in_week}" if self._in_week > 0 else ""}'
            else:
                s += "day " + str(self._day)
        s = s.ljust(45)
        s += f'{self._hour:02}:' if hasattr(self, "_hour") else "   "
        s += f'{self._minute:02}:' if hasattr(self, "_minute") else "   "
        s += f'{self._second:02}' if hasattr(self, "_second") else "  "
        s += f',  expires @ {stime(self.expire) if self.expire >=0 else "-1"}'

        return s

    def reload_on_expire(self, reference_time):
        self.catalyst.timers.remove(self)
        self.next_trigger(reference_time)
        bisect.insort(self.catalyst.timers, self)


    def start(self):
        if self.id == -1: raise RuntimeError(f'Cannot start a finished timer')
        if self.expire == -1:
            self.expire = 0
            n = time.time()
            self.next_trigger(n)
            if self.expire <= n:  # after first time initialisation expire time can buy in the past; recalculate
                self.next_trigger(n)
            bisect.insort(self.catalyst.timers, self)
        else:
            raise RuntimeError(f"Can't start a running timer ({self})")
        return self

    def restart(self):
        if self.expire == -1:
            self.start()

    def next_trigger(self, now):
        raise RuntimeError('next_trigger must be overridden')

    def ts_replace(self, ts, year=None, month=None, day=None, hour=None, minute=None, second=None):
        return time.struct_time((ts.tm_year if year is None else year,
                                 ts.tm_mon if month is None else month,
                                 ts.tm_mday if day is None else day,
                                 ts.tm_hour if hour is None else hour,
                                 ts.tm_min if minute is None else minute,
                                 ts.tm_sec if second is None else second, -1, -1, -1))

    def ts_add_time(self, ts, week=0, day=0, hour=0, minute=0, second=0):
        return time.localtime(time.mktime(ts) + week * 604800 + day * 86400 + hour * 3600 + minute * 60 + second)


class ttTimerEveryYear(ttTimerScheduled):
    def __init__(self, name=None,
                 month=None, week=None, day=None, in_week=None, hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=month, week=week, day=day, in_week=in_week, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        m = 1 if self._month is None else self._month
        if self.expire == 0:
            n = time.localtime(now)
            t = time.struct_time((n.tm_year, m, 1, self._hour, self._minute, self._second, -1, -1, -1))
        else:
            t = time.localtime(
                self.expire +
                (0 if self._month is not None else
                 (((7 * 24 * 3600) if self._week == 1 else 0) - ((14 * 24 * 3600) if self._week >= 52 else 0)))
            )
            t = self.ts_replace(t, year=t.tm_year + 1, month=m, day=1)
        first_day, days_in_month = cal.monthrange(t.tm_year, t.tm_mon)

        if self._month is None:  # by week
            t = self.ts_add_time(t, week=self._week - 1, day=self._day + 3 - (first_day + 3) % 7)
            t = self.ts_replace(t, hour=self._hour, minute=self._minute, second=self._second)

        else:  # by month
            if self._in_week is None:  # day in month
                if self._day > 0:
                    t = self.ts_replace(t, day=min(days_in_month, self._day))
                else:
                    t = self.ts_replace(t, day=max(1, days_in_month + self._day + 1))
            else:  # weekday
                wday_first_in_month = 1 + (7 + self._day - first_day) % 7
                wday_last_in_month = wday_first_in_month + (days_in_month - wday_first_in_month) // 7 * 7
                if self._in_week > 0:
                    t = self.ts_replace(t, day=min(wday_last_in_month, wday_first_in_month + (self._in_week - 1) * 7),
                                        hour=self._hour)
                else:
                    t = self.ts_replace(t, day=max(wday_first_in_month, wday_last_in_month - (-self._in_week - 1) * 7),
                                        hour=self._hour)
        self.expire = time.mktime(t)


class ttTimerEveryMonth(ttTimerScheduled):
    def __init__(self, name=None,
                 day=None, in_week=None, hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=day, in_week=in_week, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire == 0:
            n = time.localtime(now)
            t = time.struct_time((n.tm_year, n.tm_mon, 1, self._hour, self._minute, self._second, -1, -1, -1))
        else:
            t = time.localtime(self.expire + 31 * 86400)  # next month
            t = self.ts_replace(t, day=1, hour=self._hour, minute=self._minute, second=self._second)
        first_day, days_in_month = cal.monthrange(t.tm_year, t.tm_mon)

        if self._in_week is None:  # day in month
            if self._day > 0:
                t = self.ts_replace(t, day=min(days_in_month, self._day))
            else:
                t = self.ts_replace(t, day=max(1, days_in_month + self._day + 1))
        else:  # weekday
            wday_first_in_month = 1 + (7 + self._day - first_day) % 7
            wday_last_in_month = wday_first_in_month + (days_in_month - wday_first_in_month) // 7 * 7
            if self._in_week > 0:
                t = self.ts_replace(t, day=min(wday_last_in_month, wday_first_in_month + (self._in_week - 1) * 7),
                                    hour=self._hour)
            else:
                t = self.ts_replace(t, day=max(wday_first_in_month, wday_last_in_month - (-self._in_week - 1) * 7),
                                    hour=self._hour)

        self.expire = time.mktime(t)


class ttTimerEveryWeek(ttTimerScheduled):
    def __init__(self, name=None,
                 day=None, hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=day, in_week=0, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire = time.mktime(self.ts_replace(time.localtime(self.expire + 604800), hour=self._hour))
        else:
            n = time.localtime(now)
            t = time.localtime(now + (7 + self._day - n.tm_wday) % 7 * 86400)
            t = self.ts_replace(t, hour=self._hour, minute=self._minute, second=self._second)
            self.expire = time.mktime(t)


class ttTimerEveryDay(ttTimerScheduled):
    def __init__(self, name=None,
                 hour=0, minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=None, in_week=None, hour=hour, minute=minute, second=second,
                         time_str=time_str, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire = time.mktime(self.ts_replace(time.localtime(self.expire + 86400), hour=self._hour))
        else:
            n = time.localtime(now)
            t = self.ts_replace(n, hour=self._hour, minute=self._minute, second=self._second)
            self.expire = time.mktime(t)


class ttTimerEveryHour(ttTimerScheduled):
    def __init__(self, name=None,
                 minute=0, second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=None, in_week=None, hour=None, minute=minute, second=second,
                         time_str=time_str, t_units=2, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire += 3600
        else:
            self.expire = now // 3600 * 3600 + self._minute * 60 + self._second


class ttTimerEveryMinute(ttTimerScheduled):
    def __init__(self, name=None,
                 second=0,
                 time_str=None, sparkle_back=None):
        super().__init__(name=name,
                         month=None, week=None, day=None, in_week=None, hour=None, minute=None, second=second,
                         time_str=time_str, t_units=1, sparkle_back=sparkle_back)

    def next_trigger(self, now):
        if self.expire > 0:
            self.expire += 60
        else:
            self.expire = now // 60 * 60 + self._second

```

## `File: build\lib\TaskTonic\ttTonicStore\ttTkinterUi.py`
```python
import os
import sys

# Re-route the Tcl/Tk libraries to the base Python installation
base_prefix = getattr(sys, "base_prefix", sys.prefix)
os.environ['TCL_LIBRARY'] = os.path.join(base_prefix, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(base_prefix, 'tcl', 'tk8.6')

import tkinter as tk
import queue
import time
from .. import ttSparkleStack
from ..ttCatalyst import ttCatalyst


class TkinterQueue(queue.SimpleQueue):
    def __init__(self, catalyst_ui):
        super().__init__()
        self.catalyst_ui = catalyst_ui
        self.root = catalyst_ui.root

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        # Genereer een thread-safe virtueel event om de mainloop te triggeren
        self.root.event_generate("<<SparkleEvent>>", when="tail")


class ttTkinterUi(ttCatalyst):
    def __init__(self, name=None):
        self.root = tk.Tk()
        super().__init__(name=name)

        # Koppel het virtuele event aan de custom Sparkle verwerker
        self.root.bind("<<SparkleEvent>>", self.customEvent)
        self._timer_id = None

    def new_catalyst_queue(self):
        return TkinterQueue(catalyst_ui=self)

    def start_sparkling(self):
        if self.id != 0:
            raise RuntimeError(f'{self.__class__.__name__} must be a main catalyst (id==0)')

        self._schedule_next_timer()
        ttSparkleStack().catalyst = self

        self.root.mainloop()
        super().sparkle()  # Verwerk overgebleven TaskTonic calls als het scherm sluit

    def customEvent(self, event=None):
        sp_stck = ttSparkleStack()
        try:
            item = self.catalyst_queue.get_nowait()
            instance, sparkle, args, kwargs, sp_stck.source = item
            sp_name = sparkle.__name__

            sp_stck.push(instance, sp_name)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

            sp_stck.source = (instance, sp_name)
            self._process_extra_sparkles()

        except queue.Empty:
            pass
        except Exception as e:
            print(f"[ttTkinterUi] Error: {e}")
        finally:
            self._schedule_next_timer()

    def _process_extra_sparkles(self):
        sp_stck = ttSparkleStack()
        while self.extra_sparkles:
            payload = self.extra_sparkles.pop(0)
            instance, sparkle, args, kwargs = payload
            sp_stck.push(instance, sparkle.__name__)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

    def _schedule_next_timer(self):
        reference = time.time()
        next_timer_expire = 0.0
        while next_timer_expire == 0.0:
            next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0

        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

        if next_timer_expire > 0.0:
            ms = max(0, int(next_timer_expire * 1000))
            if ms > 60000: ms = 60000  # Max 1 minuut wachten als er geen timers zijn
            self._timer_id = self.root.after(ms, self._on_tk_timer_timeout)

    def _on_tk_timer_timeout(self):
        self._schedule_next_timer()

        # TaskTonic/ttTonicStore/ttTkinterUi.py

    def ttse__on_finished(self):
        # Als de Catalyst écht klaar is met z'n queues,
        # sluiten we pas het Tkinter fundament af.
        if self.root:
            try:
                self.root.destroy()
            except tk.TclError:
                pass
        super().ttse__on_finished()
```

## `File: build\lib\TaskTonic\ttTonicStore\ttTkinterWidget.py`
```python
import tkinter as tk
from .. import ttSparkleStack
from ..ttTonic import ttTonic


class ttTkinterMixin:
    """
    Voegt de 'tttk' functionaliteit toe aan Tkinter widgets.
    """

    def _get_custom_prefixes(self):
        return {'tttk': self._bind_tk_event}

    def _bind_tk_event(self, prefix, sparkle_name):
        # Format: tttk__widget_name__event_or_command
        base_name = sparkle_name[6:]  # Haal 'tttk__' eraf

        if "__" not in base_name:
            raise RuntimeError(f"Invalid naming for sparkle '{sparkle_name}'. Expected tttk__widget__event.")

        w_name, e_name = base_name.rsplit("__", 1)

        if not hasattr(self, w_name):
            raise RuntimeError(f"Widget '{w_name}' not found during binding of '{sparkle_name}'.")

        widget = getattr(self, w_name)
        tonic_wrapper = getattr(self, sparkle_name)

        # Bepaal of het een attribuut 'command' is of een reguliere event binding
        if e_name == "command":
            widget.configure(command=tonic_wrapper)
        else:
            # Bijv. e_name == "<Button-1>" of "<Return>"
            widget.bind(e_name, tonic_wrapper)


class ttTkinterFrame(ttTkinterMixin, tk.Frame, ttTonic):
    def __init__(self, parent=None, **kwargs):
        if getattr(self, '_ui_init_done', False):
            return

        ttTonic.__init__(self, **kwargs)

        tk_parent = parent
        tt_context = ttSparkleStack().get_tonic()

        # Vind de juiste master/parent
        if tk_parent is None and isinstance(tt_context, (tk.Tk, tk.Frame)):
            tk_parent = tt_context
        elif tk_parent is None and hasattr(self.base, 'root'):
            tk_parent = self.base.root

        tk.Frame.__init__(self, tk_parent)
        self.setup_ui()
        self._ui_init_done = True

    def setup_ui(self):
        """Override deze functie om je widgets aan te maken"""
        pass

```

## `File: docs\documentation.md`
## `File: docs\index.md`
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
```## `File: docs\tasting-the-tonic.md`
# 🧪 Tasting The Tonic

<img src="../assets/tasktonic-tasting.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">
Welcome to the Tonic Bar! If you are tired of the traditional `async/await` virus infecting your codebase, or debugging multi-threading race conditions, you are in the right place. 

TaskTonic introduces a paradigm called **Sparkling Programming**. Instead of blocking threads or fighting the Global Interpreter Lock, you break your code down into small, atomic, non-interruptible units of work called **Sparkles**. 

Let's pour our first glass and see how it works!

---

## Step 1: Preparation (The Setup)

Before we start brewing, you need to install the framework and get familiar with the ingredients.

**1. Install TaskTonic:**
Open your terminal and install the package via pip:
```bash
pip install tasktonic
```

2. Read the Manuals:
TaskTonic is powerful, but it requires a slightly different way of thinking. Before building massive applications, we highly recommend reading the core documentation located in the _documents folder of the repository. Understanding the ttCatalyst, the ttLedger, and the State Machine will save you hours of debugging later!
3. Generate the Starter File:
TaskTonic comes with a built-in generator. Run this command in your terminal to instantly create a hello_tasktonic.py file in your current directory:
python -m TaskTonic

## Step 2: The Recipe (Hello World)
If you open the generated hello_tasktonic.py file, you will see the following code. This is a fully functioning, state-driven, concurrent application.
You can run it directly by typing python hello_tasktonic.py.
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


if __name__ == '__main__':
    myApp()
```

## Step 3: Breaking Down the Magic

How does this actually work without a `while True` loop or `time.sleep()`? Let's break it down concept by concept.

### 1. The Formula and The Catalyst
At the very bottom, we define `myApp(ttFormula)`. The Formula is the entry point of your application. It does three vital things behind the scenes:
1. It configures the system (like setting the logging to screen).
1. It starts the ttCatalyst. The Catalyst is the underlying engine of TaskTonic. It runs a continuous loop in the background, pulling tasks from a queue and executing them sequentially.
1. It creates our first "worker" agent: HelloWorld().

### 2. The Tonic and Sparkle Naming (ttse__)
HelloWorld inherits from `ttTonic`. A Tonic is a stateful worker. It doesn't run code directly; instead, it places work orders (called `Sparkles`) onto the Catalyst's queue. TaskTonic uses smart naming conventions to automatically route these Sparkles:

1. `ttsc__ (Command)`: An external request to do something.
1. `ttse__ (Event)`: A reaction to an internal event, like a timer or a startup sequence.
When our Tonic is created, the framework automatically places the `ttse__on_start` event on the queue.

### 3. State Machines (self.to_state)
Every ttTonic is a built-in state machine. By default, a Tonic has no state (state = -1).
In `ttse__on_start`, we call `self.to_state('hello')`.
When the state changes, the framework looks for a Sparkle named `ttse_[state_name]__on_enter`. That is why `ttse_hello__on_enter` is automatically executed, logging "Hello world" to your screen!

### 4. Timers and Automatic sparkle_back
In TaskTonic, you must never use `time.sleep()`, as it would freeze the Catalyst engine. Instead, we use a `ttTimer` like `ttTimerRepeat`.
Look at this line:
`ttTimerRepeat(seconds=self.interval, name='tm_step')`

Notice that we didn't tell the timer what function to call when it expires! This is TaskTonic's automatic callback routing at work:
1. Because we named the timer tm_step, the framework automatically looks for an event sparkle named `ttse__on_tm_step`.
1. Because our Tonic is currently in the hello state, it specifically looks for `ttse_hello__on_tm_step`.
When the timer fires 1.5 seconds later, it hits `ttse_hello__on_tm_step`, which changes the state to welcome. This triggers `ttse_welcome__on_enter`, logging "Welcome to TaskTonic".

### 5. Finishing Gracefully
Finally, the timer fires again while we are in the ending state. This hits `ttse_ending__on_tm_step`, where we call `self.ttsc__finish()`.
This is the official stop command. It halts the state machine, cleans up any active timers, deregisters the Tonic from the Ledger, and allows the application to shut down cleanly without leaving zombie threads behind.


** Welcome to Sparkling Programming! **


## `File: docs\_In the future (or not)\IP communication roadmap.md`
# TaskTonic Future Architecture Roadmap: IP, Protocols & Visual Dashboards

This document serves as the architectural vision and blueprint for expanding the TaskTonic framework into network communications (UDP, HTTP, HTTPS, MQTT) and a declarative, vector-based user interface layer.

---

## 1. Core Principles of the Network Layer

All future network expansions will build upon the existing `SelectorHandler` infrastructure. By hooking the underlying native TCP/UDP sockets directly into the selector engine via `EVENT_READ`, TaskTonic handles multi-device networking **synchronously within a single background thread**, completely avoiding thread-safety issues or overhead from external concurrency engines.

---

## 2. UDP Integration (The Immediate Next Step)

UDP (User Datagram Protocol) is essential for high-speed, low-overhead local smart home automation, specifically for components like **WiZ Bulbs** (which listen natively on UDP port 38899).

### Architectural Changes
* **Connectionless:** No `accept()` or `connect()` handshakes are required. The socket simply listens or throws datagrams.
* **No De-fragmentation:** Unlike TCP, UDP delivers packets atomically. The 4-byte framing header and `rcv_buf` reconstruction logic are obsolete; `recvfrom()` returns the full payload immediately.
* **Source Tracking:** Every incoming datagram returns a `(data, addr)` tuple. The sender's address (`addr`) must be tracked to route replies.

### Code Blueprint: `UdpSocketHandler`

```python
import socket
import pickle


class UdpSocketHandler:
    def __init__(self, host, port, as_server=False):
        self.host = host
        self.port = port
        self.as_server = as_server
        
        # SOCK_DGRAM specifies UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        
        if self.as_server:
            self.sock.bind((self.host, self.port))

    def handle_read(self):
        """Called by the SelectorHandler when a UDP packet arrives."""
        try:
            data, addr = self.sock.recvfrom(65535)
            payload = pickle.loads(data)
            return payload, addr
        except Exception:
            return None, None

    def send_data(self, payload, target_addr):
        """Sends an atomic datagram to a specific target address."""
        try:
            data = pickle.dumps(payload)
            self.sock.sendto(data, target_addr)
        except Exception:
            pass
```

---

## 3. HTTP & HTTPS Integration (Shelly Components)

Shelly components expose a powerful local HTTP REST API. Integrating HTTP expands TaskTonic into a web-aware framework.

### HTTP Implementation Strategies
1. **Client Mode (TaskTonic commands Shelly):** TaskTonic sends a quick, standard HTTP GET request to the Shelly IP (e.g., `http://192.168.1.50/relay/0?turn=toggle`).
2. **Server Mode / Webhooks (Shelly commands TaskTonic):** Instead of continuous "long-polling" requests which hog resources, the Shelly is configured via its web UI to trigger an **I/O Action (Webhook)**. When a physical switch is flipped, Shelly fires an instantaneous HTTP GET to TaskTonic's lightweight HTTP Server (e.g., port 8080). TaskTonic parses the URL and immediately maps it to a Sparkle.

---

### Deep Dive: Is HTTPS a Big Step?

**Yes, transitioning from raw HTTP to HTTPS is a significant technical milestone.** While HTTP is just plain text sent over a standard TCP socket, HTTPS injects a mandatory **SSL/TLS cryptographic layer** right between TCP and HTTP.

```
HTTP:  [ Application (Plain Text) ] ----> [ TCP Socket ]
HTTPS: [ Application (Plain Text) ] ----> [ SSL/TLS Encryption ] ----> [ Secure TCP Socket ]
```

#### The Challenges of HTTPS in a Native Socket Framework:
1. **The TLS Handshake:** Before a single byte of data can be read, a complex multi-step cryptographic handshake must occur to exchange keys and verify identities.
2. **Certificate Management:** * **Server Mode:** If TaskTonic acts as an HTTPS server to receive secure webhooks, you **must** supply an SSL certificate (`.crt`) and a private key (`.key`). Local devices will reject self-signed certificates unless you manually force them to trust your custom Root CA.
   * **Client Mode:** If TaskTonic connects to a secure external server, it needs to verify the remote certificate using a local store of trusted authorities.
3. **Socket Wrapping:** In native Python sockets, you cannot just read/write anymore. You must wrap the raw socket using Python's `ssl` module.

#### Impact on `SelectorHandler`:
Fortunately, once an SSL socket finishes its handshake, it can still be registered with the `SelectorHandler` for `EVENT_READ`. However, the wrapping boilerplate introduces extra complexity:

```python
import socket
import ssl

# Example of wrapping a raw socket for HTTPS Server Mode
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(raw_socket, server_side=True)
```

**Conclusion on HTTPS:** For purely local home automation networks (isolated Wi-Fi), raw HTTP is usually preferred due to zero certificate overhead. If external cloud interaction or absolute local encryption is required, the `ssl` module integration must be implemented.

---

## 4. MQTT Integration (The Unified Smart Home Backbone)

MQTT (Message Queuing Telemetry Transport) introduces a lightweight Pub/Sub architecture via a central agent (e.g., a **Mosquitto Broker**).

### Why MQTT is Superior for Smart Homes
* **Decentralized IPs:** TaskTonic no longer needs to keep track of individual Shelly IP addresses or host an HTTP Webhook server. It opens **one permanent TCP connection** to the Mosquitto Broker and subscribes to relevant topics.
* **1:1 Mapping with Store Paths:** MQTT uses a hierarchical slash-separated topic structure that mirrors TaskTonic's Store Paths perfectly.

### Architectural Harmony
Because an MQTT client library (like `paho-mqtt`) allows you to extract its underlying raw TCP file descriptor, you can effortlessly register the Mosquitto connection straight into the `SelectorHandler`. Incoming MQTT payload updates automatically translate directly to targeted Ledger paths:

```python
def on_mqtt_message(client, userdata, message):
    path = message.topic  # e.g., "tasktonic/store/livingroom/switch_1"
    payload = message.payload.decode('utf-8')
    
    ledger = ttLedger.get_instance()
    tonic = ledger.get_tonic_by_path(path)
    
    if tonic is not None:
        # Automatically direct the external network state to the correct internal Tonic
        tonic.ttse__on_external_update(payload)
```

---

## 5. Declarative SVG Dashboards

The future UI layer allows developers to draw beautiful, responsive dashboards using standard vector design software like **Inkscape**, completely bypassing HTML/CSS layout grid nightmares.

```
+------------------+      Sets ID to:       +------------------------+
| Inkscape Drawing |  ===================>  |  "tt_kitchen_light_1"  |
+------------------+                        +------------------------+
                                                        ||
                                                        || (Auto-Maps)
                                                        \/
                                            +------------------------+
                                            |  TaskTonic Store Path: |
                                            |  "kitchen/light_1"     |
                                            +------------------------+
```

### The Workflow Blueprint
1. **Design:** Draw the UI interface visually in Inkscape. Every interactive component (button, bulb, background panel) is given a specific **Object ID** following a naming convention that maps directly to the TaskTonic Store Paths (e.g., an ID of `tt_kitchen_light_1` maps to path `kitchen/light_1`).
2. **Parse:** Upon startup, TaskTonic's lightweight web server uses an XML parser (`xml.etree.ElementTree`) to scan the SVG file, automatically creating data bindings for every element prefixed with `tt_`.
3. **Stream (WebSockets):** The server serves the SVG to any screen or mobile device. A universal, lightweight embedded JavaScript engine handles bidirectional real-time communication over a persistent WebSocket connection:
   * **User Interaction:** Clicking an SVG element in the browser immediately relays a JSON action object back to TaskTonic over the WebSocket, pushing a Sparkle onto the queue.
   * **State Updates:** When an internal Tonic shifts state (e.g., via a UDP or MQTT event), TaskTonic pushes a state message down the WebSocket. The frontend JavaScript instantly locates the corresponding SVG ID and modifies its visual attributes (e.g., changing CSS `fill` colors to yellow) in real-time.

---

## Summary of Protocol Capabilities

| Protocol | Purpose in TaskTonic | Connection Style | Overhead | Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **UDP** | WiZ Bulbs control | Connectionless Datagram | Lowest | Low |
| **HTTP** | Shelly controls & webhooks | Short-lived TCP per request | Medium | Low |
| **HTTPS** | Encrypted webhooks / external APIs | Secure TCP with TLS handshake | High | High (Certificates) |
| **MQTT** | Unified Shelly / Broker fabric | Single permanent TCP connection | Lowest | Low (via library) |
| **WebSockets**| Real-time SVG UI syncing | Single persistent HTTP Upgrade | Low | Medium |## `File: docs\CoreConcepts\10 - TaskTonic  - The introduction.md`
# TaskTonic Framework: Developer Documentation

<img src="../assets/tasktonic-introduction.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">


## 1. Philosophy & Metaphor

TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model.

The core philosophy is based on the **Tonic**. Think of your running application as a glass of tonic. It comes to life through **Sparkles**, the **bubbles** rising in a liquid.

*   **The Flow:** Code is executed in small, atomic units called *Sparkles*.
*   **The Fizz:** When these Sparkles flow continuously, the application "fizzes" with activity. It feels like a single, cohesive whole, even though it may be performing multiple logical processes simultaneously.
*   **The Rule:** A Sparkle must be short-lived. If one bubble takes too long to rise (blocking code), the flow stops, and the fizz goes flat. In practice, this is rarely an issue, as most software processes are reactive chains of short events.

This architecture allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) without the race conditions and headaches of traditional multi-threading.

---

## 2. Core Architecture

The framework is built on a strict hierarchy of classes.

| Component | Class | Description |
| :--- | :--- | :--- |
| **Liquid** | `ttLiquid` | The base substance. It handles identity, hierarchy (parent/child relationships), and lifecycle management in the `Ledger`. It is the passive foundation. |
| **Tonic** | `ttTonic` | The active ingredient. Inherits from `ttLiquid`. It adds the ability to "sparkle" (execute code), manage state (State Machines), and log activity. |
| **Catalyst** | `ttCatalyst` | The engine that makes the Tonic fizz. It owns the execution thread and the queue. It pulls Sparkles one by one and executes them. |
| **Formula** | `ttFormula` | The recipe. The entry point of your application where you define the initial mix of Tonics and configuration settings. |

---

## 3. The Tonic (`ttTonic`)

The `ttTonic` is where you write your application logic. It uses **introspection** to automatically bind your methods to the execution queue based on their names.

### 3.1 Sparkle Naming Convention

You do not register callbacks manually. You simply name your methods using specific prefixes. Every prefix starts with **tts**, it is a TaskTonic Sparkle.

*   **`ttsc__` (Command):** *Public Command.* Call this to request an action from outside the class.
    *   *Example:* `my_tonic.ttsc__start_process()`
*   **`ttse__` (Event):** *Public Event.* Call this to react to an event (like a timer or UI click).
    *   *Example:* `ttse__on_timer(info)`
*   **`tts__` , or `_tts__`(Sparkle):** *Internal.* Private logic chunks used to break up large tasks.
    *   *Example:* `self.tts__step_two()`
*   **`_ttss__` (System):** Reserved for framework lifecycle hooks (startup/shutdown).

> **Important:** When you call a sparkle method (e.g., `self.tts__calculate()`), it does **not** execute immediately. It places a "bubble" (work order) on the Catalyst queue. It will be executed when the Catalyst reaches it in the stream.

### 3.2 State Machines

Every `ttTonic` is a built-in State Machine. You can organize your code by defining which Sparkles are valid in which state.

**Changing State:**
Use `self.to_state('new_state_name')`.

**State-Specific Sparkles:**
You can prefix a Sparkle with a state name: `prefix_state__name`.

*   **Specific:** `ttsc_idle__open()` — Only runs if the Tonic is in the `idle` state.
*   **Generic:** `ttsc__open()` — Runs in any state (unless a specific version exists).
*   **Fallback:** If called in a state where no handler exists, the call is ignored (the bubble pops harmlessly).

### 3.3 Lifecycle & Termination

To ensure proper cleanup and hierarchy management, you must use the framework's lifecycle methods.

*   **`ttsc__finish(self)`**: **The Stop Command.** Call this to stop the Tonic. It initiates the graceful shutdown sequence:
    1.  Stops the State Machine (transitions to `-1`).
    2.  Sets the Tonic to "Finishing Mode" (ignoring new standard sparkles).
    3.  Triggers the `ttse__on_finished` event.
    4.  Cleans up children/infusions and removes the Tonic from the Ledger.
*   **`ttse__on_start(self)`**: Called immediately after the Tonic is created and initialized.
*   **`ttse__on_enter(self)`**: Called whenever entering a new state.
*   **`ttse__on_exit(self)`**: Called whenever leaving a state.
*   **`ttse__on_finished(self)`**: Called *during* the shutdown sequence (triggered by `ttsc__finish`). Use this to close resources like files or sockets before the object is destroyed.

---

## 4. Timers and Flow Control

Since Sparkles must be short to keep the "fizz" alive, you cannot use `time.sleep()`. Instead, use the built-in Timers to handle time-bound logic.

```python
from TaskTonic import ttTonic, ttTimerSingleShot

class MyProcess(ttTonic):
    def ttse__on_start(self):
        self.log("Starting process...")
        # Don't sleep! Schedule a sparkle for later.
        ttTimerSingleShot(seconds=2.5, sparkle_back=self.ttsc__continue)

    def ttsc__continue(self, info):
        self.log("2.5 seconds have passed. Continuing...")
        # Done with work? Stop the tonic.
        self.ttsc__finish()
```

---

## 5. Services (Singletons)

The framework uses the `ttLiquid` metaclass to manage Singleton Services effortlessly. A Service is a Tonic that exists only once but can be accessed from anywhere.

**Defining a Service:**
Set the `_tt_is_service` attribute.

```python
class Database(ttTonic):
    _tt_is_service = "db_service" # Unique ID
    
    def __init__(self, **kwargs):
        # Runs ONLY once (first creation)
        super().__init__(**kwargs)
        self.connect_db()

    def _tt_init_service_base(self, context, **kwargs):
        # Runs EVERY time the service is requested
        self.log(f"Accessed by {base.name}")
```

**Using a Service:**
Simply instantiate it. If it exists, you get the running instance.

```python
# In any other Tonic:
my_db = Database() # Returns the existing Singleton
```

---

## 6. Example: The Traffic Light

This example demonstrates `ttLiquid` hierarchy, Sparkles, and State Machine logic.

```python
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot, ttLog

class TrafficLight(ttTonic):
    def ttse__on_start(self):
        self.to_state('red')

    # --- State: RED ---
    def ttse_red__on_enter(self):
        self.log("STOP (Red)")
        ttTimerSingleShot(3, sparkle_back=self.ttsc__next)

    def ttsc_red__next(self, info):
        self.to_state('green')

    # --- State: GREEN ---
    def ttse_green__on_enter(self):
        self.log("GO (Green)")
        ttTimerSingleShot(3, sparkle_back=self.ttsc__next)

    def ttsc_green__next(self, info):
        self.to_state('yellow')

    # --- State: YELLOW ---
    def ttse_yellow__on_enter(self):
        self.log("CAUTION (Yellow)")
        ttTimerSingleShot(1, sparkle_back=self.ttsc__next)

    def ttsc_yellow__next(self, info):
        self.to_state('red')

class SimFormula(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'TrafficSim'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        TrafficLight()

if __name__ == "__main__":
    SimFormula()
```
## `File: docs\CoreConcepts\60 - TaskTonic - Active data store.md`
# TaskTonic Store for Reactive Data Management

<img src="../assets/tasktonic-store.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">


In complex, asynchronous systems, maintaining a consistent, thread-safe application state is one of the greatest challenges. The TaskTonic Store module provides a centralized, hierarchical, and reactive data engine. The module consists of two complementary core components:

1.  **`Store`**: The pure, functional, thread-safe data core. It handles hierarchical storage, lock management, MQTT-style wildcard pub/sub notifications, and atomic updates.
2.  **`Item`**: A highly powerful, cursor-like view/pointer that references a specific path within the `Store`. This enables relative navigation, local mutations, and isolated subscriptions.

Within the framework, the store is exposed as a Singleton Service via the **`ttStore`** class, accessible in your Tonics via `self.ledger.formula`.

---

## 1. Core API & Data Access

TaskTonic provides multiple ways to interact with data, balancing performance and developer convenience. 
Using the store is a bit like using a python dictionary but with hierarchical paths and strongly optimised for storing
and distributing data in een reactive systems.

### 1.1 Dictionary Syntax (`[]`)
For quick, intuitive access, both the `Store` and `Item` objects fully support standard Python dictionary bracket syntax. Reading missing paths natively returns `None` instead of raising a `KeyError`.

```python
# Writing data
store["machine/status"] = "operational"
store["machine/metrics/temperature"] = 22.5

# Reading data
current_status = store["machine/status"]
```

### 1.2 The `get` and `set` Method
If you want to read a value and provide a fallback if the path doesn't exist, use `.get()`.

```python
# Returns 60 if 'machine/metrics/speed' is not found
speed = store.get("machine/metrics/speed", default=60)
```

Setting data, single line or multipole line, can be done using set.

``` python
        # one item
        self.store.set('setting/ui/background', 'blue')
        
        # multiple items by dict
        self.store.set({
            'setting/ui/font', 'arial',
            'setting/ui/font_size', 10,
        })        
        
        # multiple items by tuple of tuples
        self.store.set((
            ('setting/ui/font', 'arial'),
            ('setting/ui/font_size', 10),
        ))
```

### 1.3 Live Links / Pointers (`Item` Cursors)
If you need to read or write to the same path repeatedly (e.g., inside a rapid timer loop), parsing the path string every time via `store["path"]` is inefficient. Instead, use `.at()` to generate an `Item` cursor. 

Storing this `Item` in a variable creates a **live link** to that location in the store. You can read/write its value directly via the `.v` property, or use it to navigate relatively.

```python
from TaskTonic import ttTonic

class DisplayTonic(ttTonic):
    def ttse__on_start(self):
        # Create a cursor to a specific branch
        self.ui_settings = self.ledger.formula.at('settings/ui')
        
        # Dictionary syntax writes relative to the cursor
        self.ui_settings['background'] = 'blue'
        
        # .v property writes directly to the cursor's path
        self.ui_settings.at('opacity').v = 0.8
```

---

## 2. Hybrid Nodes & Smart Lists

Traditional data structures force a node to be either a value (a leaf, like a string) or a container (a map or folder). The TaskTonic Store breaks this dogma by introducing **Hybrid Nodes**.

Every path in the Store can **simultaneously** hold a direct value and harbor sub-paths (children).

### 2.1 The Auto-Increment (`#`)
If you store a standard Python list in the Store and append to it, the Store *will not know* its contents changed, and subscriptions won't trigger. 

TaskTonic uses **Smart Lists** (Dictionaries with auto-incrementing keys). The `#` symbol instructs the Store to scan the active list, determine the highest numeric index, increment it by 1, and create a brand new item. Because every item gets an absolute path (e.g., `users/#1/name`), retrieving deep data is a direct `O(1)` lookup.

### 2.2 The "Sticky" Index (`.`)
The `.` symbol refers to the **most recently generated index** by that specific cursor. This is essential for adding multiple properties to the exact same newly created list item without looking up its generated index.

### 2.3 Creating Valueless Container Lists
Often, you want to create a list of complex objects where the index itself (e.g., `#0`) doesn't hold a direct value (its `.v` is `None`), but acts purely as a container for children. 

To achieve this, simply **target the child property directly during creation**, rather than assigning a value to the `#`.

```python
class UserManager(ttTonic):
    def ttsc__add_users(self):
        users = self.ledger.formula.at('settings/users')

        # METHOD A: Direct assignment to a sub-property
        # Notice how 'users/#0' has no direct value, but acts as a container for 'name'
        users.set('#/name', 'Bob')     # Creates index #0
        users.set('./role', 'Admin')   # Adds 'role' to #0
        users.set('./age', 32)         # Adds 'age' to #0

        # METHOD B: Atomic batch creation using `set()` and a tuple of tuples
        # This prevents triggering multiple incomplete notifications during setup
        users.set((
           ('emp#', 'New Employee'),   # Creates 'emp#0', where .v = 'New Employee'
           ('./department', 'Sales'),
           ('./salary', 50000),
        ))
```

### 2.4 Custom Prefixes (`prefix#`)
As seen in Method B above, you can segregate different entities within the same tree branch by placing text before the `#` symbol. Each prefix maintains its own independent counter.

```python
users.set('guest#/name', 'Charlie')  # Becomes: users/guest#0/name
users.set('guest#/name', 'Dave')     # Becomes: users/guest#1/name
```

---

## 3. Navigating the Tree (`Item` Methods)

Once you hold an `Item` cursor, you can navigate up, down, and across the data tree efficiently.

* **`.parent`**: Returns a new `Item` pointing exactly one level up to the parent container.
* **`.list_root`**: Recursively navigates up the path tree to identify the nearest list-container (identifiable by the `#` syntax). This is crucial within callbacks to find the surrounding entity of a mutated child property.
* **`.key`**: Returns the last segment of the path (e.g., `#0` or `brightness`).

### 3.1 The `children` Iterator
To loop over elements in a container, use the `.children()` method. This returns a memory-efficient **Iterator** of `Item` cursors (lazy evaluation).

```python
sensor_container = store.at("sensors")

# Efficiently iterate without loading the entire tree into memory
for child_item in sensor_container.children():
    if child_item.get("status") == "critical":
        # Handle critical sensor...
        pass
```

---

## 4. Graph Navigation (`StoreLinks`)

While the strict hierarchical tree is great for data integrity (the "Canonical State"), you often need to view data functionally (as a Graph). TaskTonic provides **Symlinks** to solve this via the `.link_to()` method.

### 4.1 Passive Links (`bubble_events=False`)
A passive link acts as a transparent shortcut. It delegates reads and writes to the target. Events bubble up the target's physical tree, but **do not** bubble up the alias tree (preventing UI event storms).

```python
class HouseController(ttTonic):
    def ttse__on_start(self):
        # Canonical state
        self.ledger.formula.set("devices/lamp#/brightness", 0)  # creating lamp#0

        # Functional grouping (Passive link)
        room_lamp = self.ledger.formula.at("house/living/main_light")
        room_lamp.link_to("devices/lamp#0", bubble_events=False)

        # Writing to the alias automatically routes to devices/lamp_1
        room_lamp["brightness"] = 80 
```

### 4.2 Active Links (`bubble_events=True`)
Active links are two-way connections. If the physical target changes, the Store automatically injects a cloned event into the alias tree. **Use this for sensors** where a room-controller needs to be actively notified of hardware triggers happening deep in the device tree.

```python
sensor_alias = self.ledger.formula.at("security/front_door")
sensor_alias.link_to("devices/motion_1", bubble_events=True)
# Now, if devices/motion_1 triggers, the 'security/front_door' path 
# will also bubble the event to any active subscribers.
```

---

## 5. Batch Iteration (`set_each`)

When updating a collection, doing it item-by-item triggers redundant pub/sub notifications. `.set_each()` iterates over children and updates them inside a single atomic `group()`.

```python
class LightingTonic(ttTonic):
    def ttsc__turn_off_all_lamps(self):
        living_room = self.ledger.formula.at("house/living/lamps")
        
        # Resolves through any StoreLinks and fires ONE batch notification
        living_room.set_each("power", "off", prefix="lamp")
```

---

## 6. Advanced Reactivity & Pub/Sub Patterns

The `subscribe` method is the core of TaskTonic's reactivity. It connects data changes to your Tonic's Sparkles (`ttse__`). 

Your event sparkle will receive a list of updates. Each update is a tuple: `(path, new_val, old_val, source_id)`.

### 6.1 Exact vs. Recursive Subscriptions
* **Exact:** Triggers only on the specific path.
* **Recursive:** Triggers on the path AND any of its nested children.

```python
class ProfileWatcher(ttTonic):
    def ttse__on_start(self):
        profile = self.ledger.formula.at("user/profile")
        
        # Trigger on ANY change inside the profile (name, age, settings)
        profile.subscribe(self.ttse__on_profile_update, recursive=True)
```

### 6.2 MQTT-Style Wildcards (`*` and `**`)
Subscribe to dynamic paths without knowing the exact IDs upfront:
* `*` (Single-level): Matches exactly **one** path segment.
* `**` (Multi-level/Recursive): Matches **all** deeper path segments.

```python
class SensorDashboard(ttTonic):
    def ttse__on_start(self):
        store = self.ledger.formula
        
        # Matches 'sensors/kitchen/temp' but NOT 'sensors/kitchen/temp/calibration'
        store.subscribe("sensors/*/temp", self.ttse__on_temp_change)

        # Matches ANY error deep inside the system tree
        store.subscribe("system/**/error", self.ttse__on_system_error)
```

### 6.3 Atomic Snapshots (`extract` and `trigger_now`)
Instead of receiving raw single-property events (which can cause UI stuttering), request a flat dictionary (snapshot). Use `.` inside the extract list to retrieve the value of the base path itself.

* **`extract`**: A list of relative properties to fetch simultaneously.
* **`trigger_now=True`**: Immediately fires a synthetic `init` event upon subscription. Perfect for rendering UI lists without manually polling the Store first.

```python
class UIRenderer(ttTonic):
    def ttse__on_start(self):
        # Subscribe to all widgets, grab their state instantly, and build snapshots
        self.ledger.formula.subscribe(
            "ui/widgets/*", 
            self.ttse__render_widget, 
            extract=[".", "color", "visible"], 
            recursive=True,
            trigger_now=True
        )

    def ttse__render_widget(self, events):
        for path, snapshot, old_val, source in events:
            # Snapshot is safely pre-assembled: {'.': 'button', 'color': 'red', 'visible': True}
            widget_type = snapshot.get(".")
            color = snapshot.get("color")
            self.log(f"Rendering {widget_type} at {path} in {color}")
```

### 6.4 Lifecycle Management (Safe Unsubscribing)
Subscriptions are automatically linked to their `owner` (the instance that created them). **Never** unsubscribe by path; always unsubscribe by `owner` to safely clean up your component.

```python
    def ttse__on_finished(self):
        # Removes ALL subscriptions globally where this Tonic is the owner
        self.ledger.formula.unsubscribe(self)
```

---

## 7. Context Managers (`group` and `source`)

* **`group(source_id=None, notify=True)`**: Batches multiple updates. Listeners are only notified once the block ends.
* **`source(source_id)`**: Tags updates with an origin ID. Vital for bidirectional UI sync to prevent infinite loops (listeners can use `ignore_source` to drop events they caused themselves).

```python
class VolumeSlider(ttTonic):
    def ttse__on_start(self):
        vol_item = self.ledger.formula.at("audio/volume")
        # Listen to the store, but ignore updates tagged with "my_slider"
        vol_item.subscribe(self.ttse__on_external_change, ignore_source="my_slider")

    def ttse__on_user_drag(self, new_value):
        # Write to the store, tagging the source so we don't trigger ourselves
        with self.ledger.formula.source("my_slider"):
            self.ledger.formula.set("audio/volume", new_value)
```

---

## 8. Store API Reference

### Core Methods on `Store`

#### `at(path: str) -> Item`
Returns an `Item` cursor pointing to the specified absolute path.

#### `set(path_or_data: Union[str, dict, tuple], value: Any = None, notify: bool = True) -> Item`
Writes data to the root level. Supports single strings, dictionaries, or tuples of tuples.
* **Returns:** The `Item` cursor of the root.

#### `get(path: str, default: Any = None) -> Any`
Retrieves a value by its absolute path. Resolves through `StoreLink`s automatically.

#### `subscribe(path: Union[str, List[str]], callback: Callable, ignore_source: str = None, recursive: bool = False, exclude: List[str] = None, extract: List[str] = None, trigger_now: bool = False, owner: object = None)`
Registers a listener.
* **`path`**: String or list of absolute paths. Supports `*` and `**` wildcards.
* **`callback`**: The `ttse__` method to execute.
* **`ignore_source`**: Drops events originating from this `source_id`.
* **`recursive`**: If `True`, catches changes in all descendant paths. (Required if using `extract`).
* **`exclude`**: List of absolute sub-paths to ignore.
* **`extract`**: List of relative child properties to return as a flat snapshot dictionary.
* **`trigger_now`**: Immediately fires an `init` event with current data.
* **`owner`**: The object owning this subscription (auto-detected if a bound method is passed).

#### `unsubscribe(target: Union[Callable, object, List[Any]])`
Removes subscriptions. Pass the specific callback function, or the class instance (`self`) to wipe all subscriptions owned by that instance.

---

### Core Methods on `Item` (Cursor)

#### Properties
* **`.v`**: Property to get/set the value of this path. Writing triggers notifications.
* **`.path`**: Absolute path string.
* **`.parent`**: Returns an `Item` pointing one level up.
* **`.list_root`**: Walks up the path tree to find the nearest ancestor created as an auto-increment list item (`#0`, `user#1`). Returns `None` if not in a list.
* **`.key`**: Returns the last segment of the path (e.g., `#0` or `brightness`).

#### `set(data: Union[str, dict, tuple], value: Any = None, notify: bool = True) -> Item`
Writes data relative to this cursor. Fully supports `#` and `.` smart syntax.
* **Returns:** Itself, for method chaining.

#### `get(key: str, default: Any = None) -> Any`
Dictionary-style lookup for children relative to this cursor.

#### `append(prefix: str = None) -> Item`
Explicitly creates a new auto-incremented child item.
* **Returns:** An `Item` pointing to the newly created element.

#### `extend(data_list: List[Any], prefix: str = None) -> Item`
Appends multiple items to the list. If `data_list` contains tuples of length 2, it builds structures instead of flat values.

#### `pop(subpath: str = None) -> Any`
Removes the node (and all descendants) and returns its base value. Operates relative to the cursor if `subpath` is provided.

#### `remove(subpath: str = None)`
Deletes the node and all descendants without returning the value. Safely handles `StoreLink` cleanup (cascading## `File: docs\CoreConcepts\40 - TaskTonic - Depending on your state.md`
# Mastering State Machines in TaskTonic

<img src="../assets/tasktonic-statemachine.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

When building asynchronous systems, keeping track of "what the system is currently doing" can quickly devolve into a nightmare of boolean flags (`is_connecting`, `has_data`, `is_waiting`). 

TaskTonic eliminates this spaghetti code by building a highly efficient **State Machine** directly into the core `ttTonic` class [1-3].

Here is everything you need to know about why, when, and how to use state machines in your Sparkling Programming journey.

---

## 1. Why and When to Use a State Machine?

A State Machine restricts which actions are valid based on the current "mode" (or state) of the application. 

**When to use one:**
*   **Complex Asynchronous Flows:** Like network communication (e.g., `disconnected` -> `connecting` -> `authenticating` -> `ready`) [4-6].
*   **User Interfaces:** Managing wizard flows, disabled/enabled button states, or traffic light simulations [7, 8].
*   **Hardware Control:** Ensuring a motor can only receive a "move" command if it is in an `idle` state, not if it is in an `error` or `moving` state.

**When NOT to use one:**
State machines are **not mandatory** in TaskTonic [2, 9]. 
If your Tonic is simply a data pipeline (e.g., it receives an event, processes it, and spits it out), or a simple standalone worker, a state machine is overkill. You can just use generic "flat" sparkles (e.g., `ttsc__process_data`) without ever calling `to_state()`. If you never call `to_state()`, the Tonic remains in its default stateless mode (`state = -1`) [10, 11].

---

## 2. How it Works: The State Lifecycle

In TaskTonic, you don't need to define massive dictionary structures to configure states. You simply transition between them using `self.to_state('state_name')` [3, 11, 12].

### The Transition Sequence
A critical concept to grasp is that calling `self.to_state()` **does not immediately change the state and interrupt your current code** [11]. Instead, it queues up a highly specific sequence of events that guarantees data integrity.

If you call `self.to_state('new_state')` inside a Sparkle, the exact sequence of execution is [11, 13]:

1.  **Current Sparkle Finishes:** The rest of the code in your current Sparkle executes to completion [11].
2.  **`on_exit` is Triggered:** TaskTonic automatically executes the exit handler for the *old* state [13].
3.  **State Transition:** The internal state variable is updated to the new state [13, 14].
4.  **`on_enter` is Triggered:** TaskTonic automatically executes the enter handler for the *new* state [13].

Because these transitions are scheduled as rapid `extra_sparkles` behind the scenes, the Catalyst executes the entire block seamlessly before grabbing the next user command from the queue [13, 15].

---

## 3. The Queueing Secret: Late State Binding

This is arguably the most powerful feature of TaskTonic’s architecture, and it is vital for concurrency:

**TaskTonic checks the state when a Sparkle is *executed*, NOT when it is placed on the queue [16, 17].**

Imagine a UI with two fast button clicks:
1.  User clicks "Disconnect" (queues `ttsc__disconnect`).
2.  A millisecond later, user clicks "Send Data" (queues `ttsc__send_data`).

If the "Disconnect" Sparkle changes the state from `connected` to `offline`, what happens to the pending "Send Data" Sparkle already sitting in the queue?

When the Catalyst pulls `ttsc__send_data` from the queue, it dynamically checks the Tonic's state *at that exact moment* [16]. Because the state is now `offline`, TaskTonic looks for `ttsc_offline__send_data`. If you haven't defined that, it safely falls back to a generic handler or silently does nothing (`_noop`) [3, 11, 18, 19]. 

You never have to write `if self.is_connected:` inside your Sparkles. The queue inherently protects you from stale asynchronous calls!

---

## 4. The Syntax for State Sparkles

TaskTonic uses smart naming conventions (introspection) to route your Sparkles. You don't need to register anything manually [20-23].

The general syntax pattern is: `prefix_[state]__name` [3, 21, 24].

### A. The Lifecycle Hooks
These are automatically called during transitions [25, 26].
*   `ttse__on_enter(self)`: Called whenever *any* state is entered [25].
*   `ttse__on_exit(self)`: Called whenever *any* state is exited [25].
*   `ttse_<state>__on_enter(self)`: Called *only* when entering a specific state (e.g., `ttse_waiting__on_enter`) [25, 26].

### B. State-Specific Sparkles
You can restrict a command or event so it behaves differently (or only exists) in a specific state [3, 19, 27].

```python
class SmartDoor(ttTonic):
    def ttse__on_start(self):
        self.to_state('locked') # Initial state [28]

    # --- STATE: LOCKED ---
    def ttse_locked__on_enter(self):
        self.log("The door is now locked.") # [28]
        
    def ttsc_locked__open(self):
        self.log("Cannot open. Door is locked!")
        
    def ttsc_locked__unlock(self):
        self.to_state('unlocked')

    # --- STATE: UNLOCKED ---
    def ttsc_unlocked__open(self):
        self.log("Opening the door...")
        self.to_state('open')
        
    def ttsc_unlocked__lock(self):
        self.to_state('locked')
```

### C. The Fallback Chain
What happens if another Tonic calls `door.ttsc__open()` while the door is in an unknown state? TaskTonic follows a strict resolution order [3, 19, 29]:

1.  **Specific:** It looks for `ttsc_<current_state>__open`.
2.  **Generic (Fallback):** If the specific method doesn't exist, it looks for a stateless fallback: `ttsc__open` [19, 30].
3.  **No-Op:** If neither exists, it safely ignores the command using an internal `_noop` (doing nothing) [11, 19]. 

This allows you to write incredibly clean code. Define the generic behavior once, and only override it with a state-specific `ttsc_<state>__name` when the behavior needs to deviate!## `File: docs\CoreConcepts\20 - TaskTonic - Sparkling Programming.md`
# Sparkling Programming: Escape the Async/Threading Nightmare

<img src="../assets/tastonic-sparkling-prog.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

If you are a seasoned Python programmer, you know the pain of concurrency. You’ve wrestled with the viral spread of `async/await` infecting your entire codebase. You’ve debugged multi-threading race conditions, scattered `Lock()` objects everywhere, and watched in horror as your PyQt UI froze because a background thread didn't marshal its signals correctly. 

**TaskTonic asks you to leave those headaches behind.** 

TaskTonic allows you to build applications that handle a large number of seemingly parallel tasks without the complexity of traditional multi-threading [1]. It introduces a paradigm called **Sparkling Programming**. 

Here is why you need to adopt it, how to think in "Sparkles", and why you will never want to go back.

---

## 1. The Core Paradigm: Atomic Immutability

In standard Python, if two threads call `my_object.calculate()` simultaneously, you have a race condition. You need locks. In `asyncio`, if you `await` a database call, another coroutine can jump in and change your object's state while you are waiting.

TaskTonic solves this by breaking work down into **Sparkles**—the smallest, non-interruptible units of work [2]. When you call a Sparkle (e.g., `self.ttsc__do_work()`), it doesn't run immediately. It is placed as a "work order" on a shared queue [3]. The **Catalyst** (the engine) continuously pulls these orders and executes them one by one [3].

### Why is this revolutionary?
Sparkles can be called from *any* thread, but they are always executed by the *same* Catalyst thread [4]. Because execution is sequential per Catalyst, **a Sparkle is atomic** [2]. 

**While you are inside a Sparkle, the state of your Tonic cannot change.** You never have to think about thread-safe programming or data locks inside your Tonic logic [4]. It is completely safe.

---

## 2. Example A: Fluid UIs without `QThread` Boilerplate

Let's look at a PySide6 window. Normally, waiting for 2 seconds or doing a background task freezes the GUI unless you write boilerplate `QThread` and `QRunnable` classes. With TaskTonic, you just use Sparkles and built-in Timers [5]. 

TaskTonic automatically binds UI signals to your Sparkles using the `ttqt__` prefix [6]. 

```python
from TaskTonic.ttTonicStore import ttPysideWindow
from TaskTonic import ttTimerSingleShot

class AppWindow(ttPysideWindow):
    def setup_ui(self):
        # Imagine we setup a simple UI with a button named 'btn_start'
        # and a label named 'lbl_status'
        pass

    def ttse__on_start(self):
        self.lbl_status.setText("Ready")

    # 1. Automatically bound to self.btn_start.clicked!
    def ttqt__btn_start__clicked(self):
        self.log("Button clicked. Starting fake download.")
        self.lbl_status.setText("Downloading...")
        self.btn_start.setEnabled(False)
        
        # 2. Start a non-blocking timer. No time.sleep()!
        ttTimerSingleShot(seconds=2.0, name='download_done')

    # 3. Executes exactly 2 seconds later. UI never freezes.
    def ttse__on_tm_download_done(self, timer_info):
        self.log("Download complete.")
        self.lbl_status.setText("Done!")
        self.btn_start.setEnabled(True)
```
No threads spawned. No signal/slot complex wiring. Just pure, readable, atomic logic.

---

## 3. Example B: The Chunked Iterator (Processing Big Data)

The first question every senior dev asks: *"If a Sparkle can't be interrupted, won't a heavy loop block the Catalyst and freeze my UI?"*

Yes, it will. If a Sparkle takes 5 seconds, the engine halts for 5 seconds. 
**The Sparkling Solution:** You break the heavy work into small, fast chunks using Python's built-in `iter()` and `next()`. You process a few items, and then explicitly queue the *next* Sparkle to continue the work. This allows the Catalyst to process UI clicks or network events in between your data chunks!

```python
from TaskTonic import ttTonic

class BigDataProcessor(ttTonic):
    def ttse__on_start(self):
        # 1. We load a massive dataset (simulated here)
        massive_list = list(range(1_000_000))
        
        # 2. We create an iterator from our data
        self.data_iterator = iter(massive_list)
        self.chunk_size = 5000 
        
    def ttsc__start_heavy_processing(self):
        self.log("Starting heavy job...")
        self.ttsc__process_chunk() # Queue the first chunk

    def ttsc__process_chunk(self):
        """ This sparkle processes a chunk, then queues itself again. """
        try:
            # 3. Process a chunk of data quickly
            for _ in range(self.chunk_size):
                item = next(self.data_iterator)
                self._do_complex_math(item)
                
            # 4. We are not done yet! Put the instruction to process the 
            # NEXT chunk at the back of the Catalyst queue.
            self.ttsc__process_chunk() 
            
        except StopIteration:
            # 5. The iterator is exhausted. We are done!
            self.log("Finished heavy processing smoothly!")
            self.to_state('done')

    def _do_complex_math(self, item):
        pass # Fast math logic here
```
This is incredibly elegant. If the user clicks "Cancel" in the UI, that `ttqt__` event is placed on the queue and will execute *between* your chunks, allowing you to instantly stop the iterator. No `threading.Event()` checks required!

---

## 4. Example C: Tonic Layering (Clean Architecture)

When your logic grows, your code shouldn't become a monolithic mess. TaskTonic encourages **Tonic Layering**. If a task becomes too large for a single Tonic, you can easily divide the work among sub-agents [7]. 

Because Tonics are hierarchical, when a parent creates a child, it becomes the child's "Context" [8]. The parent orchestrates the high-level flow, while the child handles the gritty details. When the parent is finished, the Ledger cleanly shuts down its entire tree of sub-agents automatically [7]. No zombie threads!

```python
from TaskTonic import ttTonic

# --- LOW LEVEL WORKER ---
class NetworkDownloader(ttTonic):
    def ttsc__fetch_data(self, url):
        self.log(f"Connecting to {url} and doing complex socket stuff...")
        # ... complex IP logic ...
        
        # When done, notify the parent (the base) that created us
        self.base.ttse__on_download_complete("{"data": "success"}")

# --- HIGH LEVEL ORCHESTRATOR ---
class UpdateManager(ttTonic):
    def ttse__on_start(self):
        self.log("Initializing Update Manager.")
        
        # 1. Create the worker child. It automatically binds to this parent!
        self.downloader = NetworkDownloader()
        
    def ttsc__run_update(self):
        self.log("Starting update process...")
        self.to_state('downloading')
        
        # 2. Delegate the gritty details to the child
        self.downloader.ttsc__fetch_data("https://api.example.com/update")

    def ttse_downloading__on_download_complete(self, data):
        self.log(f"Update received: {data}. Applying update...")
        self.to_state('finished')
        
        # 3. Finish the parent. The framework automatically kills 
        # the NetworkDownloader child. No resource leaks!
        self.finish() 
```
Look how clean `UpdateManager` is. It reads like a story. The low-level socket handling is completely hidden away in `NetworkDownloader`.

---

## 5. The Golden Rules & The Distiller

To master Sparkling Programming, you only need to remember two rules:
1. **Never block the thread:** Do not use `time.sleep()` or heavy `while True` loops [5]. Use `ttTimerSingleShot` [9] or the Iterator Chunk pattern.
2. **Trust the Queue:** Don't try to call execution methods directly. Let the Catalyst handle the timing [3].

**Are you still worried about performance and execution times?**
TaskTonic includes the **`ttDistiller`**, a specialized Catalyst built exclusively for testing and profiling [10]. The Distiller executes strictly controlled steps and captures a full trace of every Sparkle, including exactly how many milliseconds it took to execute (`at_enter` and `at_exit` timestamps) [10-12]. If you accidentally write a giant, blocking Sparkle, the Distiller will immediately expose the bottleneck in your unit tests.

Stop fighting the Global Interpreter Lock. Stop littering your code with `await`. Pour yourself a TaskTonic and start Sparkling.## `File: docs\CoreConcepts\90 - TaskTonic - Testing in the ttDistiller.md`
# Testing TaskTonic: Mastering the `ttDistiller`

<img src="../assets/tasktonic-distiller.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

Testing software is fundamental, but testing **concurrent, asynchronous systems** is notoriously difficult. In standard threaded or `asyncio` applications, you are at the mercy of the OS scheduler. A test might pass 99 times and fail on the 100th because a background thread executed a millisecond too late. You cannot easily pause time, inspect the exact state mid-execution, or predict the exact order of operations.

TaskTonic eliminates these threading nightmares through its atomic **Sparkles** and sequential queue. But how do you test an asynchronous queue without relying on messy `time.sleep()` calls in your tests?

Enter the **`ttDistiller`**: a specialized, deterministic test engine for TaskTonic.

---

## 1. The Print Statement vs. The Distiller (`self.log` vs `ttDistiller`)

When developing a Tonic, your first instinct is to use `self.log("Doing something...")`. This is excellent for visual debugging. You can watch the execution flow, state changes, and parameter values scroll by in your console.

However, **you cannot write an automated unit test against console output**. 
If someone breaks your Tonic's logic six months from now, `self.log` won't fail a CI/CD pipeline. 

The `ttDistiller` replaces the standard `ttCatalyst` engine during testing. Instead of running a continuous, infinite loop in the background, the Distiller acts as a **manual crank** for the TaskTonic engine. It records every Sparkle, every state change, and every parameter passed, turning your asynchronous application into a completely synchronous, predictable, and heavily inspectable data structure.

---

## 2. Usage: Pytest or Standalone

You don't need a heavy testing framework to use the Distiller, but it integrates perfectly with them.

* **Standalone:** You can write a simple Python script that instantiates a Distiller, runs your Tonic, and asserts conditions using standard `assert` statements.
* **Pytest (Recommended):** You can use `pytest` fixtures to set up your Distiller, run your Tonics through their paces, and generate beautiful test reports. The Distiller runs synchronously in the main thread, making your `pytest` suite incredibly fast and 100% deterministic.

---

## 3. Controlling Time and Execution: Distiller Functions

Because the Distiller owns the queue, you dictate exactly when and how Sparkles are executed. Every time you crank the engine, the Distiller returns a comprehensive `trace` dictionary of everything that happened.

### Step-by-Step Sparkling
Instead of `start_sparkling()`, you tell the Distiller exactly how many items to process from the queue.

```python
# Process exactly ONE Sparkle on the queue, then pause.
trace = distiller.sparkle(sparkle_count=1) 

# Process 5 Sparkles, then pause.
trace = distiller.sparkle(sparkle_count=5)
```
This allows you to freeze the universe mid-execution and inspect the state of your application.

### Condition Triggers (Single-Tonic vs. Multi-Tonic)
Often, you don't know *exactly* how many Sparkles it takes to finish a complex network handshake. You just want to run the engine until a specific event happens. 

**A. Single-Tonic Tests (Direct Parameters)**
If you are unit testing an isolated Tonic, you can pass stop conditions directly as arguments. The Distiller will pause as soon as *any* active Tonic hits the requirement.

```python
# Run the engine until the Tonic enters the 'finished' state
trace = distiller.sparkle(till_state_in=['finished'])

# Run the engine until a specific Sparkle method is called
trace = distiller.sparkle(till_sparkle_in=['ttse__on_data_received'])
```

**B. Integration Tests (The `contract` Dictionary)**
When testing multiple Tonics interacting (e.g., a Client and a Server), the direct parameters fall short because you often need to wait until *both* systems reach a specific state. For this, you use the declarative `contract` dictionary. 

The contract allows you to define strict **AND/OR logic**, assign independent conditions per Tonic, and "probe" internal variables without polluting the global trace. The Distiller uses a `_freeze_value` mechanism to safely create static snapshots of complex objects precisely before and after every Sparkle.

```python
# Tell the Distiller to stop ONLY when the Client is connected 
# AND the Server has registered exactly 1 active connection internally.
integration_contract = {
    'timeout': 5.0,
    'stop_match_count': 'all',  # 'all' = AND logic. Use '1' for OR logic.
    'tonics': {
        'ClientTonic': {
            'till_state_in': ['connected'],
            'probes': ['retry_attempts']  # Snapshot this variable on every sparkle
        },
        'ServerTonic': {
            'probes': ['active_connections'],
            'stop_on_probe': {'active_connections': 1} # Pause when probe hits this value
        }
    }
}

trace = distiller.sparkle(contract=integration_contract)
```

---

## 4. Unpacking the Status Trace (Assertions & Profiling)

Every time `distiller.sparkle()` finishes, it returns a rich status dictionary. This is your primary tool for writing `assert` statements in your tests.

### The Root Trace Elements
The returned dictionary contains metadata about the execution run:

* **`status`**: The final status of the engine (`'running'` or `'catalyst finished'`).
* **`start@` / `end@`**: Absolute timestamps of when the sparkle run started and ended.
* **`stop_condition`**: A list explaining *why* the Distiller paused. 
    * *Values can include:* `'timeout'`, `'sparkle_count'`, `'state_trigger: [state_name]'`, `'sparkle_trigger: [sparkle_name]'`, `'contract_met'`, or `'catalyst finished'`.
* **`contract_details`**: *(Present only when a contract is met)* A rich dictionary containing precise metadata about the matched conditions, including `match_count`, `target_count`, and a `matched_tonics` sub-dictionary detailing exactly which states, sparkles, or probes triggered the success.
* **`sparkle_trace`**: A detailed list of every single Sparkle that was executed.

### The `sparkle_trace` List
Each item in the `sparkle_trace` list is a dictionary describing a single atomic action:

* **`id` / `tonic`**: The ID and name of the Tonic that executed the Sparkle.
* **`sparkle`**: The exact method name (e.g., `ttsc__process_chunk`).
* **`args` / `kwargs`**: The arguments passed into the Sparkle.
* **`source`**: A tuple `(source_tonic, source_sparkle_name, source_id)` indicating who queued this Sparkle.
* **`at_enter` / `at_exit`**: Sub-dictionaries capturing the exact state *before* and *after* the Sparkle. They contain:
    * `@`: The precise timestamp (useful for profiling).
    * `state`: The name of the Tonic's state machine state.
    * `probes`: A dictionary containing the frozen values of any requested probes for this specific Tonic.
    * `sparkling`: (Only in `at_exit`) Boolean indicating if the engine is still running.

### Examples: Writing Assertions with the Trace

**1. Asserting Stop Conditions:**
Ensure your logic stopped because it reached the desired state, not because it timed out.

```python
# Using a contract for an integration test
trace = distiller.sparkle(contract={
    'timeout': 2.0,
    'stop_match_count': 'all',
    'tonics': {'ClientTonic': {'till_state_in': ['authenticated']}}
})

# Check that the distiller stopped successfully
assert 'contract_met' in trace['stop_condition']
assert 'timeout' not in trace['stop_condition']

# Inspect the exact reason the contract was met
details = trace['contract_details']
assert details['match_count'] == 1
assert "state: 'authenticated'" in details['matched_tonics']['ClientTonic']
```

**2. Asserting Probed Data:**
Verify that internal variables were updated correctly during the Sparkle execution.

```python
trace = distiller.sparkle(
    sparkle_count=1, 
    contract={
        'tonics': {
            'ClientTonic': {'probes': ['retry_attempts']}
        }
    }
)

# Grab the last executed sparkle from the trace
last_sparkle = trace['sparkle_trace'][-1]

# Check the probe values before and after the sparkle executed
assert last_sparkle['at_enter']['probes']['retry_attempts'] == 0
assert last_sparkle['at_exit']['probes']['retry_attempts'] == 1
```

**3. Profiling (Finding the "Giant Sparkle"):**
Remember the golden rule of Sparkling Programming: *Never block the Catalyst.*
If you suspect your UI is stuttering, you can check the Distiller's execution times.

```python
trace = distiller.sparkle(till_state_in=['done'])

for action in trace['sparkle_trace']:
    enter_time = action['at_enter']['@']
    exit_time = action['at_exit']['@']
    duration_ms = (exit_time - enter_time) * 1000
    
    # Fail the test if any single Sparkle blocks the thread for more than 50ms!
    assert duration_ms < 50, f"Giant Sparkle detected: {action['sparkle']} took {duration_ms}ms"
```

---

## 5. Mocking Infusions vs. Integration Testing

TaskTonic encourages building hierarchical applications where a Parent Tonic delegates work to Child Tonics (Infusions). The Distiller allows you to test these at multiple levels.

### A. The Unit Test (Mocking Infusions)
If you want to test the Parent's logic independently, you don't want the actual IP connections or databases (the children) to fire. 

1.  **Mock the Infusion:** Override the child Tonic with a mock version.
2.  **Inject Events:** From your test script, you act as the child. You manually queue up events to see how the Parent reacts.

```python
# We are the test. We pretend the child (network socket) received data.
# We inject this directly onto the queue for the parent to process.
parent_tonic.ttse__on_network_data({"status": "ok"})

# Process the injected event
trace = distiller.sparkle(sparkle_count=1)

# Verify the parent handled the mock data correctly
assert parent_tonic.get_current_state_name() == 'processing_data'
```

### B. The Integration Test (Full Hierarchy)
You can also load the parent *and* all its real infusions into the Distiller. 

Because all Tonics in the same Formula share the same Catalyst engine, the Distiller easily manages the master queue for the entire tree. You can trigger a high-level command on the Parent, tell the Distiller to run 50 Sparkles, and watch the entire cascade of commands and events flow down to the children and bubble back up to the parent. It provides a flawless, synchronous integration test of a highly asynchronous system.

---

### Summary
With TaskTonic and the `ttDistiller`, you gain the power to freeze time, inspect memory, profile execution speeds, and lock down your application's behavior with deterministic contracts.## `File: docs\CoreConcepts\30 - TaskTonic - Timers without waiting.md`
# TaskTonic: Timers without waiting 

<img src="../assets/tasktonic-timers.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

In TaskTonic, blocking the execution thread is strictly prohibited. You must **never** block execution using methods like `time.sleep()`, as this will freeze the Catalyst and stop your application from processing its queue. Instead, you must use the framework's built-in timers to keep the system running smoothly.

Timers manage time continuously in the background and trigger a callback (a "sparkle") when their duration or schedule is met.

## 1. Using the TaskTonic timers

When using the timers be aware of the basic principles.

- Create the timer and define the moment of expiration, to fire a timer sparkle.

- Timers are liquid and thus part of the TaskTonic life cycle (its a `ttLiquid` object). Finishing your tonic will automatically finish the timer. Or call `.finish()` to stop and finish.

- For timer control you got two base method `.start()` and `.stop()`, starting and stopping the timer. You're able to cascade this methods like `self.tmr = ttTimerRepeat(seconds=1.5).stop()`. Stopping the time wil not remove them from memory. When you start a timer, the expiration time is recalculated. 

A fundamental rule of TaskTonic timers is that **they start immediately upon instantiation**, creating the object is enough to begin the countdown.

When a timer fires, it needs to trigger an action within your Tonic. You define this action using the `sparkle_back` parameter. However, TaskTonic provides powerful, automatic callback generation if you omit this parameter.

### Automatic Callback Routing (Name-Based Fallback)

If no `sparkle_back` is explicitly provided, the framework uses introspection to find the right event handler in the parent Tonic. It determines the method name based on the `name` property of the timer:

1. **Named Timers (Specific Callbacks):** If you give the timer a specific `name`, the framework automatically prepends `ttse__on_` to it. For example, a timer named `tm_lights_off` will automatically launch the sparkle `ttse__on_tm_lights_off`.
2. **Unnamed Timers (Generic Fallback):** If the timer has no name, it falls back to the generic `ttse__on_timer` method.

```python
from TaskTonic import ttTonic, ttTimerSingleShot

class SmartRoom(ttTonic):
    def ttse__on_start(self):
        # 1. Explicit callback (Highest priority)
        ttTimerSingleShot(2.0, sparkle_back=self.ttsc__specific_action)

        # 2. Named Timer (Auto-routes to ttse__on_tm_lights_off)
        ttTimerSingleShot(10.0, name="tm_lights_off")

        # 3. Unnamed Timer (Auto-routes to generic ttse__on_timer)
        ttTimerSingleShot(5.0)

    def ttsc__specific_action(self, timer_info):
        self.log("The explicit 2-second timer fired!")

    # Auto-generated route for the named timer
    def ttse__on_tm_lights_off(self, timer_info):
        self.log("Turning off the lights!")

    # Generic fallback for all unnamed timers without a sparkle_back
    def ttse__on_timer(self, timer_info):
        self.log("The generic 5-second timer fired!")
```

> *Note: The callback method always receives a `timer_info` argument (usually a dictionary), allowing you to identify exactly which timer triggered the event if multiple timers share the generic fallback.*

---

## 2. Periodic Timers: Relative Time

Standard timers deal with relative durations. You set the seconds to elapse from the moment of creation (or minutes, hours, weeks, months for longer periods).

Beside `.start()` and `.stop()` Periodic timers introduce `.restart()`, to stop the timer, recalculate the expiration time and start again. With `.change_period()`  you can change the period time. This doesn't change the expiration moment, but is used when reloading the time. `self.tmr.change_period(seconds=10).restart()`

### 2.1. `ttTimerRepeat` (Periodic Loops)

Fires periodically based on a relative interval. Ideal for continuous background tasks like polling sensors or refreshing UIs.

```python
# Fires every 1.5 seconds indefinitely
self.poll_timer = ttTimerRepeat(seconds=1.5, name="sensor_poll")

def ttse__on_sensor_poll(self, timer_info):
    pass # Read sensor data
```

### 2.2. `ttTimerSingleShot` and The Watchdog Pattern

A `ttTimerSingleShot` fires only once.  Perfect for timeouts and one time events.  However, using its `.restart()` method, it becomes the perfect tool for building a **Watchdog Timer** to monitor continuous data streams (like IP connections or serial ports).



```python
class ConnectionMonitor(ttTonic):
    def ttse__on_start(self):
        # Start a 10-second watchdog
        self.watchdog = ttTimerSingleShot(10.0, name="connection_timeout")
        self.to_state('collect')

    def ttse_collect__on_data_received(self, data):
        self.log("Data packet received.")
        # process the data

        # Restart the running timer to 10 seconds.
        # As long as data flows within 10s, it never hits 0.
        self.watchdog.restart()

    def ttse__on_connection_timeout(self, timer_info):
        # timer did hit 0, timeout error!!!
        self.log("ALARM: Connection timed out!")
        self.to_state('error')
```
> *Note: when a  single shot expires it fires its sparkle_back and gets finished immediately. So an expired `ttTimerSingleShot` can't be used again. You have to make a new one.*

### 2.3. `ttTimerPausing` 

Pausing timers can also be temporarily halted. If your application enters a state where a running timer should stop counting, you can call `.pause()`. Calling `.resume()` will continue the countdown from the exact point it was paused. You can also instantiate a timer in a paused state by passing `paused=True`.

>*Note: a pausing timer that expires will immediately be paused. You have to `.resume()` in your sparkle_back to use it again*

---

## 3. Scheduled Timers: Absolute Time

While standard timers count seconds, **Scheduled Timers** deal with absolute, real-world time (calendar and clock).

`ttTimerScheduled` is the abstract base class and **cannot be used directly**. Instead, TaskTonic provides  subclasses like `ttTimerEveryWeek` to handle any calendar scenario.

The syntax is extremely flexible, allowing integers, strings (`"august"`, `"monday"`), precise time strings (`"23:59:59"`), and even negative indices to target the "last" occurrence (e.g., `day=-1` for the last day of the month).

### `ttTimerEveryYear`

Executes once a year at a highly specific moment.

```python
# Absolute dates
ttTimerEveryYear(month=2, day=3, hour=8, minute=30) # fires every year at 8:30 at februari 3
ttTimerEveryYear(month="august", day=2, hour=10)

# The 'last' day of a month using negative index
ttTimerEveryYear(month="august", day=-1, hour=10)
ttTimerEveryYear(month="december", day=-1, time_str="23:59:59")

# Complex relational dates (e.g., The last Monday of February)
ttTimerEveryYear(month="february", day="monday", in_week=-1, time_str="9:56:45")
ttTimerEveryYear(month="september", day="saturday", in_week=-1, time_str="8:00:00")

# Week-number based
ttTimerEveryYear(week=1, day="tuesday", hour=8)
ttTimerEveryYear(week=3, day=6, hour=6)
ttTimerEveryYear(week=52, day=6, time_str="23:59:59")
```

### `ttTimerEveryMonth`

Executes once a month. Excellent for monthly reports or billing cycles.

```python
# Specific days within specific weeks (e.g., First Wednesday)
ttTimerEveryMonth(day="wednesday", in_week=1, hour=10)
ttTimerEveryMonth(day="wednesday", in_week=2, hour=10)

# Negative indexing for weeks (e.g., Last Wednesday of the month)
ttTimerEveryMonth(day="wednesday", in_week=-1, hour=10)
ttTimerEveryMonth(day="wednesday", in_week=-6, hour=10) # Failsafe negative boundaries

# Overflow/Underflow weeks
ttTimerEveryMonth(day="tuesday", in_week=5, hour=10)
ttTimerEveryMonth(day="tuesday", in_week=6, hour=10)

# Absolute day of the month
ttTimerEveryMonth(day=27, time_str="13:00:00")

# Relative to the end of the month
ttTimerEveryMonth(day=-1, time_str="13:00:00")  # The very last day
ttTimerEveryMonth(day=-10, time_str="13:00:00") # 10 days before the end of the month
```

### `ttTimerEveryWeek`

Executes weekly on a specific day.

```python
# Using string literals (case-insensitive) or integers (0 = Monday)
ttTimerEveryWeek(day=0, time_str="23:59:59")
ttTimerEveryWeek(day="Tuesday", time_str="23:59:00")
ttTimerEveryWeek(day="wednesday", hour=1)
ttTimerEveryWeek(day="friday", hour=2)
ttTimerEveryWeek(day="saturday", hour=23)
```

### `ttTimerEveryDay`

Executes every day exactly when the system clock hits the target time.

```
ttTimerEveryDay(hour=0)
ttTimerEveryDay(hour=5, minute=30,seconds=0)
ttTimerEveryDay(time_str="12:15:00")
ttTimerEveryDay(hour=19)
```

### `ttTimerEveryHour` & `ttTimerEveryMinute`

Instead of full timestamps, these synchronize with the clock rolling over.

```python
# Triggers at exactly 15 minutes and 0 seconds past every hour (e.g., 01:15, 02:15, 03:15)
ttTimerEveryHour(time_str="15:00")
ttTimerEveryHour(minutes=15)

# Triggers at specific seconds within every minute
ttTimerEveryMinute(second=0)  # Exactly at the top of the minute
ttTimerEveryMinute(second=15)
ttTimerEveryMinute(second=30)
ttTimerEveryMinute(second=2.5) # with seconds, floats are allowed 
```

### Example: Implementing a Scheduled Timer

```python
from TaskTonic.ttTonicStore import ttTimerEveryWeek

class BackupService(ttTonic):
    def ttse__on_start(self):
        self.log("Backup service initialized.")

        # Schedule the backup for every Sunday at 02:00 AM using a named timer
        ttTimerEveryWeek(
            day="sunday",
            hour=2,
            name="weekly_backup"
        )

    # Automatically called by the timer named 'weekly_backup'
    def ttse__on_weekly_backup(self, timer_info):
        self.log("Executing weekly database backup...")
        # Place backup logic here
```## `File: docs\CoreConcepts\70 - TaskTonic - Understanding the ttCatalyst.md`
# The Engine of TaskTonic: Understanding the `ttCatalyst`

<img src="../assets/tasktonic-catalyst.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

If a `Tonic` is a specialized worker on an assembly line, the `ttCatalyst` is the powerful engine that drives the conveyor belt. Its primary and most crucial function is to make Tonics "sparkle" by continuously processing a shared task queue. 

To master TaskTonic, you need to understand what happens inside this engine, how to configure it, and when to spawn new ones.

---

## 1. The Basics: A Catalyst *is* a Tonic

An elegant part of the TaskTonic architecture is that `ttCatalyst` inherits directly from `ttTonic`. 
This means a Catalyst is not just a dumb loop; it is a fully-fledged agent. 

* **It has a lifecycle:** It starts up, can have its own state machine, and shuts down gracefully.
* **It can be used as a Tonic:** You can add your own application logic directly to a custom Catalyst.
* **It cleans up after itself:** When the last Tonic registered to a Catalyst finishes, the Catalyst determines its job is done and automatically initiates its own shutdown sequence.

## 2. The Core: `tt_main_catalyst`

Every TaskTonic application requires at least one Catalyst, known as the **Main Catalyst**. 
* It is strictly identified by the name `tt_main_catalyst` and always holds `id = 0`. 
* Unlike other Catalysts, the Main Catalyst runs its loop in the **main application thread**, blocking the standard execution flow to keep your application alive.
* It is defined in your `ttFormula` via the `creating_main_catalyst()` method. By default, the Formula simply spawns a standard `ttCatalyst`.

## 3. Under the Hood: The `sparkle()` Loop

When you call `start_sparkling()`, the Catalyst enters its main `while` loop. Here is exactly what happens in that loop:

1.  **Timer Check:** It looks at the list of registered timers and calculates `next_timer_expire`—the exact amount of time until the nearest timer needs to fire.
2.  **Queue Wait:** It calls `get(timeout=next_timer_expire)` on its master queue (`catalyst_queue`). The thread goes to sleep, consuming 0% CPU, until either a task arrives or the timer expires.
3.  **Execution:** If a task (work order) is pulled from the queue, it unpacks the payload and calls the internal `_execute_sparkle` method on the target Tonic.
4.  **Extra Sparkles:** After executing the main task, it rapidly drains any `extra_sparkles` (like immediate state transitions: `on_exit` -> `on_enter`) before returning to the start of the loop.

### The Catalyst Queue: What exactly is in it?
The `catalyst_queue` is a standard Python `queue.SimpleQueue`. A single "work order" payload placed on this queue contains:
* The `instance` of the target Tonic.
* The `sparkle` method to execute.
* The `args` and `kwargs` (parameters).
* The `source` (who called this sparkle, tracked via the `ttSparkleStack`).

## 4. Trade-offs: Using Multiple Catalysts

Because any Catalyst created *after* the Main Catalyst automatically spawns its own background thread, you can easily distribute workloads. 

**Why you might want to use your own Catalyst:**
* **Thread Independence:** A new Catalyst runs in its own thread. If the `tt_main_catalyst` is heavily bogged down by UI repaints or a busy Tonic, your independent Catalyst remains hyper-responsive. 

**Why you should be careful (The Drawbacks):**
* **The Deepcopy Penalty (Slower):** TaskTonic guarantees data immutability. If Thread A calls a Sparkle on a Tonic managed by Thread B (a different Catalyst), the framework detects the thread crossing. To prevent race conditions, it uses `copy.deepcopy()` on all `args` and `kwargs` before placing them on the queue. *(Framework detail: The engine smartly skips callables like functions and methods during this process, making cross-thread callback routing highly robust!)* This deep copy is completely safe, but it introduces overhead and is slower than running in the same Catalyst.
* **Thread Bloat:** Spawning a new Catalyst for every single Tonic defeats the purpose of the framework. You fall back into the trap of managing a mess of OS threads.

**Best Practice:** Use a separate Catalyst for a self-contained module or Service that manages a whole tree of sub-Tonics (infusions). Do *not* spawn a new Catalyst for a single, lightweight Tonic.

## 5. Advanced: Creating a Custom Catalyst Class

Because `ttCatalyst` is just a class, you can subclass it. Why would you write your own Catalyst engine?

### A. High-Speed Custom Queues & Interfaces (The `SelectorHandler` Pattern)

Standard queues use `time.sleep` or thread locks to wait. For ultra-fast I/O (like IP communication), you want to use OS-level selectors so your application sleeps efficiently until the operating system detects incoming network data. 

The TaskTonic framework allows you to override the `new_catalyst_queue()` method and the `sparkle()` loop to bridge the gap between Python queues and OS sockets. This is exactly how the built-in `SelectorHandler` (found in `TaskTonic.ttTonicStore.ttIpSockets`) operates.

1. **Custom Queue:** It overrides `new_catalyst_queue` with a `MyNotifyingQueue`. Whenever a standard Sparkle is put onto this queue, it also sends a single byte of data to a hidden internal socket pair (`_queue_filled_notify_channel`).
2. **Custom Loop:** The standard `sparkle()` loop is overridden. Instead of blocking on `queue.get()`, it blocks on `selectors.select()`. 
3. **Result:** The Catalyst wakes up instantly if *either* network data arrives on an IP port, *or* if another Tonic drops a Sparkle into the queue.

```python
import queue
import selectors
from TaskTonic import ttCatalyst

class SelectorHandler(ttCatalyst):
    def new_catalyst_queue(self):
        class MyNotifyingQueue(queue.SimpleQueue):
            def __init__(self, catalyst, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.catalyst = catalyst

            def put(self, item):
                super().put(item)
                try:
                    # Wake up the OS selector by writing to an internal socket pair
                    self.catalyst._queue_filled_notify_channel.send(b'1')
                except Exception:
                    pass

        return MyNotifyingQueue(self)

    def sparkle(self):
        self.sparkling = True
        while self.sparkling:
            # Block at the OS level, not the queue level!
            events = self.selector.select(timeout=next_timer_expire)
            
            for key, mask in events:
                # Handle incoming network I/O events...
                pass
            
            # Check the queue for standard TaskTonic sparkles afterwards
            try:
                instance, sparkle, args, kwargs, source = self.catalyst_queue.get_nowait()
                instance._execute_sparkle(sparkle, *args, **kwargs)
            except queue.Empty:
                pass
```

### B. Heavy Data Processing & The Blocking Problem (e.g., NumPy)

A common concern for developers adopting TaskTonic is: *"If sparkles cannot be interrupted, won't heavy data processing freeze my entire application?"*

First, it is crucial to differentiate between *waiting* and *processing*. Much of what we consider "slow code" is simply waiting for I/O, network responses, or disk access. In TaskTonic, you should **never** block a thread for waiting; you solve this elegantly using Timers or non-blocking selectors (as seen above).

However, true CPU-bound tasks—like running massive `numpy` matrix calculations, image analysis, or complex simulations—**will** legitimately block the thread. If you run this on the Main Catalyst, your entire application (and UI) will freeze.

**The Solution: The Dedicated Worker Catalyst**
You solve this by spinning up a custom `ttCatalyst` specifically for the heavy lifting, acting as an infusion or service to your main application. 

1. The parent Tonic sends a command (e.g., `ttsc__crunch_data`) to the dedicated worker Catalyst.
2. The worker Catalyst executes the sparkle and blocks *its own* thread while `numpy` processes the data. 
3. **The Main Catalyst continues to run flawlessly**, keeping your UI and other Tonics highly responsive.
4. When the math is done, the worker Catalyst sends an event sparkle (e.g., `parent.ttse__on_data_ready(result)`) back to the parent.

```python
from TaskTonic import ttCatalyst, ttTonic

class MathWorker(ttCatalyst):
    def ttsc__crunch_numbers(self):
        self.log("Starting heavy NumPy processing...")
        # This blocks THIS Catalyst's thread, but the Main Catalyst stays responsive!
        # import numpy as np ... heavy math here ...
        result = 42 
        
        # Send the result back to the parent that created us
        self.base.ttse__on_math_done(result)

class MainApp(ttTonic):
    def ttse__on_start(self):
        # Spawns the worker in its own dedicated thread!
        self.worker = MathWorker() 
        self.worker.ttsc__crunch_numbers()
        self.log("Worker is busy, but I am still free to react to UI events!")

    def ttse__on_math_done(self, result):
        self.log(f"The heavy lifting is done! Result: {result}")
```

**Handling Giant Data Blocks (Avoiding the Deepcopy Penalty):**
As mentioned earlier, crossing Catalyst boundaries triggers a `deepcopy` on arguments. Passing a 2GB NumPy array through a Sparkle argument will cause a massive performance hit. 
*The Workaround:* Share large datasets using the `ttStore`, or wrap the data in a custom object/callable that tricks or prevents the deepcopy mechanism. 
*Crucial Warning:* If you bypass the deepcopy to share memory across threads, **you are responsible for strict data discipline**. You absolutely must not mutate that shared data in the parent Tonic while the worker Catalyst is processing it!

**The Dask Alternative (Asynchronous Chunking):**
Because a Sparkle cannot be interrupted while executing, a massive C-level NumPy calculation cannot be easily cancelled or split once started. If your application requires cancelling long calculations or keeping memory usage low, you should consider using **Dask** instead of raw NumPy. Dask chunks arrays and dataframes under the hood. This chunking philosophy fits perfectly with TaskTonic's queue-based approach, allowing your Catalyst to process smaller pieces of data sequentially while remaining highly responsive to cancellation sparkles (`ttsc__cancel`) in between the chunks!## `File: docs\CoreConcepts\50 - Tasktonic - At your service.md`
# TaskTonic Services & Singleton Architecture

<img src="../assets/tasktonic-service.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">


When building complex, asynchronous applications, the need often arises for central components that must be shared across multiple subtasks (Tonics) without corrupting each other's data streams or internal states. In traditional concurrency models, this inevitably leads to global variables or complex, manually written Singleton patterns riddled with error-prone thread-locks.

TaskTonic solves this fundamentally through the runtime architecture of the `ttLiquid` metaclass (`__ttLiquidMeta`), which seamlessly integrates the Singleton pattern at the framework level.

---

## 1. What is a Service?

A Service in TaskTonic is a specialized `ttTonic` class that is managed as a strict Singleton. The framework's metaclass guarantees that exactly one instance of the Service exists throughout the entire lifecycle of the application (within the scope of the active `ttLedger`).

When any Tonic attempts to instantiate a Service, the following mechanism is triggered:
1. **First Call (Creation):** The metaclass intercepts the call, constructs the unique instance via `super().__call__()`, executes `__init__()` and `_tt_post_init_action()` exactly once, and registers the Service in the central `ttLedger` under its unique service name.
2. **Subsequent Calls (Access):** The framework intercepts the creation attempt, identifies the already registered instance in the ledger, and immediately returns this existing reference. The `__init__()` constructor is **not** executed again.

---

## 2. Architectural Use Cases

You should use the Service pattern exclusively for central resources that must be unique and shared across the entire application:
* **Database Managers:** A central connection pool (`DatabaseService`).
* **Hardware Interfaces:** A single-point-of-entry for serial ports or USB controllers to prevent data corruption from concurrent writes.
* **Shared State Spaces:** Central storage facilities like a `DigitalTwin` (built on top of `ttStore`).
* **Network/API Sockets:** Shared HTTP/REST clients or TCP/IP handlers that need to centrally manage authentication tokens and rate-limiting.

---

## 3. Implementing a Service

Building a Service requires a strict separation between one-time configuration parameters (prefixed with `srv_`) and per-access parameters (prefixed with `ctxt_`).

### Step 1: Class-level Identification
A Service defines itself by setting the class attribute `_tt_is_service` to a unique string identifier. This is the key the `ttLedger` uses to register and look up the Singleton.

### Step 2: `__init__` (One-time Setup)
The constructor is executed exclusively during the very first instantiation of the Service.
* Capture parameters here that are crucial for the initial setup (e.g., `srv_db_url`).
* **Strict Framework Rule:** You *must* always accept `**kwargs` and pass them through to `super().__init__(**kwargs)` to avoid breaking internal bootstrapping and context routing.

### Step 3: `_tt_init_service_base` (Per-Access Hook)
Unlike the constructor, `_tt_init_service_base` is executed by the metaclass **upon every access** to the Service (including the very first creation). This is the hook where the Service discovers *who* is currently calling it.
* De eerste positionele parameter die het framework meegeeft is `base` (de Tonic die de Service aanroept).
* Capture dynamic parameters here (e.g., `ctxt_access_level`).

### 🚨 Crucial for Thread-Safety: Registration via the Queue
When a Tonic calls the Service, `_tt_init_service_base` is executed *within the thread of the calling component*. If the Service runs on its own Catalyst (and thus its own OS thread), mutating Service attributes directly inside this method is a direct violation of TaskTonic's thread-safety guarantees!

**The Golden Rule:** Use `_tt_init_service_base` exclusively to place an asynchronous Command Sparkle (`ttsc__`) onto the Service's own queue. Let the Service handle the administration in its own thread scope.

```python
from TaskTonic import ttTonic


class SharedDatabaseService(ttTonic):
    # The unique framework key for the Ledger
    _tt_is_service = "SharedDatabaseService"

    def __init__(self, srv_db_url, **kwargs):
        """
        Executed EXACTLY once during the very first call.
        """
        super().__init__(**kwargs)
        self.db_url = srv_db_url
        self.authorized_clients = {}
        self.log(f"Database connected at: {self.db_url}")

    def _tt_init_service_base(self, base, ctxt_access_level="read", **kwargs):
        """
        Executed ON EVERY CALL to the service.
        WARNING: This runs in the thread of the CALLER (base)!
        Forward the data directly to the safe Catalyst queue via a sparkle.
        """
        if base is None:
            return

        # Place the registration safely on this service's own queue
        self.ttsc__register_client(base, ctxt_access_level)

    def ttsc__register_client(self, client_instance, access_level):
        """
        Runs SAFELY within the Service Catalyst's own thread.
        """
        client_id = client_instance.id
        self.authorized_clients[client_id] = {
            "instance": client_instance,
            "level": access_level
        }
        self.log(f"Client {client_id} registered with level: {access_level}")
```

---

## 4. Consuming a Service

A consumer Tonic interacts with a Service by simply instantiating the class. The framework handles the de-duplication behind the scenes.

```python
from TaskTonic import ttTonic


class DataAnalyzer(ttTonic):
    def ttse__on_start(self):
        # Request the database. Provide srv_ args in case we are the first.
        # Provide ctxt_ args specific to our own session.
        self.database = SharedDatabaseService(
            srv_db_url="postgresql://localhost:5432/prod",
            ctxt_access_level="write"
        )

    def ttsc__process_measurement(self, measurement_data):
        # Communicate via the service's asynchronous command queue
        self.database.ttsc__write_record(measurement_data)
```

---

## 5. Advanced Pattern: Decoupling via Service Base Classes

In a clean software architecture, you often want to decouple components from specific implementation details. For example: a Tonic needs a `ConnectionService`, but it shouldn't matter to that Tonic whether this runs via an `IpConnectionService` or a `BluetoothConnectionService`.

TaskTonic supports this by allowing you to define an abstract base class as the Service interface, while you start the concrete implementation under the exact same service name in the `ttFormula`.

### 1. Define the Interface (The Base Class)
```python
from TaskTonic import ttCatalyst


class ConnectionService(ttCatalyst):
    """
    The universal contract class. Consumers will instantiate this class.
    """
    _tt_is_service = "central_connection_service"

    def ttsc__send_packet(self, payload):
        pass
```

### 2. Build the Concrete Implementation
```python
class IpConnectionService(ConnectionService):
    """
    The actual network implementation.
    """
    def __init__(self, srv_host, srv_port, **kwargs):
        super().__init__(**kwargs)
        self.host = srv_host
        self.port = srv_port
        self.to_state("disconnected")

    def ttsc_disconnected__send_packet(self, payload):
        self.log("Error: Cannot send data, socket is closed!")

    def ttsc_connected__send_packet(self, payload):
        # Low-level IP write logic here...
        self.log(f"Data sent to {self.host}: {payload}")
```

### 3. The Binding in the Formula and Consumer
The consumer remains completely decoupled and only requests the base interface. The `ttFormula` determines at startup which concrete variant is loaded into the ledger.

```python
class ProductionTonic(ttTonic):
    def ttse__on_start(self):
        # Request the SERVICE via the abstract base class
        self.network = ConnectionService()
        self.network.ttsc__send_packet("Test message")


class MyApplication(ttFormula):
    def creating_starting_tonics(self):
        # 1. Start the CONCRETE service first.
        # This registers itself under 'central_connection_service'
        IpConnectionService(srv_host="10.0.0.15", srv_port=8080)

        # 2. Start the consumers.
        ProductionTonic()
```

---

## 6. Lifecycle and Teardown Mechanism

Services feature a unique, automated cleanup mechanism tied to their active users.

### Automatic Infusion Tracking
When an existing Service is requested again anywhere in the application, the metaclass intercepts this and performs the following administrative steps:
1. The calling Tonic (`base`) is automatically appended to the Service's internal `service_bases` list (`tonic.service_bases.append(base)`).
2. The Service is registered as an active dependency on the caller via `base._tt_add_infusion(tonic)`.

> **Architecture Note (First Creation Isolation):**
> By design, when a Service is created for the *very first time* by a Tonic, the framework explicitly sets its `base` to `None`. This isolates the new Service from the caller's lifecycle, preventing the Service from being destroyed if the instantiating worker finishes early. On all *subsequent* calls, the caller is properly registered as an active dependency.

### Graceful Teardown Flow
Because the Service accurately tracks which Tonics depend on it, it knows exactly when it is no longer needed. When a consumer Tonic ends its lifecycle and calls `finish()`, a cascade effect triggers within `ttTonic.py`:

1. The finishing consumer Tonic executes its `_ttss__on_finished` routine.
2. It iterates through its active `infusions` and calls `ttsc__finish()` on the Service.
3. The Service intercepts this in its own `ttsc__finish()` method and recognizes that the caller is part of its `service_bases`.
4. The Service removes this specific client from its list: `self.service_bases.remove(calling_tonic)`.
5. **The Closure:** The Service checks its remaining dependencies. If there are *no* active components left (`len(self.service_bases) <= 0`), the Service concludes its job is done. It triggers its own teardown sequence, calling `ttse__on_service_base_completed` to notify listeners, stops its state machine, and permanently removes itself from the `ttLedger`.
## `File: docs\TheToolbox\120 - TaskTonic - Networking and Sockets.md`
# TaskTonic Networking (`ttNetworking`)

The `ttNetworking` module provides a robust, non-blocking, asynchronous network stack fully integrated into the TaskTonic framework. It allows you to build highly concurrent network applications—like chat servers, IoT brokers, or webhook listeners—without writing a single line of traditional threading or `asyncio` boilerplate.

---

## 1. The Sockets API

For the standard developer, the networking module exposes simple, state-aware handlers for TCP, UDP, and HTTP protocols. These handlers are native `ttTonic` objects and communicate exclusively via Sparkles.

### TCP Communication (`TcpSocketHandler`)
The TCP handler can act as both a client and a server. It automatically manages connection states, buffering, and background reconnection.

**Example: A Simple TCP Echo Server**
```python
from TaskTonic import ttTonic
from TaskTonic.ttTonicStore.ttNetworking import TcpStrSocketHandler

class EchoServer(ttTonic):
    def ttse__on_start(self):
        self.log("Starting Echo Server on port 5555...")
        self.net = TcpStrSocketHandler(as_server=True, host='0.0.0.0', port=5555)
        self.to_state('listening')

    def ttse__on_socket_connected(self, addr):
        self.log(f"Client connected from {addr}")

    def ttse__on_socket_data(self, data):
        self.log(f"Received: {data}")
        # Echo the data back to the client
        self.net.ttsc__send_data(f"ECHO: {data}")
```

### UDP Communication (`UdpSocketHandler`)
UDP is connectionless and stateless. It is ideal for high-speed, loss-tolerant streams or simple "Ping-Pong" broadcasts.

```python
from TaskTonic import ttTonic
from TaskTonic.ttTonicStore.ttNetworking import UdpDictSocketHandler

class PingClient(ttTonic):
    def ttse__on_start(self):
        self.udp = UdpDictSocketHandler(as_server=False)
        self.to_state('ready')

    def ttse_ready__on_enter(self):
        # Send a JSON dictionary over UDP
        self.udp.ttsc__send_data({"action": "ping"}, ('127.0.0.1', 55555))

    def ttse__on_udp_data(self, data, addr):
        self.log(f"Received reply from {addr}: {data}")
```

### HTTP Webhooks
TaskTonic includes lightweight, asynchronous HTTP handlers designed specifically for IoT webhooks (like Shelly buttons) or quick REST API calls.
* **`HttpServerHandler`**: Listens for incoming GET/POST requests and auto-replies with `200 OK`.
* **`HttpClientHandler`**: Sends asynchronous HTTP requests to endpoints.

---

## 2. Extending Sockets (Serialization & Fragmentation)

Network streams (especially TCP) do not guarantee that your data arrives in neat, complete packages. A 10KB JSON payload might arrive in chunks, or two rapid messages might be glued together.

TaskTonic provides a clean interface to solve this. You do not modify the base `TcpSocketHandler`. Instead, you subclass it and override two specific methods: `send_data_conversion` and `rcv_data_conversion`.

### Example: Building a Dictionary Socket (`TcpDictSocketHandler`)
Here is how you extend a socket to automatically pack and unpack Python dictionaries safely over a TCP stream using `pickle` and a 4-byte length header (to handle fragmentation).

```python
import struct
import pickle
from TaskTonic.ttTonicStore.ttNetworking import TcpSocketHandler

class TcpDictSocketHandler(TcpSocketHandler):
    def send_data_conversion(self, dict_data):
        """Packs a dictionary into bytes with a 4-byte length prefix."""
        if not isinstance(dict_data, dict):
            raise TypeError('Data must be a dict')
            
        pdict = pickle.dumps(dict_data)
        # Prefix the payload with its exact length
        return struct.pack('!I', len(pdict)) + pdict

    def rcv_data_conversion(self, bdata):
        """Unpacks the byte stream, resolving TCP fragmentation."""
        dicts = []
        self.rcv_buf += bdata
        
        while len(self.rcv_buf) > 4:
            # Check the expected length of the upcoming payload
            plen = struct.unpack('!I', self.rcv_buf[:4])[0]
            
            if len(self.rcv_buf) < plen + 4:
                # Payload is incomplete (fragmented). Wait for more data.
                break 
                
            # We have a full payload! Extract it and load the dict.
            dicts.append(pickle.loads(self.rcv_buf[4 : plen + 4]))
            
            # Slice the buffer to process the next potential message
            self.rcv_buf = self.rcv_buf[plen + 4 :]
            
        # Return the list of completed dictionaries to the framework
        return dicts
```

---

## 3. Developer Notes: The `SelectorService` Engine

*(This section details the internal mechanics of `ttNetworking`. Standard users do not need to interact with this layer.)*

Under the hood, all socket handlers delegate their raw OS-level operations to the `SelectorService`. This service is a specialized `ttCatalyst` that runs in the background. Its design solves several critical concurrency challenges inherent to Python.

### The Dual-Wait Problem
A standard TaskTonic `ttCatalyst` executes a `while` loop that sleeps efficiently by calling `queue.get(timeout=next_timer)`. It only wakes up when a Sparkle is queued or a timer expires.

However, network sockets require the application to wait for the Operating System (via `selectors.select()`). Python cannot efficiently block a single thread on *both* a Queue and an OS Selector simultaneously without relying on heavy polling (busy-waiting).

### The Dummy Socket Solution
To solve this, the `SelectorService` overrides the core Catalyst loop to block exclusively on the OS `selector`. 
To ensure the Catalyst still processes normal TaskTonic Sparkles, it uses a custom `MyNotifyingQueue`. Whenever a Sparkle is put into this queue, it writes a single byte (`b'1'`) to an internal, hidden dummy socket pair (`_queue_filled_notify_channel`). This instantly wakes up the OS selector, allowing the Catalyst to process the Sparkle queue.

### Atomic Concurrency Benefits
By forcing all network I/O to run inside the *same* Catalyst thread, TaskTonic's uninterruptible Sparkle mechanism applies to network traffic. There are no race conditions between sending data, disconnecting, and receiving data. Locks (`threading.Lock`) are entirely obsolete.

### Level-Triggered Events vs. Edge-Triggered
A crucial architectural decision was made regarding how data is read. OS Selectors in Python are **Level-Triggered** (not Edge-Triggered). This means the OS will constantly scream *"I have data!"* as long as the receive buffer is not empty.

If TaskTonic simply placed a `ttse__on_data_ready` Sparkle on the queue when the selector fired, the selector might fire hundreds of times before the Catalyst actually executes that Sparkle and drains the OS buffer.

**The Solution:** The `SelectorService` reads the data *immediately* inside the active `select()` loop. This instantly drains the OS buffer, silencing the selector. The raw byte data is then passed directly as a parameter into the Sparkle work order (`rd_sparkle(data)`). 

Because the `SelectorService` Catalyst reads the data and executes the Sparkle within the exact same thread, the data can be passed safely by reference without triggering TaskTonic's cross-thread `copy.deepcopy()` overhead. This results in incredibly fast, memory-efficient networking.## `File: .github\workflows\00_publish.yml`
```yaml
name: Publish TaskTonic to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m build
        twine upload dist/*

```

## `File: .github\workflows\10_webdos.yml`
```yaml
name: Deploy TaskTonic Documentation

on:
  push:
    branches:
      - master
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mkdocs-material pymdown-extensions

      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force

```

## `File: .github\workflows\50_tests.yml`
```yaml
name: TaskTonic Tests

# Trigger the workflow on push or pull request events for the master branch
on:
  push:
    branches: [ "master" ]
  pull_request:
    branches: [ "master" ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies and TaskTonic
        run: |
          python -m pip install --upgrade pip
          pip install pytest
          # Install the package locally in editable mode so pytest can find it
          pip install -e . 

      - name: Run Distiller and Core tests
        run: |
          pytest testing/

```

