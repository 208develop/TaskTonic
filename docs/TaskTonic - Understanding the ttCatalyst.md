# The Engine of TaskTonic: Understanding the `ttCatalyst`

<img src="../assets/tasktonic-catalyst.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">c

If a `Tonic` is a specialized worker on an assembly line, the `ttCatalyst` is the powerful engine that drives the conveyor belt [1]. Its primary and most crucial function is to make Tonics "sparkle" by continuously processing a shared task queue [1]. 

To master TaskTonic, you need to understand what happens inside this engine, how to configure it, and when to spawn new ones.

---

## 1. The Basics: A Catalyst *is* a Tonic

An elegant part of the TaskTonic architecture is that `ttCatalyst` inherits directly from `ttTonic` [2, 3]. 
This means a Catalyst is not just a dumb loop; it is a fully-fledged agent. 

*   **It has a lifecycle:** It starts up, can have its own state machine, and shuts down gracefully.
*   **It can be used as a Tonic:** You can add your own application logic directly to a custom Catalyst [2, 3].
*   **It cleans up after itself:** When the last Tonic registered to a Catalyst finishes, the Catalyst determines its job is done and automatically initiates its own shutdown sequence [4, 5].

## 2. The Core: `tt_main_catalyst`

Every TaskTonic application requires at least one Catalyst, known as the **Main Catalyst**. 
*   It is strictly identified by the name `tt_main_catalyst` and always holds `id = 0` [6, 7]. 
*   Unlike other Catalysts, the Main Catalyst runs its loop in the **main application thread**, blocking the standard execution flow to keep your application alive [6, 8].
*   It is defined in your `ttFormula` via the `creating_main_catalyst()` method. By default, the Formula simply spawns a standard `ttCatalyst` [7, 9].

## 3. Under the Hood: The `sparkle()` Loop

When you call `start_sparkling()`, the Catalyst enters its main `while` loop [6]. Here is exactly what happens in that loop:

1.  **Timer Check:** It looks at the list of registered timers and calculates `next_timer_expire`—the exact amount of time until the nearest timer needs to fire [10].
2.  **Queue Wait:** It calls `get(timeout=next_timer_expire)` on its master queue (`catalyst_queue`). The thread goes to sleep, consuming 0% CPU, until either a task arrives or the timer expires [10].
3.  **Execution:** If a task (work order) is pulled from the queue, it unpacks the payload and calls the internal `_execute_sparkle` method on the target Tonic [11, 12].
4.  **Extra Sparkles:** After executing the main task, it rapidly drains any `extra_sparkles` (like immediate state transitions: `on_exit` -> `on_enter`) before returning to the start of the loop [11].

### The Catalyst Queue: What exactly is in it?
The `catalyst_queue` is a standard Python `queue.SimpleQueue` [13]. A single "work order" payload placed on this queue contains [10, 14]:
*   The `instance` of the target Tonic.
*   The `sparkle` method to execute.
*   The `args` and `kwargs` (parameters).
*   The `source` (who called this sparkle, tracked via the `ttSparkleStack`).

## 4. Trade-offs: Using Multiple Catalysts

Because any Catalyst created *after* the Main Catalyst automatically spawns its own background thread, you can easily distribute workloads [8, 15]. 

**Why you might want to use your own Catalyst:**
*   **Thread Independence:** A new Catalyst runs in its own thread. If the `tt_main_catalyst` is heavily bogged down by UI repaints or a busy Tonic, your independent Catalyst remains hyper-responsive. 

**Why you should be careful (The Drawbacks):**
*   **The Deepcopy Penalty (Slower):** TaskTonic guarantees data immutability. If Thread A calls a Sparkle on a Tonic managed by Thread B (a different Catalyst), the framework detects the thread crossing. To prevent race conditions, it uses `copy.deepcopy()` on all `args` and `kwargs` before placing them on the queue [16-18]. This deep copy is completely safe, but it introduces overhead and is slower than running in the same Catalyst.
*   **Thread Bloat:** Spawning a new Catalyst for every single Tonic defeats the purpose of the framework. You fall back into the trap of managing a mess of OS threads.

**Best Practice:** Use a separate Catalyst for a self-contained module or Service that manages a whole tree of sub-Tonics (infusions). Do *not* spawn a new Catalyst for a single, lightweight Tonic.

## 5. Advanced: Creating a Custom Catalyst Class

Because `ttCatalyst` is just a class, you can subclass it. Why would you write your own Catalyst engine?

### A. Interfacing with Blocking/Long-Running Processes (e.g., Numpy)
Sometimes you *have* to run a Sparkle that takes a long time (like a heavy Numpy calculation). In a shared Catalyst, this freezes all other Tonics. 
By creating a dedicated custom Catalyst just for this math module, you can explicitly *allow* long-running Sparkles. The main application remains fluid. 
*(Warning: Remember that if a Sparkle takes 5 seconds, a `finish()` command sent to that Tonic will also be delayed by up to 5 seconds because it waits in the same queue!)*

### B. High-Speed Custom Queues & Interfaces (The `SelectorHandler` Pattern)
Standard queues use `time.sleep` or locks to wait. For ultra-fast I/O (like IP communication), you want to use OS-level selectors [19]. 

The TaskTonic framework allows you to override the `new_catalyst_queue()` method [13, 20]. You can inject a custom queue that bridges the gap between Python queues and OS sockets.

**The IP Communication Example:**
In `examples/ip_communicatie.py`, a custom Catalyst named `SelectorHandler` is used [21]: 
1.  **Custom Queue:** It overrides `new_catalyst_queue` with a `MyNotifyingQueue` [20]. Whenever a Sparkle is put onto this queue, it also sends a single byte of data to a hidden internal socket (`_queue_filled_notify_channel`) [20].
2.  **Custom Loop:** The standard `sparkle()` loop is overridden. Instead of blocking on `queue.get()`, it blocks on `selectors.select()` [22]. 
3.  **Result:** The Catalyst sleeps efficiently at the OS level. It wakes up instantly if *either* network data arrives on an IP port, *or* if another Tonic drops a Sparkle into the `MyNotifyingQueue` [19, 21, 22]. 

This demonstrates the ultimate power of TaskTonic: you can bend the engine entirely to your architectural needs without rewriting the underlying Tonic logic.