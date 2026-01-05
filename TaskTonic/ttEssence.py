from typing import Type, TypeVar, Union, List
import time


class __ttEssenceMeta(type):
    """
    Metaclass for the ttEssence framework.

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

    def __call__(cls, *args, **kwargs):
        """
        Called when an instance of a class (e.g., ttEssence()) is created.

        This method contains the core logic for routing between standard
        instance creation and service/singleton retrieval.
        """
        from .ttLedger import ttLedger
        service_name = kwargs.pop('service', None)
        if service_name is None:
            service_name = getattr(cls, '_tt_is_service', None)
        is_service = service_name is not None

        if not is_service:
            # --- STANDARD PATH (NON-SINGLETON) ---
            instance = super().__call__(*args, **kwargs)
            instance._init_post_action()
            return instance

        # --- SERVICE PATH (SINGLETON) ---
        ledger = ttLedger()

        existing_instance = ledger.get_service_essence(service_name)
        kwargs['name'] = service_name

        if existing_instance is None:
            # --- CREATE NEW SERVICE (RUNS ONCE) ---
            instance = super().__call__(*args, **kwargs)
            ledger.update_record(instance.id, {'service': service_name})
            instance.service_context = []
            instance._init_post_action()
        else:
            # --- RETURN EXISTING SERVICE  and add context to service_context list ---
            instance = existing_instance
            context = kwargs.get('context', None)
            context = context if isinstance(context, ttEssence) \
                else ledger.get_essence_by_id(context) if isinstance(context, int) \
                else None
            if context is None:
                raise RuntimeError(f"Context can't be None in service_context")
            instance.service_context.append(context)

        # Call _init_service EVERY TIME (if it exists)
        if hasattr(instance, '_init_service'):
            instance._init_service(*args, **kwargs)

        return instance


T = TypeVar('T', bound='ttEssence')

class ttEssence(metaclass=__ttEssenceMeta):
    """A base class for all active components within the TaskTonic framework.

    Each 'Essence' represents a distinct, addressable entity with its own
    lifecycle, context (parent), and subjects (children). It automatically
    registers itself with the central ttLedger upon creation to receive a unique ID.
    """

    def __init__(self, name=None, context=None, log_mode=None, **kwargs):
        """
        Initializes a new ttEssence instance.

        This constructor establishes the essence's context, registers it with the
        ledger to obtain a unique ID, determines its name, and registers itself
        as a subject of its parent context.

        :param name: An optional name for this essence. If not provided, a name
                     will be generated based on its ID and class name.
        :type name: str, optional
        :param context: The parent context for this essence. Can be another
                        ttEssence instance, an ID of an existing essence (integer),
                        or None or -1 for a top-level essence.
        :type context: ttEssence or int or None
        :param log_mode: The initial logging mode for this essence.
        :type log_mode: ttLog, str, or int, optional
        :param kwargs: Catches any additional keyword arguments, allowing
                       subclasses to accept their own parameters
                       (e.g., `srv_api_key`) without breaking this
                       base class `__init__`.
        """
        from .ttLedger import ttLedger
        self.ledger = ttLedger()  # is singleton class, so the ledger is shared
        self.my_record = {}  # record to add to ledger

        self.context = context if isinstance(context, ttEssence) \
            else self.ledger.get_essence_by_id(context) if (isinstance(context, int) and context >= 0) \
            else None

        self.bindings = []
        self.id = self.ledger.register(self)
        self.name = name if isinstance(name, str) else f'{self.id:02d}.{self.__class__.__name__}'
        self.finishing = False
        self.my_record.update({
            'id': self.id,
            'name': self.name,
            'type': self.__class__.__name__,
            'context_id': self.context.id if self.context else -1,
        })

        # first, enable logging
        log_formula = self.ledger.formula.at('tasktonic/log')
        self._logger = None
        self._log_mode = None
        self._log = None
        log_to = log_formula.get('to', 'off')

        # Main Catalyst has to start logging service
        from .ttLogger import ttLogService, ttLog
        if self.id == 0 and log_to != 'off':
            log_service = None
            services = log_formula.children(prefix='service')
            for service in services:
                if service.v == log_to:
                    s_kwargs = service.get('arguments', {})
                    log_service = service.get('service')(*(), **s_kwargs)  ## startup logger service
                    break
            if log_service is None: raise RuntimeError(f'Log to service "{log_to}" not supported.')

        # Set logger service and log_mode
        if getattr(self, '_tt_force_stealth_logging', False) or log_to == 'off':
            # Essence is forcing stealth mode or no log_to set, so also no logservice needed
            self.set_log_mode(ttLog.STEALTH)
        else:
            self._logger = self.bind(ttLogService)

            if log_mode is None:
                log_mode = self.context._log_mode if self.context \
                    else log_formula.get('default', ttLog.STEALTH) if self.ledger.formula \
                    else ttLog.STEALTH
            self.set_log_mode(log_mode)

        self.log(system_flags={'created': True})
        self.log(system_flags=self.my_record)

    def _init_post_action(self):
        """
        A post-initialization hook called by the metaclass.

        This method is guaranteed to run *after* __init__ has completed.
        It is used to init your process (ie. start statemachine) if everything
        is ready.
        """
        # these parameter may be changed, so update
        self.my_record.update({
            'name': self.name,
            'context_id': self.context.id if self.context else -1,
        })
        self.log(system_flags=self.my_record, close_log=True)

    def _init_service(self, *args, **kwargs):
        """
        A hook called by the metaclass *every time* a service is accessed.

        Subclasses can override this method to capture context-specific
        parameters (from kwargs) each time they are requested.

        This method is intentionally a pass-through in the base class.
        """
        pass

    def __str__(self):
        return f'TaskTonic {self.name} in context {self.context.name if self.context else -1}'

    def __repr__(self):
        return self.__str__()

    def __deepcopy__(self, memodict={}):
        return self

    # ledger functionality
    def bind(self, essence: Union[Type[T], T], *args, **kwargs) -> T:
        """Bind a child essence (subject) to this essence.

        Called to create, start, and bind an essence as a child
        of the current context.

        :param essence: The ttEssence *class* to instantiate.
        :type essence: type
        :param args: Positional arguments for the new essence's __init__.
        :param kwargs: Keyword arguments for the new essence's __init__.
        :return: The newly created and bound essence instance.
        :rtype: ttEssence
        """
        if isinstance(essence, ttEssence):
            e = essence
            service_context = e.service_context if hasattr(e, 'service_context') else []
            if e.context != self and self not in service_context:
                raise RuntimeError(f"Add context to essence to bind! "
                                   f"({e.__class__.__name__} context: {e.context} / service_context: {service_context})")
        elif issubclass(essence, ttEssence):
            e = essence(*args, context=self, **kwargs)
        else:
            raise TypeError('Expected a class reference or an instance of a ttEssence')

        self.bindings.append(e.id)
        return e

    def unbind(self, ess_id):
        """Unbind a child essence (subject) from this essence.

        This is typically called when a child essence is finished or destroyed,
        allowing the parent to remove it from its list of active bindings.

        :param ess_id: The ID of the child ttEssence instance to unbind.
        :type ess_id: int
        """
        if ess_id in self.bindings:
            self.bindings.remove(ess_id)

    def binding_finished(self, ess_id):
        """
        Callback method for when a bound child essence has finished.

        Args:
            ess_id (int): The ID of the child essence that has finished.
        """
        self.unbind(ess_id)
        if self.finishing and not self.bindings:
            self._finished()  # finished, when finishing and no bindings left

    # standard essence functionality
    def finish(self, from_context=None):
        """
        Starts the shutdown process for this essence.

        If the essence has active bindings (children), it will
        instruct them to finish first. If not, it will call
        `self.finished()` immediately.
        """
        if self.finishing: return  # essence is already finishing
        from_context = from_context if from_context else self

        if self._finish_service_context(from_context):
            #TODO: Now a service is stopped after finishing last service_context
            #  Consider implementing the possibility to maintain te service, wait for new service context
            if len(self.service_context) > 0:
                return

        self.finishing = True
        self._finish()

    def _finish_service_context(self, from_context=None):
        if from_context is not None and hasattr(self, 'service_context') and from_context in self.service_context:
            # Finishing service connection
            self.service_context.remove(from_context)
            try:
                event = getattr(self, 'ttse__on_service_context_finished')
                event(from_context.id, len(self.service_context))
            except AttributeError: pass
            try:
                event = getattr(from_context, f'ttse__on_{self.name}_finished')
                event()
            except AttributeError: pass
            try:
                event = getattr(from_context, 'binding_finished')
                event(self.id)
            except AttributeError: pass
            return True
        return False

    def _finish(self):
        # finish the essence (or Tonic)
        if not self.bindings:
            self._finished()
        else:
            for ess_id in self.bindings.copy():
                ess = self.ledger.get_essence_by_id(ess_id)
                if ess: ess.finish(from_context=self)

    def _finished(self):
        """Signals that this essence has completed its lifecycle.

        This method should be called when the essence is finished with its work.
        It notifies its parent context (if it has one) to unbind it.
        It then unregisters itself from the ledger.
        """
        self.log(system_flags={'finished': True})

        service_context = self.service_context if hasattr(self, 'service_context') else []
        for sc in service_context:
            try:
                event = getattr(sc, f'ttse__on_{self.name}_finished')
                event()
            except AttributeError: pass
            try:
                event = getattr(sc, f'binding_finished')
                event(self.id)
            except AttributeError:
                pass

        if self.context: self.context.binding_finished(self.id)

        self.ledger.unregister(self.id)
        self.id = -1  # finished

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

    def _log_full(self, line=None, flags=None, system_flags=None, close_log=False):
        """Internal log handler for the FULL log mode."""
        if self.id == -1:
            pass
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
            if self._log.get('log') or self._log.get('sys'):
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
            raise NotImplementedError(f"Log mode '{log_mode.name}' is not implemented in ttEssence.set_log_mode.")


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
