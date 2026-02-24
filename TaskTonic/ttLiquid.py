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
