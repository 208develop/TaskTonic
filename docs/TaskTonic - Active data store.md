# TaskTonic Store for Reactive Data Management

<img src="../assets/tasktonic-store.png" align="left" width="350" style="margin-right: 25px; margin-bottom: 20px; border-radius: 8px;" alt="TaskTonic Philosophy">


In complex, asynchronous systems, maintaining a consistent, thread-safe application state is one of the greatest challenges. The TaskTonic Store module provides a centralized, hierarchical, and reactive data engine. The module consists of two complementary core components:

1.  **`Store`**: The pure, functional, thread-safe data core. It handles hierarchical storage, lock management, MQTT-style wildcard pub/sub notifications, and atomic updates.
2.  **`Item`**: A highly powerful, cursor-like view/pointer that references a specific path within the `Store`. This enables relative navigation, local mutations, and isolated subscriptions.

Within the framework, the store is exposed as a Singleton Service via the **`ttStore`** class, accessible in your Tonics via `self.ledger.formula`.

---

## 1. Core API & Data Access

TaskTonic provides multiple ways to interact with data, balancing performance and developer convenience. 
Using the store is a bit like using a python dictionary but with hierarchical paths and strongly optimised for storing
and distributing data in een reactive systems.

### 1.1 Dictionary Syntax (`[]`)
For quick, intuitive access, both the `Store` and `Item` objects fully support standard Python dictionary bracket syntax. Reading missing paths natively returns `None` instead of raising a `KeyError`.

```python
# Writing data
store["machine/status"] = "operational"
store["machine/metrics/temperature"] = 22.5

# Reading data
current_status = store["machine/status"]
```

### 1.2 The `get` and `set` Method
If you want to read a value and provide a fallback if the path doesn't exist, use `.get()`.

```python
# Returns 60 if 'machine/metrics/speed' is not found
speed = store.get("machine/metrics/speed", default=60)
```

Setting data, single line or multipole line, can be done using set.

``` python
        # one item
        self.store.set('setting/ui/background', 'blue')
        
        # multiple items by dict
        self.store.set({
            'setting/ui/font', 'arial',
            'setting/ui/font_size', 10,
        })        
        
        # multiple items by tuple of tuples
        self.store.set((
            ('setting/ui/font', 'arial'),
            ('setting/ui/font_size', 10),
        ))
```

### 1.3 Live Links / Pointers (`Item` Cursors)
If you need to read or write to the same path repeatedly (e.g., inside a rapid timer loop), parsing the path string every time via `store["path"]` is inefficient. Instead, use `.at()` to generate an `Item` cursor. 

Storing this `Item` in a variable creates a **live link** to that location in the store. You can read/write its value directly via the `.v` property, or use it to navigate relatively.

```python
from TaskTonic import ttTonic

class DisplayTonic(ttTonic):
    def ttse__on_start(self):
        # Create a cursor to a specific branch
        self.ui_settings = self.ledger.formula.at('settings/ui')
        
        # Dictionary syntax writes relative to the cursor
        self.ui_settings['background'] = 'blue'
        
        # .v property writes directly to the cursor's path
        self.ui_settings.at('opacity').v = 0.8
```

---

## 2. Hybrid Nodes & Smart Lists

Traditional data structures force a node to be either a value (a leaf, like a string) or a container (a map or folder). The TaskTonic Store breaks this dogma by introducing **Hybrid Nodes**.

Every path in the Store can **simultaneously** hold a direct value and harbor sub-paths (children).

### 2.1 The Auto-Increment (`#`)
If you store a standard Python list in the Store and append to it, the Store *will not know* its contents changed, and subscriptions won't trigger. 

TaskTonic uses **Smart Lists** (Dictionaries with auto-incrementing keys). The `#` symbol instructs the Store to scan the active list, determine the highest numeric index, increment it by 1, and create a brand new item. Because every item gets an absolute path (e.g., `users/#1/name`), retrieving deep data is a direct `O(1)` lookup.

### 2.2 The "Sticky" Index (`.`)
The `.` symbol refers to the **most recently generated index** by that specific cursor. This is essential for adding multiple properties to the exact same newly created list item without looking up its generated index.

### 2.3 Creating Valueless Container Lists
Often, you want to create a list of complex objects where the index itself (e.g., `#0`) doesn't hold a direct value (its `.v` is `None`), but acts purely as a container for children. 

To achieve this, simply **target the child property directly during creation**, rather than assigning a value to the `#`.

```python
class UserManager(ttTonic):
    def ttsc__add_users(self):
        users = self.ledger.formula.at('settings/users')

        # METHOD A: Direct assignment to a sub-property
        # Notice how 'users/#0' has no direct value, but acts as a container for 'name'
        users.set('#/name', 'Bob')     # Creates index #0
        users.set('./role', 'Admin')   # Adds 'role' to #0
        users.set('./age', 32)         # Adds 'age' to #0

        # METHOD B: Atomic batch creation using `set()` and a tuple of tuples
        # This prevents triggering multiple incomplete notifications during setup
        users.set((
           ('emp#', 'New Employee'),   # Creates 'emp#0', where .v = 'New Employee'
           ('./department', 'Sales'),
           ('./salary', 50000),
        ))
```

### 2.4 Custom Prefixes (`prefix#`)
As seen in Method B above, you can segregate different entities within the same tree branch by placing text before the `#` symbol. Each prefix maintains its own independent counter.

```python
users.set('guest#/name', 'Charlie')  # Becomes: users/guest#0/name
users.set('guest#/name', 'Dave')     # Becomes: users/guest#1/name
```

---

## 3. Navigating the Tree (`Item` Methods)

Once you hold an `Item` cursor, you can navigate up, down, and across the data tree efficiently.

* **`.parent`**: Returns a new `Item` pointing exactly one level up to the parent container.
* **`.list_root`**: Recursively navigates up the path tree to identify the nearest list-container (identifiable by the `#` syntax). This is crucial within callbacks to find the surrounding entity of a mutated child property.
* **`.key`**: Returns the last segment of the path (e.g., `#0` or `brightness`).

### 3.1 The `children` Iterator
To loop over elements in a container, use the `.children()` method. This returns a memory-efficient **Iterator** of `Item` cursors (lazy evaluation).

```python
sensor_container = store.at("sensors")

# Efficiently iterate without loading the entire tree into memory
for child_item in sensor_container.children():
    if child_item.get("status") == "critical":
        # Handle critical sensor...
        pass
```

---

## 4. Graph Navigation (`StoreLinks`)

While the strict hierarchical tree is great for data integrity (the "Canonical State"), you often need to view data functionally (as a Graph). TaskTonic provides **Symlinks** to solve this via the `.link_to()` method.

### 4.1 Passive Links (`bubble_events=False`)
A passive link acts as a transparent shortcut. It delegates reads and writes to the target. Events bubble up the target's physical tree, but **do not** bubble up the alias tree (preventing UI event storms).

```python
class HouseController(ttTonic):
    def ttse__on_start(self):
        # Canonical state
        self.ledger.formula.set("devices/lamp#/brightness", 0)  # creating lamp#0

        # Functional grouping (Passive link)
        room_lamp = self.ledger.formula.at("house/living/main_light")
        room_lamp.link_to("devices/lamp#0", bubble_events=False)

        # Writing to the alias automatically routes to devices/lamp_1
        room_lamp["brightness"] = 80 
```

### 4.2 Active Links (`bubble_events=True`)
Active links are two-way connections. If the physical target changes, the Store automatically injects a cloned event into the alias tree. **Use this for sensors** where a room-controller needs to be actively notified of hardware triggers happening deep in the device tree.

```python
sensor_alias = self.ledger.formula.at("security/front_door")
sensor_alias.link_to("devices/motion_1", bubble_events=True)
# Now, if devices/motion_1 triggers, the 'security/front_door' path 
# will also bubble the event to any active subscribers.
```

---

## 5. Batch Iteration (`set_each`)

When updating a collection, doing it item-by-item triggers redundant pub/sub notifications. `.set_each()` iterates over children and updates them inside a single atomic `group()`.

```python
class LightingTonic(ttTonic):
    def ttsc__turn_off_all_lamps(self):
        living_room = self.ledger.formula.at("house/living/lamps")
        
        # Resolves through any StoreLinks and fires ONE batch notification
        living_room.set_each("power", "off", prefix="lamp")
```

---

## 6. Advanced Reactivity & Pub/Sub Patterns

The `subscribe` method is the core of TaskTonic's reactivity. It connects data changes to your Tonic's Sparkles (`ttse__`). 

Your event sparkle will receive a list of updates. Each update is a tuple: `(path, new_val, old_val, source_id)`.

### 6.1 Exact vs. Recursive Subscriptions
* **Exact:** Triggers only on the specific path.
* **Recursive:** Triggers on the path AND any of its nested children.

```python
class ProfileWatcher(ttTonic):
    def ttse__on_start(self):
        profile = self.ledger.formula.at("user/profile")
        
        # Trigger on ANY change inside the profile (name, age, settings)
        profile.subscribe(self.ttse__on_profile_update, recursive=True)
```

### 6.2 MQTT-Style Wildcards (`*` and `**`)
Subscribe to dynamic paths without knowing the exact IDs upfront:
* `*` (Single-level): Matches exactly **one** path segment.
* `**` (Multi-level/Recursive): Matches **all** deeper path segments.

```python
class SensorDashboard(ttTonic):
    def ttse__on_start(self):
        store = self.ledger.formula
        
        # Matches 'sensors/kitchen/temp' but NOT 'sensors/kitchen/temp/calibration'
        store.subscribe("sensors/*/temp", self.ttse__on_temp_change)

        # Matches ANY error deep inside the system tree
        store.subscribe("system/**/error", self.ttse__on_system_error)
```

### 6.3 Atomic Snapshots (`extract` and `trigger_now`)
Instead of receiving raw single-property events (which can cause UI stuttering), request a flat dictionary (snapshot). Use `.` inside the extract list to retrieve the value of the base path itself.

* **`extract`**: A list of relative properties to fetch simultaneously.
* **`trigger_now=True`**: Immediately fires a synthetic `init` event upon subscription. Perfect for rendering UI lists without manually polling the Store first.

```python
class UIRenderer(ttTonic):
    def ttse__on_start(self):
        # Subscribe to all widgets, grab their state instantly, and build snapshots
        self.ledger.formula.subscribe(
            "ui/widgets/*", 
            self.ttse__render_widget, 
            extract=[".", "color", "visible"], 
            recursive=True,
            trigger_now=True
        )

    def ttse__render_widget(self, events):
        for path, snapshot, old_val, source in events:
            # Snapshot is safely pre-assembled: {'.': 'button', 'color': 'red', 'visible': True}
            widget_type = snapshot.get(".")
            color = snapshot.get("color")
            self.log(f"Rendering {widget_type} at {path} in {color}")
```

### 6.4 Lifecycle Management (Safe Unsubscribing)
Subscriptions are automatically linked to their `owner` (the instance that created them). **Never** unsubscribe by path; always unsubscribe by `owner` to safely clean up your component.

```python
    def ttse__on_finished(self):
        # Removes ALL subscriptions globally where this Tonic is the owner
        self.ledger.formula.unsubscribe(self)
```

---

## 7. Context Managers (`group` and `source`)

* **`group(source_id=None, notify=True)`**: Batches multiple updates. Listeners are only notified once the block ends.
* **`source(source_id)`**: Tags updates with an origin ID. Vital for bidirectional UI sync to prevent infinite loops (listeners can use `ignore_source` to drop events they caused themselves).

```python
class VolumeSlider(ttTonic):
    def ttse__on_start(self):
        vol_item = self.ledger.formula.at("audio/volume")
        # Listen to the store, but ignore updates tagged with "my_slider"
        vol_item.subscribe(self.ttse__on_external_change, ignore_source="my_slider")

    def ttse__on_user_drag(self, new_value):
        # Write to the store, tagging the source so we don't trigger ourselves
        with self.ledger.formula.source("my_slider"):
            self.ledger.formula.set("audio/volume", new_value)
```

---

## 8. Store API Reference

### Core Methods on `Store`

#### `at(path: str) -> Item`
Returns an `Item` cursor pointing to the specified absolute path.

#### `set(path_or_data: Union[str, dict, tuple], value: Any = None, notify: bool = True) -> Item`
Writes data to the root level. Supports single strings, dictionaries, or tuples of tuples.
* **Returns:** The `Item` cursor of the root.

#### `get(path: str, default: Any = None) -> Any`
Retrieves a value by its absolute path. Resolves through `StoreLink`s automatically.

#### `subscribe(path: Union[str, List[str]], callback: Callable, ignore_source: str = None, recursive: bool = False, exclude: List[str] = None, extract: List[str] = None, trigger_now: bool = False, owner: object = None)`
Registers a listener.
* **`path`**: String or list of absolute paths. Supports `*` and `**` wildcards.
* **`callback`**: The `ttse__` method to execute.
* **`ignore_source`**: Drops events originating from this `source_id`.
* **`recursive`**: If `True`, catches changes in all descendant paths. (Required if using `extract`).
* **`exclude`**: List of absolute sub-paths to ignore.
* **`extract`**: List of relative child properties to return as a flat snapshot dictionary.
* **`trigger_now`**: Immediately fires an `init` event with current data.
* **`owner`**: The object owning this subscription (auto-detected if a bound method is passed).

#### `unsubscribe(target: Union[Callable, object, List[Any]])`
Removes subscriptions. Pass the specific callback function, or the class instance (`self`) to wipe all subscriptions owned by that instance.

---

### Core Methods on `Item` (Cursor)

#### Properties
* **`.v`**: Property to get/set the value of this path. Writing triggers notifications.
* **`.path`**: Absolute path string.
* **`.parent`**: Returns an `Item` pointing one level up.
* **`.list_root`**: Walks up the path tree to find the nearest ancestor created as an auto-increment list item (`#0`, `user#1`). Returns `None` if not in a list.
* **`.key`**: Returns the last segment of the path (e.g., `#0` or `brightness`).

#### `set(data: Union[str, dict, tuple], value: Any = None, notify: bool = True) -> Item`
Writes data relative to this cursor. Fully supports `#` and `.` smart syntax.
* **Returns:** Itself, for method chaining.

#### `get(key: str, default: Any = None) -> Any`
Dictionary-style lookup for children relative to this cursor.

#### `append(prefix: str = None) -> Item`
Explicitly creates a new auto-incremented child item.
* **Returns:** An `Item` pointing to the newly created element.

#### `extend(data_list: List[Any], prefix: str = None) -> Item`
Appends multiple items to the list. If `data_list` contains tuples of length 2, it builds structures instead of flat values.

#### `pop(subpath: str = None) -> Any`
Removes the node (and all descendants) and returns its base value. Operates relative to the cursor if `subpath` is provided.

#### `remove(subpath: str = None)`
Deletes the node and all descendants without returning the value. Safely handles `StoreLink` cleanup (cascading