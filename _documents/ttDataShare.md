# DataShare Class: A User Guide

## 1. Introduction

`DataShare` is a powerful, thread-safe, hierarchical data store for Python. It's designed to be a centralized repository
for application state and configuration, allowing for complex, nested data structures that can be accessed and
manipulated via a simple path-based syntax.

**Key Features:**

* **Hierarchical Structure:** Access nested data using file-system-like paths (e.g., `'system/network/host'`).
* **Advanced List Support:** Natively create and manipulate lists within the hierarchy.
* **Dual-Value Nodes:** A single path can hold both a direct value and serve as a container for sub-keys.
* **Observer Pattern:** Subscribe to changes at any level of the data hierarchy and receive notifications.
* **Thread Safety:** All operations are thread-safe, making it ideal for multi-threaded applications.
* **Serialization:** Save and load the entire data store to a compact binary format.

---

## 2. Core Concepts

### Hierarchical Paths

Data is organized in a tree-like structure of nested dictionaries and lists. You interact with it using a **`key_path`
**, which is a string of keys joined by a separator (default is `/`).

```python
# This sets a value in a nested dictionary
ds.set('user/preferences/theme', 'dark')
```

### List Syntax

`DataShare` has special syntax for interacting with lists.

* **Append (`[]`):** Use an empty `[]` to append a new item to a list. If the list doesn't exist, it will be created.
* **Index (`[n]`):** Use `[index]` to access or modify a list item at a specific position. Negative indices are
  supported.

```python
# Appends 'admin' to the 'user/roles' list
ds.set('user/roles[]', 'admin')

# Accesses the first role
role = ds.get('user/roles[0]')
```

### Dual-Value Nodes (`_value`)

A powerful feature is that any node can have both a direct value and sub-keys. This is handled internally by storing the
direct value in a special `_value` key. This allows you to treat a path as both an endpoint and a container.

```python
# Set a direct value for 'lights'
ds.set('home/living/lights', 'on')

# Set a sub-key on the same 'lights' path
ds.set('home/living/lights/ceiling', '30%')

# The internal structure is now similar to:
# 'lights': { '_value': 'on', 'ceiling': {'_value': '30%'} }
```

---

## 3. Initialization

To start, import and instantiate the class.

```python
# Create an empty instance
ds = DataShare()

# Create an instance with initial data
initial = {
    'system': {
        'host': 'server.local',
        'port': 8080
    }
}
ds_with_data = DataShare(initial_data=initial)
```

The `initial_data` parameter can be one of:

* A `dict`.
* A `list` of `(key_path, value)` tuples.
* A `set` or `tuple` of `(key_path, value)` tuples.

---

## 4. API Reference

### `set(key_or_data, value=None)`

This is the primary method for adding or modifying data. It's highly versatile.

**1. Set a Single Value**

```python
ds.set('user/name', 'Alice')
ds.set('user/id', 123)
```

**2. Set a List Item by Index**
This will overwrite the value at the specified index.

```python
ds.set('user/roles[1]', 'moderator')
```

**3. Append to a List**
Use `[]` to add a new item to the end of a list.

* **Appending Simple Values:**
    ```python
    # Append a simple string
    ds.set('user/roles[]', 'guest')
    ```

* **Appending Complex Objects (Dictionaries):**
  A powerful feature is creating and populating a dictionary inside a list in one go.
    1. Use `[]` with a sub-key to create a new dictionary in the list and set its first value.
    2. Use a negative index like `[-1]` to refer to the item you *just* added and set more values on it.

    ```python
    # 1. Add a new user 'anna' to the 'app/users' list.
    # This creates a new dictionary: {'name': {'_value': 'anna'}}
    ds.set('app/users[]/name', 'anna')

    # 2. Add the role 'admin' to the user we just created.
    # The path 'app/users[-1]' now refers to anna's dictionary.
    ds.set('app/users[-1]/role', 'admin')

    # You can continue adding more users
    ds.set('app/users[]/name', 'ben')
    ds.set('app/users[-1]/role', 'editor')

    # The resulting list would look like this (in clean view):
    # (
    #   {'name': 'anna', 'role': 'admin'},
    #   {'name': 'ben', 'role': 'editor'}
    # )
    ```

> **Note:** When using negative indices like `[-1]` in a `batch_update` block, it refers to the list's state *at the
time of the call*, not including previous appends within the same batch.

**4. Batch Updates**
You can set multiple values at once by passing a `dict`, `list`, or `tuple`.

```python
# Using a dictionary
ds.set({
    'system/network/host': 'new-host.com',
    'system/network/port': 443
})

# Using a list of tuples
ds.set([
    ('user/active', True),
    ('user/last_login', '2025-09-22')
])
```

---

### `get(key_path, default=None, *, get_value=0)`

Retrieves data from the store, offering different "views" of the data.

* `key_path`: The path to the data.
* `default`: The value to return if the path is not found.
* `get_value`: (Keyword-only) An integer that controls the data view:
    * `0` **(Default) - Clean View:** Returns a user-friendly view. Internal `_value` wrappers are removed where
      possible. For example, `{'power': {'_value': 'on'}}` becomes `{'power': 'on'}`. This is the most common mode.
    * `1` **- Raw View:** Returns the data exactly as it's stored internally, including all `_value` wrappers.
      Dictionaries are returned as read-only `MappingProxyType` objects.
    * `2` **- Value-Only View:** Extracts only the direct value from a node's `_value` key, ignoring any sub-keys. If
      the `_value` key doesn't exist, it returns the `default`.

**Example Setup**

```python
ds = DataShare()
ds.set('lights', 'on')
ds.set('lights/ceiling', '30%')
ds.set('users[]', 'Alice')
```

The internal structure of `lights` is `{'lights': {'_value': 'on', 'ceiling': {'_value': '30%'}}}`.

**1. Using `get_value=0` (Clean View - Default)**
This mode simplifies the output by removing unnecessary `_value` wrappers.

```python
# Gets the 'lights' node and cleans it up
# The sub-key 'ceiling' is unwrapped from {'_value': '30%'} to '30%'
# The main '_value': 'on' remains because 'lights' also has other keys
clean_node = ds.get('lights')
# clean_node is a read-only dict: {'_value': 'on', 'ceiling': '30%'}

# Lists are also cleaned
users = ds.get('users')
# users is a read-only tuple: ('Alice',)
```

**2. Using `get_value=1` (Raw View)**
This shows you the exact internal structure.

```python
# Get the raw, untouched internal node for 'lights'
raw_node = ds.get('lights', get_value=1)
# raw_node is a read-only dict: {'_value': 'on', 'ceiling': {'_value': '30%'}}

# Get a single item node
user_node = ds.get('users[0]', get_value=1)
# user_node is a read-only dict: {'_value': 'Alice'}
```

**3. Using `get_value=2` (Value-Only View)**
This extracts a specific `_value` and ignores everything else.

```python
# Get only the direct value of 'lights'
state = ds.get('lights', get_value=2) # Returns 'on'

# If a node has no direct value, it returns the default
missing = ds.get('system', get_value=2, default='N/A') # Returns 'N/A'
```

---

### `getk(key_path, default=..., *, strip_prefix=False)`

Retrieves data as a **flattened tuple of `(full_key_path, value)` pairs**. This is useful for reading entire
configuration sections.

* `key_path`: The branch of the data tree to retrieve.
* `default`: If the `key_path` is not found, it returns `((key_path, default),)`. If `default` is not provided, returns
  `()`.
* `strip_prefix`: (Keyword-only) If `True`, the `key_path` is removed from the start of all returned keys, giving you
  relative paths.

```python
# Setup
ds.set('db/host', 'localhost')
ds.set('db/user/name', 'admin')

# 1. Get a flattened branch
all_db_config = ds.getk('db')
# Returns (('db/host', 'localhost'), ('db/user/name', 'admin'))

# 2. Get a branch with relative keys
relative_config = ds.getk('db', strip_prefix=True)
# Returns (('host', 'localhost'), ('user/name', 'admin'))

# 3. Handle a missing key with a default
missing = ds.getk('api/key', default='default_key')
# Returns (('api/key', 'default_key'),)
```

---

### `subscribe(key_path, callback)` & `unsubscribe(key_path, callback)`

Register a function to be called whenever data at or below a certain `key_path` changes.

**Callback Signature**
Your callback function must accept three arguments: `key`, `old_value`, and `new_value`.

```python
def my_callback(key, old, new):
    print(f"Change detected at '{key}':")
    print(f"  Old -> {old}")
    print(f"  New -> {new}")

ds.subscribe('system/network', my_callback)
```

> **Important:** The `old` and `new` values are automatically "unwrapped". If a value is a simple endpoint (internally
`{'_value': 'on'}`), you will receive the clean value (`'on'`). You only receive the full dictionary if the node has
both a direct value and sub-keys.

---

### `batch_update()`

A context manager to perform multiple `set` operations while only triggering a single round of notifications at the end.
This is highly efficient for bulk updates.

```python
with ds.batch_update():
    ds.set('user/profile/bio', '...')
    ds.set('user/profile/location', '...')
    ds.set('user/active', False)
# All notifications are sent here, at the end of the block.
```

---

## 5. Serialization & Debugging

### `serialize()` & `deserialize(data)`

Save and load the entire state of the `DataShare` object.

```python
# Save state to a file
# serialized_data = ds.serialize()
# with open('app_state.bin', 'wb') as f:
#     f.write(serialized_data)

# Load state from a file
# with open('app_state.bin', 'rb') as f:
#     loaded_data = f.read()
# new_ds = DataShare.deserialize(loaded_data)
```

### `dumps(indent=2)`

Get a human-readable, pretty-printed string representation of the data, perfect for debugging.

```python
print(ds.dumps())
```