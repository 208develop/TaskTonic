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
```