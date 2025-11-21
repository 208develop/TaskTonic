from .ttEssence import ttEssence
import re, threading, copy


class ttTonic(ttEssence):
    """
    A robust, passive framework class for creating task-oriented objects (Tonics).

    This class automatically discovers methods (sparkles) based on naming conventions,
    handles state management, and provides a structured logging system. All sparkle
    types (ttsc, ttse, tts, _tts) are handled uniformly by placing a 'work order'
    on a queue, which is then processed by an external execution loop.
    """

    def __init__(self, name=None, context=None, log_mode=None):
        """
        Initializes the Tonic instance, discovers sparkles, and calls startup methods.

        :param context: The context in which this tonic operates.
        :param name: An optional name for the tonic. Defaults to the class name.
        :param fixed_id: An optional fixed ID for the tonic.
        """
        super().__init__(name=name, context=context, log_mode=log_mode)

        # bind to catalyst
        if not hasattr(self, 'catalyst_queue'):
            self.catalyst = context.catalyst if hasattr(context, 'catalyst') \
                else self.ledger.get_essence_by_id(0)  # main catalyst
            self.catalyst_queue = self.catalyst.catalyst_queue  # copy queue for (a bit) faster acces

            self.log(None, {'catalyst': self.catalyst.name})
            self.catalyst._ttss__bind_tonic_to_catalyst(self.id)

        # Discover all sparkles and build the execution system.
        self.state = -1  # Start with no state (-1)
        self._pending_state = -1
        self._sparkle_init()

    def _init_post_action(self):
        super()._init_post_action()

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
        state_impls, generic_impls = {}, {}
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
                    state_impls[(prefix, state_name, sp_name)] = method
                    states.add(state_name)
                    sparkle_names.add(sp_name)
                    prefixes_by_cmd.setdefault(sp_name, set()).add(prefix)
                elif g_match:
                    # Found a generic sparkle (e.g., 'ttsc__initialize')
                    prefix, sp_name = g_match.groups()
                    generic_impls[(prefix, sp_name)] = method
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

                    # Create direct-execute methods only for 'on_enter' and 'on_exit'
                    if interface_name in ['ttse__on_enter', 'ttse__on_exit']:
                        direct_method_name = f"_direct_execute_{interface_name}"

                        # This factory creates the direct execution method
                        # It needs to capture the handler_list (_list)
                        def create_direct_executor(_list, _name):
                            # This is the exact logic copied from 'execute_state_sparkle'
                            def direct_execute_method(self, *args, **kwargs):
                                state_sparkle = _list[self.state]
                                self.log(None, {'state': self.state})
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

        if self.state != -1:
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
        self.log(None, {'sparkle': interface_name})
        # Execute the user's actual sparkle code, passing self to bind it.
        sparkle_method(self, *args, **kwargs)
        self.log(close_log=True)

    def __exec_system_sparkle(self, sparkle_method, *args, **kwargs):
        """
        sparkle execution in normal mode
        """
        interface_name = sparkle_method.__name__
        if interface_name.startswith('_ttss') \
                or interface_name in ['ttse__on_finished', 'ttse__on_exit', 'ttse__on_service_context_finished', '_ttinternal_state_machine_stop']:
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

    # convert the static essence to a sparkling tonic
    def _finished(self):
        if hasattr(self, 'catalyst'):
            self.catalyst._ttss__remove_tonic_from_catalyst(self.id)
        super()._finished()

    def finish(self, from_context=None):
        # Finish on tonic level, will first stop the tonic, and after that finish admin in the essence
        if self.finishing: return
        self._ttss__finish(from_context if from_context else self)

    def _ttss__finish(self, from_context=None):
        if self.finishing: return

        if self._finish_service_context(from_context):
            # TODO: Now a service is stopped when no service context is left.
            #  Consider implementing the possibility to maintain te service, wait for new service context
            if len(self.service_context) > 0:
                return

        self.finishing = True

        # --- patch the _execute_sparkle function to finish mode, only executing system sparkles ---
        self._execute_sparkle = self.__exec_system_sparkle

        # stop the tonic
        if self.state != -1: self.to_state(-1)  # stop state machine if active
        self.ttse__on_finished()  # stop tonic
        self._ttss__on_finished(from_context)  # cleanup tonic

    def _ttss__on_finished(self, from_context=None):
        """System-level sparkle for final cleanup."""
        super()._finish()  # finish at essence level

    def binding_finished(self, ess_id):
        self._ttss__on_binding_finished(ess_id)

    def _ttss__on_binding_finished(self, ess_id):
        super().binding_finished(ess_id) # call the static admin method

