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

