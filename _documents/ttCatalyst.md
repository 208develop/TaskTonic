# Documentation: The `ttCatalyst` Class

This document describes the functionality of the `ttCatalyst` class within the TaskTonic framework.

---

## 1. Introduction: The Engine of the System

If a `Tonic` is a specialized worker on an assembly line, the `ttCatalyst` is the powerful engine that drives the
conveyor belt. Its primary and most crucial function is to make `Tonic`s "sparkle" by continuously processing a
shared task queue.

It's important to understand the `Catalyst`'s role:

* **It provides EXECUTION power**: The `Catalyst` runs the main loop that pulls tasks from a queue and executes them.
* **It does NOT provide COORDINATION**: The `Catalyst` is not the brain of the operation. It doesn't decide
  which `Tonic`s to create or what tasks they should perform. That higher-level logic is handled by other
  components in the framework, such as the `Formula` and `Ledger`.

[Image of a powerful, clean industrial engine]

---

## 2. Core Functionality

The `Catalyst` has three main responsibilities: managing the queue, running the execution loop, and tracking the
lifecycle of the `Tonic`s it powers.

### The Master Queue (`catalyst_queue`)

The `Catalyst` owns the central `Queue` that all its managed `Tonic`s will use. When any `Tonic` calls one of
its sparkle methods (e.g., `ttsc__process`), it places a "work order" onto this shared `catalyst_queue`.

### The Execution Loop (`sparkle()`)

This is the heart of the `Catalyst`. It's a `while` loop with a single job:

1. Wait for and retrieve a work order from the `catalyst_queue`.
2. Unpack the work order to identify the target `Tonic` instance and the sparkle to be executed.
3. Call the `_execute_sparkle` method on that specific `Tonic`, handing off the task.

The loop uses a timeout when getting items from the queue. This ensures it doesn't block forever and can gracefully
shut down when instructed.

### Lifecycle Management

The `Catalyst` keeps a register of all the `Tonic`s it is currently powering.

* **Startup (`_ttss__startup_tonic`)**: When a `Tonic` is initialized, it calls this system sparkle on its
  `Catalyst` to register itself as active.
* **Shutdown (`_ttss__tonic_finished`)**: When a `Tonic` completes its `finish()` sequence, it calls this
  system sparkle to de-register itself.
* **Automatic Shutdown**: When the last registered `Tonic` finishes, the `Catalyst` determines its job is
  done and automatically initiates its own shutdown sequence.

---

## 3. Usage and Operation

### Starting the Catalyst (`start_sparkling()`)

To begin processing the queue, you must call the `start_sparkling()` method. This kicks off the `sparkle()` loop.
The framework distinguishes between the main `Catalyst` (with `id=0`) and others:

* **Main Catalyst**: Runs the loop in the current (main) thread, blocking further execution in that thread.
* **Other Catalysts**: Start the execution loop in a new, separate background thread.

### Binding a Tonic to a Catalyst

A `Tonic` automatically binds itself to its `Catalyst` during initialization. It looks for the `Catalyst` in the
`context` it receives.

```python
# --- Inside a Tonic's __init__ method ---

# It finds the catalyst in its context and gets a reference to the shared queue.
self.catalyst = context.catalyst if hasattr(context, 'catalyst') else ...
self.catalyst_queue = self.catalyst.catalyst_queue

# It then registers itself with the catalyst as an active component.
self.catalyst._ttss__startup_tonic(self.id)
```
