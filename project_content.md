# Introduction
This file contains all source code and documentation for the project.
       All markdown documents are add, all other files are wrapped in formatting blocks.
    

---

# Project Structure

```text
TaskTonic/
    readme.md
    pyproject.toml
    collect_for_nlm.py
    project_content.md
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
    testing/
        test_core.py
        conftest.py
        test_distiller.py
        test_store.py
    _documents/
        TaskTonic  - The introduction.md
        TaskTonic - Sparkling Programming.md
        TaskTonic - Understanding the ttCatalyst.md
        TaskTonic - Timers without waiting.md
        TaskTonic - Testing in the ttDistiller.md
        TaskTonic - Depending on your state.md
        Tasktonic - At you Service.md
        TaskTonic - Active data store.md
        old_documents_not_matching_the_code/
            ttDataShare.md
            ttTonic.md
            ttCatalyst.md
            _introduction.md
            Tonic Services.md
            finisching flow.md
            ttStore.md
            developer documentation.md
```

---

# File Contents

## `File: readme.md`
# What is TaskTonic?

## Philosophy & Metaphor

TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model.

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

No documentation, no framework. Look into the **\_documents** map and read it all.## `File: pyproject.toml`
```toml
[project]
name = "TaskTonic"
version = "0.2.0"
authors = [
    { name = "Peter", email = "208develop@gmail.com" },
]
description = """ \
TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model.
It allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) \
without the race conditions and headaches of traditional multi-threading. \
"""

readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/208develop/TaskTonicc"
Issues = "https://github.com/208develop/TaskTonic/issues"
Documentation = "https://github.com/208develop/TaskTonic/tree/master/_documents"
```

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
        self.log(system_flags={'states': self._index_to_state, 'sparkles': self.sparkles})

    def _noop(self, *args, **kwargs):
        """A do-nothing method used as a default for unbound sparkles."""
        pass

    def to_state(self, state):
        """
        Requests a state transition. The change is handled by the _execute_sparkle
        method after the current sparkle finishes.

        :param state: The name (str) or index (int) of the target state. When target == -1, stop machine stops
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
        if system_flags: self._log.setdefault('sys', {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            self._log['duration'] = time.time() - self._log['start@']
            self._log_push(self._log)
            self._log = None

    def _log_quiet(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the QUIET log mode."""
        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault('sys', {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            if 'log' in self._log or 'sys' in self._log:
                self._log_push(self._log)
            self._log = None

    def _log_off(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the OFF log mode (lifecycle only)."""
        if system_flags:
            if self._log is None: self._log = {'id': self.id, 'start@': time.time()}
            self._log.setdefault('sys', {}).update(system_flags)
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
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        self._store.remove_item(target)

    def pop(self, subpath: str = None) -> Any:
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        val = self._store.get_value(target)
        self._store.remove_item(target)
        return val

    def append(self, prefix: str = None) -> 'Item':
        """Creates a new child item with an auto-incrementing index (e.g. #0, #1)."""
        return self._store.create_list_item(self._path, prefix)

    def extend(self, data_list: List[Any], prefix: str = None) -> 'Item':
        """Appends multiple items to the list."""
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

## `File: TaskTonic\ttLoggers\__init__.py`
```python
from .ttScreenLogger import ttLogService, ttScreenLogService
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

        print(f"[{l_time_start}] TaskTonic log for '{prj['name'].v}', started at {time.strftime("%H:%M:%S", lt)}")
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

        if log.get('sys',{}).get('created', False):

            while len(self.log_records) <= l_id:
                self.log_records.append(None)
            self.log_records[l_id] = log.copy()

        sparkle_name = log.get('sparkle', '')
        sparkle_state_idx = log.get('state', -1)

        if sparkle_name == '_ttinternal_state_change_to':
            sparkle_name = f" TO STATE [{self.log_records[l_id]['sys']['states'][log['sys']['new_state']]}]"

        ts = log['start@']
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        header = f"{self.log_records[l_id]['sys']['name']}"
        if sparkle_state_idx >= 0:
            header += f"[{self.log_records[l_id]['sys']['states'][sparkle_state_idx]}]"
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

## `File: TaskTonic\ttTonicStore\__init__.py`
```python
from .ttDistiller import ttDistiller
from .ttPyside6Ui import ttPyside6Ui
from .ttPysideWidget import ttPysideWindow, ttPysideWidget
from .ttTkinterUi import ttTkinterUi
from .ttTkinterWidget import ttTkinterFrame
from .ttTimerScheduled import (ttTimerEveryYear, ttTimerEveryMonth, ttTimerEveryWeek, ttTimerEveryDay,
                               ttTimerEveryHour, ttTimerEveryMinute)
from .ttStore import ttStore


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
                    instance._execute_sparkle(sparkle, *args, **kwargs)
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


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

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
# test_distiller.py
import pytest
import time
from TaskTonic import ttTonic, ttFormula, ttTimerSingleShot
from TaskTonic.ttTonicStore import ttDistiller


# --- Definitie van de Device Under Test (DUT) ---
class DUT(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.tm = None

    def ttse__on_start(self):
        self.to_state('init')

    def ttse_init__on_enter(self):
        self.to_state('paused')

    def ttsc_paused__start_timer(self):
        # Start een timer van 2 seconden
        self.tm = ttTimerSingleShot(seconds=2)
        self.to_state('wait_on_timer')

    def ttse_wait_on_timer__on_timer(self, info):
        # Wordt aangeroepen als de timer afloopt (default handler)
        self.to_state('finished_cycle')

    def ttse_finished_cycle__on_enter(self):
        pass  # empty state

    def ttsc__dut_finish(self):
        self.ttsc__finish()


# --- Definitie van de Test Formula ---
class TestRecipe(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/log/to': 'off',  # Geen output tijdens tests
            'tasktonic/log/default': 'full',
        }

    def creating_main_catalyst(self):
        # We gebruiken de Distiller in plaats van de standaard Catalyst
        ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        DUT(name="MyDevice")


# --- De Test ---
def test_dut_flow_with_timer():
    # 1. Initialiseer de applicatie
    recipe = TestRecipe()

    # 2. Haal de referenties op via de Ledger
    ledger = recipe.ledger
    distiller = ledger.get_tonic_by_name('tt_main_catalyst')
    dut = ledger.get_tonic_by_name("MyDevice")

    assert isinstance(distiller, ttDistiller)
    assert dut is not None
    assert set(dut._index_to_state) == {'init', 'paused', 'wait_on_timer', 'finished_cycle'}

    # 3. STAP 1: Start de distiller en run tot de DUT in 'paused' komt.
    # Dit test de initiële flow: on_start -> init -> paused
    status = distiller.sparkle(timeout=1, till_state_in=['paused'])

    # Verifieer dat we gestopt zijn vanwege de state trigger, niet door timeout
    stop_conditions = status.get('stop_condition', [])
    assert 'state_trigger: [paused]' in stop_conditions
    assert dut.get_current_state_name() == 'paused'

    # 4. STAP 2: Vuur handmatig een commando af (start timer)
    dut.ttsc__start_timer()

    # Run de distiller tot de status verandert naar 'wait_on_timer'
    status = distiller.sparkle(timeout=1, till_state_in=['wait_on_timer'])
    assert dut.get_current_state_name() == 'wait_on_timer'

    # 5. STAP 3: Wacht op de timer.
    # De Distiller spoelt de tijd automatisch vooruit als er geen sparkles zijn,
    # maar er wel actieve timers zijn.
    status = distiller.sparkle(timeout=5, till_sparkle_in=['ttse__on_timer'])

    # Check of de timer event daadwerkelijk is afgegaan
    assert 'sparkle_trigger: [ttse__on_timer]' in status.get('stop_condition', [])

    # Check of de logica na de timer de state heeft aangepast
    assert dut.get_current_state_name() == 'finished_cycle'

    # finish DUT
    dut.ttsc__dut_finish()
    status = distiller.sparkle(timeout=.5)
    assert 'catalyst finished' in status['stop_condition']
    assert dut.id == -1

    # 6. Opruimen
    distiller.finish_distiller()
    assert distiller.sparkling == False

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
from TaskTonic.ttTonicStore import Store, Item, ttStore


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
        return MockStore()

    def test_subscribe_and_callback(self, store):
        """
        Test if subscribers receive the correct updates.
        """
        received_updates = []

        def on_update(updates):
            # updates is expected to be a list of tuples: (path, new, old, source)
            received_updates.extend(updates)

        # Subscribe to the 'sensors' path
        store.subscribe('sensors', on_update)

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

        store.subscribe('config', callback)

        with store.group():
            store.set([
                ('config/a', 1),
                ('config/nested/b', 2),  # Should also trigger 'config' listener
                ('outside', 3)
            ])

        assert updates_received == 2

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
```

## `File: _documents\TaskTonic  - The introduction.md`
# TaskTonic Framework: Developer Documentation

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

*   **Specific:** `ttsc_idle__start()` — Only runs if the Tonic is in the `idle` state.
*   **Generic:** `ttsc__start()` — Runs in any state (unless a specific version exists).
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

    def _init_service(self, context, **kwargs):
        # Runs EVERY time the service is requested
        self.log(f"Accessed by {context.name}")
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
## `File: _documents\TaskTonic - Sparkling Programming.md`
# Sparkling Programming: Escape the Async/Threading Nightmare

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

Stop fighting the Global Interpreter Lock. Stop littering your code with `await`. Pour yourself a TaskTonic and start Sparkling.## `File: _documents\TaskTonic - Understanding the ttCatalyst.md`
# The Engine of TaskTonic: Understanding the `ttCatalyst`

If a `Tonic` is a specialized worker on an assembly line, the `ttCatalyst` is the powerful engine that drives the conveyor belt [1]. Its primary and most crucial function is to make Tonics "sparkle" by continuously processing a shared task queue [1]. 

To master TaskTonic, you need to understand what happens inside this engine, how to configure it, and when to spawn new ones.

---

## 1. The Basics: A Catalyst *is* a Tonic

An elegant part of the TaskTonic architecture is that `ttCatalyst` inherits directly from `ttTonic` [2, 3]. 
This means a Catalyst is not just a dumb loop; it is a fully-fledged agent. 

*   **It has a lifecycle:** It starts up, can have its own state machine, and shuts down gracefully.
*   **It can be used as a Tonic:** You can add your own application logic directly to a custom Catalyst [2, 3].
*   **It cleans up after itself:** When the last Tonic registered to a Catalyst finishes, the Catalyst determines its job is done and automatically initiates its own shutdown sequence [4, 5].

## 2. The Core: `tt_main_catalyst`

Every TaskTonic application requires at least one Catalyst, known as the **Main Catalyst**. 
*   It is strictly identified by the name `tt_main_catalyst` and always holds `id = 0` [6, 7]. 
*   Unlike other Catalysts, the Main Catalyst runs its loop in the **main application thread**, blocking the standard execution flow to keep your application alive [6, 8].
*   It is defined in your `ttFormula` via the `creating_main_catalyst()` method. By default, the Formula simply spawns a standard `ttCatalyst` [7, 9].

## 3. Under the Hood: The `sparkle()` Loop

When you call `start_sparkling()`, the Catalyst enters its main `while` loop [6]. Here is exactly what happens in that loop:

1.  **Timer Check:** It looks at the list of registered timers and calculates `next_timer_expire`—the exact amount of time until the nearest timer needs to fire [10].
2.  **Queue Wait:** It calls `get(timeout=next_timer_expire)` on its master queue (`catalyst_queue`). The thread goes to sleep, consuming 0% CPU, until either a task arrives or the timer expires [10].
3.  **Execution:** If a task (work order) is pulled from the queue, it unpacks the payload and calls the internal `_execute_sparkle` method on the target Tonic [11, 12].
4.  **Extra Sparkles:** After executing the main task, it rapidly drains any `extra_sparkles` (like immediate state transitions: `on_exit` -> `on_enter`) before returning to the start of the loop [11].

### The Catalyst Queue: What exactly is in it?
The `catalyst_queue` is a standard Python `queue.SimpleQueue` [13]. A single "work order" payload placed on this queue contains [10, 14]:
*   The `instance` of the target Tonic.
*   The `sparkle` method to execute.
*   The `args` and `kwargs` (parameters).
*   The `source` (who called this sparkle, tracked via the `ttSparkleStack`).

## 4. Trade-offs: Using Multiple Catalysts

Because any Catalyst created *after* the Main Catalyst automatically spawns its own background thread, you can easily distribute workloads [8, 15]. 

**Why you might want to use your own Catalyst:**
*   **Thread Independence:** A new Catalyst runs in its own thread. If the `tt_main_catalyst` is heavily bogged down by UI repaints or a busy Tonic, your independent Catalyst remains hyper-responsive. 

**Why you should be careful (The Drawbacks):**
*   **The Deepcopy Penalty (Slower):** TaskTonic guarantees data immutability. If Thread A calls a Sparkle on a Tonic managed by Thread B (a different Catalyst), the framework detects the thread crossing. To prevent race conditions, it uses `copy.deepcopy()` on all `args` and `kwargs` before placing them on the queue [16-18]. This deep copy is completely safe, but it introduces overhead and is slower than running in the same Catalyst.
*   **Thread Bloat:** Spawning a new Catalyst for every single Tonic defeats the purpose of the framework. You fall back into the trap of managing a mess of OS threads.

**Best Practice:** Use a separate Catalyst for a self-contained module or Service that manages a whole tree of sub-Tonics (infusions). Do *not* spawn a new Catalyst for a single, lightweight Tonic.

## 5. Advanced: Creating a Custom Catalyst Class

Because `ttCatalyst` is just a class, you can subclass it. Why would you write your own Catalyst engine?

### A. Interfacing with Blocking/Long-Running Processes (e.g., Numpy)
Sometimes you *have* to run a Sparkle that takes a long time (like a heavy Numpy calculation). In a shared Catalyst, this freezes all other Tonics. 
By creating a dedicated custom Catalyst just for this math module, you can explicitly *allow* long-running Sparkles. The main application remains fluid. 
*(Warning: Remember that if a Sparkle takes 5 seconds, a `finish()` command sent to that Tonic will also be delayed by up to 5 seconds because it waits in the same queue!)*

### B. High-Speed Custom Queues & Interfaces (The `SelectorHandler` Pattern)
Standard queues use `time.sleep` or locks to wait. For ultra-fast I/O (like IP communication), you want to use OS-level selectors [19]. 

The TaskTonic framework allows you to override the `new_catalyst_queue()` method [13, 20]. You can inject a custom queue that bridges the gap between Python queues and OS sockets.

**The IP Communication Example:**
In `examples/ip_communicatie.py`, a custom Catalyst named `SelectorHandler` is used [21]: 
1.  **Custom Queue:** It overrides `new_catalyst_queue` with a `MyNotifyingQueue` [20]. Whenever a Sparkle is put onto this queue, it also sends a single byte of data to a hidden internal socket (`_queue_filled_notify_channel`) [20].
2.  **Custom Loop:** The standard `sparkle()` loop is overridden. Instead of blocking on `queue.get()`, it blocks on `selectors.select()` [22]. 
3.  **Result:** The Catalyst sleeps efficiently at the OS level. It wakes up instantly if *either* network data arrives on an IP port, *or* if another Tonic drops a Sparkle into the `MyNotifyingQueue` [19, 21, 22]. 

This demonstrates the ultimate power of TaskTonic: you can bend the engine entirely to your architectural needs without rewriting the underlying Tonic logic.## `File: _documents\TaskTonic - Timers without waiting.md`
# TaskTonic: Timers without waiting 

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

    def ttse__on_data_received(self, data):
        self.log("Data packet received.")
        # Reset the timer. As long as data flows within 10s, it never hits 0.
        self.watchdog.restart()

    def ttse__on_connection_timeout(self, timer_info):
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
```## `File: _documents\TaskTonic - Testing in the ttDistiller.md`
# Testing TaskTonic: Mastering the `ttDistiller`

Testing software is fundamental, but testing **concurrent, asynchronous systems** is notoriously difficult. In standard threaded or `asyncio` applications, you are at the mercy of the OS scheduler. A test might pass 99 times and fail on the 100th because a background thread executed a millisecond too late. You cannot easily pause time, inspect the exact state mid-execution, or predict the exact order of operations.

TaskTonic eliminates these threading nightmares through its atomic **Sparkles** and sequential queue. But how do you test an asynchronous queue without relying on messy `time.sleep()` calls in your tests?

Enter the **`ttDistiller`**: a specialized, deterministic test engine for TaskTonic.

---

## 1. The Print Statement vs. The Distiller (`self.log` vs `ttDistiller`)

When developing a Tonic, your first instinct is to use `self.log("Doing something...")`. This is excellent for visual debugging. You can watch the execution flow, state changes, and parameter values scroll by in your console.

However, **you cannot write an automated unit test against console output**. 
If someone breaks your Tonic's logic six months from now, `self.log` won't fail a CI/CD pipeline. 

The `ttDistiller` replaces the standard `ttCatalyst` engine during testing. Instead of running a continuous, infinite loop in the background, the Distiller acts as a **manual crank** for the TaskTonic engine. It records every Sparkle, every state change, and every parameter passed, turning your asynchronous application into a completely synchronous, predictable, and heavily inspectable data structure.

## 2. Usage: Pytest or Standalone

You don't need a heavy testing framework to use the Distiller, but it integrates perfectly with them.
*   **Standalone:** You can write a simple Python script that instantiates a Distiller, runs your Tonic, and asserts conditions using standard `assert` statements.
*   **Pytest (Recommended):** You can use `pytest` fixtures to set up your Distiller, run your Tonics through their paces, and generate beautiful test reports. The Distiller runs synchronously in the main thread, making your `pytest` suite incredibly fast and 100% deterministic.

---

## 3. Controlling Time and Execution: Distiller Functions

Because the Distiller owns the queue, you dictate exactly when and how Sparkles are executed.

### Step-by-Step Sparkling
Instead of `start_sparkling()`, you tell the Distiller exactly how many items to process from the queue.
```python
# Process exactly ONE Sparkle on the queue, then pause.
distiller.sparkle(steps=1) 

# Process 5 Sparkles, then pause.
distiller.sparkle(steps=5)
```
This allows you to freeze the universe mid-execution and inspect the state of your application.

### Sparkling Until a Condition
Often, you don't know *exactly* how many Sparkles it takes to finish a complex network handshake. You just want to run the engine until a specific event happens.
```python
# Run the engine until the Tonic enters the 'finished' state
distiller.run_until_state(tonic_instance, target_state='finished')

# Run the engine until a specific Sparkle method is called
distiller.run_until_sparkle(tonic_instance, target_sparkle='ttse__on_data_received')
```

### Data Probing
While frozen between Sparkles, you can "probe" your Tonic. Since the Distiller runs in your testing thread, you have safe, direct access to the Tonic's internal variables. You can assert that `tonic_instance.download_count == 5` exactly at the moment it enters the 'saving' state.

### Contract Testing (The Ultimate Regression Guard)
Because TaskTonic executes predictably, the sequence of Sparkles and State changes forms a rigid "Contract". 
The Distiller can record a "Golden Run" of your Tonic. If a junior developer later modifies the code and accidentally triggers an extra `ttsc__reconnect` Sparkle, the Distiller will fail the test immediately because the execution signature (the Contract) no longer matches the expected sequence.

---

## 4. Unpacking the Status Content (and Profiling)

Every time a Sparkle is executed, the Distiller logs a comprehensive status record. This isn't just a string; it's a rich data structure containing:

*   **Target:** Which Tonic instance executed the Sparkle.
*   **Method:** The exact method name (e.g., `ttsc__process_chunk`).
*   **Arguments:** The `args` and `kwargs` passed into the Sparkle.
*   **State:** The state of the Tonic before and after the Sparkle.
*   **Execution Time (Profiling):** Crucially, the Distiller records the exact `at_enter` and `at_exit` timestamps for every Sparkle. 

**Finding the "Giant Sparkle":**
Remember the golden rule of Sparkling Programming: *Never block the Catalyst.*
If you suspect your UI is stuttering, you can write a test and check the Distiller's execution times. If the Distiller reports that `ttsc__parse_xml` took 450ms, you instantly know you have found a "Giant Sparkle" that needs to be broken down using the Chunked Iterator pattern.

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
distiller.inject_sparkle(parent_tonic.ttse__on_network_data, {"status": "ok", "payload": "123"})
distiller.sparkle(steps=1)
assert parent_tonic.current_state == 'processing_data'
```

### B. The Integration Test (Full Hierarchy)
You can also load the parent *and* all its real infusions into the Distiller. 
Because all Tonics in the same Formula share the same Catalyst engine, the Distiller easily manages the master queue for the entire tree. You can trigger a high-level command on the Parent, tell the Distiller to run 50 Sparkles, and watch the entire cascade of commands and events flow down to the children and bubble back up to the parent. It provides a flawless, synchronous integration test of a highly asynchronous system.

---

### Summary
Testing concurrent code used to mean adding `time.sleep(1)` everywhere and praying. With TaskTonic and the `ttDistiller`, you gain the power to freeze time, inspect memory, profile execution speeds, and lock down your application's behavior with deterministic contracts.
```## `File: _documents\TaskTonic - Depending on your state.md`
# Mastering State Machines in TaskTonic

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

This allows you to write incredibly clean code. Define the generic behavior once, and only override it with a state-specific `ttsc_<state>__name` when the behavior needs to deviate!## `File: _documents\Tasktonic - At you Service.md`
# Mastering TaskTonic Services (The Singleton Pattern)

When building complex applications, you often need a central resource that multiple Tonics can share without stepping on each other's toes. In traditional programming, you might use global variables or implement complex Singleton patterns with thread locks. 

TaskTonic provides an elegant, built-in solution for this: **Services** [1].

Here is everything you need to know about what Services are, when to use them, how to create them, and the best practices for context-aware initialization.

---

## 1. What is a Service and When Do You Use It?

A Service is a special `ttTonic` class that is managed as a **Singleton** [1, 2]. The TaskTonic metaclass guarantees that **only one instance of a Service ever exists** throughout your application's lifecycle [3, 4].

When a Tonic tries to create an instance of a Service:
*   **The First Time:** The framework creates the instance, executes its `__init__` method, and registers it in the `ttLedger` [3-5].
*   **Every Subsequent Time:** The framework intercepts the creation, finds the existing instance in the ledger, and returns it. `__init__` is *not* called again [4, 5].

**When to use a Service:**
You should use a Service for any central resource that needs to be unique and shared [6, 7]:
*   **Databases:** A single connection pool manager (`DatabaseService`) [6, 7].
*   **Hardware Control:** A single handler for a serial port to prevent multiple Tonics from sending conflicting bytes (`SerialService`) [7, 8].
*   **State Management:** A centralized data store like the `DigitalTwin` (using `ttStore`) [9].
*   **Logging/Configuration:** A central logger or config file loader [6, 7].

---

## 2. How to Create a Service

Creating a Service requires only a few specific steps. 

### Step 1: The Class Flag
You define a Service by inheriting from `ttTonic` (or another essence) and setting the `_tt_is_service` class variable to a unique string [10, 11]. This string is the name the Ledger uses to identify the singleton [10, 11].

```python
from TaskTonic import ttTonic

class DatabaseService(ttTonic):
    _tt_is_service = "SharedDatabaseService" # Unique identifier
```

### Step 2: `__init__` (One-Time Setup)
Implement your `__init__` method for configuration that should only happen **once** (like connecting to the database) [11, 12]. 
*   **Naming Convention:** Prefix parameters intended for one-time setup with `srv_` (e.g., `srv_db_url`) [12, 13].
*   **Kwargs Rule:** You *must* accept `**kwargs` and pass them to `super().__init__(**kwargs)` so the framework can handle context routing [12, 13].

```python
    def __init__(self, srv_db_url, **kwargs):
        super().__init__(**kwargs)
        self.db_url = srv_db_url
        self.log(f"Connecting to database at {self.db_url} (Happens ONCE)")
        self.connected_clients = {}
```

---

## 3. The `_init_service` Hook (Per-Access Setup)

Because `__init__` only runs once, how does the Service know when a *new* Tonic connects to it? 

TaskTonic provides the **`_init_service`** hook. This method is called by the framework **every single time** a Tonic asks for the Service (including the very first time) [5, 14, 15]. 

*   **Naming Convention:** Prefix parameters intended for per-access setup with `ctxt_` (e.g., `ctxt_access_level`) [13, 16].
*   This is where you register the new client (the `context`) with your Service [17].

### 🚨 Best Practice: Use a Sparkle for Registration!
When a worker Tonic requests your Service, the `_init_service` method is executed *in the calling Tonic's thread*. If your Service is running on its own Catalyst (its own thread), modifying Service variables directly inside `_init_service` violates TaskTonic's thread-safety guarantees!

**The Golden Rule:** Use `_init_service` strictly to put a command (`ttsc__`) onto the Service's queue [18, 19]. Let the Service process the registration in its own time, ensuring atomic thread safety.

```python
    def _init_service(self, context, ctxt_access_level="read", **kwargs):
        """
        Runs EVERY time a Tonic binds this service.
        Runs in the CALLER'S thread. Do not modify state directly!
        """
        if context is None:
            return
            
        # Queue a sparkle to handle the registration safely!
        self.ttsc__register_new_client(context, ctxt_access_level)

    def ttsc__register_new_client(self, context, access_level):
        """
        Runs in the SERVICE'S thread. 100% thread-safe.
        """
        self.log(f"Registering client '{context.name}' with level: {access_level}")
        self.connected_clients[context.id] = {
            'instance': context, 
            'level': access_level
        }
```

---

## 4. How to Use a Service

To use a Service, you simply instantiate it as if it were a normal Tonic [20, 21]. The framework handles the Singleton magic behind the scenes.

```python
class DataAnalyzer(ttTonic):
    def ttse__on_start(self):
        # 1. Ask for the service. 
        # Pass 'srv_' args just in case this is the first time it's created.
        # Pass 'ctxt_' args for this specific analyzer.
        self.db = DatabaseService(
            srv_db_url="postgres://user:pass@localhost",
            ctxt_access_level="write"
        )
        
    def ttsc__save_data(self):
        self.db.ttsc__store_record({"data": "123"})
```

### ⚠️ The Context Trap (Warning!)

By default, when you instantiate a Tonic inside another Tonic, the new Tonic becomes a child of the caller (it binds to the caller's context) [22, 23]. 

If you create a Service from a temporary worker Tonic, the Service becomes a child of that worker [22, 23]. **If the worker finishes, it will recursively finish all its children—killing your shared Service for the entire application!** [22, 23]

**How to avoid this:**
It is highly recommended to create Services at the top level of your application (in your `ttFormula` inside `creating_starting_tonics`) [23, 24]. If you *must* create a Service from inside a worker, explicitly break the context chain by passing `context=None` (or `context=-1`):

```python
    def ttse__on_start(self):
        # By passing context=None, the Service is registered at the root level,
        # completely immune to this worker's lifecycle.
        self.db = DatabaseService(
            context=None, 
            srv_db_url="postgres://..."
        )
        # Manually trigger the access hook for this worker
        self.db._init_service(context=self, ctxt_access_level="read")
```

## Summary Checklist for Services
1. Add `_tt_is_service = "name"` to your class [10, 11].
2. Use `__init__` for one-time setup (`srv_` kwargs) [11, 12].
3. Use `_init_service` for per-client setup (`ctxt_` kwargs) [13, 14, 16].
4. **Always** dispatch a `ttsc__` sparkle inside `_init_service` to modify the Service's internal state [18, 19]. 
5. Instantiate Services at the Formula level to prevent accidental teardowns [22-24].
```## `File: _documents\TaskTonic - Active data store.md`
# ttStore & Store/Item: Central Data Repository

This documentation describes the functionality of the `Store` and `Item` classes and their integration within TaskTonic
via `ttStore`.

## Introduction

In complex applications, it is essential to share data between different components in a structured and accessible way.
`ttStore` functions as a **Central Data Repository**. It offers a hierarchical storage structure (comparable to a file
system or a nested dictionary) that is:

1. **Centralized:** A single source of truth for parameters, sensor values, and configurations.
2. **Reactive:** Components can subscribe to changes in specific data paths.
3. **Flexible:** Data can be accessed via absolute paths or relative pointers (`Item`).

---

## Concepts: Store vs. ttStore

The system consists of two layers that can also be used **independently**.

### 1. The Core: `Store` and `Item`

The `Store` is the pure data container. It is a standalone class that holds the data and provides methods to read or
write data via paths (e.g., `'sensors/temp/value'`).

The `Item` is a smart "pointer" or "cursor" to a specific location in the `Store`. It allows for relative navigation
without needing to know the full absolute path.

> **Note:** `Store` and `Item` can be used outside of TaskTonic in any Python project requiring a powerful, hierarchical
data structure.

### 2. The Service: `ttStore`

`ttStore` is the TaskTonic wrapper around a `Store`. It transforms the store into a **Service** within the TaskTonic
ecosystem. This adds capabilities such as:

* **Event-driven updates:** Automatically notify other Tonics (like UI or controllers) upon changes.
* **Service Binding:** Easily linked to other Tonics via `self.bind()`.

---

## API Reference & Methods

Below is an overview of the most important methods for data manipulation and navigation.

### Dictionary Access (`[]` Syntax)

For convenience, `ttStore` and `Item` support standard Python dictionary syntax.

* **Reading:** `val = store['path']`
    * Equivalent to `.get('path')`.
    * Returns `None` if the path does not exist (unlike standard Python dicts which raise KeyError).
* **Writing:** `store['path'] = val`
    * Equivalent to `.set([('path', val)])`.
    * Triggers updates immediately (unless inside a `group`).

**Example:**

```python
# Read
current_limit = self.twin['parameters/temp_limit']

# Write
self.twin['parameters/temp_limit'] = 12.0
```

### Writing Data (`set`, `.v`, `.append`)

#### `set(data)`

Writes one or multiple values to the store. It accepts a `dict` or an `Iterable` (list/tuple) of tuples.

* **Usage:** Initialization, bulk updates, or when you need to write multiple values atomically.
* **Smart Paths:**
    * `#`: Creates a new unique entry (auto-increment list).
    * `./`: Refers to the last created entry (useful for setting properties of an item).

**Example:**

```python
# Initialize a store with parameters and sensors
self.twin.set([
    ('parameters/update_freq', 2),     # Set update frequency to 2
    ('sensors/#', 'temp'),             # Create new sensor 'temp'
    ('sensors/./value', 15.0),         # Set value of THAT sensor
    ('sensors/./unit', '℃'),           # Set unit of THAT sensor
])
```

#### `.v` (Value Property via Item)

If you hold an `Item` object (a pointer to a location), you can read and write directly via the `.v` property. This is
the most efficient way to manipulate data if you already have the Item.

**Example:**

```python
# Assume we have a pointer (Item) to the sensor value
sensor_val_item = self.twin.at('sensors/#0/value')

# Write a new value
sensor_val_item.v = 22.5
```

#### `append(value)` (via Item) or `append(path, value)` (via Store)

Adds a new item to a list. This is a cleaner, more pythonic alternative to using the `'path/#'` syntax when adding
single items.

* **Via Item:** `item.append(value)`
* **Via Store:** `store.append(path, value)`

**Example:**

```python
# Append via Store (adds 'System Started' to the 'logs' list)
self.twin.append('logs', 'System Started')

# Append via Item
log_item = self.twin.at('logs')
log_item.append('User logged in')
```

### Reading Data (`get`, `at`)

#### `get(path, default=None)`

Retrieves the value of a specific path. If the path does not exist, the `default` value is returned.

**Example:**

```python
freq = self.twin.get('parameters/update_freq', 5)  # Default 5 if not found
```

#### `at(path) -> Item`

Returns an `Item` object pointing to the location `path`. This is **more powerful** than `get` because it allows further
navigation from that point.

**Example:**

```python
# Get a pointer (Item) to the first sensor
sensor_item = self.twin.at('sensors/#0')

# Read values via the Item
print(sensor_item['value'].v)  # Prints: 15.0
```

### Navigation (`Item` objects)

An `Item` object acts as a smart window onto your data.

* **`item['child']`**: Navigate to a sub-item.
    ```python
    val = sensor_item['value'].v
    ```
* **`item.parent`**: Returns an `Item` to the parent.
    ```python
    root_sensors = sensor_item.parent # Now points to 'sensors'
    ```
* **`item.list_root`**: If the item is part of a list (like sensors), this returns the item itself, regardless of how
  deep you are in the hierarchy.
    ```python
    # If located at 'sensors/#0/value', list_root returns 'sensors/#0'
    sensor_name = sensor_item.list_root.v # Returns e.g., 'temp'
    ```

#### `.children(prefix=None)`

Returns an **iterator** (not a list) of `Item` objects that are direct children of the current item.

* **Why an iterator?** It is memory efficient (lazy evaluation). If you have thousands of items, it doesn't create
  objects for all of them unless you consume them.
* **prefix:** Optional string to filter children (e.g., useful if you have different types of lists in one folder).

**Example 1: Converting to a list**
If you need index access or the length, convert it to a list explicitly.

```python
sensors = self.twin.at('sensors')
sensor_list = list(sensors.children())
print(f"Count: {len(sensor_list)}")
```

**Example 2: Iterating directly (Efficient)**
Searching for a specific sensor without creating a full list in memory.

```python
target_sensor = None
for item in self.twin.at('sensors').children():
    if item.v == 'humidity':
        target_sensor = item
        break
```

### Reactivity (`subscribe`)

Only available in `ttStore`. This allows subscribing a method to data changes.

#### `subscribe(path, callback)`

* **path:** The path to monitor (e.g., `'sensors'`).
* **callback:** The method called upon change.

The callback receives a list of `updates`. Each update is a tuple: `(path, new_value, old_value, source)`.

**Example:**

```python
def ttse__on_start(self):
    # Listen to anything changing under 'sensors'
    self.twin.subscribe("sensors", self.ttse__on_sensor_update)

def ttse__on_sensor_update(self, updates):
    for path, new, old, source in updates:
        print(f"Sensor update at {path}: {old} -> {new}")
```

### Utilities (`dumps`, `group`, `source`)

#### `dumps()`

Returns a string representation of the entire store (useful for debugging).

```python
print(self.twin.dumps())
```

#### `group(notify=True, source_id=None)` & `source(source_id)`

Context managers to control how updates are processed.

1. **`group(notify=False)`**: Performs updates atomically.

* **Usage:** Batch initialization. No events are fired until the block ends (or never if `notify=False`).

  ```python
  with self.twin.group(notify=False):
      self.twin.set(...) 
  ```

2. **`source(source_id)` / `group(..., source_id=...)`**:

* **Usage:** Identifying *who* made the change. This is crucial for bidirectional sync (e.g., connecting a GUI slider to
  a value).
* If a GUI updates the Store, the Store notifies the GUI. You want the GUI to ignore that notification to prevent an
  infinite loop.

  ```python
  # Example: Updating from a specific source (e.g., 'GUI')
  with self.twin.source('GUI'):
      self.twin['parameters/speed'] = 50
  
  # In the callback, you can check the source:
  def on_change(self, updates):
      for path, new, old, src in updates:
          if src == 'GUI':
              continue # Ignore changes I made myself
          # Update GUI display...
  ```

---

## Performance & Best Practices

Although `ttStore` is powerful, consider the following points for optimal performance and clean code.

### 1. Batch Updates with `group`

When modifying a lot of data simultaneously (e.g., during startup or reset), always use
`with self.group(notify=False):`.

* **Reason:** Without this, every single write action triggers all subscribers immediately. `group` prevents this "
  update storm".

### 2. Efficiency of `Item`

If you need to read or write the same value frequently in a loop (e.g., a timer), retrieve the `Item` **once** during
`__init__` or `on_start`, and cache it.

* **Inefficient:** Calling `self.twin.get('sensors/#0/value')` in every cycle (must parse the path string every time).
* **Efficient:**
    ```python
    # In __init__:
    self.temp_val_item = self.twin.at('sensors/#0/value')

    # In timer loop:
    self.temp_val_item.v += 0.1
    ```

### 3. Data Types

The Store is not strictly typed (it is Python), but consistency is key. If a path starts as a `float` (`15.0`), try to
keep it that way and do not suddenly change it to a `string` ("15"), unless your application logic specifically handles
this.

---

## Example Implementation

Below is a full integration where `MyProcess` writes data and `OperatorInterface` reacts to that data via the
`DigitalTwin` store.

```python
from TaskTonic import *
from TaskTonic.ttTonicStore import ttStore
import random


# --- The Data Repository Service ---
class DigitalTwin(ttStore):
    _tt_is_service = "digital_twin"  # Service name for binding

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_record['auto_finish'] = True

    def _init_post_action(self):
        super()._init_post_action()
        # Use group(notify=False) for performance during init
        with self.group(notify=False):
            # Because the set method uses Iterable, both tuples (()) and lists [] are valid.
            self.set((
                ('parameters/update_freq', 2),
                ('parameters/temp_limit', 10),
                ('sensors/#', 'temp'),         # Create sensor 0
                ('sensors/./value', 15.0),
                ('sensors/./unit', '℃'),
                ('sensors/./high_alarm', False),
                ('sensors/#', 'humidity'),     # Create sensor 1
                ('sensors/./value', -1),
            ))

        self.log(f"Digital Twin is initialized\n{self.dumps()}")


# --- The Observer (e.g., GUI or Logger) ---
class OperatorInterface(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        # Bind to the service
        self.twin = DigitalTwin()

    def ttse__on_start(self):
        # Subscribe to sensor changes
        self.twin.subscribe("sensors", self.ttse__on_sensor_update)
        # Schedule parameter update and end of program
        ttTimerSingleShot(5, sparkle_back=self.ttse__on_parm_update)
        ttTimerSingleShot(8, sparkle_back=self.ttse__on_end_program)

    def ttse__on_sensor_update(self, updates):
        for path, new, old, source in updates:
            # Use .at(path) to get an Item for smart navigation
            # .list_root automatically navigates up to the sensor item (e.g., 'sensors/#0')
            sensor_item = self.twin.at(path).list_root

            # Retrieve name and value via the item
            name = sensor_item.v
            val = sensor_item['value'].v
            unit = sensor_item.get('unit', '')

            self.log(f"UPDATE OF SENSOR {name}: {val:.3f}{unit}")

    def ttse__on_parm_update(self, tmr):
        self.twin['parameters/update_freq'] = .5

    def ttse__on_end_program(self, tmr):
        self.finish()


# --- The Controller (Process Logic) ---
class MyProcess(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        self.my_record['auto_finish'] = True
        self.twin = self.bind(DigitalTwin)

        # Performance optimization: Cache the item pointer
        # This avoids parsing the path string in every loop cycle
        self.temp_sens_item = self.twin.at('sensors/#0')

    def ttse__on_start(self):
        self.twin.subscribe("parameters", self.ttse__on_param_update)
        # Start a timer based on a parameter from the store
        freq = self.twin.get('parameters/update_freq', 5)
        self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__on_param_update(self, updates):
        for path, new, old, source in updates:
            if path == 'parameters/update_freq':
                self.utmr.stop()
                # Restart timer with new frequency
                freq = self.twin.get('parameters/update_freq', 5)
                self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__update_timer(self, tmr):
        # Writing directly via the cached item is very efficient
        self.temp_sens_item['value'].v += random.uniform(-2, 2)


# --- App Configuration ---
class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        DigitalTwin()
        OperatorInterface()
        MyProcess()


if __name__ == '__main__':
    myApp()
```## `File: _documents\old_documents_not_matching_the_code\ttDataShare.md`
# DataShare Class: A User Guide

## 1. Introduction

`DataShare` is a powerful, thread-safe, hierarchical data store for Python. It's designed to be a centralized repository
for application state and configuration, allowing for complex, nested data structures that can be accessed and
manipulated via a simple path-based syntax.

**Key Features:**

* **Hierarchical Structure:** Access nested data using file-system-like paths (e.g., `'system/network/host'`).
* **Advanced List Support:** Natively create and manipulate lists within the hierarchy.
* **Dual-Value Nodes:** A single path can hold both a direct value and serve as a container for sub-keys.
* **Observer Pattern:** Subscribe to changes at any level of the data hierarchy and receive notifications.
* **Thread Safety:** All operations are thread-safe, making it ideal for multi-threaded applications.
* **Serialization:** Save and load the entire data store to a compact binary format.

---

## 2. Core Concepts

### Hierarchical Paths

Data is organized in a tree-like structure of nested dictionaries and lists. You interact with it using a **`key_path`
**, which is a string of keys joined by a separator (default is `/`).

```python
# This sets a value in a nested dictionary
ds.set('user/preferences/theme', 'dark')
```

### List Syntax

`DataShare` has special syntax for interacting with lists.

* **Append (`[]`):** Use an empty `[]` to append a new item to a list. If the list doesn't exist, it will be created.
* **Index (`[n]`):** Use `[index]` to access or modify a list item at a specific position. Negative indices are
  supported.

```python
# Appends 'admin' to the 'user/roles' list
ds.set('user/roles[]', 'admin')

# Accesses the first role
role = ds.get('user/roles[0]')
```

### Dual-Value Nodes (`_value`)

A powerful feature is that any node can have both a direct value and sub-keys. This is handled internally by storing the
direct value in a special `_value` key. This allows you to treat a path as both an endpoint and a container.

```python
# Set a direct value for 'lights'
ds.set('home/living/lights', 'on')

# Set a sub-key on the same 'lights' path
ds.set('home/living/lights/ceiling', '30%')

# The internal structure is now similar to:
# 'lights': { '_value': 'on', 'ceiling': {'_value': '30%'} }
```

---

## 3. Initialization

To start, import and instantiate the class.

```python
# Create an empty instance
ds = DataShare()

# Create an instance with initial data
initial = {
    'system': {
        'host': 'server.local',
        'port': 8080
    }
}
ds_with_data = DataShare(initial_data=initial)
```

The `initial_data` parameter can be one of:

* A `dict`.
* A `list` of `(key_path, value)` tuples.
* A `set` or `tuple` of `(key_path, value)` tuples.

---

## 4. API Reference

### `set(key_or_data, value=None)`

This is the primary method for adding or modifying data. It's highly versatile.

**1. Set a Single Value**

```python
ds.set('user/name', 'Alice')
ds.set('user/id', 123)
```

**2. Set a List Item by Index**
This will overwrite the value at the specified index.

```python
ds.set('user/roles[1]', 'moderator')
```

**3. Append to a List**
Use `[]` to add a new item to the end of a list.

* **Appending Simple Values:**
    ```python
    # Append a simple string
    ds.set('user/roles[]', 'guest')
    ```

* **Appending Complex Objects (Dictionaries):**
  A powerful feature is creating and populating a dictionary inside a list in one go.
    1. Use `[]` with a sub-key to create a new dictionary in the list and set its first value.
    2. Use a negative index like `[-1]` to refer to the item you *just* added and set more values on it.

    ```python
    # 1. Add a new user 'anna' to the 'app/users' list.
    # This creates a new dictionary: {'name': {'_value': 'anna'}}
    ds.set('app/users[]/name', 'anna')

    # 2. Add the role 'admin' to the user we just created.
    # The path 'app/users[-1]' now refers to anna's dictionary.
    ds.set('app/users[-1]/role', 'admin')

    # You can continue adding more users
    ds.set('app/users[]/name', 'ben')
    ds.set('app/users[-1]/role', 'editor')

    # The resulting list would look like this (in clean view):
    # (
    #   {'name': 'anna', 'role': 'admin'},
    #   {'name': 'ben', 'role': 'editor'}
    # )
    ```

> **Note:** When using negative indices like `[-1]` in a `batch_update` block, it refers to the list's state *at the
time of the call*, not including previous appends within the same batch.

**4. Batch Updates**
You can set multiple values at once by passing a `dict`, `list`, or `tuple`.

```python
# Using a dictionary
ds.set({
    'system/network/host': 'new-host.com',
    'system/network/port': 443
})

# Using a list of tuples
ds.set([
    ('user/active', True),
    ('user/last_login', '2025-09-22')
])
```

---

### `get(key_path, default=None, *, get_value=0)`

Retrieves data from the store, offering different "views" of the data.

* `key_path`: The path to the data.
* `default`: The value to return if the path is not found.
* `get_value`: (Keyword-only) An integer that controls the data view:
    * `0` **(Default) - Clean View:** Returns a user-friendly view. Internal `_value` wrappers are removed where
      possible. For example, `{'power': {'_value': 'on'}}` becomes `{'power': 'on'}`. This is the most common mode.
    * `1` **- Raw View:** Returns the data exactly as it's stored internally, including all `_value` wrappers.
      Dictionaries are returned as read-only `MappingProxyType` objects.
    * `2` **- Value-Only View:** Extracts only the direct value from a node's `_value` key, ignoring any sub-keys. If
      the `_value` key doesn't exist, it returns the `default`.

**Example Setup**

```python
ds = DataShare()
ds.set('lights', 'on')
ds.set('lights/ceiling', '30%')
ds.set('users[]', 'Alice')
```

The internal structure of `lights` is `{'lights': {'_value': 'on', 'ceiling': {'_value': '30%'}}}`.

**1. Using `get_value=0` (Clean View - Default)**
This mode simplifies the output by removing unnecessary `_value` wrappers.

```python
# Gets the 'lights' node and cleans it up
# The sub-key 'ceiling' is unwrapped from {'_value': '30%'} to '30%'
# The main '_value': 'on' remains because 'lights' also has other keys
clean_node = ds.get('lights')
# clean_node is a read-only dict: {'_value': 'on', 'ceiling': '30%'}

# Lists are also cleaned
users = ds.get('users')
# users is a read-only tuple: ('Alice',)
```

**2. Using `get_value=1` (Raw View)**
This shows you the exact internal structure.

```python
# Get the raw, untouched internal node for 'lights'
raw_node = ds.get('lights', get_value=1)
# raw_node is a read-only dict: {'_value': 'on', 'ceiling': {'_value': '30%'}}

# Get a single item node
user_node = ds.get('users[0]', get_value=1)
# user_node is a read-only dict: {'_value': 'Alice'}
```

**3. Using `get_value=2` (Value-Only View)**
This extracts a specific `_value` and ignores everything else.

```python
# Get only the direct value of 'lights'
state = ds.get('lights', get_value=2) # Returns 'on'

# If a node has no direct value, it returns the default
missing = ds.get('system', get_value=2, default='N/A') # Returns 'N/A'
```

---

### `getk(key_path, default=..., *, strip_prefix=False)`

Retrieves data as a **flattened tuple of `(full_key_path, value)` pairs**. This is useful for reading entire
configuration sections.

* `key_path`: The branch of the data tree to retrieve.
* `default`: If the `key_path` is not found, it returns `((key_path, default),)`. If `default` is not provided, returns
  `()`.
* `strip_prefix`: (Keyword-only) If `True`, the `key_path` is removed from the start of all returned keys, giving you
  relative paths.

```python
# Setup
ds.set('db/host', 'localhost')
ds.set('db/user/name', 'admin')

# 1. Get a flattened branch
all_db_config = ds.getk('db')
# Returns (('db/host', 'localhost'), ('db/user/name', 'admin'))

# 2. Get a branch with relative keys
relative_config = ds.getk('db', strip_prefix=True)
# Returns (('host', 'localhost'), ('user/name', 'admin'))

# 3. Handle a missing key with a default
missing = ds.getk('api/key', default='default_key')
# Returns (('api/key', 'default_key'),)
```

---

### `subscribe(key_path, callback)` & `unsubscribe(key_path, callback)`

Register a function to be called whenever data at or below a certain `key_path` changes.

**Callback Signature**
Your callback function must accept three arguments: `key`, `old_value`, and `new_value`.

```python
def my_callback(key, old, new):
    print(f"Change detected at '{key}':")
    print(f"  Old -> {old}")
    print(f"  New -> {new}")

ds.subscribe('system/network', my_callback)
```

> **Important:** The `old` and `new` values are automatically "unwrapped". If a value is a simple endpoint (internally
`{'_value': 'on'}`), you will receive the clean value (`'on'`). You only receive the full dictionary if the node has
both a direct value and sub-keys.

---

### `batch_update()`

A context manager to perform multiple `set` operations while only triggering a single round of notifications at the end.
This is highly efficient for bulk updates.

```python
with ds.batch_update():
    ds.set('user/profile/bio', '...')
    ds.set('user/profile/location', '...')
    ds.set('user/active', False)
# All notifications are sent here, at the end of the block.
```

---

## 5. Serialization & Debugging

### `serialize()` & `deserialize(data)`

Save and load the entire state of the `DataShare` object.

```python
# Save state to a file
# serialized_data = ds.serialize()
# with open('app_state.bin', 'wb') as f:
#     f.write(serialized_data)

# Load state from a file
# with open('app_state.bin', 'rb') as f:
#     loaded_data = f.read()
# new_ds = DataShare.deserialize(loaded_data)
```

### `dumps(indent=2)`

Get a human-readable, pretty-printed string representation of the data, perfect for debugging.

```python
print(ds.dumps())
```## `File: _documents\old_documents_not_matching_the_code\ttTonic.md`
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
  finishes. A special value of `-1` can be passed to immediately stop the state machine.
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
## `File: _documents\old_documents_not_matching_the_code\ttCatalyst.md`
# Documentation: The `ttCatalyst` Class

This document describes the functionality of the `ttCatalyst` class within the TaskTonic framework.

---

## 1. Introduction: The Engine of the System

If a `Tonic` is a specialized worker on an assembly line, the `ttCatalyst` is the powerful engine that drives the
conveyor belt. Its primary and most crucial function is to make `Tonic`s "sparkle" by continuously processing a
shared task queue.

It's important to understand the `Catalyst`'s role:

* **It provides EXECUTION power**: The `Catalyst` runs the main loop that pulls tasks from a queue and executes them.
* **It does NOT provide COORDINATION**: The `Catalyst` is not the brain of the operation. It doesn't decide
  which `Tonic`s to create or what tasks they should perform. That higher-level logic is handled by other
  components in the framework, such as the `Formula` and `Ledger`.

[Image of a powerful, clean industrial engine]

---

## 2. Core Functionality

The `Catalyst` has three main responsibilities: managing the queue, running the execution loop, and tracking the
lifecycle of the `Tonic`s it powers.

### The Master Queue (`catalyst_queue`)

The `Catalyst` owns the central `Queue` that all its managed `Tonic`s will use. When any `Tonic` calls one of
its sparkle methods (e.g., `ttsc__process`), it places a "work order" onto this shared `catalyst_queue`.

### The Execution Loop (`sparkle()`)

This is the heart of the `Catalyst`. It's a `while` loop with a single job:

1. Wait for and retrieve a work order from the `catalyst_queue`.
2. Unpack the work order to identify the target `Tonic` instance and the sparkle to be executed.
3. Call the `_execute_sparkle` method on that specific `Tonic`, handing off the task.

The loop uses a timeout when getting items from the queue. This ensures it doesn't block forever and can gracefully
shut down when instructed.

### Lifecycle Management

The `Catalyst` keeps a register of all the `Tonic`s it is currently powering.

* **Startup (`_ttss__startup_tonic`)**: When a `Tonic` is initialized, it calls this system sparkle on its
  `Catalyst` to register itself as active.
* **Shutdown (`_ttss__tonic_finished`)**: When a `Tonic` completes its `finish()` sequence, it calls this
  system sparkle to de-register itself.
* **Automatic Shutdown**: When the last registered `Tonic` finishes, the `Catalyst` determines its job is
  done and automatically initiates its own shutdown sequence.

---

## 3. Usage and Operation

### Starting the Catalyst (`start_sparkling()`)

To begin processing the queue, you must call the `start_sparkling()` method. This kicks off the `sparkle()` loop.
The framework distinguishes between the main `Catalyst` (with `id=0`) and others:

* **Main Catalyst**: Runs the loop in the current (main) thread, blocking further execution in that thread.
* **Other Catalysts**: Start the execution loop in a new, separate background thread.

### Binding a Tonic to a Catalyst

A `Tonic` automatically binds itself to its `Catalyst` during initialization. It looks for the `Catalyst` in the
`context` it receives.

```python
# --- Inside a Tonic's __init__ method ---

# It finds the catalyst in its context and gets a reference to the shared queue.
self.catalyst = context.catalyst if hasattr(context, 'catalyst') else ...
self.catalyst_queue = self.catalyst.catalyst_queue

# It then registers itself with the catalyst as an active component.
self.catalyst._ttss__bind_tonic_to_catalyst(self.id)
```
## `File: _documents\old_documents_not_matching_the_code\_introduction.md`
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
self.db = DatabaseService()
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
ttTimerSingleShot(5.0)

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
controlled steps and captures a full trace of sparkles and state changes for analysis.## `File: _documents\old_documents_not_matching_the_code\Tonic Services.md`
# The Service (Singleton) Pattern

This document explains how to create and use "Services" within the TaskTonic framework. A Service is a special type of
`ttTonic` class that is managed as a **Singleton**, ensuring only one instance ever exists.

It also introduces the concept of a "per-access" hook (`_init_service`) for context-aware interactions.

---

## 1. What is a Service?

A Service is a `ttTonic` class that is guaranteed to have **only one instance** throughout the application's lifecycle.

The `ttMeta` metaclass (which `ttEssence` and `ttTonic` use) manages this. When you try to create an instance of a
Service:

* **The First Time:** The metaclass creates the instance, runs its `__init__` and `_init_post_action` methods once, and
  stores it in the `ttLedger` under a unique name.
* **Every Subsequent Time:** The metaclass intercepts the call, finds the *existing* instance in the `ttLedger`, and
  returns it immediately. `__init__` is **not** called again.

### Key Feature: The `_init_service` Hook

A Service is "context-aware." Every time a Service is accessed (both on creation *and* on subsequent retrievals), the
metaclass will call its `_init_service` method.

This allows you to pass context-specific parameters (e.g., `ctxt_ip`, `ctxt_access_level`) that are processed *every
time*, while one-time setup parameters (e.g., `srv_api_key`) are only processed *once* in `__init__`.

---

## 2. Application Examples

You should use this pattern for any class that needs to be unique and shared across your entire application. 📈

* **Logging:** A `LoggerService` that all other `ttTonic` tasks call to write logs. You only want one instance managing
  the log file or screen output.
* **Configuration:** A `ConfigService` that loads a `.ini` or `.yaml` file once and provides settings to any task that
  asks for it.
* **Database Management:** A `DatabaseService` that manages a single connection pool for the entire application.
* **API Clients:** An `ApiService` that handles a single OAuth2 token, rate limiting, and authentication for a shared
  REST API.
* **Hardware Control:** A `SerialService` that manages a single connection to a piece of hardware, preventing multiple
  tasks from trying to access the same port.

---

## 3. How to Create a Service

Creating a service is simple and follows four steps.

### Step 1: Inherit from `ttTonic`

Your service class must inherit from `ttTonic` (or any class that inherits from `ttEssence`).

```python
class MyService(ttTonic):
    pass
```

### Step 2: Set the Service Flag

Set the `_tt_is_service` class variable to a unique string name. This name is how the `ttLedger` will identify your
singleton.

```python
class MyService(ttTonic):
    # This tells the metaclass to treat this class as a
    # service identified by the name "MyUniqueService"
    _tt_is_service = "MyUniqueService"
```

### Step 3: Implement `__init__` (One-Time Setup)

This is your standard constructor. It is **only called once** when the service is first created.

* Use parameters prefixed with `srv_` (service) for one-time setup (e.g., `srv_api_key`).
* **Crucially:** You must also accept any context parameters (e.g., `ctxt_...`) and `**kwargs` so you can cleanly pass
  the correct arguments to `super().__init__`.

```python
class MyService(ttTonic):
    _tt_is_service = "MyUniqueService"

    def __init__(self, srv_api_key, ctxt_ip=None, **kwargs):
        """
        Runs ONCE.
        Catches the 'srv_api_key' for setup.
        Catches 'ctxt_ip' (and others) just to remove them
        before calling super().
        """
        print(f"  MyService __init__: Service is being CREATED.")
        print(f"  > Setting API Key to: {srv_api_key}")
        
        # 'name' is in kwargs, passed by the metaclass
        super().__init__(**kwargs) 
        
        self.api_key = srv_api_key
        self.context_data = {}
```

### Step 4: Implement `_init_service` (Per-Access Hook)

This method is **called every time** the service is accessed, including the first time (right after
`_init_post_action`).

* Use parameters prefixed with `ctxt_` (context) for per-access logic.
* Use `**kwargs` to safely ignore the one-time `srv_` parameters that are also passed in.

```python
class MyService(ttTonic):
    _tt_is_service = "MyUniqueService"

    def __init__(self, srv_api_key, ctxt_ip=None, **kwargs):
        # ... (from Step 3) ...
        print(f"  MyService __init__: Service is being CREATED.")
        print(f"  > Setting API Key to: {srv_api_key}")
        super().__init__(**kwargs) 
        self.api_key = srv_api_key
        self.context_data = {}

    def _init_service(self, context, ctxt_ip, **kwargs):
        """
        Runs EVERY time.
        Catches 'context' and 'ctxt_ip'.
        Ignores 'srv_api_key' (which is in **kwargs).
        """
        if context is None:
            return
            
        print(f"  MyService _init_service__: Context '{context.name}' "
              f"is accessing from IP '{ctxt_ip}'")
        
        # Store context-specific data
        self.context_data[context.id] = {'ip': ctxt_ip}

    def get_ip_for(self, context):
        return self.context_data.get(context.id, {}).get('ip')
```

### **A Critical Warning on Context and Lifecycle**

> **BE AWARE:** When creating a service, be careful with its `context`. If you create a service *within the context of
another essence* (e.g., `MyService(context=another_task)`), it becomes a child of that essence via the `bind` mechanism.
>
> If `another_task` is finished, it will call `finish()` on all its children. This **will finish and unregister your
service singleton for everyone**.
>
> **Recommendation:** It is almost always better to create services with `context=None` (making them top-level) or from
a single, persistent root task (e.g., your "formula" or main application runner).

---

# 5. Using a Service Base Class

Sometimes you want to use a service, without knowing what kind of service implementation is used. For instance when
you use an `ConnectionService`, that can be een `IpConnectionService` or `BluToothConnectionService`.

## 5.1 How to
For that create a service base class (or interface) that provides a universal contract for a specific type of 
functionality (e.g., "connecting" or "logging"). This approach is central to creating a decoupled and 
maintainable architecture.

In the formula the implementation of a specific service is started. The service name wil be the same for every
implementation. Tonics that are using the service should depend on the universal base class and use the service name.
The specific service, with that name, will be used due to the singleton service implementation. 


## 5.2 Example: ConnectionService

Let's walk through an example with a universal `ConnectionService` (the base class) and two specific implementations:
`IpConnectionService` and `BluToothConnectionService`.

### 1. Defining the Services

First, we define the abstract base class and the concrete implementations. The Tonics will only know about
`ConnectionService`.

```python
# === services/connection_service.py ===
from TaskTonic import *


class ConnectionService(ttCatalyst):
  """
  The universal base class (interface) for all connection services.
  Tonics will depend on this class.
  
  It defines the 'contract' that all connection services must follow.
  """
  _tt_is_service = 'connection_service'

  def ttsc__connect(self):
    pass

  def ttsc__disconnect(self):
    pass

  def ttsc__transmit(self, data):
    pass


# === services/ip_connection.py ===
from .connection_service import ConnectionService


class IpConnectionService(ConnectionService):
  """
  Specific implementation for IP-based connections (e.g., WiFi, Ethernet).
  """

  def __init__(self, context=None, host: str, port: int):
    super().__init__(context=context, log_mode='quiet')
    self.host = host
    self.port = port
    self.status = "Disconnected"
    self.log(f"IpConnectionService: Initialized for {host}:{port}")
    self.to_state('disconnected')

  def ttsc__disconnected__connect(self):
    # Specific logic for IP connection
    self.log(f"Connecting via IP to {self.host}:{self.port}...")
    # ... implementation details ...
    self.status = f"Connected (IP to {self.host})"
    self.log("IpConnectionService: Established.")
    self.to_state('connected')

  def ttsc__connected__disconnect(self):
    self.log("Disconnecting IP connection.")
    self.to_state('disconnected')

  def ttsc__connected__transmit(self, data):
    self.log(f'Tranmitting: {data}')
    # ... implementation details ...

  def ttse__connected__on_exit(self):
# implement disconnection


# === same for all other connection services

# === myTonic 
class MyTonic(ttTonic):
  def ttse__on_start(self):
    from services.connection_service import ConnectionService
    self.conn = ConnectionService() # use the service base class
    self.conn.ttsc__connect()


#  == Formula
class MyFormula(ttFormula):
  def creating_starting_tonics(self):
    IpConnectionService(context=-1, 'localhost', 123456) # startup the ip connection service
    MyTonic(context=-1)

```

## 6. Full Example

Here is a complete example showing how two different tasks (`RootTask` and `WorkerTask`) access the same service.

```python
from TaskTonic import *

class RootTask(ttTonic):
    """A standard, non-service task."""
    pass
    
class WorkerTask(ttTonic):
    """Another standard, non-service task."""
    pass

class NetService(ttTonic):
    """
    A singleton service that manages a network resource.
    """
    
    # 1. Set the unique service name
    _tt_is_service = "NetworkManager"
    
    def __init__(self, srv_host_url, ctxt_port=None, **kwargs):
        """
        Runs ONCE to configure the service.
        """
        self.log(f"  NetService __init__: CONNECTING to {srv_host_url}...")
        
        # Pass standard args (name, context) up to ttEssence
        super().__init__(**kwargs) 
        
        self.host_url = srv_host_url
        self.context_ports = {}

    def _init_service(self, context, ctxt_port, **kwargs):
        """
        Runs EVERY time to register context-specific info.
        """
        self.ttsc__new_service_entry(context, ctxt_port)
                
    def ttsc__new_service_entry(context, ctxt_port):
        self.log(f"  NetService _init_service__: Context '{context.name}' "
                 f"registered on port {ctxt_port}.")
        self.context_ports[context.id] = ctxt_port
        
# --- Example Usage ---
if __name__ == "__main__":

    print("--- 1. Creating Tasks ---")
    root = RootTask(name="Root")
    worker = WorkerTask(name="Worker", context=root)

    print("\n--- 2. RootTask requests the NetService ---")
    # This is the FIRST call. __init__ will run.
    # We create it with context=None as recommended.
    service1 = NetService(
        context=None,
        srv_host_url="httpsa://api.tasktonic.com",
        ctxt_port=8080
    )
    # Manually log access for root
    service1._init_service(context=root, ctxt_port=8080)


    print("\n--- 3. WorkerTask requests the SAME NetService ---")
    # This is the SECOND call. __init__ is SKIPPED.
    service2 = NetService(
        context=worker,
        srv_host_url="[https://api.IGNORED.com](https://api.IGNORED.com)", # This is ignored
        ctxt_port=9090
    )
    
    print("\n--- 4. Verification ---")
    print(f"service1 is service2: {service1 is service2}")
    print(f"Service Host URL: {service1.host_url}")
    print(f"Root's Port: {service1.context_ports[root.id]}")
    print(f"Worker's Port: {service1.context_ports[worker.id]}")
## `File: _documents\old_documents_not_matching_the_code\finisching flow.md`
# TaskTonic Framework: Developer Manual

## 1. Introduction

**TaskTonic** is a Python framework designed to manage complex, asynchronous applications with ease. It allows you to
build responsive UIs, sensor networks, and simulation engines without the headache of traditional multi-threading.

### The Philosophy

The framework uses an "Alchemist" metaphor. Instead of calling methods directly, you create "Tonics" (agents) that
emit "Sparkles" (atomic actions), all driven by a "Catalyst" (engine).

**Key Benefits:**

* **Event-Driven:** "Don't call us, we'll call you."
* **Thread Safety:** Tasks are processed sequentially by the Catalyst, removing race conditions.
* **State Machines:** Tonics have built-in state management.
* **Hierarchy:** Automatic lifecycle management for parent/child tasks.

---

## 2. Core Concepts (The Lexicon)

Understanding the vocabulary is crucial to using TaskTonic effectively.

| Term | Component | Description |
| :--- | :--- | :--- |
| **Formula** | `ttFormula` | The "recipe" for your app. The entry point where you define initial tasks. |
| **Tonic** | `ttTonic` | The worker agent. A stateful object that executes tasks. |
| **Sparkle** | Method | A specific unit of work (a method) inside a Tonic. |
| **Catalyst** | `ttCatalyst` | The engine. It pulls "Sparkles" from a queue and executes them. |
| **Ledger** | `ttLedger` | The registry that tracks all active Tonics. |

### Architecture Overview

```mermaid
graph TD
    Queue[Catalyst Queue]
    Cat[Catalyst Engine]
    
    subgraph "Tonic (Agent)"
        S1[Sparkle: on_start]
        S2[Sparkle: process_data]
        State[State Machine]
    end

    Formula -->|Creates| Cat
    Formula -->|Creates| Tonic
    Tonic -->|Places Work| Queue
    Cat -->|Pulls Work| Queue
    Cat -->|Executes| S1
    Cat -->|Executes| S2
```

**

---

## 3. Getting Started

### A Simple "Hello World"

To create an application, you need a `Tonic` (the logic) and a `Formula` (the launcher).

```python
from TaskTonic import ttTonic, ttFormula

# 1. Define your Tonic (The Worker)
class HelloWorldTonic(ttTonic):
    def ttse__on_start(self):
        """Runs automatically when the Tonic starts."""
        self.log("Hello TaskTonic!")
        self.finish() # Signal that work is done

    def ttse__on_finished(self):
        """Runs automatically during cleanup."""
        self.log("Goodbye!")

# 2. Define the Formula (The Application)
class MyApp(ttFormula):
    def creating_starting_tonics(self):
        # Create the tonic with no parent (context=-1)
        HelloWorldTonic(context=-1)

# 3. Run it
if __name__ == "__main__":
    MyApp()
```

**

---

## 4. The Tonic: Deep Dive

The `ttTonic` is the heart of the framework. Its behavior is defined by **Sparkles**. You do not register callbacks
manually; instead, you name your methods according to a strict convention.

### 4.1 Naming Convention (Sparkles)

The framework scans your class for methods with specific prefixes:

* **`ttsc__<name>` (Command):** Public methods meant to *start* an action (e.g., `ttsc__process`).
* **`ttse__<name>` (Event):** Public methods meant to *react* to an event (e.g., `ttse__on_start`).
* **`tts__<name>` (Internal):** Internal steps, not meant for public access.
* **`ttsc_<state>__<name>`:** A command that only runs when the Tonic is in a specific `<state>`.

> **Note:** When you call `self.ttsc__do_work()`, it does not run immediately. It places a "work order" on the Catalyst
queue.

### 4.2 Built-in State Machine

Every Tonic is a state machine. You can transition states using `self.to_state('new_state')`.

**State Routing:**
If you call `ttsc__flip()`, the framework looks for a handler in this order:

1. `ttsc_<current_state>__flip` (Specific to current state)
2. `ttsc__flip` (Generic fallback)
3. `_noop` (Do nothing)

**Example: A Light Switch**

```python
class LightSwitch(ttTonic):
    def ttse__on_start(self):
        self.to_state('off')

    # The public command
    def ttsc__flip(self):
        pass 

    # Logic when State is OFF
    def ttsc_off__flip(self):
        self.log("Turning ON")
        self.to_state('on')

    # Logic when State is ON
    def ttsc_on__flip(self):
        self.log("Turning OFF")
        self.to_state('off')
```

**

### 4.3 Hierarchy & Context (Binding)

Tonics are hierarchical. When a Tonic creates a child (using `bind`), it becomes the child's **Context**.

* **Binding:** `self.child = WorkerTonic()` auto binds to current context (in sparkle_stack)
* **Automatic Cleanup:** If a parent finishes, all children are automatically finished.

---

## 5. Services (Singleton Pattern)

Services are specialized Tonics used for shared resources (Logging, Database, Hardware). They follow the Singleton
pattern: only one instance exists per application.

### 5.1 Creating a Service

Inherit from `ttTonic` and set `_tt_is_service`.

```python
class DatabaseService(ttTonic):
    _tt_is_service = "DB_Service_Unique_Name"

    def __init__(self, srv_db_url, **kwargs):
        """Runs ONCE when the VERY FIRST instance is created."""
        super().__init__(**kwargs)
        self.db_url = srv_db_url
        self.connect()

    def _init_service(self, context, ctxt_user_id, **kwargs):
        """Runs EVERY TIME the service is accessed/bound."""
        self.log(f"User {ctxt_user_id} accessed DB.")
```

**

### 5.2 Using a Service

Any Tonic can access the service. The first call creates it; subsequent calls return the existing instance.

```python
# In some worker Tonic
self.db = DatabaseService(
                    srv_db_url="sqlite:///",   # Used only on 1st creation
                    ctxt_user_id="Worker_1")   # Used every time
```

---

## 6. DataShare: Managing State

`DataShare` is a thread-safe, hierarchical data store (like a Registry or Redux store). It allows complex data access
via path strings.

### 6.1 Basic Usage

```python
ds = DataShare()

# Setting Data
ds.set('user/preferences/theme', 'dark')
ds.set('user/roles[]', 'admin') # Append to list

# Getting Data
theme = ds.get('user/preferences/theme')
```

### 6.2 Advanced Views

DataShare nodes store both a value AND sub-keys. You can control what you retrieve:

* `get(..., get_value=0)`: **Clean View** (Default). Returns simple Python dicts/values.
* `get(..., get_value=1)`: **Raw View**. Shows internal structure `{'theme': {'_value': 'dark'}}`.

### 6.3 Subscriptions

You can observe changes in data:

```python
def on_theme_change(key, old, new):
    print(f"Theme changed to {new}")

ds.subscribe('user/preferences', on_theme_change)
```

---

## 7. Advanced Features

### 7.1 Timers

Don't use `time.sleep()`. Use timers to keep the Catalyst running smoothly.

```python
from TaskTonic import ttTimerRepeat

# Bind a timer to call 'ttsc__tick' every 1 second
ttTimerRepeat(seconds=1, sparkle_back=self.ttsc__tick)
```

**

### 7.2 The Catalyst Loop

The Catalyst runs a loop that:

1. Pulls a work order from `catalyst_queue`.
2. Finds the target Tonic.
3. Calls `_execute_sparkle`.
4. Repeats.
   *It manages lifecycle, ensuring Tonics are registered on startup and deregistered on finish.*

---

## 8. Summary Checklist for Developers

1. **Inheritance:** Always inherit from `ttTonic`.
2. **Naming:** Use `ttsc__` for commands and `ttse__` for events.
3. **State:** Use `to_state()` to switch contexts; use `ttsc_state__name` for specific logic.
4. **Blocking:** **Never block** execution (no long `sleep` or heavy computation in the main thread). Use sub-tonics or
   threads for heavy lifting.
5. **Hierarchy:** Create ttEssence (or subclass) creates children so cleanup automatic.




```mermaid
zenuml
title Finishing ttEssence (static)
c as Context
e as Essence
b as Binding
l as ledger

//finish from context (C); no bindings
c->e.finish(C) {
    e->e._finished() {
        e->l.unregister()
    }

}
//finish from context (C); with bindings
c->e.finish(C) { 
    e->b.finish(E) {
        b->b._finished() {
            b->l.unregister()
        }
        b->e.binding_finished()
        {
           e->l.unregister()
       }
    }
    
}
```

When essence.finish is called the essence will check if it has 1 or more bindings. If not the essencese is finished and unregistered in the ledger.
If the essence does have a binding, the finish of that binding is called. After calling unregister the method binding_finished of its context is called (the context is the initiating essence). In that method the essence unbinds and checks if there are bindings left. If not it will unregister it self.

There is one extra functionality, not in the timeline. If the essence is a service and the calling context is in its service context list, that context is removed and binding finished is called. However, when the creating context is finishing the service, all service bindings get notified with binding_finished, and the service finishes as normal.

## Tonic finish

2 system sparkles are created. _ttss_finish wil be called from the (rewriten) finish method. In the sparkle, super().finish is called. The same for _ttss_binding finished called from binding_finished.

Besides that, in _ttss__finish the sparkle execution wil be set to the system sparkles only mode. The tonic is finishing and dont execpt normal commands or events.


## `File: _documents\old_documents_not_matching_the_code\ttStore.md`
# ttStore & Store/Item: Central Data Repository

This documentation describes the functionality of the `Store` and `Item` classes and their integration within TaskTonic
via `ttStore`.

## Introduction

In complex applications, it is essential to share data between different components in a structured and accessible way.
`ttStore` functions as a **Central Data Repository**. It offers a hierarchical storage structure (comparable to a file
system or a nested dictionary) that is:

1. **Centralized:** A single source of truth for parameters, sensor values, and configurations.
2. **Reactive:** Components can subscribe to changes in specific data paths.
3. **Flexible:** Data can be accessed via absolute paths or relative pointers (`Item`).

---

## Concepts: Store vs. ttStore

The system consists of two layers that can also be used **independently**.

### 1. The Core: `Store` and `Item`

The `Store` is the pure data container. It is a standalone class that holds the data and provides methods to read or
write data via paths (e.g., `'sensors/temp/value'`).

The `Item` is a smart "pointer" or "cursor" to a specific location in the `Store`. It allows for relative navigation
without needing to know the full absolute path.

> **Note:** `Store` and `Item` can be used outside of TaskTonic in any Python project requiring a powerful, hierarchical
data structure.

### 2. The Service: `ttStore`

`ttStore` is the TaskTonic wrapper around a `Store`. It transforms the store into a **Service** within the TaskTonic
ecosystem. This adds capabilities such as:

* **Event-driven updates:** Automatically notify other Tonics (like UI or controllers) upon changes.
* **Service Binding:** Easily linked to other Tonics via `self.bind()`.

---

## API Reference & Methods

Below is an overview of the most important methods for data manipulation and navigation.

### Dictionary Access (`[]` Syntax)

For convenience, `ttStore` and `Item` support standard Python dictionary syntax.

* **Reading:** `val = store['path']`
    * Equivalent to `.get('path')`.
    * Returns `None` if the path does not exist (unlike standard Python dicts which raise KeyError).
* **Writing:** `store['path'] = val`
    * Equivalent to `.set([('path', val)])`.
    * Triggers updates immediately (unless inside a `group`).

**Example:**

```python
# Read
current_limit = self.twin['parameters/temp_limit']

# Write
self.twin['parameters/temp_limit'] = 12.0
```

### Writing Data (`set`, `.v`, `.append`)

#### `set(data)`

Writes one or multiple values to the store. It accepts a `dict` or an `Iterable` (list/tuple) of tuples.

* **Usage:** Initialization, bulk updates, or when you need to write multiple values atomically.
* **Smart Paths:**
    * `#`: Creates a new unique entry (auto-increment list).
    * `./`: Refers to the last created entry (useful for setting properties of an item).

**Example:**

```python
# Initialize a store with parameters and sensors
self.twin.set([
    ('parameters/update_freq', 2),     # Set update frequency to 2
    ('sensors/#', 'temp'),             # Create new sensor 'temp'
    ('sensors/./value', 15.0),         # Set value of THAT sensor
    ('sensors/./unit', '℃'),           # Set unit of THAT sensor
])
```

#### `.v` (Value Property via Item)

If you hold an `Item` object (a pointer to a location), you can read and write directly via the `.v` property. This is
the most efficient way to manipulate data if you already have the Item.

**Example:**

```python
# Assume we have a pointer (Item) to the sensor value
sensor_val_item = self.twin.at('sensors/#0/value')

# Write a new value
sensor_val_item.v = 22.5
```

#### `append(value)` (via Item) or `append(path, value)` (via Store)

Adds a new item to a list. This is a cleaner, more pythonic alternative to using the `'path/#'` syntax when adding
single items.

* **Via Item:** `item.append(value)`
* **Via Store:** `store.append(path, value)`

**Example:**

```python
# Append via Store (adds 'System Started' to the 'logs' list)
self.twin.append('logs', 'System Started')

# Append via Item
log_item = self.twin.at('logs')
log_item.append('User logged in')
```

### Reading Data (`get`, `at`)

#### `get(path, default=None)`

Retrieves the value of a specific path. If the path does not exist, the `default` value is returned.

**Example:**

```python
freq = self.twin.get('parameters/update_freq', 5)  # Default 5 if not found
```

#### `at(path) -> Item`

Returns an `Item` object pointing to the location `path`. This is **more powerful** than `get` because it allows further
navigation from that point.

**Example:**

```python
# Get a pointer (Item) to the first sensor
sensor_item = self.twin.at('sensors/#0')

# Read values via the Item
print(sensor_item['value'].v)  # Prints: 15.0
```

### Navigation (`Item` objects)

An `Item` object acts as a smart window onto your data.

* **`item['child']`**: Navigate to a sub-item.
    ```python
    val = sensor_item['value'].v
    ```
* **`item.parent`**: Returns an `Item` to the parent.
    ```python
    root_sensors = sensor_item.parent # Now points to 'sensors'
    ```
* **`item.list_root`**: If the item is part of a list (like sensors), this returns the item itself, regardless of how
  deep you are in the hierarchy.
    ```python
    # If located at 'sensors/#0/value', list_root returns 'sensors/#0'
    sensor_name = sensor_item.list_root.v # Returns e.g., 'temp'
    ```

#### `.children(prefix=None)`

Returns an **iterator** (not a list) of `Item` objects that are direct children of the current item.

* **Why an iterator?** It is memory efficient (lazy evaluation). If you have thousands of items, it doesn't create
  objects for all of them unless you consume them.
* **prefix:** Optional string to filter children (e.g., useful if you have different types of lists in one folder).

**Example 1: Converting to a list**
If you need index access or the length, convert it to a list explicitly.

```python
sensors = self.twin.at('sensors')
sensor_list = list(sensors.children())
print(f"Count: {len(sensor_list)}")
```

**Example 2: Iterating directly (Efficient)**
Searching for a specific sensor without creating a full list in memory.

```python
target_sensor = None
for item in self.twin.at('sensors').children():
    if item.v == 'humidity':
        target_sensor = item
        break
```

### Reactivity (`subscribe`)

Only available in `ttStore`. This allows subscribing a method to data changes.

#### `subscribe(path, callback)`

* **path:** The path to monitor (e.g., `'sensors'`).
* **callback:** The method called upon change.

The callback receives a list of `updates`. Each update is a tuple: `(path, new_value, old_value, source)`.

**Example:**

```python
def ttse__on_start(self):
    # Listen to anything changing under 'sensors'
    self.twin.subscribe("sensors", self.ttse__on_sensor_update)

def ttse__on_sensor_update(self, updates):
    for path, new, old, source in updates:
        print(f"Sensor update at {path}: {old} -> {new}")
```

### Utilities (`dumps`, `group`, `source`)

#### `dumps()`

Returns a string representation of the entire store (useful for debugging).

```python
print(self.twin.dumps())
```

#### `group(notify=True, source_id=None)` & `source(source_id)`

Context managers to control how updates are processed.

1. **`group(notify=False)`**: Performs updates atomically.

* **Usage:** Batch initialization. No events are fired until the block ends (or never if `notify=False`).

  ```python
  with self.twin.group(notify=False):
      self.twin.set(...) 
  ```

2. **`source(source_id)` / `group(..., source_id=...)`**:

* **Usage:** Identifying *who* made the change. This is crucial for bidirectional sync (e.g., connecting a GUI slider to
  a value).
* If a GUI updates the Store, the Store notifies the GUI. You want the GUI to ignore that notification to prevent an
  infinite loop.

  ```python
  # Example: Updating from a specific source (e.g., 'GUI')
  with self.twin.source('GUI'):
      self.twin['parameters/speed'] = 50
  
  # In the callback, you can check the source:
  def on_change(self, updates):
      for path, new, old, src in updates:
          if src == 'GUI':
              continue # Ignore changes I made myself
          # Update GUI display...
  ```

---

## Performance & Best Practices

Although `ttStore` is powerful, consider the following points for optimal performance and clean code.

### 1. Batch Updates with `group`

When modifying a lot of data simultaneously (e.g., during startup or reset), always use
`with self.group(notify=False):`.

* **Reason:** Without this, every single write action triggers all subscribers immediately. `group` prevents this "
  update storm".

### 2. Efficiency of `Item`

If you need to read or write the same value frequently in a loop (e.g., a timer), retrieve the `Item` **once** during
`__init__` or `on_start`, and cache it.

* **Inefficient:** Calling `self.twin.get('sensors/#0/value')` in every cycle (must parse the path string every time).
* **Efficient:**
    ```python
    # In __init__:
    self.temp_val_item = self.twin.at('sensors/#0/value')

    # In timer loop:
    self.temp_val_item.v += 0.1
    ```

### 3. Data Types

The Store is not strictly typed (it is Python), but consistency is key. If a path starts as a `float` (`15.0`), try to
keep it that way and do not suddenly change it to a `string` ("15"), unless your application logic specifically handles
this.

---

## Example Implementation

Below is a full integration where `MyProcess` writes data and `OperatorInterface` reacts to that data via the
`DigitalTwin` store.

```python
from TaskTonic import *
from TaskTonic.ttTonicStore import ttStore
import random


# --- The Data Repository Service ---
class DigitalTwin(ttStore):
    _tt_is_service = "digital_twin"  # Service name for binding

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_record['auto_finish'] = True

    def _init_post_action(self):
        super()._init_post_action()
        # Use group(notify=False) for performance during init
        with self.group(notify=False):
            # Because the set method uses Iterable, both tuples (()) and lists [] are valid.
            self.set((
                ('parameters/update_freq', 2),
                ('parameters/temp_limit', 10),
                ('sensors/#', 'temp'),         # Create sensor 0
                ('sensors/./value', 15.0),
                ('sensors/./unit', '℃'),
                ('sensors/./high_alarm', False),
                ('sensors/#', 'humidity'),     # Create sensor 1
                ('sensors/./value', -1),
            ))

        self.log(f"Digital Twin is initialized\n{self.dumps()}")


# --- The Observer (e.g., GUI or Logger) ---
class OperatorInterface(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        # Bind to the service
        self.twin = DigitalTwin()

    def ttse__on_start(self):
        # Subscribe to sensor changes
        self.twin.subscribe("sensors", self.ttse__on_sensor_update)
        # Schedule parameter update and end of program
        ttTimerSingleShot(5, sparkle_back=self.ttse__on_parm_update)
        ttTimerSingleShot(8, sparkle_back=self.ttse__on_end_program)

    def ttse__on_sensor_update(self, updates):
        for path, new, old, source in updates:
            # Use .at(path) to get an Item for smart navigation
            # .list_root automatically navigates up to the sensor item (e.g., 'sensors/#0')
            sensor_item = self.twin.at(path).list_root

            # Retrieve name and value via the item
            name = sensor_item.v
            val = sensor_item['value'].v
            unit = sensor_item.get('unit', '')

            self.log(f"UPDATE OF SENSOR {name}: {val:.3f}{unit}")

    def ttse__on_parm_update(self, tmr):
        self.twin['parameters/update_freq'] = .5

    def ttse__on_end_program(self, tmr):
        self.finish()


# --- The Controller (Process Logic) ---
class MyProcess(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        self.my_record['auto_finish'] = True
        self.twin = self.bind(DigitalTwin)

        # Performance optimization: Cache the item pointer
        # This avoids parsing the path string in every loop cycle
        self.temp_sens_item = self.twin.at('sensors/#0')

    def ttse__on_start(self):
        self.twin.subscribe("parameters", self.ttse__on_param_update)
        # Start a timer based on a parameter from the store
        freq = self.twin.get('parameters/update_freq', 5)
        self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__on_param_update(self, updates):
        for path, new, old, source in updates:
            if path == 'parameters/update_freq':
                self.utmr.stop()
                # Restart timer with new frequency
                freq = self.twin.get('parameters/update_freq', 5)
                self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__update_timer(self, tmr):
        # Writing directly via the cached item is very efficient
        self.temp_sens_item['value'].v += random.uniform(-2, 2)


# --- App Configuration ---
class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        DigitalTwin()
        OperatorInterface()
        MyProcess()


if __name__ == '__main__':
    myApp()
```## `File: _documents\old_documents_not_matching_the_code\developer documentation.md`
# TaskTonic Framework: Developer Documentation

## 1. Philosophy & Metaphor

TaskTonic is a Python framework designed to manage application complexity through a unique concurrency model.

The core philosophy is based on the **Tonic**. Think of your running application as a glass of tonic. It comes to life through **Sparkles**—not electrical sparks, but **bubbles** rising in a liquid.

- **The Flow:** Code is executed in small, atomic units called *Sparkles*.
- **The Fizz:** When these Sparkles flow continuously, the application "fizzes" with activity. It feels like a single, cohesive whole, even though it may be performing multiple logical processes simultaneously.
- **The Rule:** A Sparkle must be short-lived. If one bubble takes too long to rise (blocking code), the flow stops, and the fizz goes flat. In practice, this is rarely an issue, as most software processes are reactive chains of short events.

This architecture allows you to write highly responsive, concurrent applications (like UIs or IoT controllers) without the race conditions and headaches of traditional multi-threading.

---

## 2. Core Architecture

The framework is built on a strict hierarchy of classes.

| Component    | Class        | Description                                                                                                                                                                         |
| ------------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Liquid**   | `ttLiquid`   | **(Formerly `ttEssence`)** The base substance. It handles identity, hierarchy (parent/child relationships), and lifecycle management in the `Ledger`. It is the passive foundation. |
| **Tonic**    | `ttTonic`    | The active ingredient. Inherits from `ttLiquid`. It adds the ability to "sparkle" (execute code), manage state (State Machines), and log activity.                                  |
| **Catalyst** | `ttCatalyst` | The engine that makes the Tonic fizz. It owns the execution thread and the queue. It pulls Sparkles one by one and executes them.                                                   |
| **Formula**  | `ttFormula`  | The recipe. The entry point of your application where you define the initial mix of Tonics and configuration settings.                                                              |

---

## 3. The Tonic (`ttTonic`)

The `ttTonic` is where you write your application logic. It uses **introspection** to automatically bind your methods to the execution queue based on their names.

### 3.1 Sparkle Naming Convention

You do not register callbacks manually. You simply name your methods using specific prefixes.

- **`ttsc__` (Command):** *Public Command.* Call this to request an action from outside the class.
  - *Example:* `my_tonic.ttsc__start_process()`
- **`ttse__` (Event):** *Public Event.* Call this to react to an event (like a timer or UI click).
  - *Example:* `ttse__on_timer(info)`
- **`tts__` (Sparkle):** *Internal.* Private logic chunks used to break up large tasks.
  - *Example:* `self.tts__step_two()`
- **`_ttss__` (System):** Reserved for framework lifecycle hooks (startup/shutdown).

> **Important:** When you call a sparkle method (e.g., `self.tts__calculate()`), it does **not** execute immediately. It places a "bubble" (work order) on the Catalyst queue. It will be executed when the Catalyst reaches it in the stream.

### 3.2 State Machines

Every `ttTonic` is a built-in State Machine. You can organize your code by defining which Sparkles are valid in which state.

**Changing State:** Use `self.to_state('new_state_name')`.

**State-Specific Sparkles:** You can prefix a Sparkle with a state name: `prefix_state__name`.

- **Specific:** `ttsc_idle__start()` — Only runs if the Tonic is in the `idle` state.
- **Generic:** `ttsc__start()` — Runs in any state (unless a specific version exists).
- **Fallback:** If called in a state where no handler exists, the call is ignored (the bubble pops harmlessly).

### 3.3 Lifecycle & Termination

To ensure proper cleanup and hierarchy management, you must use the framework's lifecycle methods.

- **`ttsc__finish()`**: **The Stop Command.** Call this to stop the Tonic. It initiates the graceful shutdown sequence:
  1. Stops the State Machine (transitions to `-1`).
  2. Sets the Tonic to "Finishing Mode" (ignoring new standard sparkles).
  3. Triggers the `ttse__on_finished` event.
  4. Cleans up children/infusions and removes the Tonic from the Ledger.
- **`ttse__on_start()`**: Called immediately after the Tonic is created and initialized.
- **`ttse__on_enter()`**: Called whenever entering a new state.
- **`ttse__on_exit()`**: Called whenever leaving a state.
- **`ttse__on_finished()`**: Called *during* the shutdown sequence (triggered by `ttsc__finish()`). Use this to close resources like files or sockets before the object is destroyed.

---

## 4. Timers and Flow Control

Since Sparkles must be short to keep the "fizz" alive, you cannot use `time.sleep()`. Instead, use the built-in Timers to handle time-bound logic.

```python
from TaskTonic import ttTonic, ttTimerSingleShot

class MyProcess(ttTonic):
    def ttse__on_start(self):
        self.log("Starting process...")
        # Don't sleep! Schedule a sparkle for later.
        ttTimerSingleShot(seconds=2.5, name='tm_continue')

    def ttse__on_tm_continue(self, info):
        self.log("2.5 seconds have passed. Continuing...")
        # Done with work? Stop the tonic.
        self.ttsc__finish()
```

---

## 5. Services (Singletons)

The framework uses the `ttLiquid` metaclass to manage Singleton Services effortlessly. A Service is a Tonic that exists only once but can be accessed from anywhere.

**Defining a Service:** Set the `_tt_is_service` attribute.

```python
class Database(ttTonic):
    _tt_is_service = "db_service" # Unique ID

    def __init__(self, **kwargs):
        # Runs ONLY once (first creation)
        super().__init__(**kwargs)
        self.connect_db()

    def _init_service(self, context, **kwargs):
        # Runs EVERY time the service is requested
        self.log(f"Accessed by {context.name}")
```

**Using a Service:** Simply instantiate it. If it exists, you get the running instance.

```python
# In any other Tonic:
my_db = Database() # Returns the existing Singleton
```

---

## 6. Example: The Traffic Light

This example demonstrates `ttLiquid` hierarchy, Sparkles, and State Machine logic.

```py
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

# 


