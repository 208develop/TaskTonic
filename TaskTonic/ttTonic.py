from TaskTonic.ttEssence import ttEssence
import re, time, threading, copy


class ttTonic(ttEssence):
    """
    A robust, passive framework class for creating task-oriented objects (Tonics).

    This class automatically discovers methods (sparkles) based on naming conventions,
    handles state management, and provides a structured logging system. All sparkle
    types (ttsc, ttse, tts, _tts) are handled uniformly by placing a 'work order'
    on a queue, which is then processed by an external execution loop.
    """

    def __init__(self, name=None, context=None, log_mode=None, fixed_id=None):
        """
        Initializes the Tonic instance, discovers sparkles, and calls startup methods.

        :param context: The context in which this tonic operates.
        :param name: An optional name for the tonic. Defaults to the class name.
        :param fixed_id: An optional fixed ID for the tonic.
        """
        super().__init__(name=name, context=context, log_mode=log_mode, fixed_id=fixed_id)

        # bind to catalyst
        if not hasattr(self, 'catalyst_queue'):
            self.catalyst = context.catalyst if hasattr(context, 'catalyst') \
                else self.ledger.get_essence_by_id(0)  # main catalyst
            self.catalyst_queue = self.catalyst.catalyst_queue  # copy queue for (a bit) faster acces

            self.log(None, {'catalyst': self.catalyst.name})
            self.catalyst._ttss__startup_tonic(self.id)

        # Init internals
        self.finishing = False

        # Discover all sparkles and build the execution system.
        self.state = -1  # Start with no state (-1)
        self._pending_state = -1
        self._on_enter_handler = self._noop
        self._on_exit_handler = self._noop
        self._sparkle_init()

    def _post_init_action(self):
        super()._post_init_action()

        # After initialization is completed, queue the synchronous startup sparkles.
        if hasattr(self, '_ttss__on_start'):
            self._ttss__on_start()
        if hasattr(self, 'ttse__on_start'):
            self.ttse__on_start()

    def _sparkle_init(self):
        """
        Performs a one-time, intensive setup to discover all sparkles, build
        the dispatch system, and create the public-facing callable methods. This
        is the core of the Tonic's introspection and setup logic.
        """

        # Define the regular expressions used to identify different sparkle types.
        state_pattern = re.compile(r'^(ttsc|ttse|tts|_tts|_ttss)_([a-zA-Z0-9_]+)__([a-zA-Z0-9_]+)$')
        general_pattern = re.compile(r'^(ttsc|ttse|tts|_tts|_ttss)__([a-zA-Z0-9_]+)$')

        # --- Phase 1: Discover all implementations from the class hierarchy (MRO) ---
        specific_impls, generic_impls = {}, {}
        states, sparkle_names = set(), set()
        prefixes_by_cmd = {}

        # Iterate through the MRO (Method Resolution Order) in reverse to ensure
        # that methods in child classes correctly override those in parent classes.
        for cls in reversed(self.__class__.__mro__):
            if cls in (ttEssence, object):
                continue
            for name, method in cls.__dict__.items():
                s_match = state_pattern.match(name)
                g_match = general_pattern.match(name)
                if s_match:
                    # Found a state-specific sparkle (e.g., 'ttsc_waiting__process')
                    prefix, state_name, sp_name = s_match.groups()
                    specific_impls[(prefix, state_name, sp_name)] = method
                    states.add(state_name)
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)
                elif g_match:
                    # Found a generic sparkle (e.g., 'ttsc__initialize')
                    prefix, sp_name = g_match.groups()
                    generic_impls[(prefix, sp_name)] = method
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)
                    # Specifically find and assign the global handlers
                    if f"{prefix}__{sp_name}" == 'ttse__on_enter':
                        self._on_enter_handler = method
                    elif f"{prefix}__{sp_name}" == 'ttse__on_exit':
                        self._on_exit_handler = method

        # --- Phase 2: Build fast lookup tables for states ---
        self._state_to_index = {name: i for i, name in enumerate(sorted(list(states)))}
        self._index_to_state = sorted(list(states))
        num_states = len(self._index_to_state)

        # --- Phase 3: Create and bind all public-facing dispatcher methods ---
        sparkle_list = []
        for sp_name in sparkle_names:
            is_state_aware = any(sp_name == key[2] for key in specific_impls.keys())
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
                        specific_handler = specific_impls.get((prefix, state_name, sp_name))
                        if specific_handler:
                            handler_list[state_idx] = specific_handler

                    def create_put_state_sparkle(_list, _name):
                        # Create a state execution that will select the correct method by state from the list at
                        #  runtime and create the put_state_sparkle to put if on the queue
                        def create_executer():
                            def execute_state_sparkle(self, *args, **kwargs):
                                state_sparkle = _list[self.state]
                                self.log(None, {'state': self.state})
                                state_sparkle(self, *args, **kwargs)
                            execute_state_sparkle.__name__ = _name
                            return execute_state_sparkle

                        def put_state_sparkle(self, *args, **kwargs):
                            if threading.get_ident() != self.catalyst.thread_id:
                                args = tuple((arg if callable(arg) else copy.deepcopy(arg)) for arg in args)
                                kwargs = {key: (value if callable(value) else copy.deepcopy(value))
                                             for key, value in kwargs.items()}
                            self.catalyst_queue.put((self, create_executer(), args, kwargs))
                        return put_state_sparkle

                    # Bind the new put_state_sparkle function to the instance, making it a method.
                    setattr(self, interface_name, create_put_state_sparkle(handler_list, interface_name).__get__(self))

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
                            self.catalyst_queue.put((self, _method, args, kwargs))
                        return put_sparkle

                    # Bind the new put_sparkle function to the instance, making it a method.
                    setattr(self, interface_name, create_put_sparkle(handler_method).__get__(self))

        # --- Phase 4: Build fast lookup tables for sparkles ---
        self.sparkles = sorted(sparkle_list)

        # --- Phase 5: patch the _execute_sparkle function to normal mode ---
        self._execute_sparkle = self.__exec_sparkle

        # Log the results of the discovery process.
        self.log(system_flags={'states': self._index_to_state, 'sparkles': self.sparkles})

    def _noop(self, *args, **kwargs):
        """A do-nothing method used as a default for unbound sparkles."""
        pass

    def to_state(self, state):
        """
        Requests a state transition. The change is handled by the _execute_sparkle
        method after the current sparkle finishes.

        :param state: The name (str) or index (int) of the target state. When target = -99, stop machine stops
        """
        if isinstance(state, str):
            self._pending_state = self._state_to_index.get(state, -1)
        elif isinstance(state, int) and 0 <= state < len(self._index_to_state):
            self._pending_state = state
        elif isinstance(state, int) and state == -99:
            self._pending_state = -99
        else:
            self._pending_state = -1  # no action

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
        self.log(None, {'sparkle': interface_name})

        # Execute the user's actual sparkle code, passing self to bind it.
        sparkle_method(self, *args, **kwargs)
        self.log(close_log=True)

        # After the sparkle runs, check if a state transition was requested.
        if self._pending_state == -1: return

        if self.state != -1:
            # Call the global on_exit handler.
            self.log(None, {'sparkle': 'ttse__on_exit', 'state': self.state})
            self._on_exit_handler(self)
            self.log(close_log=True)

        if self._pending_state == -99:
            self.log(system_flags={'state': self.state, 'new_state': None}, close_log=True)
            # stop state machine
            self.state = -1
            self._pending_state = -1
        else:
            # Officially change the state.
            self.log(system_flags={'state': self.state, 'new_state': self._pending_state}, close_log=True)
            self.state = self._pending_state
            self._pending_state = -1

            # Call the global on_enter handler.
            self.log(None, {'sparkle': 'ttse__on_enter', 'state': self.state})
            self._on_enter_handler(self)
            self.log(close_log=True)

    def __exec_system_sparkle(self, sparkle_method, *args, **kwargs):
        """
        sparkle execution in normal mode
        """
        interface_name = sparkle_method.__name__
        if interface_name.startswith('_ttss') \
        or interface_name in ['ttse__on_finished', 'ttse__on_exit']:
            self.__exec_sparkle(sparkle_method, *args, **kwargs)

    def get_current_state_name(self):
        """
        Gets the name of the current state.

        :return: The name of the state (str) or "None".
        """
        if self.state == -1:
            return "None"
        return self._index_to_state[self.state]

    # standard tonic sparkle
    def ttse__on_start(self):
        """Event sparkle for user-defined startup logic."""
        pass

    def ttse__on_finished(self):
        """Event sparkle for user-defined cleanup logic (conceptual)."""
        pass

    # --- System Lifecycle Sparkles ---
    def _ttss__on_start(self):
        """System-level sparkle for internal framework setup."""
        pass

    def _ttss__on_finished(self):
        """System-level sparkle for final cleanup (conceptual)."""
        if not self.bindings:
            self.finished()
        else:
            for ess_id in self.bindings:
                self.ledger.get_essence_by_id(ess_id).finish()

    def _ttss__finish(self):
        if self.finishing: return
        self.finishing = True
        # --- patch the _execute_sparkle function to finish mode, only exec system sparkles ---
        self._execute_sparkle = self.__exec_system_sparkle
        if self.state != -1: self.to_state(-99)  # stop state machine if active
        self.ttse__on_finished()  # stop tonic
        self._ttss__on_finished()  # cleanup tonic

    def _ttss__on_binding_finished(self, ess_id):
        self.unbind(ess_id)
        self.ledger.unregister(ess_id)
        if not self.bindings: self.finished()

    # convert the static essence to a sparkling tonic
    def finished(self):
        if hasattr(self, 'catalyst'):
            self.catalyst._ttss__tonic_finished(self.id)
        super().finished()

    def finish(self):
        if self.finishing: return
        self._ttss__finish()

    def binding_finished(self, ess_id):
        self._ttss__on_binding_finished(ess_id)

