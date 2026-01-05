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
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        self._store.remove_item(target)

    def pop(self, subpath: str = None) -> Any:
        target = f"{self._path}/{subpath}".strip("/") if subpath else self._path
        val = self._store.get_value(target)
        self._store.remove_item(target)
        return val

    def append(self, prefix: str = None) -> 'Item':
        """Creates a new child item with an auto-incrementing index (e.g. #0, #1)."""
        return self._store.create_list_item(self._path, prefix)

    def extend(self, data_list: List[Any], prefix: str = None) -> 'Item':
        """Appends multiple items to the list."""
        if not isinstance(data_list, list):
            raise ValueError("extend() expects a list")
        for data in data_list:
            new_item = self.append(prefix)
            # If data looks like a batch tuple structure, set it as structure
            if isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)) and len(
                    data[0]) == 2:
                new_item.set(data)
            else:
                new_item.v = data
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

    # --- MAGIC ---

    def at(self, subpath: str) -> 'Item':
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
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._storage: Dict[str, Dict[str, Any]] = {}
        # Pre-allocate root
        self._storage[""] = {"val": None, "children": set()}
        self._subscribers: Dict[str, List[Dict]] = {}
        # Thread Local Storage for batching contexts
        self._local = threading.local()

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

    def subscribe(self, path: str, callback: ListenerCallback, ignore_source: str = None, recursive: bool = True,
                  exclude: List[str] = None):
        """
        Register a callback.
        recursive: If True, trigger on path and descendants.
        exclude: List of absolute sub-paths to ignore (e.g. ['sensor/current']).
        """
        clean_path = path.strip("/")
        clean_exclude = [e.strip("/") for e in exclude] if exclude else []

        with self._lock:
            if clean_path not in self._subscribers:
                self._subscribers[clean_path] = []

            self._subscribers[clean_path].append({
                "cb": callback,
                "ignore_source": ignore_source,
                "recursive": recursive,
                "exclude": clean_exclude
            })

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
                if parent_entry: parent_entry["children"].add(part)

    def set_value(self, path: str, value: Any, notify: bool = True):
        # Optimized Fast Path
        with self._lock:
            if path in self._storage:
                entry = self._storage[path]
                old_value = entry["val"]
                entry["val"] = value
            else:
                self._ensure_node(path)
                entry = self._storage[path]
                old_value = entry["val"]
                entry["val"] = value

        if notify and old_value != value:
            self._queue_notification(path, value, old_value)

    def get_value(self, path: str) -> Any:
        with self._lock:
            if path in self._storage:
                return self._storage[path]["val"]
            return None

    def remove_item(self, path: str):
        clean_path = path.strip("/")
        if clean_path == "":
            with self._lock: self._storage[""]["val"] = None
            return

        with self._lock:
            if clean_path not in self._storage: return
            self._queue_notification(clean_path, None, self._storage[clean_path]["val"])
            self._recursive_delete(clean_path)

            if "/" in clean_path:
                parent_path, child_key = clean_path.rsplit("/", 1)
            else:
                parent_path, child_key = "", clean_path

            if parent_path in self._storage:
                self._storage[parent_path]["children"].discard(child_key)

    def _recursive_delete(self, path: str):
        if path not in self._storage: return
        children = list(self._storage[path]["children"])
        for child_key in children:
            child_path = f"{path}/{child_key}"
            if child_path in self._storage:
                self._queue_notification(child_path, None, self._storage[child_path]["val"])
            self._recursive_delete(child_path)

        if path in self._subscribers: del self._subscribers[path]
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
                    if idx > max_idx: max_idx = idx

            new_key = f"{prefix}#{max_idx + 1}" if prefix else f"#{max_idx + 1}"
            new_path = f"{clean_path}/{new_key}" if clean_path else new_key

            self.set_value(new_path, None)
            return self.at(new_path)

    def get_children_keys(self, path: str) -> List[str]:
        clean_path = path.strip("/")
        with self._lock:
            if clean_path in self._storage:
                return sorted(list(self._storage[clean_path]["children"]))
            return []

    def get_subtree(self, base_path: str) -> DumpData:
        clean_base = base_path.strip("/")
        result = []
        with self._lock:
            for path in sorted(self._storage.keys()):
                if clean_base and len(path) < len(clean_base): continue
                if path not in self._storage: continue
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

    def _flush_notifications(self):
        # OPTIMIZED: Ancestor Lookup Strategy
        if not hasattr(self._local, "pending_changes") or not self._local.pending_changes: return
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

        # 3. Process events against this filtered subset of subscribers
        for sub_path, sub_entries in relevant_entries:
            relevant_events = []
            for event in events:
                evt_path = event[0]
                # Match logic:
                if evt_path == sub_path:
                    relevant_events.append(event)
                elif evt_path.startswith(sub_path + "/"):
                    relevant_events.append(event)

            if relevant_events:
                for entry in sub_entries:
                    # A. Recursive Filter
                    is_recursive = entry["recursive"]

                    if not is_recursive:
                        events_for_sub = [e for e in relevant_events if e[0] == sub_path]
                    else:
                        events_for_sub = relevant_events

                    # B. Exclude Filter (Subtree pruning)
                    exclusions = entry["exclude"]
                    if exclusions and events_for_sub:
                        filtered_events = []
                        for e in events_for_sub:
                            ep = e[0]
                            is_excluded = False
                            for ex in exclusions:
                                if ep == ex or ep.startswith(ex + "/"):
                                    is_excluded = True
                                    break
                            if not is_excluded:
                                filtered_events.append(e)
                        events_for_sub = filtered_events

                    # C. Source Filter
                    ignore = entry["ignore_source"]
                    filtered = [e for e in events_for_sub if ignore is None or e[3] != ignore]
                    if filtered:
                        try:
                            entry["cb"](filtered)
                        except Exception as e:
                            print(f"[Store] Callback error {sub_path}: {e}")

