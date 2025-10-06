import re
import threading
import weakref
import pprint
# import msgpack
import datetime
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, cast, overload, Collection

CallbackType = Callable[[str, Any, Any], None]


class DataShare:
    VALUE_KEY = '_value'
    APPEND = object()
    _sentinel = object()

    def __init__(self,
                 initial_data: Union[Dict[str, Any], List[Tuple[str, Any]], Set[Tuple[str, Any]], Tuple[
                     Tuple[str, Any], ...], None] = None,
                 separator: str = '/'):
        """
        Initializes the DataShare instance.

        :param initial_data: Optional data to pre-populate the store. It can be a
                             dictionary, or a list/set/tuple of (key, value) pairs.
        :param separator: The character for separating keys in a path. Defaults to '/'.
        """
        self._separator = separator
        self._data: Dict[str, Any] = {}

        if isinstance(initial_data, dict):
            self._data = initial_data
        elif isinstance(initial_data, (list, set, tuple)):
            self._data = self._build_data_from_iterable(initial_data)

        self._subscribers: Dict[str, Set[weakref.ReferenceType]] = {}
        self._lock = threading.RLock()
        self._batch_update_active = False
        self._pending_changes: List[Tuple[str, Any, Any]] = []

    def _parse_path(self, key_path: str) -> List[Union[str, int, object]]:
        """
        Parses a key path string into a list of keys and indices.

        Handles dictionary keys, list indices '[n]', and the list append token '[]'.
        Example: 'a/b[1]/c[]' -> ['a', 'b', 1, 'c', self.APPEND]

        :param key_path: The string path to parse.
        :return: A list of parsed path components.
        """
        if not key_path: return []
        parts = re.findall(r'[^/\[\]]+|\[-?\d+\]|\[\]', key_path)
        parsed = []
        for part in parts:
            if part == '[]':
                parsed.append(self.APPEND)
            elif part.startswith('[') and part.endswith(']'):
                parsed.append(int(part[1:-1]))
            else:
                parsed.append(part)
        return parsed

    def _traverse_path(self, parsed_path: List[Union[str, int]], create_if_missing: bool = False) \
            -> Optional[Tuple[Union[dict, list], Union[str, int]]]:
        """
        Navigates the data structure using a pre-parsed path.

        :param parsed_path: A list of keys and indices from _parse_path.
        :param create_if_missing: If True, creates nested dictionaries along the path.
        :return: A tuple containing the parent container (dict or list) and the final
                 key/index, or None if the path is not found.
        """
        if not parsed_path: return None
        current_level: Union[dict, list] = self._data

        for part in parsed_path[:-1]:
            try:
                if isinstance(part, int):
                    if not isinstance(current_level, list): return None
                    next_level = current_level[part]
                else:
                    if not isinstance(current_level, dict): return None
                    if create_if_missing:
                        # If the key exists but is not a container, we can't proceed.
                        if part in current_level and not isinstance(current_level[part], (dict, list)):
                            return None
                        next_level = current_level.setdefault(part, {})
                    else:
                        next_level = current_level.get(part)

                if next_level is None: return None
                current_level = next_level
            except (KeyError, IndexError):
                return None
        return current_level, parsed_path[-1]

    @overload
    def set(self, key_path: str, val: Any) -> None:
        ...

    @overload
    def set(self, data: Collection[Tuple[str, Any]]) -> None:
        ...

    @overload
    def set(self, data: Dict[str, Any]) -> None:
        ...

    def set(self, key_or_data: Union[str, Collection[Tuple[str, Any]], Dict[str, Any]],
            val: Any = None) -> None:
        """
        Sets a value or multiple values in the data store.

        This method is overloaded to handle single items or batch updates. It also
        handles list append syntax ('[]') and setting values at specific
        list indices ('[n]').

        :param key_or_data: The key path string or a collection (dict, list, etc.) with key / value pairs.
        For dict use key: val, for lists etc used Tuples with key and val.
        :param val: The value to set for a single key_path string.
        :raises TypeError: If the input data is not a supported type.
        :raises KeyError: If a path cannot be found or created.
        """
        if not isinstance(key_or_data, str):
            if isinstance(key_or_data, (list, set, tuple, dict)):
                with self.batch_update():
                    items_to_iterate = key_or_data.items() if isinstance(key_or_data, dict) else key_or_data
                    for key, val_item in items_to_iterate: self.set(key, val_item)
                return
            else:
                raise TypeError("Argument must be a string (key_path) or a collection.")

        key_path, value = key_or_data, val
        with self._lock:
            parsed_path = self._parse_path(key_path)

            # Case 1: List append operation ('[]')
            if self.APPEND in parsed_path:
                append_index = parsed_path.index(self.APPEND)
                path_to_list = parsed_path[:append_index]
                sub_path_in_item = parsed_path[append_index + 1:]

                res = self._traverse_path(path_to_list, create_if_missing=True)
                if res is None: raise KeyError(
                    f"Path '{'/'.join(map(str, path_to_list))}' not found or is not a container.")
                list_parent, list_key = res

                # Ensure target is a list, creating it if necessary
                if list_key not in list_parent or not isinstance(list_parent[list_key], list):
                    list_parent[list_key] = []
                target_list = list_parent[list_key]

                if sub_path_in_item:
                    new_item = {}
                    level = new_item
                    for part in sub_path_in_item[:-1]: level = level.setdefault(part, {})
                    level[sub_path_in_item[-1]] = {self.VALUE_KEY: value}
                else:
                    new_item = {self.VALUE_KEY: value}

                old_list = list(target_list)
                target_list.append(new_item)
                full_list_path_str = self._build_path_string(path_to_list)
                if not self._batch_update_active:
                    self._notify_subscribers(full_list_path_str, old_list, target_list)
                else:
                    self._pending_changes.append((full_list_path_str, old_list, target_list))
                return

            # Case 2: Standard set operation (with _value logic)
            res = self._traverse_path(parsed_path, create_if_missing=True)
            if res is None: raise KeyError(f"Could not create path at '{key_path}'")
            parent, key = res

            try:
                old_node = parent[key] if isinstance(key, int) else parent.get(key)
            except (KeyError, IndexError):
                old_node = None

            if not isinstance(old_node, dict):
                new_node = {self.VALUE_KEY: value}
            else:
                new_node = old_node.copy()  # Create a copy to avoid modifying in place before notification
                new_node[self.VALUE_KEY] = value

            if old_node == new_node: return

            if isinstance(key, int):
                if isinstance(parent, list):
                    parent[key] = new_node
            else:
                if isinstance(parent, dict):
                    parent[key] = new_node

            if not self._batch_update_active:
                self._notify_subscribers(key_path, old_node, new_node)
            else:
                self._pending_changes.append((key_path, old_node, new_node))

    def _unwrap_data(self, data: Any) -> Any:
        """
        Recursively "unwraps" data for a clean user-facing view.
        - Replaces {VALUE_KEY: val} with val.
        - Processes items in lists/tuples.
        - Leaves dictionaries with VALUE_KEY and other keys as is.
        """
        if isinstance(data, dict):
            if self.VALUE_KEY in data and len(data) == 1:
                return self._unwrap_data(data[self.VALUE_KEY])
            return {k: self._unwrap_data(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._unwrap_data(item) for item in data]
        if isinstance(data, tuple):
            return tuple(self._unwrap_data(item) for item in data)
        return data

    def get(self, key_path: str, default: Any = None, *, get_value: int = 0) -> Any:
        """
        Retrieves a value from the data store with different view modes.

        :param key_path: The path to the desired data. A trailing separator is ignored.
                         An empty path returns the entire data store.
        :param default: A value to return if the key is not found.
        :param get_value: Defines the view of the returned data:
                          - 0 (Default): Returns a "clean" view. Dictionaries
                            containing only a `_value` key are replaced by the
                            value itself, recursively.
                          - 1: Returns the "raw" internal structure. Dictionaries are
                            returned as read-only MappingProxyType and lists as tuples.
                            All `_value` keys are preserved.
                          - 2: Returns only the direct `_value` of the node, ignoring
                            any sub-keys. If `_value` does not exist, returns `default`.
        :return: The requested value, formatted according to the `get_value` mode.
        """
        if get_value not in {0, 1, 2}:
            raise ValueError("get_value must be 0, 1, or 2.")

        with self._lock:
            cleaned_key_path = key_path.rstrip(self._separator)
            if not cleaned_key_path:
                node = self._data
            else:
                try:
                    parsed_path = self._parse_path(cleaned_key_path)
                    res = self._traverse_path(parsed_path)
                    if res is None: return default
                    parent, key = res
                    node = parent[key] if isinstance(key, int) else parent.get(key, self._sentinel)
                    if node is self._sentinel: return default
                except (KeyError, IndexError, TypeError):
                    return default

            # Mode 2: Return only the _value or default
            if get_value == 2:
                if isinstance(node, dict):
                    return node.get(self.VALUE_KEY, default)
                # If it's a list or a raw value, it has no _value key.
                return default

            # Mode 1: Return the raw, immutable internal structure
            if get_value == 1:
                if isinstance(node, dict): return MappingProxyType(node)
                if isinstance(node, list): return tuple(node)
                return node

            # Mode 0 (Default): Return the "clean", unwrapped structure
            unwrapped_node = self._unwrap_data(node)
            if isinstance(unwrapped_node, dict): return MappingProxyType(unwrapped_node)
            if isinstance(unwrapped_node, list): return tuple(unwrapped_node)
            return unwrapped_node

    def getk(self, key_path: str, default: Any = _sentinel, *, strip_prefix: bool = False) \
            -> Tuple[Tuple[str, Any], ...]:
        """
        Retrieves data as a flattened tuple of (full_key_path, value) pairs.

        :param key_path: The path to the branch to retrieve.
        :param default: Value to return if the key is not found. If provided, returns
                        ((key_path, default),). Otherwise, returns an empty tuple.
        :param strip_prefix: If True, the key_path is removed from the start of all
                             returned keys, resulting in relative paths.
        :return: A tuple of (key, value) pairs.
        """
        # We use get_value=1 to get the raw structure for flattening
        value = self.get(key_path, default=self._sentinel, get_value=1)
        base_path = key_path.rstrip(self._separator)

        if value is self._sentinel:
            if default is self._sentinel:
                return ()
            else:
                final_key = "" if strip_prefix else base_path
                return ((final_key, default),)

        if not isinstance(value, (dict, list, tuple, MappingProxyType)):
            final_key = "" if strip_prefix else base_path
            return ((final_key, value),)

        path_to_strip = base_path if strip_prefix else ""
        return tuple(self._flatten_item(value, prefix=base_path, path_to_strip=path_to_strip))

    def _flatten_item(self, item: Any, prefix: str, path_to_strip: str = "") -> List[Tuple[str, Any]]:
        """
        Chooses the correct flattening method based on item type (dict or list).

        :param item: The dictionary or list to flatten.
        :param prefix: The current key path prefix for recursion.
        :param path_to_strip: The base path to remove if strip_prefix is enabled.
        :return: A list of (key, value) pairs.
        """
        if isinstance(item, (dict, MappingProxyType)):
            return self._flatten_dict(item, prefix=prefix, path_to_strip=path_to_strip)
        elif isinstance(item, (list, tuple)):
            return self._flatten_list(item, prefix=prefix, path_to_strip=path_to_strip)
        else:
            final_key = prefix
            if path_to_strip: final_key = final_key.removeprefix(path_to_strip).lstrip(self._separator)
            return [(final_key, item)]

    def _flatten_dict(self, data: Dict[str, Any], prefix: str, path_to_strip: str) -> List[Tuple[str, Any]]:
        """
        Recursively flattens a dictionary into a list of (full_path, value) pairs.

        :param data: The dictionary to flatten.
        :param prefix: The current key path prefix for recursion.
        :param path_to_strip: The base path to remove if strip_prefix is enabled.
        :return: A list of (key, value) pairs.
        """
        pairs = []
        if self.VALUE_KEY in data:
            final_key = prefix
            if path_to_strip: final_key = final_key.removeprefix(path_to_strip).lstrip(self._separator)
            pairs.append((final_key, data[self.VALUE_KEY]))

        for key, val in data.items():
            if key == self.VALUE_KEY: continue
            current_path = f"{prefix}{self._separator}{key}" if prefix else key
            pairs.extend(self._flatten_item(val, prefix=current_path, path_to_strip=path_to_strip))
        return pairs

    def _flatten_list(self, data: Union[List[Any], Tuple[Any, ...]], prefix: str, path_to_strip: str) \
            -> List[Tuple[str, Any]]:
        """
        Recursively flattens a list into a list of (full_path, value) pairs.

        :param data: The list to flatten.
        :param prefix: The current key path prefix for recursion.
        :param path_to_strip: The base path to remove if strip_prefix is enabled.
        :return: A list of (key, value) pairs.
        """
        pairs = []
        for index, val in enumerate(data):
            current_path = f"{prefix}[{index}]"
            pairs.extend(self._flatten_item(val, prefix=current_path, path_to_strip=path_to_strip))
        return pairs

    def _build_path_string(self, parsed_path: List[Union[str, int, object]]) -> str:
        """
        Reconstructs a key_path string from a parsed path list.

        :param parsed_path: A list of keys, indices, and tokens.
        :return: The reconstructed string path.
        """
        path_str = ""
        for i, part in enumerate(parsed_path):
            if part is self.APPEND:
                path_str += '[]'
            elif isinstance(part, int):
                path_str += f"[{part}]"
            else:
                is_first = (i == 0)
                is_after_list_index = (i > 0 and isinstance(parsed_path[i - 1], (int, type(self.APPEND))))
                if not is_first and not is_after_list_index:
                    path_str += self._separator
                path_str += str(part)
        return path_str

    def _build_data_from_iterable(self, data: Union[
        List[Tuple[str, Any]], Set[Tuple[str, Any]], Tuple[Tuple[str, Any], ...]]) -> Dict[str, Any]:
        """
        Builds the initial nested dictionary from a flat iterable.

        :param data: An iterable of (key_path, value) tuples.
        :return: A nested dictionary representing the initial data.
        """
        root = {}
        for key_path, value in data:
            parsed_path = self._parse_path(key_path)
            current_level = root
            for part in parsed_path[:-1]:
                if isinstance(part, str):
                    current_level = current_level.setdefault(part, {})

            final_key = parsed_path[-1]
            if isinstance(final_key, str):
                current_level[final_key] = {self.VALUE_KEY: value}
        return root

    def _simplify_value(self, value: Any) -> Any:
        """
        Simplifies a value for callbacks.

        If it's a dict with only a _value key, it returns the inner value.
        Otherwise, it returns the original value.

        :param value: The value to potentially simplify.
        :return: The simplified value.
        """
        if isinstance(value, dict) and self.VALUE_KEY in value and len(value) == 1:
            return value[self.VALUE_KEY]
        return value

    def _notify_subscribers(self, key_path: str, old_value: Any, new_value: Any) -> None:
        """
        Notifies subscribers about a change, implementing event bubbling.

        :param key_path: The full path of the key that changed.
        :param old_value: The value before the change.
        :param new_value: The value after the change.
        """
        simplified_old = self._simplify_value(old_value)
        simplified_new = self._simplify_value(new_value)

        # Optimization: if nothing changed after simplification, don't notify
        if simplified_old == simplified_new:
            return

        parsed_path = self._parse_path(key_path)
        notified_paths = set()

        for i in range(len(parsed_path), -1, -1):
            # For list item changes like 'a/b[0]', notify subscribers of 'a/b' as well.
            sub_path = parsed_path[:i]
            if i < len(parsed_path) and isinstance(parsed_path[i], int):
                # This handles cases like a/b[0], we already notified a/b[0], now we should notify a/b
                pass

            current_path_str = self._build_path_string(sub_path)
            if not current_path_str and i > 0: continue  # Skip empty path string unless it's the root
            if current_path_str in notified_paths: continue
            notified_paths.add(current_path_str)

            if current_path_str in self._subscribers:
                for weak_callback in list(self._subscribers.get(current_path_str, set())):
                    callback = weak_callback()
                    if callback:
                        try:
                            # For parent notifications, old/new values are less relevant,
                            # so we pass the specific change info.
                            callback(key_path, simplified_old, simplified_new)
                        except Exception as e:
                            print(f"Error in callback for key '{current_path_str}': {e}")
                    else:
                        self._subscribers[current_path_str].remove(weak_callback)

    def subscribe(self, key_path: str, callback: CallbackType) -> None:
        """
        Subscribes a callback function to changes for a specific key path.

        :param key_path: The path to subscribe to.
        :param callback: The function to call when a change occurs.
        """
        with self._lock:
            if key_path not in self._subscribers:
                self._subscribers[key_path] = set()
            if hasattr(callback, '__self__'):
                ref = weakref.WeakMethod(callback)
            else:
                ref = weakref.ref(callback)
            self._subscribers[key_path].add(ref)

    def unsubscribe(self, key_path: str, callback: CallbackType) -> None:
        """
        Unsubscribes a callback function from a key path.

        :param key_path: The path to unsubscribe from.
        :param callback: The callback function to remove.
        """
        with self._lock:
            if key_path in self._subscribers:
                ref_to_remove = None
                for weak_callback in self._subscribers[key_path]:
                    if weak_callback() == callback:
                        ref_to_remove = weak_callback
                        break
                if ref_to_remove:
                    self._subscribers[key_path].remove(ref_to_remove)

    def dumps(self, indent: int = 2) -> str:
        """
        Returns a human-readable string representation of the data store.

        :param indent: The indentation level for the formatted string.
        :return: A formatted string of the data.
        """
        with self._lock:
            return pprint.pformat(self._data, indent=indent)

    def _datetime_serializer(self, obj: Any) -> Any:
        """
        Custom serializer for datetime objects for MessagePack.

        :param obj: The object to serialize.
        :return: A serializable representation of the object.
        """
        if isinstance(obj, datetime.datetime):
            return {'__datetime__': True, 'as_iso': obj.isoformat()}
        return obj

    def serialize(self) -> bytes:
        """
        Serializes the entire data store to a compact binary format (MessagePack).

        :return: The serialized data as a bytes object.
        """
        # with self._lock:
        #     return msgpack.packb(self._data, default=self._datetime_serializer, use_bin_type=True)
        # todo
        pass

    @staticmethod
    def _datetime_deserializer(obj: Dict) -> Any:
        """
        Custom deserializer for datetime objects for MessagePack.

        :param obj: The object hook dictionary from MessagePack.
        :return: The deserialized object.
        """
        if '__datetime__' in obj:
            return datetime.datetime.fromisoformat(obj['as_iso'])
        return obj

    @classmethod
    def deserialize(cls, serialized_data: bytes) -> 'DataShare':
        """
        Creates a new DataShare instance from serialized data.

        :param serialized_data: The data previously serialized with .serialize().
        :return: A new DataShare instance.
        """
        # data = msgpack.unpackb(serialized_data, object_hook=cls._datetime_deserializer, raw=False)
        # return cls(initial_data=data)
        # todo
        return None

    def __enter__(self):
        """
        Enters the batch update context, deferring notifications.

        :return: The DataShare instance.
        """
        self._lock.acquire()
        self._batch_update_active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the batch update context, sending all deferred notifications.

        :param exc_type: The exception type if an exception occurred.
        :param exc_val: The exception value if an exception occurred.
        :param exc_tb: The traceback if an exception occurred.
        """
        try:
            if not exc_type:
                changes_to_notify = list(self._pending_changes)
                for key_path, old_value, new_value in changes_to_notify:
                    self._notify_subscribers(key_path, old_value, new_value)
        finally:
            self._pending_changes.clear()
            self._batch_update_active = False
            self._lock.release()

    def batch_update(self):
        """
        Returns a context manager for performing updates in a batch.

        Notifications are consolidated and sent only once upon exiting the block.
        Example:
            with ds.batch_update():
                ds.set('key1', 'val1')
                ds.set('key2', 'val2')

        :return: The DataShare instance to be used as a context manager.
        """
        return self

#####################################################################################################################
# import re
# import threading
# import weakref
# import pprint
# # import msgpack
# import datetime
# from types import MappingProxyType
# from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, cast, overload, Collection
#
# CallbackType = Callable[[str, Any, Any], None]
#
# # document: (copy and paste to .md file)
# """
# # DataShare Class: A User Guide
#
# ## 1. Introduction
#
# `DataShare` is a powerful, thread-safe, hierarchical data store for Python. It's designed to be a centralized repository for application state and configuration, allowing for complex, nested data structures that can be accessed and manipulated via a simple path-based syntax.
#
# **Key Features:**
# * **Hierarchical Structure:** Access nested data using file-system-like paths (e.g., `'system/network/host'`).
# * **Advanced List Support:** Natively create and manipulate lists within the hierarchy.
# * **Dual-Value Nodes:** A single path can hold both a direct value and serve as a container for sub-keys.
# * **Observer Pattern:** Subscribe to changes at any level of the data hierarchy and receive notifications.
# * **Thread Safety:** All operations are thread-safe, making it ideal for multi-threaded applications.
# * **Serialization:** Save and load the entire data store to a compact binary format.
#
# ---
#
# ## 2. Core Concepts
#
# ### Hierarchical Paths
# Data is organized in a tree-like structure of nested dictionaries and lists. You interact with it using a **`key_path`**, which is a string of keys joined by a separator (default is `/`).
#
# ```python
# # This sets a value in a nested dictionary
# ds.set('user/preferences/theme', 'dark')
# ```
#
# ### List Syntax
# `DataShare` has special syntax for interacting with lists.
#
# * **Append (`[]`):** Use an empty `[]` to append a new item to a list. If the list doesn't exist, it will be created.
# * **Index (`[n]`):** Use `[index]` to access or modify a list item at a specific position. Negative indices are supported.
#
# ```python
# # Appends 'admin' to the 'user/roles' list
# ds.set('user/roles[]', 'admin')
#
# # Accesses the first role
# role = ds.get('user/roles[0]')
# ```
#
# ### Dual-Value Nodes (`_value`)
# A powerful feature is that any node can have both a direct value and sub-keys. This is handled internally by storing the direct value in a special `_value` key. This allows you to treat a path as both an endpoint and a container.
#
# ```python
# # Set a direct value for 'lights'
# ds.set('home/living/lights', 'on')
#
# # Set a sub-key on the same 'lights' path
# ds.set('home/living/lights/ceiling', '30%')
#
# # The internal structure is now similar to:
# # 'lights': { '_value': 'on', 'ceiling': {'_value': '30%'} }
# ```
#
# ---
#
# ## 3. Initialization
#
# To start, import and instantiate the class.
#
# ```python
# # Create an empty instance
# ds = DataShare()
#
# # Create an instance with initial data
# initial = {
#     'system': {
#         'host': 'server.local',
#         'port': 8080
#     }
# }
# ds_with_data = DataShare(initial_data=initial)
# ```
#
# The `initial_data` parameter can be one of:
# * A `dict`.
# * A `list` of `(key_path, value)` tuples.
# * A `set` or `tuple` of `(key_path, value)` tuples.
#
# ---
#
# ## 4. API Reference
#
# ### `set(key_or_data, value=None)`
# This is the primary method for adding or modifying data. It's highly versatile.
#
# **1. Set a Single Value**
# ```python
# ds.set('user/name', 'Alice')
# ds.set('user/id', 123)
# ```
#
# **2. Set a List Item by Index**
# This will overwrite the value at the specified index.
# ```python
# ds.set('user/roles[1]', 'moderator')
# ```
#
# **3. Append to a List**
# Use `[]` to add a new item to the end of a list.
#
# ```python
# # Append a simple string
# ds.set('user/roles[]', 'guest')
#
# # Append a more complex object (a dictionary)
# ds.set('user/tasks[]/title', 'Finish report')
# ds.set('user/tasks[-1]/priority', 'high')
# ```
# > **Note:** When using negative indices like `[-1]` in a `batch_update` block, it refers to the list's state *at the time of the call*, not including previous appends within the same batch.
#
# **4. Batch Updates**
# You can set multiple values at once by passing a `dict`, `list`, or `tuple`.
#
# ```python
# # Using a dictionary
# ds.set({
#     'system/network/host': 'new-host.com',
#     'system/network/port': 443
# })
#
# # Using a list of tuples
# ds.set([
#     ('user/active', True),
#     ('user/last_login', '2025-09-22')
# ])
# ```
#
# ---
#
# ### `get(key_path, default=None, *, get_value=False)`
# Retrieves data from the store.
#
# * `key_path`: The path to the data.
# * `default`: The value to return if the path is not found.
# * `get_value`: (Keyword-only) If `True`, extracts the direct value from a node, ignoring any sub-keys.
#
# **1. Basic Retrieval**
# ```python
# name = ds.get('user/name') # Returns 'Alice'
# port = ds.get('system/network/port', default=80) # Returns 443
# ```
#
# **2. Accessing Lists**
# ```python
# first_role = ds.get('user/roles[0]') # Returns 'admin'
# all_roles = ds.get('user/roles')     # Returns a read-only tuple of all roles
# ```
#
# **3. Getting a Direct Value (`get_value`)**
# This is used for dual-value nodes.
#
# ```python
# ds.set('lights', 'on')
# ds.set('lights/ceiling', '30%')
#
# # Default behavior: returns the container
# node = ds.get('lights')
# # node is a read-only dict: {'_value': 'on', 'ceiling': {'_value': '30%'}}
#
# # Using get_value=True: returns the direct value
# state = ds.get('lights', get_value=True) # Returns 'on'
#
# # If a node has no direct value, returns the default
# missing = ds.get('user', get_value=True, default='N/A') # Returns 'N/A'
# ```
#
# ---
#
# ### `getk(key_path, default=..., *, strip_prefix=False)`
# Retrieves data as a **flattened tuple of `(full_key_path, value)` pairs**. This is useful for reading entire configuration sections.
#
# * `key_path`: The branch of the data tree to retrieve.
# * `default`: If the `key_path` is not found, it returns `((key_path, default),)`. If `default` is not provided, returns `()`.
# * `strip_prefix`: (Keyword-only) If `True`, the `key_path` is removed from the start of all returned keys, giving you relative paths.
#
# ```python
# # Setup
# ds.set('db/host', 'localhost')
# ds.set('db/user/name', 'admin')
#
# # 1. Get a flattened branch
# all_db_config = ds.getk('db')
# # Returns (('db/host', 'localhost'), ('db/user/name', 'admin'))
#
# # 2. Get a branch with relative keys
# relative_config = ds.getk('db', strip_prefix=True)
# # Returns (('host', 'localhost'), ('user/name', 'admin'))
#
# # 3. Handle a missing key with a default
# missing = ds.getk('api/key', default='default_key')
# # Returns (('api/key', 'default_key'),)
# ```
#
# ---
#
# ### `subscribe(key_path, callback)` & `unsubscribe(key_path, callback)`
# Register a function to be called whenever data at or below a certain `key_path` changes.
#
# **Callback Signature**
# Your callback function must accept three arguments: `key`, `old_value`, and `new_value`.
#
# ```python
# def my_callback(key, old, new):
#     print(f"Change detected at '{key}':")
#     print(f"  Old -> {old}")
#     print(f"  New -> {new}")
#
# ds.subscribe('system/network', my_callback)
# ```
# > **Important:** The `old` and `new` values are automatically "unwrapped". If a value is a simple endpoint (internally `_value: 'on'}`), you will receive the clean value (`'on'`). You only receive the full dictionary if the node has both a direct value and sub-keys.
#
# ---
#
# ### `batch_update()`
# A context manager to perform multiple `set` operations while only triggering a single round of notifications at the end. This is highly efficient for bulk updates.
#
# ```python
# with ds.batch_update():
#     ds.set('user/profile/bio', '...')
#     ds.set('user/profile/location', '...')
#     ds.set('user/active', False)
# # All notifications are sent here, at the end of the block.
# ```
#
# ---
#
# ## 5. Serialization & Debugging
#
# ### `serialize()` & `deserialize(data)`
# Save and load the entire state of the `DataShare` object.
#
# ```python
# # Save state to a file
# serialized_data = ds.serialize()
# with open('app_state.bin', 'wb') as f:
#     f.write(serialized_data)
#
# # Load state from a file
# with open('app_state.bin', 'rb') as f:
#     loaded_data = f.read()
# new_ds = DataShare.deserialize(loaded_data)
# ```
#
# ### `dumps(indent=2)`
# Get a human-readable, pretty-printed string representation of the data, perfect for debugging.
#
# ```python
# print(ds.dumps())
# ```
#
# """
#
#
# class DataShare:
#     """
#     A thread-safe, hierarchical data store with an observer pattern.
#
#     This class provides a centralized repository for application state and
#     configuration parameters. It allows getting and setting values using
#     path-based keys (e.g., 'system/network/host').
#
#     Core Concepts:
#     - Hierarchical Paths: Data is organized in a tree of nested dictionaries
#       and lists, accessed via a string path with a separator (default '/').
#
#     - List Syntax: The class natively supports lists. Use 'path[]' to append
#       to a list and 'path[index]' to access or modify a specific element.
#       Negative indices are supported.
#
#     - Dual-Value Nodes (_value): A key path can hold both a direct value and
#       be a container for sub-keys. This is handled by storing the direct value
#       in a special '_value' key, making the node a dictionary.
#
#     - Thread Safety: All read and write operations are protected by a
#       re-entrant lock, making it safe for use in multi-threaded applications.
#
#     - Observer Pattern: Users can subscribe a callback function to any key
#       path to be notified of changes to that data or any data nested below it.
#
#     - Serialization: The entire data store can be serialized to a compact
#       binary format using MessagePack for saving and loading state.
#     """
#     VALUE_KEY = '_value'
#     APPEND = object()
#     _sentinel = object()
#
#     def __init__(self,
#                  initial_data: Union[Dict[str, Any], List[Tuple[str, Any]], Set[Tuple[str, Any]], Tuple[
#                      Tuple[str, Any], ...], None] = None,
#                  separator: str = '/'):
#         """
#         Initializes the DataShare instance.
#
#         :param initial_data: Optional data to pre-populate the store. It can be a
#                              dictionary, or a list/set/tuple of (key, value) pairs.
#         :param separator: The character for separating keys in a path. Defaults to '/'.
#         """
#         self._separator = separator
#         self._data: Dict[str, Any] = {}
#
#         if isinstance(initial_data, dict):
#             self._data = initial_data
#         elif isinstance(initial_data, (list, set, tuple)):
#             self._data = self._build_data_from_iterable(initial_data)
#
#         self._subscribers: Dict[str, Set[weakref.ReferenceType]] = {}
#         self._lock = threading.RLock()
#         self._batch_update_active = False
#         self._pending_changes: List[Tuple[str, Any, Any]] = []
#
#     def _parse_path(self, key_path: str) -> List[Union[str, int, object]]:
#         """
#         Parses a key path string into a list of keys and indices.
#
#         Handles dictionary keys, list indices '[n]', and the list append token '[]'.
#         Example: 'a/b[1]/c[]' -> ['a', 'b', 1, 'c', self.APPEND]
#
#         :param key_path: The string path to parse.
#         :return: A list of parsed path components.
#         """
#         if not key_path: return []
#         parts = re.findall(r'[^/\[\]]+|\[-?\d+\]|\[\]', key_path)
#         parsed = []
#         for part in parts:
#             if part == '[]':
#                 parsed.append(self.APPEND)
#             elif part.startswith('[') and part.endswith(']'):
#                 parsed.append(int(part[1:-1]))
#             else:
#                 parsed.append(part)
#         return parsed
#
#     def _traverse_path(self, parsed_path: List[Union[str, int]], create_if_missing: bool = False) \
#             -> Optional[Tuple[Union[dict, list], Union[str, int]]]:
#         """
#         Navigates the data structure using a pre-parsed path.
#
#         :param parsed_path: A list of keys and indices from _parse_path.
#         :param create_if_missing: If True, creates nested dictionaries along the path.
#         :return: A tuple containing the parent container (dict or list) and the final
#                  key/index, or None if the path is not found.
#         """
#         if not parsed_path: return None
#         current_level: Union[dict, list] = self._data
#
#         for part in parsed_path[:-1]:
#             try:
#                 if isinstance(part, int):
#                     if not isinstance(current_level, list): return None
#                     next_level = current_level[part]
#                 else:
#                     if not isinstance(current_level, dict): return None
#                     if create_if_missing:
#                         if not isinstance(current_level.get(part), (dict, list)):
#                             current_level.setdefault(part, {})
#                         next_level = current_level.get(part)
#                     else:
#                         next_level = current_level.get(part)
#
#                 if next_level is None: return None
#                 current_level = next_level
#             except (KeyError, IndexError):
#                 return None
#         return current_level, parsed_path[-1]
#
#     @overload
#     def set(self, key_path: str, val: Any) -> None:
#         ...
#
#     @overload
#     def set(self, data: Collection[Tuple[str, Any]]) -> None:
#         ...
#
#     @overload
#     def set(self, data: Dict[str, Any]) -> None:
#         ...
#
#     def set(self, key_or_data: Union[str, Collection[Tuple[str, Any]], Dict[str, Any]],
#             val: Any = None) -> None:
#         """
#         Sets a value or multiple values in the data store.
#
#         This method is overloaded to handle single items or batch updates. It also
#         handles list append syntax ('[]') and setting values at specific
#         list indices ('[n]').
#
#         :param key_or_data: The key path string or a collection (dict, list, etc.) with key / value pairs.
#         For dict use key: val, for lists etc used Tuples with key and val.
#         :param val: The value to set for a single key_path string.
#         :raises TypeError: If the input data is not a supported type.
#         :raises KeyError: If a path cannot be found or created.
#         """
#         if not isinstance(key_or_data, str):
#             if isinstance(key_or_data, (list, set, tuple, dict)):
#                 with self.batch_update():
#                     items_to_iterate = key_or_data.items() if isinstance(key_or_data, dict) else key_or_data
#                     for key, val_item in items_to_iterate: self.set(key, val_item)
#                 return
#             else:
#                 raise TypeError("Argument must be a string (key_path) or a collection.")
#
#         key_path, value = key_or_data, val
#         with self._lock:
#             parsed_path = self._parse_path(key_path)
#
#             # Case 1: List append operation ('[]')
#             if self.APPEND in parsed_path:
#                 append_index = parsed_path.index(self.APPEND)
#                 path_to_list = parsed_path[:append_index]
#                 sub_path_in_item = parsed_path[append_index + 1:]
#
#                 res = self._traverse_path(path_to_list, create_if_missing=True)
#                 if res is None: raise KeyError(f"Path '{'/'.join(map(str, path_to_list))}' not found.")
#                 list_parent, list_key = res
#
#                 target_list = list_parent.setdefault(list_key, [])
#                 if not isinstance(target_list, list): raise TypeError(
#                     f"Target at '{'/'.join(map(str, path_to_list))}' is not a list.")
#
#                 if sub_path_in_item:
#                     new_item = {}
#                     level = new_item
#                     for part in sub_path_in_item[:-1]: level = level.setdefault(part, {})
#                     level[sub_path_in_item[-1]] = {self.VALUE_KEY: value}
#                 else:
#                     new_item = {self.VALUE_KEY: value}
#
#                 old_list = list(target_list)
#                 target_list.append(new_item)
#                 full_list_path_str = self._build_path_string(path_to_list)
#                 if not self._batch_update_active:
#                     self._notify_subscribers(full_list_path_str, old_list, target_list)
#                 else:
#                     self._pending_changes.append((full_list_path_str, old_list, target_list))
#                 return
#
#             # Case 2: Standard set operation (with _value logic)
#             res = self._traverse_path(parsed_path, create_if_missing=True)
#             if res is None: raise KeyError(f"Could not create path at '{key_path}'")
#             parent, key = res
#
#             try:
#                 old_node = parent[key] if isinstance(key, int) else parent.get(key)
#             except (KeyError, IndexError):
#                 old_node = None
#
#             if not isinstance(old_node, dict):
#                 new_node = {self.VALUE_KEY: value}
#             else:
#                 new_node = old_node
#                 new_node[self.VALUE_KEY] = value
#
#             if old_node == new_node: return
#
#             if isinstance(key, int):
#                 parent[key] = new_node
#             else:
#                 parent[key] = new_node
#
#             if not self._batch_update_active:
#                 self._notify_subscribers(key_path, old_node, new_node)
#             else:
#                 self._pending_changes.append((key_path, old_node, new_node))
#
#     def get(self, key_path: str, default: Any = None, *, get_value: bool = False) -> Any:
#         """
#         Retrieves a value from the data store.
#
#         :param key_path: The path to the desired data. A trailing separator is ignored.
#                          An empty path returns the entire data store.
#         :param default: A value to return if the key is not found.
#         :param get_value: If True, extracts the direct `_value` from a node,
#                           ignoring any sub-keys.
#         :return: The requested value. Dictionaries are returned as read-only
#                  MappingProxyType and lists are returned as tuples.
#         """
#         with self._lock:
#             cleaned_key_path = key_path.rstrip(self._separator)
#             if not cleaned_key_path: return MappingProxyType(self._data)
#
#             try:
#                 parsed_path = self._parse_path(cleaned_key_path)
#                 res = self._traverse_path(parsed_path)
#                 if res is None: return default
#                 parent, key = res
#
#                 value = parent[key] if isinstance(key, int) else parent.get(key, default)
#
#                 if get_value:
#                     if isinstance(value, dict): return value.get(self.VALUE_KEY, default)
#                     return value
#
#                 if isinstance(value, dict): return MappingProxyType(value)
#                 if isinstance(value, list): return tuple(value)
#                 return value
#             except (KeyError, IndexError, TypeError):
#                 return default
#
#     def getk(self, key_path: str, default: Any = _sentinel, *, strip_prefix: bool = False) \
#             -> Tuple[Tuple[str, Any], ...]:
#         """
#         Retrieves data as a flattened tuple of (full_key_path, value) pairs.
#
#         :param key_path: The path to the branch to retrieve.
#         :param default: Value to return if the key is not found. If provided, returns
#                         ((key_path, default),). Otherwise, returns an empty tuple.
#         :param strip_prefix: If True, the key_path is removed from the start of all
#                              returned keys, resulting in relative paths.
#         :return: A tuple of (key, value) pairs.
#         """
#         value = self.get(key_path, default=self._sentinel)
#         base_path = key_path.rstrip(self._separator)
#
#         if value is self._sentinel:
#             if default is self._sentinel:
#                 return ()
#             else:
#                 final_key = "" if strip_prefix else base_path
#                 return ((final_key, default),)
#
#         if not isinstance(value, (dict, list, tuple, MappingProxyType)):
#             final_key = "" if strip_prefix else base_path
#             return ((final_key, value),)
#
#         path_to_strip = base_path if strip_prefix else ""
#         return tuple(self._flatten_item(value, prefix=base_path, path_to_strip=path_to_strip))
#
#     def _flatten_item(self, item: Any, prefix: str, path_to_strip: str = "") -> List[Tuple[str, Any]]:
#         """
#         Chooses the correct flattening method based on item type (dict or list).
#
#         :param item: The dictionary or list to flatten.
#         :param prefix: The current key path prefix for recursion.
#         :param path_to_strip: The base path to remove if strip_prefix is enabled.
#         :return: A list of (key, value) pairs.
#         """
#         if isinstance(item, (dict, MappingProxyType)):
#             return self._flatten_dict(item, prefix=prefix, path_to_strip=path_to_strip)
#         elif isinstance(item, (list, tuple)):
#             return self._flatten_list(item, prefix=prefix, path_to_strip=path_to_strip)
#         else:
#             final_key = prefix
#             if path_to_strip: final_key = final_key.removeprefix(path_to_strip).lstrip(self._separator)
#             return [(final_key, item)]
#
#     def _flatten_dict(self, data: Dict[str, Any], prefix: str, path_to_strip: str) -> List[Tuple[str, Any]]:
#         """
#         Recursively flattens a dictionary into a list of (full_path, value) pairs.
#
#         :param data: The dictionary to flatten.
#         :param prefix: The current key path prefix for recursion.
#         :param path_to_strip: The base path to remove if strip_prefix is enabled.
#         :return: A list of (key, value) pairs.
#         """
#         pairs = []
#         if self.VALUE_KEY in data:
#             final_key = prefix
#             if path_to_strip: final_key = final_key.removeprefix(path_to_strip).lstrip(self._separator)
#             pairs.append((final_key, data[self.VALUE_KEY]))
#
#         for key, val in data.items():
#             if key == self.VALUE_KEY: continue
#             current_path = f"{prefix}{self._separator}{key}" if prefix else key
#             pairs.extend(self._flatten_item(val, prefix=current_path, path_to_strip=path_to_strip))
#         return pairs
#
#     def _flatten_list(self, data: Union[List[Any], Tuple[Any, ...]], prefix: str, path_to_strip: str) \
#             -> List[Tuple[str, Any]]:
#         """
#         Recursively flattens a list into a list of (full_path, value) pairs.
#
#         :param data: The list to flatten.
#         :param prefix: The current key path prefix for recursion.
#         :param path_to_strip: The base path to remove if strip_prefix is enabled.
#         :return: A list of (key, value) pairs.
#         """
#         pairs = []
#         for index, val in enumerate(data):
#             current_path = f"{prefix}[{index}]"
#             pairs.extend(self._flatten_item(val, prefix=current_path, path_to_strip=path_to_strip))
#         return pairs
#
#     def _build_path_string(self, parsed_path: List[Union[str, int, object]]) -> str:
#         """
#         Reconstructs a key_path string from a parsed path list.
#
#         :param parsed_path: A list of keys, indices, and tokens.
#         :return: The reconstructed string path.
#         """
#         path_str = ""
#         for i, part in enumerate(parsed_path):
#             if part is self.APPEND:
#                 path_str += '[]'
#             elif isinstance(part, int):
#                 path_str += f"[{part}]"
#             else:
#                 is_first = (i == 0)
#                 is_after_list = (i > 0 and isinstance(parsed_path[i - 1], int))
#                 if not is_first and not is_after_list:
#                     path_str += self._separator
#                 path_str += str(part)
#         return path_str
#
#     def _build_data_from_iterable(self, data: Union[
#         List[Tuple[str, Any]], Set[Tuple[str, Any]], Tuple[Tuple[str, Any], ...]]) -> Dict[str, Any]:
#         """
#         Builds the initial nested dictionary from a flat iterable.
#
#         :param data: An iterable of (key_path, value) tuples.
#         :return: A nested dictionary representing the initial data.
#         """
#         root = {}
#         for key_path, value in data:
#             parsed_path = self._parse_path(key_path)
#             current_level = root
#             for part in parsed_path[:-1]:
#                 if isinstance(part, str):
#                     current_level = current_level.setdefault(part, {})
#
#             final_key = parsed_path[-1]
#             if isinstance(final_key, str):
#                 current_level[final_key] = {self.VALUE_KEY: value}
#         return root
#
#     def _simplify_value(self, value: Any) -> Any:
#         """
#         Simplifies a value for callbacks.
#
#         If it's a dict with only a _value key, it returns the inner value.
#         Otherwise, it returns the original value.
#
#         :param value: The value to potentially simplify.
#         :return: The simplified value.
#         """
#         if isinstance(value, dict) and self.VALUE_KEY in value and len(value) == 1:
#             return value[self.VALUE_KEY]
#         return value
#
#     def _notify_subscribers(self, key_path: str, old_value: Any, new_value: Any) -> None:
#         """
#         Notifies subscribers about a change, implementing event bubbling.
#
#         :param key_path: The full path of the key that changed.
#         :param old_value: The value before the change.
#         :param new_value: The value after the change.
#         """
#         simplified_old = self._simplify_value(old_value)
#         simplified_new = self._simplify_value(new_value)
#
#         parsed_path = self._parse_path(key_path)
#         for i in range(len(parsed_path), 0, -1):
#             current_path_str = self._build_path_string(parsed_path[:i])
#             if current_path_str in self._subscribers:
#                 for weak_callback in list(self._subscribers.get(current_path_str, set())):
#                     callback = weak_callback()
#                     if callback:
#                         try:
#                             callback(key_path, simplified_old, simplified_new)
#                         except Exception as e:
#                             print(f"Error in callback for key '{current_path_str}': {e}")
#                     else:
#                         self._subscribers[current_path_str].remove(weak_callback)
#
#     def subscribe(self, key_path: str, callback: CallbackType) -> None:
#         """
#         Subscribes a callback function to changes for a specific key path.
#
#         :param key_path: The path to subscribe to.
#         :param callback: The function to call when a change occurs.
#         """
#         with self._lock:
#             if key_path not in self._subscribers:
#                 self._subscribers[key_path] = set()
#             if hasattr(callback, '__self__'):
#                 ref = weakref.WeakMethod(callback)
#             else:
#                 ref = weakref.ref(callback)
#             self._subscribers[key_path].add(ref)
#
#     def unsubscribe(self, key_path: str, callback: CallbackType) -> None:
#         """
#         Unsubscribes a callback function from a key path.
#
#         :param key_path: The path to unsubscribe from.
#         :param callback: The callback function to remove.
#         """
#         with self._lock:
#             if key_path in self._subscribers:
#                 ref_to_remove = None
#                 for weak_callback in self._subscribers[key_path]:
#                     if weak_callback() == callback:
#                         ref_to_remove = weak_callback
#                         break
#                 if ref_to_remove:
#                     self._subscribers[key_path].remove(ref_to_remove)
#
#     def dumps(self, indent: int = 2) -> str:
#         """
#         Returns a human-readable string representation of the data store.
#
#         :param indent: The indentation level for the formatted string.
#         :return: A formatted string of the data.
#         """
#         with self._lock:
#             return pprint.pformat(self._data, indent=indent)
#
#     def _datetime_serializer(self, obj: Any) -> Any:
#         """
#         Custom serializer for datetime objects for MessagePack.
#
#         :param obj: The object to serialize.
#         :return: A serializable representation of the object.
#         """
#         if isinstance(obj, datetime.datetime):
#             return {'__datetime__': True, 'as_iso': obj.isoformat()}
#         return obj
#
#     def serialize(self) -> bytes:
#         """
#         Serializes the entire data store to a compact binary format (MessagePack).
#
#         :return: The serialized data as a bytes object.
#         """
#         # with self._lock:
#         #     return msgpack.packb(self._data, default=self._datetime_serializer, use_bin_type=True)
#         # todo
#
#     @staticmethod
#     def _datetime_deserializer(obj: Dict) -> Any:
#         """
#         Custom deserializer for datetime objects for MessagePack.
#
#         :param obj: The object hook dictionary from MessagePack.
#         :return: The deserialized object.
#         """
#         if '__datetime__' in obj:
#             return datetime.datetime.fromisoformat(obj['as_iso'])
#         return obj
#
#     @classmethod
#     def deserialize(cls, serialized_data: bytes) -> 'DataShare':
#         """
#         Creates a new DataShare instance from serialized data.
#
#         :param serialized_data: The data previously serialized with .serialize().
#         :return: A new DataShare instance.
#         """
#         # data = msgpack.unpackb(serialized_data, object_hook=cls._datetime_deserializer, raw=False)
#         # return cls(initial_data=data)
#         # todo
#         return None
#
#     def __enter__(self):
#         """
#         Enters the batch update context, deferring notifications.
#
#         :return: The DataShare instance.
#         """
#         self._lock.acquire()
#         self._batch_update_active = True
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """
#         Exits the batch update context, sending all deferred notifications.
#
#         :param exc_type: The exception type if an exception occurred.
#         :param exc_val: The exception value if an exception occurred.
#         :param exc_tb: The traceback if an exception occurred.
#         """
#         try:
#             if not exc_type:
#                 changes_to_notify = list(self._pending_changes)
#                 for key_path, old_value, new_value in changes_to_notify:
#                     self._notify_subscribers(key_path, old_value, new_value)
#         finally:
#             self._pending_changes.clear()
#             self._batch_update_active = False
#             self._lock.release()
#
#     def batch_update(self):
#         """
#         Returns a context manager for performing updates in a batch.
#
#         Notifications are consolidated and sent only once upon exiting the block.
#         Example:
#             with ds.batch_update():
#                 ds.set('key1', 'val1')
#                 ds.set('key2', 'val2')
#
#         :return: The DataShare instance to be used as a context manager.
#         """
#         return self
#
