import pytest
import threading
import time
from typing import List, Tuple, Any

# Adjust the import below to match your actual project structure
# from TaskTonic.ttTonicStore import Store, Item, ttStore
# For this example, assuming they are available in the context:
from TaskTonic.ttTonicStore import ttStore
from TaskTonic.internals.Store import Store, Item


# ======================================================================================================================
# PART 1: Core Data & Structure Tests (Store & Item)
# ======================================================================================================================
class TestStoreCore:
    """
    Tests for the foundational Store and Item classes.
    Focuses on path manipulation, data retrieval, syntax support, and hierarchical navigation.
    """

    @pytest.fixture
    def store(self):
        """
        Fixture to provide a clean Store instance for every test method.
        """
        return Store()

    def test_basic_set_and_get(self, store):
        """
        Test simple key-value setting and retrieval using absolute paths.
        """
        store.set([
            ('config/version', '1.0.0'),
            ('config/debug', True)
        ])

        assert store.get('config/version') == '1.0.0'
        assert store.get('config/debug') is True
        # Test default value for missing key
        assert store.get('config/missing', 'default') == 'default'

    def test_iterable_types_in_set(self, store):
        """
        Test that .set() accepts both lists and tuples (Iterable check).
        This validates the fix for the PyCharm warning/static analysis.
        """
        # Case 1: List of tuples (Standard)
        store.set([('a', 1)])
        assert store.get('a') == 1

        # Case 2: Tuple of tuples (The specific requested fix)
        # This ensures ((k,v), (k,v)) is valid runtime syntax
        store.set((
            ('b', 2),
            ('c', 3)
        ))
        assert store.get('b') == 2
        assert store.get('c') == 3

    def test_children_filtering(self, store):
        """
        Test the .children() iterator with and without prefix filtering.
        Verifies that:
        - No argument returns ALL children (lists and properties).
        - prefix='' returns only standard list items (created with '#').
        - prefix='name' returns only specific list items (created with 'name#').
        """
        # Define complex data structure as requested
        data = [
            ('sensors/#', 'temp_sensor_1'),  # Creates index 0 (e.g., sensors/#0)
            ('sensors/./unit', 'C'),
            ('sensors/./val', 25.5),

            ('sensors/#', 'hum_sensor'),  # Creates index 1 (e.g., sensors/#1)
            ('sensors/./unit', '%'),
            ('sensors/./val', 60),

            ('sensors/extra', 33),  # A standard property (not a list item)

            ('sensors/sens#', 'temp_sensor_2'),  # Creates named list index 0 (e.g., sensors/sens#0)
            ('sensors/sens./unit', 'C'),
            ('sensors/sens./val', 25.5),
        ]
        store.set(data)

        # 1. Test .children() WITHOUT arguments -> Should return EVERYTHING (4 items)
        # Expected keys: #0, #1, extra, sens#0
        sensors_node = store.at('sensors')
        all_children = list(sensors_node.children())

        assert len(all_children) == 4

        # Verify that 'extra' is among them
        # We look for the item where the value is 33
        has_extra = any(item.v == 33 for item in all_children)
        assert has_extra is True

        # 2. Test .children(prefix='') -> Should return only standard list items (2 items)
        # Expected: #0 (temp_sensor_1) and #1 (hum_sensor)
        # It should EXCLUDE 'extra' and 'sens#0'
        standard_list_items = list(sensors_node.children(prefix=''))

        assert len(standard_list_items) == 2
        assert standard_list_items[0].v == 'temp_sensor_1'
        assert standard_list_items[1].v == 'hum_sensor'

        # 3. Test .children(prefix='sens') -> Should return only 'sens#' items (1 item)
        # Expected: sens#0 (temp_sensor_2)
        sens_list_items = list(sensors_node.children(prefix='sens'))

        assert len(sens_list_items) == 1
        assert sens_list_items[0].v == 'temp_sensor_2'
        assert sens_list_items[0]['unit'].v == 'C'

    def test_item_navigation_and_value(self, store):
        """
        Test the Item object (cursor) functionality: .v property and navigation via [].
        """
        store.set([('machine/settings/speed', 100)])

        # Get an Item pointer
        speed_item = store.at('machine/settings/speed')

        assert isinstance(speed_item, Item)
        assert speed_item.v == 100

        # Change value via Item
        speed_item.v = 150
        assert store.get('machine/settings/speed') == 150

    def test_item_parent_navigation(self, store):
        """
        Test navigating up the tree using .parent.

        This test covers two scenarios:
        1. Hierarchy where every level has an explicit value.
        2. Hierarchy where intermediate levels are just containers (value is None),
           verified by checking their children.
        """
        # --- Scenario 1: Explicit values at every level ---
        store.set([
            ('grandparent', 100),
            ('grandparent/parent', 200),
            ('grandparent/parent/child', 300)
        ])

        item_child = store.at('grandparent/parent/child')
        item_parent = item_child.parent
        item_gp = item_parent.parent

        # Verify values to ensure .parent returned the correct node
        assert item_child.v == 300
        assert item_parent.v == 200
        assert item_gp.v == 100

        # Verify that root parent is None (or handles gracefully)
        # Assuming 'grandparent' is at root level:
        assert item_gp.parent is None or item_gp.parent.path == ''

        # --- Scenario 2: Container nodes (folders without values) ---
        store.set([
            ('folder/doc_a', 'content_a'),
            ('folder/doc_b', 'content_b')
        ])

        item_doc_a = store.at('folder/doc_a')
        item_folder = item_doc_a.parent

        # The folder itself was never assigned a value, so it should be None
        assert item_folder.v is None

        # However, it acts as a parent container, so we verify via children()
        # We expect 'doc_a' and 'doc_b' to be children of 'folder'
        folder_contents = list(item_folder.children())

        assert len(folder_contents) == 2

        # Extract values from children to verify content
        child_values = [child.v for child in folder_contents]
        assert 'content_a' in child_values
        assert 'content_b' in child_values

    def test_item_list_root(self, store):
        """
        Test .list_root functionality.
        This should find the list item itself, even when deep inside that item's properties.
        """
        store.set([
            ('users/#', 'alice'),
            ('users/./profile/age', 30)
        ])

        # We are deep inside the structure: users -> #0 -> profile -> age
        age_item = store.at('users/#0/profile/age')

        # list_root should return the item at 'users/#0'
        root_item = age_item.list_root

        assert root_item.v == 'alice'

    def test_dict_set_input(self, store):
        """
        Test that .set() also handles standard dictionaries correctly.
        """
        store.set({
            'direct/path': 123,
            'another/path': 'abc'
        })
        assert store.get('direct/path') == 123

    def test_complex_nested_updates(self, store):
        """
        Test updating an existing structure without wiping siblings.
        """
        # Initial setup
        store.set([
            ('grp/a', 1),
            ('grp/b', 2)
        ])

        # Update only 'a'
        store.set([('grp/a', 99)])

        assert store.get('grp/a') == 99
        assert store.get('grp/b') == 2  # Should still exist


# ======================================================================================================================
# PART 2: Advanced ttStore Features (Events, Locking, Concurrency)
# ======================================================================================================================

class MockStore(ttStore):
    """
    Minimal subclass of ttStore to test service functionalities in isolation.
    """
    _tt_is_service = "mock_store"

class TestTTStoreFeatures:
    """
    Tests for ttStore specific features: Subscriptions, Event Callbacks, and Thread Safety.
    """

    @pytest.fixture
    def store(self):
        # return MockStore()
        return Store()

    def test_subscribe_and_callback(self, store):
        """
        Test if subscribers receive the correct updates.
        """
        received_updates = []

        def on_update(updates):
            # updates is expected to be a list of tuples: (path, new, old, source)
            received_updates.extend(updates)

        # Subscribe to the 'sensors' path
        store.subscribe('sensors', on_update, recursive=True)

        # Perform a set action inside a group
        with store.group():
            store.set([
                ('sensors/temp', 20),
                ('other/param', 5)  # Should NOT trigger the callback
            ])

        # Assertions
        # 1. We expect only 1 update (for sensors/temp), not for other/param
        assert len(received_updates) == 1

        path, new_val, old_val, source = received_updates[0]
        assert path == 'sensors/temp'
        assert new_val == 20

    def test_wildcard_subscription(self, store):
        """
        Test if subscribing to a parent path catches changes in children.
        """
        updates_received = 0

        def callback(updates):
            nonlocal updates_received
            updates_received += len(updates)

        store.subscribe('config', callback, recursive=True)

        with store.group():
            store.set([
                ('config/a', 1),
                ('config/nested/b', 2),  # Should also trigger 'config' (no recursive set)
                ('config/nested', 3),
                ('outside', 4)
            ])

        assert updates_received == 3

    def test_multithreading_locking_integrity(self, store):
        """
        STRESS TEST: Thread Safety.

        Scenario: 10 threads running simultaneously.
        Each thread appends 100 items to the SAME list in the store ('logs/#').

        Expected Result: The list 'logs' must contain exactly 1000 items.
        Failure Mode: Race conditions cause items to be overwritten or RuntimeErrors.
        """
        num_threads = 10
        items_per_thread = 100
        total_expected = num_threads * items_per_thread

        def worker(thread_id):
            for i in range(items_per_thread):
                # Using '#' syntax forces a read-modify-write operation (get len, add item).
                # This requires robust locking inside the Store implementation.
                store.set([
                    ('logs/#', f"t{thread_id}-{i}"),
                    ('logs/./val', i)
                ])
                # Tiny sleep to encourage context switching to provoke race conditions
                time.sleep(0.0001)

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Check results
        # We cannot use store.get('logs') as it returns None for containers.
        # Instead, we use .children() to count the created items.
        logs_container = store.at('logs')
        all_logs = list(logs_container.children())

        assert len(all_logs) == total_expected, \
            f"Race condition detected! Expected {total_expected} items, found {len(all_logs)}."

        # Optional: Verify data integrity of the last item
        # This confirms that the values were stored correctly associated with the list items
        last_item = all_logs[-1]
        assert 't' in str(last_item.v)
        assert isinstance(last_item['val'].v, int)

    def test_read_write_concurrency(self, store):
        """
        Test stability when one thread reads continuously while another writes continuously.
        Ensures no RuntimeError (dictionary changed size during iteration) occurs.
        """
        stop_event = threading.Event()

        def writer():
            idx = 0
            while not stop_event.is_set():
                store.set([('status/heartbeat', idx)])
                idx += 1
                time.sleep(0.001)

        def reader():
            reads = 0
            while not stop_event.is_set():
                val = store.get('status/heartbeat')
                reads += 1
                time.sleep(0.001)
            return reads

        w_thread = threading.Thread(target=writer)
        r_thread = threading.Thread(target=reader)

        w_thread.start()
        r_thread.start()

        # Let them run concurrently for 1 second
        time.sleep(1)

        stop_event.set()
        w_thread.join()
        r_thread.join()

        # If we reached here without an exception, the test passed.
        assert store.get('status/heartbeat') > 0


class TestStoreNewFeatures:
    """
    Tests for the newly added advanced subscription features:
    - MQTT-style wildcards (* and **)
    - Atomic Snapshots (extract)
    - Self-reference in Snapshots (.)
    - Immediate Initialization (trigger_now)
    - Subscribing via Items
    """

    @pytest.fixture
    def store(self):
        return Store()

    def test_wildcard_single_level(self, store):
        """
        Test the single-level wildcard (*).
        It should match exactly one path segment.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Subscribe to any view under ui/
        store.subscribe("ui/*/view", callback)

        with store.group():
            store.set("ui/dashboard/view", "active")  # Should match
            store.set("ui/settings/view", "hidden")  # Should match
            store.set("ui/dashboard/other", 123)  # Should NOT match (wrong suffix)
            store.set("backend/dashboard/view", 1)  # Should NOT match (wrong prefix)

        assert len(events) == 2

        paths = [e[0] for e in events]
        assert "ui/dashboard/view" in paths
        assert "ui/settings/view" in paths

    def test_wildcard_recursive_level(self, store):
        """
        Test the recursive wildcard (**).
        It should match across multiple path segments.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.subscribe("system/**/status", callback)

        with store.group():
            # Should match (one level deep)
            store.set("system/network/status", "ok")
            # Should match (two levels deep)
            store.set("system/cpu/core_1/status", "high")
            # Should NOT match (doesn't end with status)
            store.set("system/cpu/core_1/usage", 99)

        assert len(events) == 2

        paths = [e[0] for e in events]
        assert "system/network/status" in paths
        assert "system/cpu/core_1/status" in paths

    def test_atomic_snapshots_with_extract_and_self(self, store):
        """
        Test extracting specific fields into a flat dictionary,
        including the self-reference (.).
        """
        events = []

        def callback(e):
            events.extend(e)

        # Initial state setup
        store.set([
            ("sensor/temp", 25.0),
            ("sensor/temp/unit", "Celsius"),
            ("sensor/temp/battery", 80)
        ])

        # Subscribe to the temp sensor, but only extract the value itself and the unit
        # We explicitly exclude battery by not listing it
        store.subscribe(
            "sensor/temp",
            callback,
            extract=[".", "unit"],
            recursive=False
        )

        # Trigger a change on the base path
        store.set("sensor/temp", 26.5)

        assert len(events) == 1

        path, snapshot, old_val, source = events[0]
        assert path == "sensor/temp"

        # Verify the snapshot dictionary
        assert isinstance(snapshot, dict)
        assert snapshot["."] == 26.5
        assert snapshot["unit"] == "Celsius"

        # Verify unrequested fields are not in the snapshot
        assert "battery" not in snapshot

    def test_trigger_now(self, store):
        """
        Test if trigger_now=True immediately fires the callback with the current state.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set("app/ready", True)

        # Subscribe with trigger_now, it should fire immediately during the function call
        store.subscribe("app/ready", callback, trigger_now=True)

        assert len(events) == 1

        path, val, old_val, source = events[0]
        assert path == "app/ready"
        assert val is True
        assert old_val is None
        assert source == "init"

    def test_trigger_now_with_extract(self, store):
        """
        Test if trigger_now=True works correctly in combination with extract snapshots.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set([
            ("ui/button", "submit"),
            ("ui/button/color", "blue")
        ])

        # This should immediately return a snapshot of the current state
        store.subscribe("ui/button", callback, extract=[".", "color"], trigger_now=True)

        assert len(events) == 1

        path, snapshot, old_val, source = events[0]
        assert path == "ui/button"
        assert snapshot["."] == "submit"
        assert snapshot["color"] == "blue"

    def test_item_subscribe(self, store):
        """
        Test if subscribing directly via an Item object works identically
        to calling subscribe on the store.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Get the cursor
        btn_item = store.at("ui/dialog/btn_ok")

        # Subscribe via the item
        btn_item.subscribe(callback)

        # Trigger an update using the item's .v setter
        btn_item.v = "clicked"

        assert len(events) == 1
        assert events[0][0] == "ui/dialog/btn_ok"
        assert events[0][1] == "clicked"

    def test_wildcard_combined_with_snapshot(self, store):
        """
        Test combining single-level wildcards (*) with atomic snapshots (extract).
        Scenario: A list of UI parameters where modifying any ID triggers a snapshot
        of that specific ID's properties (color and active state).
        """
        events = []

        def callback(e):
            events.extend(e)

        # 1. Initial setup: Two UI buttons with their own state
        store.set([
            ("ui/items/btn_save/color", "blue"),
            ("ui/items/btn_save/active", True),
            ("ui/items/btn_cancel/color", "red"),
            ("ui/items/btn_cancel/active", False)
        ])

        # 2. Subscribe to ANY item under ui/items/
        # We want to extract 'color' and 'active' relative to the matched item.
        store.subscribe(
            "ui/items/*",
            callback,
            extract=["color", "active"],
            recursive=True
        )

        # 3. Action: Modify the color of btn_cancel
        store.set("ui/items/btn_cancel/color", "grey")

        # 4. Assertions for the first action
        assert len(events) == 1

        path, snapshot, old_val, source = events[0]

        # It should trigger exactly on the modified item's root path
        assert path == "ui/items/btn_cancel"

        # The snapshot must contain the new color, AND the unchanged active state
        assert isinstance(snapshot, dict)
        assert snapshot["color"] == "grey"
        assert snapshot["active"] is False

        # 5. Action: Modify the other button
        events.clear()
        store.set("ui/items/btn_save/active", False)

        # 6. Assertions for the second action
        assert len(events) == 1
        assert events[0][0] == "ui/items/btn_save"
        assert events[0][1]["color"] == "blue"  # Fetched the unchanged color
        assert events[0][1]["active"] is False  # The newly set active state

    def test_trigger_now_basic_value(self, store):
        """
        Test of trigger_now direct de huidige state afvuurt als een 'init' event.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Zet een initiële waarde in de store
        store.set("system/status", "online")

        # Abonneer met trigger_now=True
        store.subscribe("system/status", callback, trigger_now=True)

        # De callback moet onmiddellijk afgevuurd zijn, zonder dat er een nieuwe set() is gedaan
        assert len(events) == 1

        path, val, old_val, source = events[0]
        assert path == "system/status"
        assert val == "online"
        assert old_val is None  # Bij een init is er conceptueel geen old_val
        assert source == "init"  # Dit bewijst dat het door de trigger_now logica komt

    def test_trigger_now_empty_path(self, store):
        """
        Test of trigger_now netjes omgaat met paden waar nog geen data in zit.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Abonneer op een pad dat nog niet bestaat
        store.subscribe("ghost/path", callback, trigger_now=True)

        assert len(events) == 1

        path, val, old_val, source = events[0]
        assert path == "ghost/path"
        assert val is None  # Moet veilig None teruggeven
        assert source == "init"

    def test_trigger_now_with_extract_snapshot(self, store):
        """
        Test of trigger_now correct een atomische snapshot (dictionary) opbouwt
        als dit gecombineerd wordt met de extract parameter.
        """
        events = []

        def callback(e):
            events.extend(e)

        # Zet een complexe structuur op
        store.set([
            ("ui/widget_1", "active"),
            ("ui/widget_1/color", "blue"),
            ("ui/widget_1/size", 100),
            ("ui/widget_1/hidden", False)
        ])

        # Abonneer met zowel trigger_now als extract
        store.subscribe(
            "ui/widget_1",
            callback,
            extract=[".", "color", "size"],
            trigger_now=True
        )

        assert len(events) == 1

        path, snapshot, old_val, source = events[0]

        assert path == "ui/widget_1"
        assert source == "init"

        # Verifieer dat de snapshot een correct opgebouwde dictionary is
        assert isinstance(snapshot, dict)
        assert snapshot["."] == "active"
        assert snapshot["color"] == "blue"
        assert snapshot["size"] == 100

        # Het veld 'hidden' mag niet in de snapshot zitten, want het zat niet in de extract lijst
        assert "hidden" not in snapshot

    def test_trigger_now_with_wildcard_and_snapshot(self, store):
        """
        Test if trigger_now correctly fetches a list of items using a wildcard,
        builds snapshots for ALL existing matches, and returns them in one initial batch.
        Crucial for initial UI rendering of lists.
        """
        events = []

        def callback(e):
            events.extend(e)

        # 1. Pre-fill the store with multiple items
        store.set([
            ("ui/list/item_1/color", "red"),
            ("ui/list/item_1/active", True),
            ("ui/list/item_2/color", "blue"),
            ("ui/list/item_2/active", False),
            ("ui/other_stuff/color", "green")  # Should be ignored
        ])

        # 2. Subscribe with trigger_now, wildcard, AND extract
        store.subscribe(
            "ui/list/*",
            callback,
            extract=["color", "active"],
            recursive=True,
            trigger_now=True
        )

        # 3. Assertions
        assert len(events) == 2

        # Extract paths and snapshots for easy checking
        results = {e[0]: e[1] for e in events}

        assert "ui/list/item_1" in results
        assert "ui/list/item_2" in results

        assert results["ui/list/item_1"]["color"] == "red"
        assert results["ui/list/item_1"]["active"] is True

        assert results["ui/list/item_2"]["color"] == "blue"
        assert results["ui/list/item_2"]["active"] is False

    def test_unsubscribe_by_instance(self, store):
        """Test if unsubscribing via an instance (owner) removes all linked callbacks."""

        class MockWidget:
            def __init__(self):
                self.count = 0

            def on_change(self, events):
                self.count += 1

        widget = MockWidget()
        # Automatically detects 'widget' as owner because on_change is a bound method
        store.subscribe("ui/theme", widget.on_change)

        # Update 1: Should trigger
        store.set("ui/theme", "dark")
        assert widget.count == 1

        # Unsubscribe using the instance
        store.unsubscribe(widget)

        # Update 2: Should NOT trigger
        store.set("ui/theme", "light")
        assert widget.count == 1

    def test_unsubscribe_lambda_with_owner(self, store):
        """Test if a lambda linked to an owner is correctly removed."""
        results = []

        class Owner: pass

        my_owner = Owner()

        # Subscribe a lambda and manually link it to my_owner
        store.subscribe("data/val", lambda e: results.append(e), owner=my_owner)

        # Update 1: Should trigger
        store.set("data/val", 100)
        assert len(results) == 1

        # Unsubscribe the owner
        store.unsubscribe(my_owner)

        # Update 2: Should NOT trigger
        store.set("data/val", 200)
        assert len(results) == 1

    def test_unsubscribe_by_callback_function(self, store):
        """Test if unsubscribing via the function itself works."""
        self.call_count = 0

        def my_callback(events):
            self.call_count += 1

        store.subscribe("system/status", my_callback)

        store.set("system/status", "online")
        assert self.call_count == 1

        # Unsubscribe using the function reference
        store.unsubscribe(my_callback)

        store.set("system/status", "offline")
        assert self.call_count == 1

    def test_item_unsubscribe_all_on_path(self, store):
        """Test if item.unsubscribe() without args clears the entire path."""
        count_a = 0
        count_b = 0

        def cb_a(e): nonlocal count_a; count_a += 1

        def cb_b(e): nonlocal count_b; count_b += 1

        item = store.at("ui/sidebar")
        item.subscribe(cb_a, owner=self) # use owner, because internal function, no class method
        item.subscribe(cb_b, owner=self)

        item.v = "open"
        assert count_a == 1
        assert count_b == 1

        # Remove ALL listeners for this path
        item.unsubscribe(self)

        item.v = "closed"
        assert count_a == 1
        assert count_b == 1


# ======================================================================================================================
# PART 3: Proxy Nodes (StoreLink) & Batch Iteration (set_each)
# ======================================================================================================================

class TestStoreLinkAndSetEach:
    """
    Tests for the StoreLink proxy pattern (aliasing) via the .link_to() method
    and the set_each batching method.
    """

    @pytest.fixture
    def store(self):
        """Fixture to provide a clean Store instance for every test method."""
        return Store()

    def test_storelink_passive_read_write(self, store):
        """
        Test if a passive link (bubble_events=False) correctly redirects basic reads
        and writes to the canonical target path.
        """
        # 1. Setup canonical data
        store.set("devices/lamp_1", {"state": "off", "brightness": 0})

        # 2. Create a passive link via Item method
        store.at("house/living/main_light").link_to("devices/lamp_1", bubble_events=False)

        # 3. Test reading via alias
        alias_item = store.at("house/living/main_light")
        assert alias_item.v["state"] == "off"

        # 4. Test writing via alias
        alias_item.set("brightness", 100)

        # 5. Verify the canonical path was updated
        assert store.get("devices/lamp_1/brightness") == 100

    def test_storelink_deep_path_resolution(self, store):
        """
        Test if the Store correctly resolves paths segment by segment when
        writing to or reading from a sub-property of a link.
        """
        store.set("devices/thermostat_1/temperature", 21.5)

        store.at("rooms/kitchen/climate").link_to("devices/thermostat_1", bubble_events=False)

        # Access deep property through the link
        deep_item = store.at("rooms/kitchen/climate/temperature")
        assert deep_item.v == 21.5

        # Modify deep property through the link
        deep_item.v = 22.0

        # Verify the physical device was updated
        assert store.get("devices/thermostat_1/temperature") == 22.0

    def test_storelink_active_event_bubbling(self, store):
        """
        Test if an active link (bubble_events=True) intercepts changes from the canonical path
        and injects an event into its own alias path so subscribers are notified.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set("devices/sensor_1/motion", False)

        store.at("security/zones/front_door").link_to("devices/sensor_1", bubble_events=True)

        # Subscribe to the alias path sub-property
        store.subscribe("security/zones/front_door/motion", callback)

        # Change the canonical path
        store.set("devices/sensor_1/motion", True)

        # The active link should have injected an event for the alias
        assert len(events) == 1
        path, new_val, old_val, source = events[0]
        assert path == "security/zones/front_door/motion"
        assert new_val is True

    def test_storelink_cascading_delete(self, store):
        """
        Test if deleting a canonical item automatically destroys the link
        and propagates a 'None' event to alias subscribers.
        """
        events = []

        def callback(e):
            events.extend(e)

        store.set("system/users/u1", {"name": "Alice"})

        store.at("ui/current_user").link_to("system/users/u1", bubble_events=True)
        store.subscribe("ui/current_user", callback)

        # Remove canonical item
        store.remove_item("system/users/u1")

        # Link should be destroyed and None propagated to alias
        assert store.get("ui/current_user") is None

        # Check the events. One should be the removal of the alias.
        removal_events = [e for e in events if e[0] == "ui/current_user" and e[1] is None]
        assert len(removal_events) == 1

    def test_storelink_circular_prevention(self, store):
        """
        Test if the deep path resolution catches circular links and raises
        a ValueError to prevent infinite recursion/loops.
        """
        store.at("folder_a").link_to("folder_b")
        store.at("folder_b").link_to("folder_a")

        with pytest.raises(ValueError) as excinfo:
            store.get("folder_a/prop")

        assert "Circular StoreLink detected" in str(excinfo.value)

    def test_storelink_dump_format(self, store):
        """
        Test if links are serialized correctly during a store dump,
        allowing them to be restored later.
        """
        store.set("devices/dummy", 123)
        store.at("alias/dummy").link_to("devices/dummy", bubble_events=True)

        dump_data = dict(store.dump())

        assert dump_data["devices/dummy"] == 123

        alias_dump = dump_data["alias/dummy"]
        assert isinstance(alias_dump, dict)
        assert alias_dump["$link"] == "devices/dummy"
        assert alias_dump["bubble_events"] is True

    def test_item_set_each_with_prefix(self, store):
        """
        Test the set_each method with a prefix filter.
        It should update matching children and ignore others.
        """
        store.set([
            ("room/lamp#0/brightness", 0),
            ("room/lamp#1/brightness", 0),
            ("room/fan#0/speed", 0)
        ])

        room = store.at("room")

        # Use set_each with a prefix to target only lamps
        room.set_each("brightness", 100, prefix="lamp")

        assert store.get("room/lamp#0/brightness") == 100
        assert store.get("room/lamp#1/brightness") == 100

        # Fan should remain unaffected and not have a brightness property
        assert store.get("room/fan#0/speed") == 0
        assert store.get("room/fan#0/brightness") is None

    def test_item_set_each_without_prefix(self, store):
        """
        Test the set_each method without a prefix filter.
        It should update all immediate children.
        """
        store.set([
            ("ui/widgets/#/disabled", False),
            ("ui/widgets/#/disabled", False),
            ("ui/widgets/#/disabled", False)
        ])

        assert store.get("ui/widgets/#0/disabled") is False
        assert store.get("ui/widgets/#1/disabled") is False
        assert store.get("ui/widgets/#2/disabled") is False

        widgets = store.at("ui/widgets")

        # Apply to all children
        widgets.set_each("disabled", True)

        assert store.get("ui/widgets/#0/disabled") is True
        assert store.get("ui/widgets/#1/disabled") is True
        assert store.get("ui/widgets/#2/disabled") is True

    def test_set_each_through_storelink(self, store):
        """
        Complex scenario: Test if set_each works correctly when the children
        it iterates over are actually links pointing elsewhere.
        """
        store.set("devices/l1/power", "off")
        store.set("devices/l2/power", "off")

        store.at("house/lamps/l1").link_to("devices/l1")
        store.at("house/lamps/l2").link_to("devices/l2")

        # Perform set_each on the alias folder
        store.at("house/lamps").set_each("power", "on")

        # Check if canonical devices were updated via deep resolution
        assert store.get("devices/l1/power") == "on"
        assert store.get("devices/l2/power") == "on"


# ======================================================================================================================
# PART 4: Event Routing Scenarios
# ======================================================================================================================

class TestEventRoutingScenarios:

    @pytest.fixture
    def store(self):
        return Store()

    def test_event_routing_passive_link(self, store):
        """
        Scenario 1: Passive Link (bubble_events=False)
        Proves that a physical change ONLY bubbles up the physical tree,
        and leaves the alias tree completely silent (no event storms).
        """
        store.set("devices/l1/power", "off")
        store.at("house/lamps/l1").link_to("devices/l1", bubble_events=False)

        device_events = []
        house_events = []

        store.subscribe("devices", lambda e: device_events.extend(e), recursive=True, owner=self)
        store.subscribe("house/lamps", lambda e: house_events.extend(e), recursive=True, owner=self)

        store.set("devices/l1/power", "on")

        assert len(device_events) == 1, "The physical tree should receive the event."
        assert device_events[0][0] == "devices/l1/power"

        assert len(house_events) == 0, "A passive link should NOT bubble events to its alias tree."

    def test_event_routing_active_link(self, store):
        """
        Scenario 2: Active Link (bubble_events=True)
        Proves that a physical change bubbles up the physical tree,
        AND is actively injected into the alias tree so context-listeners are notified.
        """
        store.set("devices/motion_1/detected", False)
        store.at("house/living/motion").link_to("devices/motion_1", bubble_events=True)

        device_events = []
        house_events = []

        store.subscribe("devices", lambda e: device_events.extend(e), recursive=True, owner=self)
        store.subscribe("house/living", lambda e: house_events.extend(e), recursive=True, owner=self)

        store.set("devices/motion_1/detected", True)

        assert len(device_events) == 1, "The physical tree should receive the event."
        assert device_events[0][0] == "devices/motion_1/detected"

        assert len(house_events) == 1, "An active link MUST bubble events to its alias tree."
        assert house_events[0][0] == "house/living/motion/detected"
        assert house_events[0][1] is True

    def test_wildcard_combined_with_active_storelink(self, store):
        """
        Scenario 3: Wildcards over Active Links
        Proves that a wildcard subscription on an alias folder correctly catches
        injected events from multiple active StoreLinks inside that folder.
        """
        # 1. Setup physical devices
        store["devices/sw_1/state"] = "off"
        store["devices/sw_2/state"] = "off"
        store["devices/sensor/temp"] = 20   # Unrelated device

        # 2. Setup the functional room layout with active links
        # We explicitly want to hear about changes to these switches in this room
        store.at("house/living/switches/main").link_to("devices/sw_1", bubble_events=True)
        store.at("house/living/switches/reading").link_to("devices/sw_2", bubble_events=True)

        events_caught = []

        def callback(e):
            events_caught.extend(e)

        # 3. Subscribe to ALL switches in the living room
        # Using recursive=True so we also catch the '/state' sub-property
        store.subscribe("house/living/switches/*", callback, recursive=True, owner=self)

        # 4. Trigger changes on the physical devices
        store.set("devices/sw_1/state", "on")
        store.set("devices/sensor/temp", 21)  # Should NOT trigger the wildcard
        store.set("devices/sw_2/state", "on")

        # 5. Assertions
        # We expect exactly 2 events (the two switches). The temp sensor is ignored.
        assert len(events_caught) == 2, "Wildcard should have caught exactly 2 injected alias events."

        # Verify the paths were correctly translated to the alias paths
        paths_caught = [e[0] for e in events_caught]
        assert "house/living/switches/main/state" in paths_caught
        assert "house/living/switches/reading/state" in paths_caught

        # Verify the values
        assert events_caught[0][1] == "on"
        assert events_caught[1][1] == "on"