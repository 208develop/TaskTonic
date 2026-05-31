import threading
import re
import contextlib
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple, Callable, Iterable

# ------------------------------------------------------------------------------
# Type definitions
# ------------------------------------------------------------------------------
PathStr = str
# ChangeEvent: (path, new_value, old_value, source_id)
ChangeEvent = Tuple[str, Any, Any, Optional[str]]
ListenerCallback = Callable[[List[ChangeEvent]], None]
DumpData = Iterable[Tuple[str, Any]]


# ------------------------------------------------------------------------------
# Class: StoreLink (The Smart Proxy Node)
# ------------------------------------------------------------------------------
class StoreLink:
    """
    A smart node that resides inside the Store's storage tree.
    It acts as a proxy to another path and manages its own subscriptions.
    """
    __slots__ = ('store', 'alias_path', 'target_path', 'bubble_events')

    def __init__(self, store: 'Store', alias_path: str, target_path: str, bubble_events: bool = False):
        self.store = store
        self.alias_path = alias_path.strip("/")
        self.target_path = target_path.strip("/")
        self.bubble_events = bubble_events

    def setup(self):
        """Called when the link is inserted into the store."""
        if self.bubble_events:
            self.store.at(self.target_path).subscribe(self._on_target_change, recursive=True, owner=self)

    def teardown(self):
        """Called when this link is removed from the store."""
        if self.bubble_events:
            self.store.unsubscribe(self)

    def _on_target_change(self, events):
        """Routes events from the canonical path to the alias path."""
        for path, new_val, old_val, source_id in events:
            # If the canonical item is destroyed, self-destruct the link
            if new_val is None and path == self.target_path:
                self.store.remove_item(self.alias_path)
                continue

            # Route the event deeper if the change happened in a sub-property
            relative_target = path[len(self.target_path):]
            inject_path = f"{self.alias_path}{relative_target}".strip("/")
            self.store._inject_event(inject_path, new_val, old_val, source_id)

    def __repr__(self):
        return f"<StoreLink(bubble_events={self.bubble_events}) {self.alias_path} -> {self.target_path}>"


# ------------------------------------------------------------------------------
# Class: Item (The Cursor/View)
# ------------------------------------------------------------------------------
class Item:
    """
    Represents a specific cursor/view on a path in the Store.
    Acts like a pointer to a specific location in the data tree.
    """
    __slots__ = ('_store', '_path')

    def __init__(self, store: 'Store', path: PathStr):
        self._store = store
        self._path = path.strip("/")

    @property
    def path(self) -> str:
        """Returns the absolute path of this item."""
        return self._path

    @property
    def v(self) -> Any:
        """
        Property for direct value access.
        Writing to .v ALWAYS sends a notification (notify=True), unless inside a silent group.
        """
        return self._store.get_value(self._path)

    @v.setter
    def v(self, value: Any):
        self._store.set_value(self._path, value, notify=True)

    # --- NAVIGATION HELPERS ---

    @property
    def parent(self) -> 'Item':
        """
        Returns an Item cursor pointing to the direct parent container.
        Example: "users/#0/name" -> "users/#0"
        """
        if "/" not in self._path:
            # Already at root or top-level, return root
            return self._store.at("")

        parent_path, _ = self._path.rsplit("/", 1)
        return self._store.at(parent_path)

    @property
    def list_root(self) -> Optional['Item']:
        """
        Walks up the path tree to find the nearest List Item ancestor.
        Identifies ancestors by the '#' syntax (e.g., '#0', 'user#1').

        Use this when a deep property changes (e.g. 'users/#0/address/street')
        and you need the context of the user record ('users/#0').

        Returns None if no list index is found in the path.
        """
        parts = self._path.split("/")

        # Iterate backwards to find the deepest list index
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            # Check syntax: contains '#' and ends with digit (e.g. "#0" or "name#1")
            if "#" in part and part[-1].isdigit():
                root_path = "/".join(parts[:i + 1])
                return self._store.at(root_path)

        return None

    # --- VALUE ACCESS ---

    def val(self, default: Any = None) -> Any:
        """
        Retrieves the value of THIS item (self).
        Returns 'default' if the value is None or item doesn't exist.
        """
        value = self.v
        return value if value is not None else default

    def get(self, key: str, default: Any = None) -> Any:
        """
        Dictionary-style lookup for CHILDREN.
        Retrieves the value of a child item relative to this item.

        Args:
            key: Relative path/key to the child.
            default: Value to return if child doesn't exist.
        """
        target_path = f"{self._path}/{key}" if self._path else key
        val = self._store.get_value(target_path)
        return val if val is not None else default

    # --- SET LOGIC ---

    def set(self, data: Union[DumpData, str, dict, tuple], value: Any = None, notify: bool = True) -> 'Item':
        """
        Versatile setter method.

        Args:
            data:
                - str: Relative path/key to set 'value' to.
                - dict: Batch update {key: val}.
                - list/tuple: Batch update [(key, val)] OR Value if not pairs.
            value: The value to set (only used if data is a string).
            notify: If False, this update will NOT trigger callbacks (Silent Mode).
        """

        # 1. Dictionary Batch
        if isinstance(data, dict):
            with self._store.group(notify=notify):
                for k, v in data.items():
                    self.set(str(k), v, notify=notify)
            return self

        # 2. List or Tuple Batch (STRUCTURAL UPDATE)
        # We only treat it as a batch if it contains pairs.
        if isinstance(data, (list, tuple)):
            # Check if it looks like a batch of pairs
            is_batch = len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) == 2

            if is_batch:
                with self._store.group(notify=notify):
                    for entry in data:
                        k, v = entry
                        self.set(k, v, notify=notify)
                return self

            # If not a batch of pairs, it falls through to be treated as a VALUE (list assignment)

        # 3. Single Key (String) -> WRITE VALUE
        if isinstance(data, str):
            path_str = data

            # Check for Dynamic Syntax (# or .) which needs parsing
            if "#" in path_str or "." in path_str:
                self._smart_set_path(path_str, value, notify)
            else:
                # Static Path -> Fast Write
                if path_str == "" or path_str == ".":
                    self._store.set_value(self._path, value, notify=notify)
                else:
                    target_path = f"{self._path}/{path_str}" if self._path else path_str
                    self._store.set_value(target_path.strip("/"), value, notify=notify)
            return self

        raise ValueError(f"Invalid arguments for set(). Got type: {type(data)}")

    def _smart_set_path(self, relative_path: str, value: Any, notify: bool):
        """Parses path strings with special characters (#, .)."""
        parts = relative_path.split("/")
        cursor = self

        for i, part in enumerate(parts):
            is_last_part = (i == len(parts) - 1)

            if part == "":
                continue
            elif part == "#":
                cursor = cursor.append(None)
            elif part == ".":
                cursor = self._get_last_list_item(cursor, prefix=None)
            elif part.endswith("#"):
                cursor = cursor.append(part[:-1])
            elif part.endswith("."):
                prefix = part[:-1]
                children_keys = cursor._store.get_children_keys(cursor.path)
                if prefix in children_keys:
                    cursor = cursor.at(prefix)
                    cursor = self._get_last_list_item(cursor, prefix=None)
                else:
                    cursor = self._get_last_list_item(cursor, prefix=prefix)
            else:
                cursor = cursor.at(part)

            if is_last_part:
                cursor._store.set_value(cursor.path, value, notify=notify)
                return

    def _get_last_list_item(self, cursor: 'Item', prefix: str = None) -> 'Item':
        children = cursor._store.get_children_keys(cursor.path)
        if prefix:
            pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
        else:
            pattern = re.compile(r"^#(\d+)$")

        max_idx = -1
        last_key = None
        for key in children:
            match = pattern.match(key)
            if match:
                idx = int(match.group(1))
                if idx > max_idx:
                    max_idx = idx
                    last_key = key
        return cursor.at(last_key) if last_key else cursor

    # --- MANIPULATION ---

    def remove(self, subpath: str = None) -> None:
        """
        Remove Item from store
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        self._store.remove_item(target)

    def pop(self, subpath: str = None) -> Any:
        """
        Remove Item from store and return its value after that
        :param subpath: sub path to remove, if empty, remove item
        :return:
        """
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        val = self._store.get_value(target)
        self._store.remove_item(target)
        return val

    def append(self, prefix: str = None) -> 'Item':
        """
        Creates a new list child item with an auto-incrementing index (e.g. #0, #1).
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item
        """
        return self._store.create_list_item(self._path, prefix)

    def extend(self, data_list: List[Any], prefix: str = None) -> 'Item':
        """
        Appends multiple items to the list.
        :param data_list: list of data to append
        :param prefix: List prefix (e.g. sensor, because sensor#0 etc)
        :return: Item with created list
        """
        if not isinstance(data_list, list):
            raise ValueError("extend() expects a list")
        for data in data_list:
            new_item = self.append(prefix)
            # If data looks like a batch tuple structure, set it as structure
            is_valid_tuple = isinstance(data, (list, tuple)) and len(data) > 0
            if is_valid_tuple and isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                new_item.set(data)
            else:
                new_item.v = data
        return self

    def set_each(self, subpath: str, value: Any, prefix: str = None) -> 'Item':
        """
        Updates a specific subpath for each child of the current item.
        Filters children by prefix if provided.

        Args:
            subpath: The relative path to update (e.g., "brightness" or "state").
            value: The new value to apply.
            prefix: Optional filter for children (e.g., "lamp").

        Returns:
            The current Item instance for method chaining.
        """
        with self.group():
            for child in self.children(prefix=prefix):
                target_item = child.at(subpath)
                target_item.v = value

        return self

    def link_to(self, target_path: str, bubble_events: bool = False) -> 'Item':
        """
        Creates a StoreLink at the current item's path, pointing to a target path.

        Args:
            target_path: The canonical path this link should point to.
            bubble_events: If True, changes on the target will bubble up this alias path.

        Returns:
            The current Item instance for method chaining.
        """
        link_obj = StoreLink(self._store, self._path, target_path, bubble_events=bubble_events)
        self._store.set_value(self._path, link_obj, notify=True)
        return self

    # --- QUERY ---

    def children(self, prefix: str = None) -> Iterator['Item']:
        """Iterates over children keys."""
        for key in self._store.get_children_keys(self._path):
            if prefix is not None:
                target_start = f"{prefix}#"
                if not key.startswith(target_start):
                    continue
            yield self.at(key)

    @property
    def key(self) -> str:
        """Returns the last segment of the path (e.g., '#0' from 'ui/id/#0')."""
        if not self._path:
            return ""
        return self._path.split('/')[-1]

    def dump(self) -> DumpData:
        return self._store.get_subtree(self._path)

    def dumps(self) -> str:
        data = self.dump()
        lines = [f"Dump of <{self._path or 'ROOT'}>:"]
        if not data:
            lines.append("  (empty)")
        else:
            for key, val in data:
                display_key = key if key else "."
                lines.append(f"  {display_key} = {val}")
        return "\n".join(lines)

    # --- CONTEXT MANAGERS ---

    def group(self, source_id: str = None, notify: bool = True):
        """
        Proxy to the Store's group context manager.
        Allows batching updates directly from an Item instance.
        """
        return self._store.group(source_id=source_id, notify=notify)

    def source(self, source_id: str):
        """
        Proxy to the Store's source context manager.
        """
        return self._store.source(source_id=source_id)

    # --- SUBSCRIBING ---

    def subscribe(self, path_or_callback: Union[str, List[str], ListenerCallback],
                  callback: ListenerCallback = None,
                  ignore_source: str = None, recursive: bool = False,
                  exclude: List[str] = None, extract: List[str] = None,
                  trigger_now: bool = False, owner: object = None) -> 'Item':
        """
        Subscribes to changes on this item or its relative sub-paths.
        """
        # Logic to handle item.subscribe(callback) vs item.subscribe("path", callback)
        if callable(path_or_callback):
            # Case: item.subscribe(callback)
            target_path = self._path
            real_callback = path_or_callback
        else:
            # Case: item.subscribe("subpath", callback) or item.subscribe(["a", "b"], callback)
            real_callback = callback
            if isinstance(path_or_callback, list):
                target_path = [f"{self._path}/{p}".strip("/") for p in path_or_callback]
            else:
                target_path = f"{self._path}/{path_or_callback}".strip("/")

        if real_callback is None:
            raise ValueError("A callback must be provided to subscribe().")

        self._store.subscribe(
            target_path,
            real_callback,
            ignore_source=ignore_source,
            recursive=recursive,
            exclude=exclude,
            extract=extract,
            trigger_now=trigger_now,
            owner=owner  # Pass the owner to the store
        )
        return self

    def unsubscribe(self, target: Union[ListenerCallback, object] = None) -> 'Item':
        """
        Unsubscribe from this item.
        If target is None, it removes all subscriptions where THIS item instance is the owner.
        Otherwise, it removes the specific callback or owner provided.
        """
        if target is None:
            # If no target is given, we assume the user wants to clear
            # everything linked to this item's specific path
            self._store.unsubscribe(self._path)
        else:
            self._store.unsubscribe(target)
        return self

    # --- MAGIC ---

    def at(self, subpath: str) -> 'Item':
        """
        Returns Item at subpath. From there you can access the item directly
        :param subpath: subpath of item
        :return:
        """
        full_path = f"{self._path}/{subpath}" if self._path else subpath
        return self._store.at(full_path)

    def __getitem__(self, key: str) -> 'Item':
        return self.at(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.remove(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._store.get_children_keys(self._path))

    def __repr__(self):
        val = self.v
        return f"<Item '{self._path}': {val}>" if val is not None else f"<Item '{self._path}'>"


# ------------------------------------------------------------------------------
# Class: Store (Base Functionality)
# ------------------------------------------------------------------------------
class Store:
    """
    Thread-safe, hierarchical data store (Functional Core).
    Supports:
    - Pub/Sub with Ancestor Lookup (O(depth) instead of O(subscribers)).
    - Grouped updates (Batching).
    - Silent updates (notify=False) per set or per group.
    - MQTT-style wildcards (* and **)
    - Atomic Snapshots via extraction
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._storage: Dict[str, Dict[str, Any]] = {}
        # Pre-allocate root
        self._storage[""] = {"val": None, "children": set()}
        self._subscribers: Dict[str, List[Dict]] = {}
        # Thread Local Storage for batching contexts
        self._local = threading.local()

    def _resolve_deep_path(self, path: str, visited_links: set = None) -> str:
        """
        Resolves paths segment by segment to support deep writing/reading into StoreLinks.
        Example: 'alias/folder/prop' -> hits link at 'alias/folder' -> returns 'target/device/prop'
        """
        if visited_links is None:
            visited_links = set()

        parts = path.strip("/").split("/")
        current_path = ""

        for i, part in enumerate(parts):
            current_path = f"{current_path}/{part}" if current_path else part

            with self._lock:
                entry = self._storage.get(current_path)

            if entry and isinstance(entry["val"], StoreLink):
                if current_path in visited_links:
                    raise ValueError(f"Circular StoreLink detected at {current_path}")
                visited_links.add(current_path)

                target_base = entry["val"].target_path
                remaining_parts = parts[i + 1:]

                if remaining_parts:
                    rest_of_path = "/".join(remaining_parts)
                    new_full_path = f"{target_base}/{rest_of_path}"
                    return self._resolve_deep_path(new_full_path, visited_links)
                else:
                    return target_base

        return current_path

    # --- Context Managers ---

    @contextlib.contextmanager
    def group(self, source_id: str = None, notify: bool = True):
        """
        Context manager to group multiple changes.
        Args:
            source_id: Optional source tag.
            notify: If False, ALL changes inside are silent (overrides set()).
        """
        # 1. Init Locals
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
        if not hasattr(self._local, "current_source"):
            self._local.current_source = None
        if not hasattr(self._local, "group_notify"):
            self._local.group_notify = True

        # 2. Save previous states
        prev_src = self._local.current_source
        prev_notify = self._local.group_notify

        # 3. Apply new context
        if source_id is not None:
            self._local.current_source = source_id

        # Combine parent silence with current request
        self._local.group_notify = prev_notify and notify

        self._local.batch_stack += 1

        try:
            yield
        finally:
            self._local.batch_stack -= 1

            # 4. Flush only if notifying and root/end of batch
            if self._local.batch_stack == 0 and self._local.group_notify:
                self._flush_notifications()

            # 5. Restore
            if source_id is not None:
                self._local.current_source = prev_src
            self._local.group_notify = prev_notify

    @contextlib.contextmanager
    def source(self, source_id: str):
        with self.group(source_id=source_id):
            yield

    # --- Core Access ---

    def at(self, path: str) -> Item:
        return Item(self, path)

    def set(self, path_or_data: Union[str, DumpData, dict], value: Any = None, notify: bool = True) -> Item:
        return self.at("").set(path_or_data, value, notify=notify)

    def get(self, path: str, default: Any = None) -> Any:
        """Shortcut to retrieve value by absolute path."""
        val = self.get_value(path)
        return val if val is not None else default

    def __getitem__(self, path: str) -> Item:
        return self.at(path)

    def __setitem__(self, path: str, value: Any):
        self.at("").set(path, value)

    def __delitem__(self, path: str):
        self.remove_item(path)

    def subscribe(self, path: Union[str, List[str]], callback: ListenerCallback,
                  ignore_source: str = None, recursive: bool = False,
                  exclude: List[str] = None, extract: List[str] = None,
                  trigger_now: bool = False, owner: object = None) -> Union[int, List[int]]:
        """
        Register a callback.
                recursive: If True, trigger on path and descendants.
        :param exclude: List of absolute sub-paths to ignore (e.g. ['sensor/current']).
        :param extract: List of relative fields to return as a flat dict in new_val.
        :param trigger_now: Immediately fire the callback with current state.
        :param owner: Optional object instance to link this subscription to.
        """

        # If a list of paths is provided, subscribe to each one individually
        if isinstance(path, list):
            for p in path:
                self.subscribe(p, callback, ignore_source, recursive,
                               exclude, extract, trigger_now, owner)
            return

        clean_path = path.strip("/")
        clean_exclude = [e.strip("/") for e in exclude] if exclude else []

        # Determine static prefix for O(1) lookups and compile regex if wildcard is used
        is_wildcard = "*" in clean_path
        static_prefix = clean_path
        pattern = None

        if is_wildcard:
            static_prefix = clean_path.split("*")[0].rstrip("/")

            # Convert MQTT-style to regex safely using a placeholder
            regex_str = clean_path.replace("**", "\0").replace("*", "[^/]+").replace("\0", ".*")
            regex_str = "^" + regex_str

            if not recursive:
                regex_str += "$"
            pattern = re.compile(regex_str)

        with self._lock:
            if static_prefix not in self._subscribers:
                self._subscribers[static_prefix] = []

            # Detect owner if not explicitly provided
            effective_owner = owner
            if effective_owner is None and hasattr(callback, "__self__"):
                effective_owner = callback.__self__

            self._subscribers[static_prefix].append({
                "cb": callback,
                "owner": effective_owner,
                "ignore_source": ignore_source,
                "recursive": recursive,
                "exclude": clean_exclude,
                "extract": extract,
                "pattern": pattern,
                "raw_path": clean_path
            })

        if trigger_now:
            self._trigger_init_event(clean_path, callback, extract, pattern)

    def unsubscribe(self, target: Union[ListenerCallback, object, List[Any]]):
        """
        Remove subscriptions by callback function or class instance (owner).
        """
        if isinstance(target, list):
            for t in target:
                self.unsubscribe(t)
            return

        with self._lock:
            for path in list(self._subscribers.keys()):
                # Filter based on callback or owner
                self._subscribers[path] = [
                    s for s in self._subscribers[path]
                    if s["cb"] != target and s["owner"] != target
                ]

                if not self._subscribers[path]:
                    del self._subscribers[path]

    def _trigger_init_event(self, path: str, callback: ListenerCallback,
                            extract: List[str] = None, pattern: re.Pattern = None):
        """Helper to fire immediate initial state for UI components."""
        events = []

        if pattern:
            # --- WILDCARD INIT ---
            static_prefix = path.split("*")[0].rstrip("/")
            matched_bases = set()

            # Find all existing paths that match the wildcard pattern
            with self._lock:
                for stored_path in self._storage.keys():
                    if stored_path.startswith(static_prefix) and pattern.match(stored_path):
                        base_path = pattern.match(stored_path).group(0)
                        matched_bases.add(base_path)

            if not matched_bases:
                return

            # Build a snapshot for each matched base path
            for base_path in matched_bases:
                if extract:
                    snapshot = {}
                    for field in extract:
                        if field == ".":
                            snapshot["."] = self.get_value(base_path)
                        else:
                            target = f"{base_path}/{field}" if base_path else field
                            snapshot[field] = self.get_value(target)
                    events.append((base_path, snapshot, None, "init"))
                else:
                    events.append((base_path, self.get_value(base_path), None, "init"))
        else:
            # --- STANDARD INIT ---
            current_val = self.get_value(path)

            if extract:
                snapshot = {}
                for field in extract:
                    if field == ".":
                        snapshot["."] = current_val
                    else:
                        target = f"{path}/{field}" if path else field
                        snapshot[field] = self.get_value(target)
                current_val = snapshot

            events.append((path, current_val, None, "init"))

        if events:
            try:
                callback(events)
            except Exception as e:
                print(f"[Store] Init callback error {path}: {e}")

    def dump(self) -> DumpData:
        return self.at("").dump()

    def dumps(self) -> str:
        return self.at("").dumps()

    # --- Implementation Details ---

    def _ensure_node(self, path: str):
        parts = path.split("/")
        current_path = ""
        for i, part in enumerate(parts):
            parent_path = current_path
            if i > 0:
                current_path = f"{current_path}/{part}"
            else:
                current_path = part

            if current_path not in self._storage:
                self._storage[current_path] = {"val": None, "children": set()}
                parent_entry = self._storage.get(parent_path)
                if parent_entry:
                    parent_entry["children"].add(part)

    def set_value(self, path: str, value: Any, notify: bool = True):
        clean_path = path.strip("/")

        with self._lock:
            # If we are directly storing a StoreLink, assign it at the explicit alias path
            if isinstance(value, StoreLink):
                entry = self._storage.get(clean_path)
                old_val = entry["val"] if entry else None
                if isinstance(old_val, StoreLink):
                    old_val.teardown()

                self._ensure_node(clean_path)
                self._storage[clean_path]["val"] = value
                value.setup()

                if notify:
                    self._queue_notification(clean_path, value, old_val)
                return

            # For normal values, resolve the path to support deep writing into links
            resolved_path = self._resolve_deep_path(clean_path)
            entry = self._storage.get(resolved_path)

            if entry:
                old_value = entry["val"]
                entry["val"] = value
            else:
                self._ensure_node(resolved_path)
                entry = self._storage[resolved_path]
                old_value = entry["val"]
                entry["val"] = value

        if notify and old_value != value:
            self._queue_notification(resolved_path, value, old_value)

    def get_value(self, path: str) -> Any:
        resolved_path = self._resolve_deep_path(path.strip("/"))
        with self._lock:
            if resolved_path in self._storage:
                return self._storage[resolved_path]["val"]
            return None

    def remove_item(self, path: str):
        clean_path = path.strip("/")
        if clean_path == "":
            with self._lock:
                self._storage[""]["val"] = None
            return

        with self._lock:
            # Check if the exact path itself is a StoreLink.
            # If it is, we want to remove the link, NOT follow it and delete the target!
            entry = self._storage.get(clean_path)
            if entry and isinstance(entry["val"], StoreLink):
                resolved_path = clean_path
            else:
                resolved_path = self._resolve_deep_path(clean_path)

            if resolved_path not in self._storage:
                return

            old_val = self._storage[resolved_path]["val"]
            if isinstance(old_val, StoreLink):
                old_val.teardown()

            self._queue_notification(resolved_path, None, old_val)
            self._recursive_delete(resolved_path)

            if "/" in resolved_path:
                parent_path, child_key = resolved_path.rsplit("/", 1)
            else:
                parent_path, child_key = "", resolved_path

            if parent_path in self._storage:
                self._storage[parent_path]["children"].discard(child_key)

    def _recursive_delete(self, path: str):
        if path not in self._storage:
            return
        children = list(self._storage[path]["children"])
        for child_key in children:
            child_path = f"{path}/{child_key}"
            if child_path in self._storage:
                old_val = self._storage[child_path]["val"]
                if isinstance(old_val, StoreLink):
                    old_val.teardown()
                self._queue_notification(child_path, None, old_val)
            self._recursive_delete(child_path)

        if path in self._subscribers:
            del self._subscribers[path]
        del self._storage[path]

    def create_list_item(self, base_path: str, prefix: str = None) -> Item:
        clean_path = base_path.strip("/")
        with self._lock:
            if clean_path not in self._storage:
                self._ensure_node(clean_path)

            children = self._storage[clean_path]["children"]
            max_idx = -1

            if prefix:
                pattern = re.compile(r"^" + re.escape(prefix) + r"#(\d+)$")
            else:
                pattern = re.compile(r"^#(\d+)$")

            for child in children:
                match = pattern.match(child)
                if match:
                    idx = int(match.group(1))
                    if idx > max_idx:
                        max_idx = idx

            new_key = f"{prefix}#{max_idx + 1}" if prefix else f"#{max_idx + 1}"
            new_path = f"{clean_path}/{new_key}" if clean_path else new_key

            self.set_value(new_path, None)
            return self.at(new_path)

    def get_children_keys(self, path: str) -> List[str]:
        resolved_path = self._resolve_deep_path(path.strip("/"))
        with self._lock:
            if resolved_path in self._storage:
                return sorted(list(self._storage[resolved_path]["children"]))
            return []

    def get_subtree(self, base_path: str) -> DumpData:
        clean_base = base_path.strip("/")
        result = []
        with self._lock:
            for path in sorted(self._storage.keys()):
                if clean_base and len(path) < len(clean_base):
                    continue
                if path not in self._storage:
                    continue
                val = self._storage[path]["val"]
                if val is not None:
                    if clean_base == "":
                        is_self = (path == "")
                        is_child = (path != "")
                    else:
                        is_self = (path == clean_base)
                        is_child = path.startswith(clean_base + "/")

                    if is_self or is_child:
                        rel_key = "" if is_self else (path if clean_base == "" else path[len(clean_base) + 1:])
                        # If exporting a StoreLink, format it so it can be restored later
                        if isinstance(val, StoreLink):
                            link_data = {"$link": val.target_path, "bubble_events": val.bubble_events}
                            result.append((rel_key, link_data))
                        else:
                            result.append((rel_key, val))
        return result

    def _queue_notification(self, path: str, new_val: Any, old_val: Any):
        if not hasattr(self._local, "batch_stack"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
            self._local.group_notify = True

        # If group is silent, drop event immediately
        if hasattr(self._local, "group_notify") and not self._local.group_notify:
            return

        if not hasattr(self._local, "current_source"):
            self._local.current_source = None

        event = (path, new_val, old_val, self._local.current_source)
        self._local.pending_changes.append(event)

        if self._local.batch_stack == 0:
            self._flush_notifications()

    def _inject_event(self, path: str, new_val: Any, old_val: Any, source_id: str = None):
        """Allows StoreLinks to manually inject events into the current batch sequence."""
        if not hasattr(self._local, "pending_changes"):
            self._local.batch_stack = 0
            self._local.pending_changes = []
            self._local.group_notify = True
            self._local.current_source = None

        if hasattr(self._local, "group_notify") and not self._local.group_notify:
            return

        event = (path, new_val, old_val, source_id)
        self._local.pending_changes.append(event)

        if self._local.batch_stack == 0:
            self._flush_notifications()

    def _flush_notifications(self):
        # OPTIMIZED: Ancestor Lookup Strategy
        if not hasattr(self._local, "pending_changes") or not self._local.pending_changes:
            return

        events = self._local.pending_changes
        self._local.pending_changes = []

        # 1. Identify all relevant paths (the path itself + all ancestors)
        relevant_sub_paths = set()
        for event in events:
            path = event[0]
            relevant_sub_paths.add(path)
            while "/" in path:
                path, _ = path.rsplit("/", 1)
                relevant_sub_paths.add(path)
            if path != "":
                relevant_sub_paths.add("")  # Root always relevant

        # 2. Retrieve only subscribers on those paths (O(1) lookups)
        with self._lock:
            relevant_entries = []
            for sub_path in relevant_sub_paths:
                if sub_path in self._subscribers:
                    relevant_entries.append((sub_path, self._subscribers[sub_path]))

        # 3. Process events per subscriber safely through a clean pipeline
        for sub_path, sub_entries in relevant_entries:
            # Get all events relevant to this base lookup path
            events_in_scope = [e for e in events if e[0] == sub_path or e[0].startswith(sub_path + "/")]

            if not events_in_scope:
                continue

            for entry in sub_entries:
                filtered_events = []

                # --- A. Apply All Filters ---
                for e in events_in_scope:
                    ep = e[0]

                    # 1. Source filter
                    if entry["ignore_source"] is not None and e[3] == entry["ignore_source"]:
                        continue

                    # 2. Wildcard Regex filter
                    pattern = entry.get("pattern")
                    if pattern and not pattern.match(ep):
                        continue

                    # 3. Recursive filter
                    # If not recursive, the path must match exactly.
                    # Wildcards handle non-recursive via a $ at the end of the regex.
                    if not entry["recursive"]:
                        if pattern:
                            pass
                        elif ep != sub_path:
                            continue

                    # 4. Exclude filter
                    if entry["exclude"]:
                        if any(ep == ex or ep.startswith(ex + "/") for ex in entry["exclude"]):
                            continue

                    filtered_events.append(e)

                if not filtered_events:
                    continue

                # --- B. Apply Snapshots (extract) ---
                extract_fields = entry.get("extract")
                if extract_fields:
                    final_events = []
                    seen_bases = set()

                    for e in filtered_events:
                        # Find the correct base path for the snapshot.
                        # Wildcards use the dynamically matched regex segment.
                        if pattern:
                            base_path = pattern.match(e[0]).group(0)
                        else:
                            base_path = sub_path

                        # Deduplicate batch updates for the same snapshot root
                        if base_path in seen_bases:
                            continue
                        seen_bases.add(base_path)

                        # Generate the atomic snapshot
                        snapshot = {}
                        for field in extract_fields:
                            if field == ".":
                                snapshot["."] = self.get_value(base_path)
                            else:
                                target = f"{base_path}/{field}" if base_path else field
                                snapshot[field] = self.get_value(target)

                        final_events.append((base_path, snapshot, e[2], e[3]))
                else:
                    final_events = filtered_events

                # --- C. Emit Callback ---
                try:
                    entry["cb"](final_events)
                except Exception as e:
                    print(f"[Store] Callback error {sub_path}: {e}")
