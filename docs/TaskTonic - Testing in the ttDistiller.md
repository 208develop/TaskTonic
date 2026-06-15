# Testing TaskTonic: Mastering the `ttDistiller`

<img src="../assets/tasktonic-distiller.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

Testing software is fundamental, but testing **concurrent, asynchronous systems** is notoriously difficult. In standard threaded or `asyncio` applications, you are at the mercy of the OS scheduler. A test might pass 99 times and fail on the 100th because a background thread executed a millisecond too late. You cannot easily pause time, inspect the exact state mid-execution, or predict the exact order of operations.

TaskTonic eliminates these threading nightmares through its atomic **Sparkles** and sequential queue. But how do you test an asynchronous queue without relying on messy `time.sleep()` calls in your tests?

Enter the **`ttDistiller`**: a specialized, deterministic test engine for TaskTonic.

---

## 1. The Print Statement vs. The Distiller (`self.log` vs `ttDistiller`)

When developing a Tonic, your first instinct is to use `self.log("Doing something...")`. This is excellent for visual debugging. You can watch the execution flow, state changes, and parameter values scroll by in your console.

However, **you cannot write an automated unit test against console output**. 
If someone breaks your Tonic's logic six months from now, `self.log` won't fail a CI/CD pipeline. 

The `ttDistiller` replaces the standard `ttCatalyst` engine during testing. Instead of running a continuous, infinite loop in the background, the Distiller acts as a **manual crank** for the TaskTonic engine. It records every Sparkle, every state change, and every parameter passed, turning your asynchronous application into a completely synchronous, predictable, and heavily inspectable data structure.

---

## 2. Usage: Pytest or Standalone

You don't need a heavy testing framework to use the Distiller, but it integrates perfectly with them.

* **Standalone:** You can write a simple Python script that instantiates a Distiller, runs your Tonic, and asserts conditions using standard `assert` statements.
* **Pytest (Recommended):** You can use `pytest` fixtures to set up your Distiller, run your Tonics through their paces, and generate beautiful test reports. The Distiller runs synchronously in the main thread, making your `pytest` suite incredibly fast and 100% deterministic.

---

## 3. Controlling Time and Execution: Distiller Functions

Because the Distiller owns the queue, you dictate exactly when and how Sparkles are executed. Every time you crank the engine, the Distiller returns a comprehensive `trace` dictionary of everything that happened.

### Step-by-Step Sparkling
Instead of `start_sparkling()`, you tell the Distiller exactly how many items to process from the queue.

```python
# Process exactly ONE Sparkle on the queue, then pause.
trace = distiller.sparkle(sparkle_count=1) 

# Process 5 Sparkles, then pause.
trace = distiller.sparkle(sparkle_count=5)
```
This allows you to freeze the universe mid-execution and inspect the state of your application.

### Sparkling Until a Condition
Often, you don't know *exactly* how many Sparkles it takes to finish a complex network handshake. You just want to run the engine until a specific event happens.

```python
# Run the engine until the Tonic enters the 'finished' state
trace = distiller.sparkle(till_state_in=['finished'])

# Run the engine until a specific Sparkle method is called
trace = distiller.sparkle(till_sparkle_in=['ttse__on_data_received'])
```

### Data Probing (The `contract` Parameter)
While running the engine, you can instruct the Distiller to "probe" your Tonic and extract internal variables exactly before and after every Sparkle. You define these probes using the `contract` parameter. 

The Distiller uses a `_freeze_value` mechanism to safely create static snapshots of complex objects (like dictionaries, lists, or even Tonics) at that exact microsecond.

```python
# Tell the Distiller to track the internal 'download_count' and 'is_connected' variables
trace = distiller.sparkle(
    timeout=5.0, 
    till_state_in=['saving'],
    contract={'probes': ['download_count', 'is_connected']}
)
```

---

## 4. Unpacking the Status Trace (Assertions & Profiling)

Every time `distiller.sparkle()` finishes, it returns a rich status dictionary. This is your primary tool for writing `assert` statements in your tests.

### The Root Trace Elements
The returned dictionary contains metadata about the execution run:

* **`status`**: The final status of the engine (`'running'` or `'catalyst finished'`).
* **`start@` / `end@`**: Absolute timestamps of when the sparkle run started and ended.
* **`stop_condition`**: A list explaining *why* the Distiller paused. 
    * *Values can include:* `'timeout'`, `'sparkle_count'`, `'state_trigger: [state_name]'`, `'sparkle_trigger: [sparkle_name]'`, or `'catalyst finished'`.
* **`sparkle_trace`**: A detailed list of every single Sparkle that was executed.

### The `sparkle_trace` List
Each item in the `sparkle_trace` list is a dictionary describing a single atomic action:

* **`id` / `tonic`**: The ID and name of the Tonic that executed the Sparkle.
* **`sparkle`**: The exact method name (e.g., `ttsc__process_chunk`).
* **`args` / `kwargs`**: The arguments passed into the Sparkle.
* **`source`**: A tuple `(source_tonic, source_sparkle_name, source_id)` indicating who queued this Sparkle.
* **`at_enter` / `at_exit`**: Sub-dictionaries capturing the exact state *before* and *after* the Sparkle. They contain:
    * `@`: The precise timestamp (useful for profiling).
    * `state`: The name of the Tonic's state machine state.
    * `probes`: A dictionary containing the frozen values of any requested probes.
    * `sparkling`: (Only in `at_exit`) Boolean indicating if the engine is still running.

### Examples: Writing Assertions with the Trace

**1. Asserting Stop Conditions:**
Ensure your logic stopped because it reached the desired state, not because it timed out.

```python
trace = distiller.sparkle(timeout=2.0, till_state_in=['authenticated'])

# Check why the distiller stopped
assert 'state_trigger: [authenticated]' in trace['stop_condition']
assert 'timeout' not in trace['stop_condition']
```

**2. Asserting Probed Data:**
Verify that internal variables were updated correctly during the Sparkle execution.

```python
trace = distiller.sparkle(
    sparkle_count=1, 
    contract={'probes': ['retry_attempts']}
)

# Grab the last executed sparkle from the trace
last_sparkle = trace['sparkle_trace'][-1]

# Check the probe values before and after the sparkle executed
assert last_sparkle['at_enter']['probes']['retry_attempts'] == 0
assert last_sparkle['at_exit']['probes']['retry_attempts'] == 1
```

**3. Profiling (Finding the "Giant Sparkle"):**
Remember the golden rule of Sparkling Programming: *Never block the Catalyst.*
If you suspect your UI is stuttering, you can check the Distiller's execution times.

```python
trace = distiller.sparkle(till_state_in=['done'])

for action in trace['sparkle_trace']:
    enter_time = action['at_enter']['@']
    exit_time = action['at_exit']['@']
    duration_ms = (exit_time - enter_time) * 1000
    
    # Fail the test if any single Sparkle blocks the thread for more than 50ms!
    assert duration_ms < 50, f"Giant Sparkle detected: {action['sparkle']} took {duration_ms}ms"
```

---

## 5. Mocking Infusions vs. Integration Testing

TaskTonic encourages building hierarchical applications where a Parent Tonic delegates work to Child Tonics (Infusions). The Distiller allows you to test these at multiple levels.

### A. The Unit Test (Mocking Infusions)
If you want to test the Parent's logic independently, you don't want the actual IP connections or databases (the children) to fire. 

1.  **Mock the Infusion:** Override the child Tonic with a mock version.
2.  **Inject Events:** From your test script, you act as the child. You manually queue up events to see how the Parent reacts.

```python
# We are the test. We pretend the child (network socket) received data.
# We inject this directly onto the queue for the parent to process.
parent_tonic.ttse__on_network_data({"status": "ok"})

# Process the injected event
trace = distiller.sparkle(sparkle_count=1)

# Verify the parent handled the mock data correctly
assert parent_tonic.get_current_state_name() == 'processing_data'
```

### B. The Integration Test (Full Hierarchy)
You can also load the parent *and* all its real infusions into the Distiller. 

Because all Tonics in the same Formula share the same Catalyst engine, the Distiller easily manages the master queue for the entire tree. You can trigger a high-level command on the Parent, tell the Distiller to run 50 Sparkles, and watch the entire cascade of commands and events flow down to the children and bubble back up to the parent. It provides a flawless, synchronous integration test of a highly asynchronous system.

---

### Summary
Tith TaskTonic and the `ttDistiller`, you gain the power to freeze time, inspect memory, profile execution speeds, and lock down your application's behavior with deterministic contracts.
