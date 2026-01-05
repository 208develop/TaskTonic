# ttStore & Store/Item: Central Data Repository

This documentation describes the functionality of the `Store` and `Item` classes and their integration within TaskTonic
via `ttStore`.

## Introduction

In complex applications, it is essential to share data between different components in a structured and accessible way.
`ttStore` functions as a **Central Data Repository**. It offers a hierarchical storage structure (comparable to a file
system or a nested dictionary) that is:

1. **Centralized:** A single source of truth for parameters, sensor values, and configurations.
2. **Reactive:** Components can subscribe to changes in specific data paths.
3. **Flexible:** Data can be accessed via absolute paths or relative pointers (`Item`).

---

## Concepts: Store vs. ttStore

The system consists of two layers that can also be used **independently**.

### 1. The Core: `Store` and `Item`

The `Store` is the pure data container. It is a standalone class that holds the data and provides methods to read or
write data via paths (e.g., `'sensors/temp/value'`).

The `Item` is a smart "pointer" or "cursor" to a specific location in the `Store`. It allows for relative navigation
without needing to know the full absolute path.

> **Note:** `Store` and `Item` can be used outside of TaskTonic in any Python project requiring a powerful, hierarchical
data structure.

### 2. The Service: `ttStore`

`ttStore` is the TaskTonic wrapper around a `Store`. It transforms the store into a **Service** within the TaskTonic
ecosystem. This adds capabilities such as:

* **Event-driven updates:** Automatically notify other Tonics (like UI or controllers) upon changes.
* **Service Binding:** Easily linked to other Tonics via `self.bind()`.

---

## API Reference & Methods

Below is an overview of the most important methods for data manipulation and navigation.

### Dictionary Access (`[]` Syntax)

For convenience, `ttStore` and `Item` support standard Python dictionary syntax.

* **Reading:** `val = store['path']`
    * Equivalent to `.get('path')`.
    * Returns `None` if the path does not exist (unlike standard Python dicts which raise KeyError).
* **Writing:** `store['path'] = val`
    * Equivalent to `.set([('path', val)])`.
    * Triggers updates immediately (unless inside a `group`).

**Example:**

```python
# Read
current_limit = self.twin['parameters/temp_limit']

# Write
self.twin['parameters/temp_limit'] = 12.0
```

### Writing Data (`set`, `.v`, `.append`)

#### `set(data)`

Writes one or multiple values to the store. It accepts a `dict` or an `Iterable` (list/tuple) of tuples.

* **Usage:** Initialization, bulk updates, or when you need to write multiple values atomically.
* **Smart Paths:**
    * `#`: Creates a new unique entry (auto-increment list).
    * `./`: Refers to the last created entry (useful for setting properties of an item).

**Example:**

```python
# Initialize a store with parameters and sensors
self.twin.set([
    ('parameters/update_freq', 2),     # Set update frequency to 2
    ('sensors/#', 'temp'),             # Create new sensor 'temp'
    ('sensors/./value', 15.0),         # Set value of THAT sensor
    ('sensors/./unit', '℃'),           # Set unit of THAT sensor
])
```

#### `.v` (Value Property via Item)

If you hold an `Item` object (a pointer to a location), you can read and write directly via the `.v` property. This is
the most efficient way to manipulate data if you already have the Item.

**Example:**

```python
# Assume we have a pointer (Item) to the sensor value
sensor_val_item = self.twin.at('sensors/#0/value')

# Write a new value
sensor_val_item.v = 22.5
```

#### `append(value)` (via Item) or `append(path, value)` (via Store)

Adds a new item to a list. This is a cleaner, more pythonic alternative to using the `'path/#'` syntax when adding
single items.

* **Via Item:** `item.append(value)`
* **Via Store:** `store.append(path, value)`

**Example:**

```python
# Append via Store (adds 'System Started' to the 'logs' list)
self.twin.append('logs', 'System Started')

# Append via Item
log_item = self.twin.at('logs')
log_item.append('User logged in')
```

### Reading Data (`get`, `at`)

#### `get(path, default=None)`

Retrieves the value of a specific path. If the path does not exist, the `default` value is returned.

**Example:**

```python
freq = self.twin.get('parameters/update_freq', 5)  # Default 5 if not found
```

#### `at(path) -> Item`

Returns an `Item` object pointing to the location `path`. This is **more powerful** than `get` because it allows further
navigation from that point.

**Example:**

```python
# Get a pointer (Item) to the first sensor
sensor_item = self.twin.at('sensors/#0')

# Read values via the Item
print(sensor_item['value'].v)  # Prints: 15.0
```

### Navigation (`Item` objects)

An `Item` object acts as a smart window onto your data.

* **`item['child']`**: Navigate to a sub-item.
    ```python
    val = sensor_item['value'].v
    ```
* **`item.parent`**: Returns an `Item` to the parent.
    ```python
    root_sensors = sensor_item.parent # Now points to 'sensors'
    ```
* **`item.list_root`**: If the item is part of a list (like sensors), this returns the item itself, regardless of how
  deep you are in the hierarchy.
    ```python
    # If located at 'sensors/#0/value', list_root returns 'sensors/#0'
    sensor_name = sensor_item.list_root.v # Returns e.g., 'temp'
    ```

#### `.children(prefix=None)`

Returns an **iterator** (not a list) of `Item` objects that are direct children of the current item.

* **Why an iterator?** It is memory efficient (lazy evaluation). If you have thousands of items, it doesn't create
  objects for all of them unless you consume them.
* **prefix:** Optional string to filter children (e.g., useful if you have different types of lists in one folder).

**Example 1: Converting to a list**
If you need index access or the length, convert it to a list explicitly.

```python
sensors = self.twin.at('sensors')
sensor_list = list(sensors.children())
print(f"Count: {len(sensor_list)}")
```

**Example 2: Iterating directly (Efficient)**
Searching for a specific sensor without creating a full list in memory.

```python
target_sensor = None
for item in self.twin.at('sensors').children():
    if item.v == 'humidity':
        target_sensor = item
        break
```

### Reactivity (`subscribe`)

Only available in `ttStore`. This allows subscribing a method to data changes.

#### `subscribe(path, callback)`

* **path:** The path to monitor (e.g., `'sensors'`).
* **callback:** The method called upon change.

The callback receives a list of `updates`. Each update is a tuple: `(path, new_value, old_value, source)`.

**Example:**

```python
def ttse__on_start(self):
    # Listen to anything changing under 'sensors'
    self.twin.subscribe("sensors", self.ttse__on_sensor_update)

def ttse__on_sensor_update(self, updates):
    for path, new, old, source in updates:
        print(f"Sensor update at {path}: {old} -> {new}")
```

### Utilities (`dumps`, `group`, `source`)

#### `dumps()`

Returns a string representation of the entire store (useful for debugging).

```python
print(self.twin.dumps())
```

#### `group(notify=True, source_id=None)` & `source(source_id)`

Context managers to control how updates are processed.

1. **`group(notify=False)`**: Performs updates atomically.

* **Usage:** Batch initialization. No events are fired until the block ends (or never if `notify=False`).

  ```python
  with self.twin.group(notify=False):
      self.twin.set(...) 
  ```

2. **`source(source_id)` / `group(..., source_id=...)`**:

* **Usage:** Identifying *who* made the change. This is crucial for bidirectional sync (e.g., connecting a GUI slider to
  a value).
* If a GUI updates the Store, the Store notifies the GUI. You want the GUI to ignore that notification to prevent an
  infinite loop.

  ```python
  # Example: Updating from a specific source (e.g., 'GUI')
  with self.twin.source('GUI'):
      self.twin['parameters/speed'] = 50
  
  # In the callback, you can check the source:
  def on_change(self, updates):
      for path, new, old, src in updates:
          if src == 'GUI':
              continue # Ignore changes I made myself
          # Update GUI display...
  ```

---

## Performance & Best Practices

Although `ttStore` is powerful, consider the following points for optimal performance and clean code.

### 1. Batch Updates with `group`

When modifying a lot of data simultaneously (e.g., during startup or reset), always use
`with self.group(notify=False):`.

* **Reason:** Without this, every single write action triggers all subscribers immediately. `group` prevents this "
  update storm".

### 2. Efficiency of `Item`

If you need to read or write the same value frequently in a loop (e.g., a timer), retrieve the `Item` **once** during
`__init__` or `on_start`, and cache it.

* **Inefficient:** Calling `self.twin.get('sensors/#0/value')` in every cycle (must parse the path string every time).
* **Efficient:**
    ```python
    # In __init__:
    self.temp_val_item = self.twin.at('sensors/#0/value')

    # In timer loop:
    self.temp_val_item.v += 0.1
    ```

### 3. Data Types

The Store is not strictly typed (it is Python), but consistency is key. If a path starts as a `float` (`15.0`), try to
keep it that way and do not suddenly change it to a `string` ("15"), unless your application logic specifically handles
this.

---

## Example Implementation

Below is a full integration where `MyProcess` writes data and `OperatorInterface` reacts to that data via the
`DigitalTwin` store.

```python
from TaskTonic import *
from TaskTonic.ttTonicStore import ttStore
import random


# --- The Data Repository Service ---
class DigitalTwin(ttStore):
    _tt_is_service = "digital_twin"  # Service name for binding

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_record['auto_finish'] = True

    def _init_post_action(self):
        super()._init_post_action()
        # Use group(notify=False) for performance during init
        with self.group(notify=False):
            # Because the set method uses Iterable, both tuples (()) and lists [] are valid.
            self.set((
                ('parameters/update_freq', 2),
                ('parameters/temp_limit', 10),
                ('sensors/#', 'temp'),         # Create sensor 0
                ('sensors/./value', 15.0),
                ('sensors/./unit', '℃'),
                ('sensors/./high_alarm', False),
                ('sensors/#', 'humidity'),     # Create sensor 1
                ('sensors/./value', -1),
            ))

        self.log(f"Digital Twin is initialized\n{self.dumps()}")


# --- The Observer (e.g., GUI or Logger) ---
class OperatorInterface(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        # Bind to the service
        self.twin = self.bind(DigitalTwin)

    def ttse__on_start(self):
        # Subscribe to sensor changes
        self.twin.subscribe("sensors", self.ttse__on_sensor_update)
        # Schedule parameter update and end of program
        self.bind(ttTimerSingleShot, 5, sparkle_back=self.ttse__on_parm_update)
        self.bind(ttTimerSingleShot, 8, sparkle_back=self.ttse__on_end_program)

    def ttse__on_sensor_update(self, updates):
        for path, new, old, source in updates:
            # Use .at(path) to get an Item for smart navigation
            # .list_root automatically navigates up to the sensor item (e.g., 'sensors/#0')
            sensor_item = self.twin.at(path).list_root

            # Retrieve name and value via the item
            name = sensor_item.v
            val = sensor_item['value'].v
            unit = sensor_item.get('unit', '')

            self.log(f"UPDATE OF SENSOR {name}: {val:.3f}{unit}")

    def ttse__on_parm_update(self, tmr):
        self.twin['parameters/update_freq'] = .5

    def ttse__on_end_program(self, tmr):
        self.finish()


# --- The Controller (Process Logic) ---
class MyProcess(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        self.my_record['auto_finish'] = True
        self.twin = self.bind(DigitalTwin)

        # Performance optimization: Cache the item pointer
        # This avoids parsing the path string in every loop cycle
        self.temp_sens_item = self.twin.at('sensors/#0')

    def ttse__on_start(self):
        self.twin.subscribe("parameters", self.ttse__on_param_update)
        # Start a timer based on a parameter from the store
        freq = self.twin.get('parameters/update_freq', 5)
        self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__on_param_update(self, updates):
        for path, new, old, source in updates:
            if path == 'parameters/update_freq':
                self.utmr.stop()
                # Restart timer with new frequency
                freq = self.twin.get('parameters/update_freq', 5)
                self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__update_timer(self, tmr):
        # Writing directly via the cached item is very efficient
        self.temp_sens_item['value'].v += random.uniform(-2, 2)


# --- App Configuration ---
class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_starting_tonics(self):
        DigitalTwin()
        OperatorInterface()
        MyProcess()


if __name__ == '__main__':
    myApp()
```