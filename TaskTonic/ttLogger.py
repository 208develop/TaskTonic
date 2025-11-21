from .ttCatalyst import ttCatalyst
from .ttEssence import ttEssence
import enum

# empty log class, base for all loggers in ttLoggers map
# A logservice allways gets te service name log_service

class ttLogOff(ttEssence):
    _tt_is_service = 'log_service'
    _tt_force_stealth_logging = True

    def put_log(self, log):
        pass

class ttLogService(ttCatalyst):
    _tt_is_service = 'log_service'
    _tt_force_stealth_logging = True

    def _ttss__main_catalyst_finished(self):
        if len(self.service_context) == 0:
            self.finish()
        pass

    def ttse__on_service_context_finished(self, ctxt, ctxts_left):
        if ctxts_left == 0:  # logger is also from essence, so is bound to itself as well
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
