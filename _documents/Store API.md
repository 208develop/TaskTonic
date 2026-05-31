# TaskTonic Store & Item API Documentation

The TaskTonic state management system consists of two primary components:

1. **`Store`**: The thread-safe, hierarchical data core that handles storage, pub/sub notifications, and batching.
2. **`Item`**: A convenient, cursor-like view representing a specific path within the `Store`, allowing for intuitive
   data manipulation and traversal.

---

## 1. Class: `Store`

The central registry. It holds the state and manages all updates and subscriptions.

### Core Methods

#### `at(path: str) -> Item`

Returns an `Item` cursor pointing to the specified path in the store.

```python
from TaskTonic.internals import Store

store = Store()
settings = store.at("app/settings")
```

#### `set(path_or_data, value=None, notify=True) -> Item`

Updates a value or performs a batch update at the root level.

```python
# Single value update
store.set("system/status", "online")

# Batch dictionary update
store.set("system/metrics", {
    "cpu": 45,
    "memory": 1024
})
```

#### `get(path: str, default=None) -> Any`

Retrieves a value by its absolute path.

```python
cpu_usage = store.get("system/metrics/cpu", default=0)
```

#### `subscribe(path, callback, ignore_source=None, recursive=True, exclude=None)`

Listens for changes on a specific path. By default, it also triggers when descendant paths change.

```python
def on_user_change(events):
    for path, new_val, old_val, source in events:
        print(f"Path '{path}' changed from {old_val} to {new_val}")

# Listen to all changes under 'users', except for 'users/temporary'
store.subscribe("users", on_user_change, exclude=["users/temporary"])
```

### Context Managers

#### `group(source_id=None, notify=True)`

Batches multiple updates into a single notification event. Highly recommended when updating multiple related fields to
prevent redundant callback triggers.

```python
# Both updates happen, but listeners are only notified once at the end of the block.
with store.group(source_id="network_sync"):
    store["player/x"] = 150
    store["player/y"] = 200
```

---

## 2. Class: `Item`

An object-oriented way to interact with the `Store`. You usually get an `Item` by calling `store.at("path")` or
`store["path"]`.

### Properties

#### `.v`

Directly gets or sets the value of the current item. Writing to `.v` always triggers a notification unless grouped.

```python
health_item = store.at("player/health")
health_item.v = 100

if health_item.v < 20:
    print("Warning: Low health!")
```

#### `.parent`

Returns an `Item` pointing to the direct parent container.

```python
city_item = store.at("users/profile/address/city")
address_item = city_item.parent  # Points to "users/profile/address"
```

#### `.list_root`

Walks up the path tree to find the nearest ancestor created as a list item (identified by the `#` syntax, e.g., `#0`,
`user#1`). Very useful in callbacks to find the context of a deeply nested change.

```python
# Imagine a path: "devices/#0/sensors/temperature"
temp_item = store.at("devices/#0/sensors/temperature")

# Quickly grab the device root item ("devices/#0")
device_root = temp_item.list_root
print(f"Device name: {device_root['name'].v}")
```

### Methods

#### `set(data, value=None, notify=True)`

The most versatile way to write data. It supports **Smart Pathing**:

- `#`: Appends a new item to a list.
- `.`: Targets the *last created* item in a list.

```python
users = store.at("users")

# Smart Pathing: Add a new user and assign sub-properties instantly
users.set("#", "Alice")           # Creates users/#0
users.set("./role", "Admin")      # Targets users/#0/role
users.set("./age", 32)            # Targets users/#0/age

# Batch setting via dictionary
users.set("#", "Bob")             # Creates users/#1
users.at(".").set({
    "role": "Editor",
    "age": 25
})
```

#### `get(key: str, default=None)`

Dictionary-style lookup for children relative to this item.

```python
bob_item = store.at("users/#1")
bob_role = bob_item.get("role", "Guest")
```

#### `append(prefix=None)` / `extend(data_list, prefix=None)`

Explicit methods to add items to a list container.

```python
devices = store.at("devices")

# Using append explicitly instead of '#'
new_device = devices.append(prefix="sensor")  # Creates devices/sensor#0
new_device.v = "Thermometer"
new_device["active"] = True

# Extend with multiple items
devices.extend(["Barometer", "Hygrometer"], prefix="sensor")
```

#### `pop(subpath=None)` / `remove(subpath=None)`

Removes an item (or a child of the item). `pop` returns the value before deletion.

```python
cart = store.at("shopping_cart")
cart["apples"] = 5

# Remove and get the value
apple_count = cart.pop("apples")  # returns 5
```

#### `children(prefix=None)`

Iterates over all direct child `Item`s.

```python
for user in store.at("users").children():
    print(f"User path: {user.path}, Value: {user.v}")
```

#### `dumps()`

Returns a formatted string representing the subtree, perfect for debugging.

```python
print(store.at("users").dumps())
```

---

## 3. Store Lists: A Deep Dive

Unlike a standard Python `list` where elements are stored in a linear array (making finding a specific deep item
potentially slow), TaskTonic **Store Lists** use a hierarchical key-value structure with auto-incrementing keys (like
`#0`, `#1`).

**The Speed Advantage:** Because every list item has an absolute path (`teams/#1/score`), retrieving it is a direct
`O(1)` dictionary lookup. You never have to iterate through an array to find or update an item; you just target its
exact path.

Let's build a list step-by-step to see how the syntax changes the structure.

### 3.1. Basic Append vs. Container Append

There is a big difference between assigning a value directly to the list node (`list/# = value`) versus making the list
node a container for other properties (`list/#/property = value`).

```python
store = Store()
team = store.at("team")

# 1. Basic Append: The node itself holds the value.
team["#"] = "Alice"

print(team.dumps())
# Dump of <team>:
#   #0 = Alice

# 2. Container Append: The node holds children, not a direct value.
team["#/name"] = "Bob"

print(team.dumps())
# Dump of <team>:
#   #0 = Alice
#   #1/name = Bob    <-- Notice #1 has no direct value, it's a container for 'name'
```

### 3.2. Targeting the Last Item (`.`)

When you create a container item, you often want to add more properties to that *exact same* newly created item. You use
the `.` syntax for this.

```python
# The '.' points to the last created item (#1 in this case)
team["./role"] = "Developer"
team["./age"] = 30

print(team.dumps())
# Dump of <team>:
#   #0 = Alice
#   #1/name = Bob
#   #1/role = Developer
#   #1/age = 30
```

### 3.3. Custom Prefixes (`prefix#`)

If you store different types of entities in the same container, you can prefix the `#`. Each prefix maintains its own
auto-incrementing counter.

```python
store["devices/sensor#"] = "TempSensor"
store["devices/sensor#"] = "LightSensor"
store["devices/camera#"] = "MainCamera"

print(store.at("devices").dumps())
# Dump of <devices>:
#   camera#0 = MainCamera
#   sensor#0 = TempSensor
#   sensor#1 = LightSensor
```

### 3.4. Popping an Entire Tree

Because the store is hierarchical, calling `pop()` or `remove()` on a list root item deletes that element **and all of
its children** instantly.

```python
# Bob (#1) leaves the team
popped_val = team.at("#1").pop()

print(team.dumps())
# Dump of <team>:
#   #0 = Alice
# (Bob's name, role, and age are all completely removed from the store)
```

---

## 4. Crucial Concept: Native Python Collections in the Store

You can store native Python collections (like `list`, `dict`, `set`) as a value in the Store, but **you must be aware of
how notifications work.**

```python
# Storing a native Python list
store["inventory/items"] = ["Sword", "Shield"]
```

⚠️ **WARNING:** If you mutate this native list directly, the Store will **NOT** trigger a change notification, because
the object reference hasn't changed (the Store doesn't know the inside of the list changed).

```python
# THIS DOES NOT TRIGGER NOTIFICATIONS!
store["inventory/items"].v.append("Potion") 
```

**The Solution:**
If you need to store native collections and still want UI updates/notifications, you should maintain a separate
`version` or `length` parameter that you update alongside the mutation, and subscribe to that instead.

```python
# Subscribe to the version instead
store.subscribe("inventory/version", on_inventory_update)

# When modifying the native list, also update the version trigger
with store.group():
    store["inventory/items"].v.append("Potion")
    # This triggers the notification!
    store["inventory/version"].v = store.get("inventory/version", 0) + 1 
```

*Alternatively, translate the data into a TaskTonic Store List (using `#`) so the Store tracks every deep change
natively.*

---

## 5. TaskTonic Framework: Do's and Don'ts

- **DO** use `with store.group():` when updating multiple properties of the same object to prevent spamming your
  subscribers with incomplete data states.
- **DO** use the smart pathing (`#` and `.`) for clean, readable list building.
- **DO** use `item.list_root` inside your event listeners to easily find the primary record associated with a nested
  change.
- **DON'T** mutate native Python `list` or `dict` objects stored in `.v` and expect listeners to fire. Use a sibling
  `version` node or convert them to TaskTonic Store Lists.
- **DON'T** use single-line `if` statements with colons (e.g., `if True: return`) in your callbacks or business logic.
  Always put the statement on a new line.
- **DON'T** let line lengths exceed 120 characters to maintain readability across the framework.
- **DON'T** write to `item.v` inside a rapid loop without a silent group, as it will trigger massive amounts of callback
  notifications.