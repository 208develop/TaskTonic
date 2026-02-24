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
