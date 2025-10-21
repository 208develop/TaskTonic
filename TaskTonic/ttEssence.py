from TaskTonic.ttLedger import ttLedger
import time, enum

class __PostInitMeta(type):
    """
        A metaclass that runs a post_init_action hook after the
        instance's __init__ (of the most derived class) has completed.
    """
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance._post_init_action()
        return instance

class ttEssence(metaclass=__PostInitMeta):
    """A base class for all active components within the TaskTonic framework.

    Each 'Essence' represents a distinct, addressable entity with its own
    lifecycle, context (parent), and subjects (children). It automatically
    registers itself with the central ttLedger upon creation to receive a unique ID.
    """

    def __init__(self, name=None, context=None, log_mode=None, fixed_id=None):
        """Initializes a new ttEssence instance.

        This constructor establishes the essence's context, registers it with the
        ledger to obtain a unique ID, determines its name, and registers itself
        as a subject of its parent context.

        :param context: The parent context for this essence. Can be another
                        ttEssence instance, an ID of an existing essence (integer),
                        or None or -1 for a top-level essence.
        :type context: ttEssence or int or None
        :param name: An optional name for this essence. If not provided, a name
                     will be generated based on its ID and class name.
        :type name: str, optional
        :param fixed_id: An optional fixed ID (integer or string name) to assign
                         to this essence. This is used for essences that need a
                         predictable, static identifier.
        :type fixed_id: int or str, optional
        """
        self.ledger = ttLedger()  # is singleton class, so the ledger is shared within the whole project
        self.my_record = {}  # record to add to ledger

        self.context = context if isinstance(context, ttEssence) \
            else self.ledger.get_essence_by_id(context) if (isinstance(context, int) and context >= 0) \
            else None

        self.bindings = []
        self.id = self.ledger.register(self, fixed_id)
        self.name = name if isinstance(name, str) else f'{self.id:02d}.{self.__class__.__name__}'
        self.my_record.update({
            'id': self.id,
            'name': self.name,
            'type': self.__class__.__name__,
            'context_id': self.context.id if self.context else -1,
        })
        if fixed_id is not None:
            self.my_record.update({
                'fixed_id': True,
            })

        # first, enable logging
        self._logger = None
        self._log_mode = None
        self._log = None
        if log_mode is None:
            log_mode = self.context._log_mode if self.context else \
                       self.ledger.formula.get('tasktonic/log/default', ttLog.STEALTH) if self.ledger.formula else \
                       ttLog.STEALTH
        log_mode = ttLog.from_any(log_mode)
        self.set_log_mode(log_mode)
        self.log(system_flags={'created': True})
        self.log(system_flags=self.my_record)

    def _post_init_action(self):
        # these parameter may be changed, so update
        self.my_record.update({
            'name': self.name,
            'context_id': self.context.id if self.context else -1,
        })
        self.log(system_flags=self.my_record, close_log=True)

    def __str__(self):
        return f'TaskTonic {self.name} in context {self.context.name if self.context else -1}'

    def __repr__(self):
        return self.__str__()

    def __deepcopy__(self, memodict={}):
        return self

    # ledger functionality
    def bind(self, essence, *args, **kwargs):
        """Bind a child essence (subject) to this essence.

        Called to bind create, start and bind an essence.

        :param essence: The child ttEssence instance to register.
        :type essence: ttEssence
        """
        if not issubclass(essence, ttEssence):
            raise TypeError('Expected an instance of a ttEssence')
        e = essence(*args, context=self, **kwargs)
        self.bindings.append(e.id)
        return e

    def unbind(self, ess_id):
        """Unbind a child essence (subject) from this essence.

        This is typically called when a child essence is finished or destroyed,
        allowing the parent to remove it from its list of active bindings.

        :param essence: The child ttEssence instance to unbind.
        :type essence: ttEssence
        """
        if ess_id in self.bindings:
            self.bindings.remove(ess_id)

    def binding_finished(self, ess_id):
        self.unbind(ess_id)

    def main_essence(self, essence, *args, **kwargs):
        if not issubclass(essence, ttEssence):
            raise TypeError('Expected an instance of a ttEssence')
        e = essence(None, *args, **kwargs)
        return e

    # standard essence functionality
    def finish(self):
        if not self.bindings:
            self.finished()
        else:
            for ess_id in self.bindings:
                self.ledger.get_essence_by_id(ess_id).finish()

    def finished(self):
        """Signals that this essence has completed its lifecycle.

        This method should be called when the essence is finished with its work.
        It notifies its parent context to unregister it as an active subject.
        """
        self.log(system_flags={'finished': True})
        if self.context:
            self.context.binding_finished(self.id)
            self.ledger.unregister(self.id)
        else:
            self.ledger.unregister(self.id)
        self.id = -1  # finished


    # create logger functions for ttLog to overwrite
    def log(self, line=None, flags=None, system_flags=None, close_log=False):
        """
        Adds a text line and/or (system) flags to the current log entry.
        A log entry is created when empty en sent and closed when close_log is active.
        This is a placeholder and will be altered to the current log_mode

        :param line: The string message to log.
        :param flags: A dictionary of flags to add to the log entry.
        :param system_flags: A dictionary of system flags to add to the log entry.
        :param close_log: When true, this log entry will be sent for display and then closed
        """

    def _log_full(self, line=None, flags=None, system_flags=None, close_log=False):
        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault('sys', {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            self._log_push(self._log)
            self._log = None

    def _log_quiet(self, line=None, flags=None, system_flags=None, close_log=False):
        if self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault('sys', {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            if self._log.get('log') or self._log.get('sys'):
                self._log_push(self._log)
            self._log = None

    def _log_off(self, line=None, flags=None, system_flags=None, close_log=False):
        if system_flags:
            if self._log is None: self._log = {'id': self.id, 'start@': time.time()}
            self._log.setdefault('sys', {}).update(system_flags)
        if close_log and self._log:
            self._log_push(self._log)
            self._log = None

    def _log_stealth(self, line=None, flags=None, system_flags=None, close_log=False):
        pass

    def set_log_mode(self, log_mode):
        log_mode = ttLog.from_any(log_mode)
        self._log_mode = log_mode
        if log_mode == ttLog.STEALTH:   self.log = self._log_stealth
        elif log_mode == ttLog.OFF:     self.log = self._log_off
        elif log_mode == ttLog.QUIET:   self.log = self._log_quiet
        elif log_mode == ttLog.FULL:    self.log = self._log_full
        else:raise NotImplementedError(f"Log mode '{log_mode.name}' is not implemented in ttEssence.set_log_mode.")

    def _log_push(self, log):
        """
        Formats and prints the collected log entry for an event, then resets it.
        """
        if log.get('new'):
            pass
        sparkle_name = self._log.get('sparkle', '')
        sparkle_state_idx = self._log.get('state', -1)

        l_id = log.get('id', -1)
        ts = log['start@']
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        header = f"{self.name}"
        if sparkle_state_idx >= 0:
            header += f"[{self._index_to_state[sparkle_state_idx]}]"
        header += f".{sparkle_name}"

        dont_print_flags = []#'id', 'start@', 'log', 'sparkle', 'state', 'sparkles', 'states']
        flags_to_print = {k: v for k, v in self._log.items() if k not in dont_print_flags}

        print(f"[{l_time_start}] {l_id:02d} - {header:.<45} {flags_to_print}")
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
                print(f"{16 * ' '}- {line}")


class ttLog(enum.IntEnum):
    STEALTH = enum.auto()  # No logging at all
    OFF = enum.auto()  # Logs lifecycle, creating and finishing of Essence
    QUIET = enum.auto()  # + Logs sparkles, only if log line is given
    FULL = enum.auto()  # + Logs sparkles, always

    @classmethod
    def from_any(cls, value):
        """
        Converts a string, int, or existing ttLog instance into a ttLog member.
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
