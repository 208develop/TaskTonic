import time, bisect

from TaskTonic.ttEssence import ttEssence


class ttTimer(ttEssence):
    """
    Base implementatie of timers. Inherit when you're creating a timer class.
    BE AWARE: Never use to create an instance!!
    """
    def __init__(self, name=None, context=None, sparkle_back=None):
        super(ttTimer, self).__init__(name=name, context=context)
        if self.__class__ is ttTimer:
            raise RuntimeError('ttTimer is a base class and not meant to be instantiated')
        self.expire = -1  # -1 -> timer not running
        self.period = 10  # 10 sec if not initialed
        self.catalyst = context.catalyst
        if sparkle_back is None:
            self.sparkle_back = self.context.ttse__on_timer
        else:
            self.sparkle_back = sparkle_back

    # used to sort timers in the list
    def __lt__(self, other):
        return self.expire < other.expire

    def __str__(self):
        return super().__str__() + f', expires in {self.expire - time.time():3.3f}sec'

    def _finished(self):
        """
        Overrides the base method to stop the timer
        """
        self.stop()
        super()._finished()
        self.log(close_log=True)  # force log close, needed because of special (not Tonic) flow

    def start(self):
        if self.id == -1: raise RuntimeError(f'Cannot start a finished timer')
        if self.expire == -1:
            self.expire = time.time() + self.period
            bisect.insort(self.catalyst.timers, self)
        else:
            raise RuntimeError(f"Can't start a running timer ({self})")
        return self

    def restart(self):
        if self.id == -1: raise RuntimeError(f'Cannot restart a finished timer')
        if self.expire == -1:
            bisect.insort(self.catalyst.timers, self)
        self.expire = time.time() + self.period
        return self

    def stop(self):
        self.expire = -1
        if self in self.catalyst.timers:
            self.catalyst.timers.remove(self)

    def check_on_expiration(self, reference):
        if reference >= self.expire:
            info = {'id': self.id, 'name': self.name}
            self.reload_on_expire(reference, info)
            self.sparkle_back(info)
            return 0.0  # ==0, expired
        else:
            return self.expire - reference  # >0, not expired, seconds before expiring returned

    def reload_on_expire(self, reference, info):
        raise Exception('Timer callback_and_reload() must be overridden with proper implementation')

class ttTimerSingleShot(ttTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, context=None, sparkle_back=None):
        super().__init__(name=name, context=context, sparkle_back=sparkle_back)
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        self.start()

    def reload_on_expire(self, reference, info):
        self.catalyst.timers.remove(self)
        self.finish()

class ttTimerRepeat(ttTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, context=None, sparkle_back=None):
        super().__init__(name=name, context=context, sparkle_back=sparkle_back)
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        self.start()

    def reload_on_expire(self, reference, info):
        self.catalyst.timers.remove(self)
        self.expire += self.period
        bisect.insort(self.catalyst.timers, self)

class ttTimerPausing(ttTimer):
    def __init__(self, seconds=0.0, minutes=0.0, hours=0.0, days=0.0, name=None, context=None, sparkle_back=None):
        super().__init__(name=name, context=context, sparkle_back=sparkle_back)
        self.period = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
        self.paused_at = -1
        self.start()

    def pause(self):
        if self.paused_at != -1: return
        self.paused_at = time.time()
        self.catalyst.timers.remove(self)

    def pause_ends(self):
        if self.paused_at == -1: return
        self.expire += time.time() - self.paused_at
        bisect.insort(self.catalyst.timers, self)

    def reload_on_expire(self, reference, info):
        self.catalyst.timers.remove(self)
        self.paused_at = self.expire
        self.expire += self.period
