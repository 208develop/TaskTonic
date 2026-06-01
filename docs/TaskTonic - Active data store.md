# ttStore & Store/Item: Central Data Repository

<img src="../assets/tasktonic-store.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">

This documentation describes the complete functionality of the `Store` and `Item` classes, and their integration within TaskTonic via `ttStore`.

## Introduction

In complex applications, it is essential to share data between different components in a structured and accessible way. `ttStore` functions as a **Central Data Repository**. It offers a hierarchical storage structure (comparable to a file system or a nested dictionary) that is:

1. **Centralized:** A single source of truth for parameters, sensor values, and configurations.
2. **Reactive:** Components can subscribe to changes in specific data paths.
3. **Flexible:** Data can be accessed via absolute paths or relative pointers (`Item`).

By utilizing the Store, you create a clean **separation of concerns** in your application. For example: a hardware processing component simply writes sensor data to the Store, and the UI component receives an automatic notification to update its display, without either component needing to know about the other's existence.

---

## Concepts: Store vs. ttStore

The system consists of two layers that can also be used **independently**.

### 1. The Core: `Store` and `Item`

The `Store` is the pure data container. It is a standalone class that holds the data and provides methods to read or write data via paths (e.g., `'sensors/temp/value'`).

The `Item` is a smart "pointer" or "cursor" to a specific location in the `Store`. It allows for relative navigation without needing to know the full absolute path.

> **Note:** `Store` and `Item` can be used outside of TaskTonic in any Python project requiring a powerful, hierarchical data structure. Every node can be a "value" AND a "container" simultaneously.

### 2. The Service: `ttStore`

`ttStore` is the TaskTonic wrapper around a `Store`. It transforms the store into a **Service** within the TaskTonic ecosystem. This adds capabilities such as:

- **Event-driven updates:** Automatically notify other Tonics (like UI or controllers) upon changes.
- **Service Binding:** Easily linked to other Tonics via `self.bind()`.

---

## The Basics: Reading & Writing Data

Below is an overview of the foundational methods for data manipulation.

### Dictionary Access (`[]` Syntax)

For convenience, `ttStore` and `Item` support standard Python dictionary syntax.

- **Reading:** `val = store['path']` (Equivalent to `.get('path')`. Returns `None` if not found).
- **Writing:** `store['path'] = val` (Equivalent to `.set([('path', val)])`. Triggers updates immediately).

```python
# Read
current_limit = self.twin['parameters/temp_limit']

# Write
self.twin['parameters/temp_limit'] = 12.0
```

### Writing Data (`set`, `.v`, `.append`)

#### `set(data)`

Writes one or multiple values to the store atomically. It accepts a `dict` or an `Iterable` (list/tuple) of tuples.

- **Usage:** Initialization, bulk updates, or when you need to write multiple values without triggering incomplete notifications.
- **Smart Paths:**
  - `#`: Creates a new unique entry (auto-increment list). Finds the highest index and adds 1.
  - `./`: Refers to the most recently generated index by that specific cursor.

```python
# Initialize a store with parameters and sensors using smart paths
self.twin.set((
    ('parameters/update_freq', 2),     # Set update frequency to 2
    ('sensors/#', 'temp'),             # Create new sensor 'temp' (e.g., sensors/#0)
    ('sensors/./value', 15.0),         # Set value of THAT sensor
    ('sensors/./unit', 'C'),           # Set unit of THAT sensor
))
```

#### `.v` (Value Property via Item)

If you hold an `Item` object (a pointer to a location), you can read and write directly via the `.v` property.

```python
# Assume we have a pointer (Item) to the sensor value
sensor_val_item = self.twin.at('sensors/#0/value')

# Write a new value
sensor_val_item.v = 22.5
```

#### `append(value)` and `append(path, value)`

Adds a new item to a list. A cleaner alternative to using the `'path/#'` syntax when adding single items.

```python
# Append via Store
self.twin.append('logs', 'System Started')

# Append via Item
log_item = self.twin.at('logs')
log_item.append('User logged in')
```

### Reading Data (`get`, `at`)

#### `get(path, default=None)`

Retrieves the value of a specific path. If the path does not exist, the `default` value is returned. Resolves through `StoreLinks` automatically.

```python
freq = self.twin.get('parameters/update_freq', 5)  # Default 5 if not found
```

#### `at(path) -> Item`

Returns an `Item` cursor pointing to the location `path`. This is **more powerful** than `get` because it allows further navigation.

```python
# Get a pointer (Item) to the first sensor
sensor_item = self.twin.at('sensors/#0')

# Read values via the Item
print(sensor_item['value'].v)
```

---

## Details & Smart Usage

### Navigation (`Item` objects)

An `Item` object acts as a smart window onto your data.

- **`item['child']`**: Navigate to a sub-item.
- **`item.parent`**: Returns an `Item` to the parent node.
- **`item.list_root`**: If the item is part of a list, this returns the list item itself (e.g., `#0`), regardless of how deep you are in the hierarchy.

```python
# If located at 'sensors/#0/value', list_root returns 'sensors/#0'
sensor_name = sensor_item.list_root.v 
```

#### `.children(prefix=None)`

Returns an **iterator** (lazy evaluation for memory efficiency) of `Item` objects that are direct children.

```python
# Iterating directly without creating a full list in memory
target_sensor = None
for item in self.twin.at('sensors').children():
    if item.v == 'humidity':
        target_sensor = item
        break
```

### Graph Navigation (`StoreLinks`)

While strict hierarchy ensures data integrity, `StoreLinks` provide symlinks to solve functional grouping via `.link_to()`.

- **Passive Links (`bubble_events=False`):** Delegates reads/writes. Events do not bubble up the alias tree (prevents UI event storms).
- **Active Links (`bubble_events=True`):** Two-way connections. If the physical target changes, an event bubbles up the alias tree. Perfect for sensors.

```python
room_lamp = self.twin.at("house/living/main_light")
room_lamp.link_to("devices/lamp_1", bubble_events=False)

# Writing to the alias automatically routes to devices/lamp_1
room_lamp.at("brightness").v = 80 
```

### Batch Iteration (`set_each`)

Updates a specific sub-property across all children of a node within a single atomic group.

```python
living_room = self.twin.at("house/living/lamps")
living_room.set_each("power", "off", prefix="lamp")
```

### Reactivity (`subscribe`)

Connects data changes to your Tonic's Sparkles (`ttse__`). The callback receives a list of `updates`. Each update is a tuple: `(path, new_value, old_value, source)`.

#### Exact, Recursive & Wildcards (`*`, `**`)

- **Exact:** Triggers only on the specific path.
- **Recursive:** Triggers on the path AND any of its children.
- **`*`:** Matches exactly one path level.
- **`**`:** Matches all underlying path levels.

```python
# Matches 'sensors/kitchen/temp' but NOT 'sensors/kitchen/temp/calibration'
self.twin.subscribe("sensors/*/temp", self.ttse__on_temp_change)
```

#### Atomic Snapshots (`extract` & `trigger_now`)

Fetch a flat dictionary snapshot instantly instead of piecing together single-property events. Easy for grouping data and essential when you need to be certain of all value at the moment on of them changed.

```python
def ttse__on_start(self):
    self.twin.subscribe(
        "ui/widgets/*", 
        self.ttse__render_widget, 
        extract=[".", "color", "visible"], 
        recursive=True,
        trigger_now=True
    )

def ttse__render_widget(self, events):
    for path, snapshot, old, source in events:
        color = snapshot.get("color")
```

### Context Managers & Utilities (`group`, `source`, `dumps`)

- **`dumps()`**: Returns a string representation of the entire store (useful for debugging).
- **`group(notify=True, source_id=None)`**: Batches multiple updates atomically. `notify=False` silences updates entirely (useful during init).
- **`source(source_id)`**: Tags updates with an origin ID. Vital for bidirectional UI sync to prevent infinite loops.

```python
# Identifying who made the change
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

1. **Batch Updates with `group`:** When modifying a lot of data simultaneously (e.g., during startup or reset), always use `with self.group(notify=False):`. This prevents "update storms".
2. **Efficiency of `Item`:** If you need to read or write the same value frequently in a loop (e.g., a timer), retrieve the `Item` **once** during `__init__` or `on_start`, and cache it. Avoid parsing path strings in every cycle.
3. **Data Types:** The Store is not strictly typed, but consistency is key. If a path starts as a `float` (`15.0`), try to keep it that way.

---

## API Reference

### Core Methods on `Store` & `ttStore`

- `at(path: str) -> Item`
- `get(path: str, default: Any = None) -> Any`
- `set(data: Union[str, dict, tuple], value: Any = None, notify: bool = True) -> Item`
- `append(path: str, value: Any) -> Item`
- `subscribe(path: Union[str, List[str]], callback: Callable, ignore_source: str = None, recursive: bool = False, exclude: List[str] = None, extract: List[str] = None, trigger_now: bool = False, owner: object = None)`
- `unsubscribe(target: Union[Callable, object])`
- `dumps() -> str`

### Core Methods on `Item` (Cursor)

- `.v` (Property: get/set value)
- `.path` (Property: absolute path string)
- `.parent` (Property: parent Item)
- `.list_root` (Property: nearest auto-increment list ancestor)
- `.key` (Property: last segment of the path)
- `set(data, value=None, notify=True)`
- `append(prefix=None) -> Item`
- `pop(subpath=None) -> Any`
- `remove(subpath=None)`
- `children(prefix=None) -> Iterator['Item']`
- `link_to(target_path: str, bubble_events: bool = False) -> Item`
- `set_each(subpath: str, value: Any, prefix: str = None) -> Item`

---

## Example Implementation

Below is a full integration where `MyProcess` writes data and `OperatorInterface` reacts to that data via the `DigitalTwin` store.

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
            self.set((
                ('parameters/update_freq', 2),
                ('parameters/temp_limit', 10),
                ('sensors/#', 'temp'),         # Create sensor 0
                ('sensors/./value', 15.0),
                ('sensors/./unit', 'C'),
                ('sensors/./high_alarm', False),
                ('sensors/#', 'humidity'),     # Create sensor 1
                ('sensors/./value', -1),
            ))

        self.log(f"Digital Twin is initialized\n{self.dumps()}")


# --- The Observer (e.g., GUI or Logger) ---
class OperatorInterface(ttTonic):

    def __init__(self, name=None, context=None, log_mode=None, catalyst=None):
        super().__init__(name, context, log_mode, catalyst)
        self.twin = DigitalTwin()

    def ttse__on_start(self):
        # Subscribe to sensor changes
        self.twin.subscribe("sensors", self.ttse__on_sensor_update)
        # Schedule parameter update and end of program
        ttTimerSingleShot(5, sparkle_back=self.ttse__on_parm_update)
        ttTimerSingleShot(8, sparkle_back=self.ttse__on_end_program)

    def ttse__on_sensor_update(self, updates):
        for path, new, old, source in updates:
            # .list_root automatically navigates up to the sensor item (e.g., 'sensors/#0')
            sensor_item = self.twin.at(path).list_root

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
        self.twin = DigitalTwin()

        # Performance optimization: Cache the item pointer
        self.temp_sens_item = self.twin.at('sensors/#0')

    def ttse__on_start(self):
        self.twin.subscribe("parameters", self.ttse__on_param_update)
        freq = self.twin.get('parameters/update_freq', 5)
        self.utmr = self.bind(ttTimerRepeat, freq, sparkle_back=self.ttse__update_timer)

    def ttse__on_param_update(self, updates):
        for path, new, old, source in updates:
            if path == 'parameters/update_freq':
                self.utmr.stop()
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