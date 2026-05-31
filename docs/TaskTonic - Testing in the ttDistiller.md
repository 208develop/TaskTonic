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

## 2. Usage: Pytest or Standalone

You don't need a heavy testing framework to use the Distiller, but it integrates perfectly with them.
*   **Standalone:** You can write a simple Python script that instantiates a Distiller, runs your Tonic, and asserts conditions using standard `assert` statements.
*   **Pytest (Recommended):** You can use `pytest` fixtures to set up your Distiller, run your Tonics through their paces, and generate beautiful test reports. The Distiller runs synchronously in the main thread, making your `pytest` suite incredibly fast and 100% deterministic.

---

## 3. Controlling Time and Execution: Distiller Functions

Because the Distiller owns the queue, you dictate exactly when and how Sparkles are executed.

### Step-by-Step Sparkling
Instead of `start_sparkling()`, you tell the Distiller exactly how many items to process from the queue.
```python
# Process exactly ONE Sparkle on the queue, then pause.
distiller.sparkle(steps=1) 

# Process 5 Sparkles, then pause.
distiller.sparkle(steps=5)
```
This allows you to freeze the universe mid-execution and inspect the state of your application.

### Sparkling Until a Condition
Often, you don't know *exactly* how many Sparkles it takes to finish a complex network handshake. You just want to run the engine until a specific event happens.
```python
# Run the engine until the Tonic enters the 'finished' state
distiller.run_until_state(tonic_instance, target_state='finished')

# Run the engine until a specific Sparkle method is called
distiller.run_until_sparkle(tonic_instance, target_sparkle='ttse__on_data_received')
```

### Data Probing
While frozen between Sparkles, you can "probe" your Tonic. Since the Distiller runs in your testing thread, you have safe, direct access to the Tonic's internal variables. You can assert that `tonic_instance.download_count == 5` exactly at the moment it enters the 'saving' state.

### Contract Testing (The Ultimate Regression Guard)
Because TaskTonic executes predictably, the sequence of Sparkles and State changes forms a rigid "Contract". 
The Distiller can record a "Golden Run" of your Tonic. If a junior developer later modifies the code and accidentally triggers an extra `ttsc__reconnect` Sparkle, the Distiller will fail the test immediately because the execution signature (the Contract) no longer matches the expected sequence.

---

## 4. Unpacking the Status Content (and Profiling)

Every time a Sparkle is executed, the Distiller logs a comprehensive status record. This isn't just a string; it's a rich data structure containing:

*   **Target:** Which Tonic instance executed the Sparkle.
*   **Method:** The exact method name (e.g., `ttsc__process_chunk`).
*   **Arguments:** The `args` and `kwargs` passed into the Sparkle.
*   **State:** The state of the Tonic before and after the Sparkle.
*   **Execution Time (Profiling):** Crucially, the Distiller records the exact `at_enter` and `at_exit` timestamps for every Sparkle. 

**Finding the "Giant Sparkle":**
Remember the golden rule of Sparkling Programming: *Never block the Catalyst.*
If you suspect your UI is stuttering, you can write a test and check the Distiller's execution times. If the Distiller reports that `ttsc__parse_xml` took 450ms, you instantly know you have found a "Giant Sparkle" that needs to be broken down using the Chunked Iterator pattern.

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
distiller.inject_sparkle(parent_tonic.ttse__on_network_data, {"status": "ok", "payload": "123"})
distiller.sparkle(steps=1)
assert parent_tonic.current_state == 'processing_data'
```

### B. The Integration Test (Full Hierarchy)
You can also load the parent *and* all its real infusions into the Distiller. 
Because all Tonics in the same Formula share the same Catalyst engine, the Distiller easily manages the master queue for the entire tree. You can trigger a high-level command on the Parent, tell the Distiller to run 50 Sparkles, and watch the entire cascade of commands and events flow down to the children and bubble back up to the parent. It provides a flawless, synchronous integration test of a highly asynchronous system.

---

### Summary
Testing concurrent code used to mean adding `time.sleep(1)` everywhere and praying. With TaskTonic and the `ttDistiller`, you gain the power to freeze time, inspect memory, profile execution speeds, and lock down your application's behavior with deterministic contracts.
```