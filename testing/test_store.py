import pytest
import threading
import time
from typing import List, Tuple, Any

# Adjust the import below to match your actual project structure
# from TaskTonic.ttTonicStore import Store, Item, ttStore
# For this example, assuming they are available in the context:
from TaskTonic.ttTonicStore import Store, Item, ttStore


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
        return MockStore()

    def test_subscribe_and_callback(self, store):
        """
        Test if subscribers receive the correct updates.
        """
        received_updates = []

        def on_update(updates):
            # updates is expected to be a list of tuples: (path, new, old, source)
            received_updates.extend(updates)

        # Subscribe to the 'sensors' path
        store.subscribe('sensors', on_update)

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

        store.subscribe('config', callback)

        with store.group():
            store.set([
                ('config/a', 1),
                ('config/nested/b', 2),  # Should also trigger 'config' listener
                ('outside', 3)
            ])

        assert updates_received == 2

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