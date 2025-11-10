import pytest
from types import MappingProxyType
from unittest.mock import Mock

from TaskTonic.utils.ttDataShare import DataShare

@pytest.fixture
def ds():
    """Provides a fresh DataShare instance for each test."""
    return DataShare()


class TestInitialization:
    def test_init_empty(self):
        ds = DataShare()
        assert ds.get('') == {}

    def test_init_with_dict(self):
        initial = {'a': {'b': {'_value': 1}}}
        ds = DataShare(initial_data=initial)
        assert ds.get('a/b') == 1

    def test_init_with_list_of_tuples(self):
        initial = [('a/b', 1), ('c', 2)]
        ds = DataShare(initial_data=initial)
        assert ds.get('a/b') == 1
        assert ds.get('c') == 2
        assert ds.get('a', get_value=1) == {'b': {'_value': 1}}

class TestSet:
    def test_set_simple_value(self, ds):
        ds.set('a', 10)
        assert ds.get('a', get_value=1) == {'_value': 10}

    def test_set_nested_value(self, ds):
        ds.set('a/b/c', 'hello')
        assert ds.get('a/b/c') == 'hello'
        assert isinstance(ds.get('a/b'), MappingProxyType)

    def test_set_dual_value_node(self, ds):
        ds.set('a', 'parent_value')
        ds.set('a/b', 'child_value')
        raw_node = ds.get('a', get_value=1)
        assert raw_node == {'_value': 'parent_value', 'b': {'_value': 'child_value'}}

    def test_set_list_append_simple(self, ds):
        ds.set('items[]', 'first')
        ds.set('items[]', 'second')
        assert ds.get('items') == ('first', 'second')
        assert ds.get('items[0]') == 'first'
        assert ds.get('items[1]') == 'second'

    def test_set_list_append_complex(self, ds):
        ds.set('tasks[]/title', 'Buy milk')
        ds.set('tasks[]/title', 'Read book')
        ds.set('tasks[0]/priority', 'high')

        assert ds.get('tasks[0]/title') == 'Buy milk'
        assert ds.get('tasks[0]/priority') == 'high'
        assert ds.get('tasks[1]/title') == 'Read book'
        assert ds.get('tasks', get_value=0) == (
            {'title': 'Buy milk', 'priority': 'high'},
            {'title': 'Read book'}
        )

    def test_set_list_by_index(self, ds):
        ds.set('items[]', 'a')
        ds.set('items[]', 'b')
        ds.set('items[0]', 'A')
        ds.set('items[-1]', 'B')
        assert ds.get('items') == ('A', 'B')

    def test_batch_set_with_dict(self, ds):
        data = {'a/b': 1, 'c': 2}
        ds.set(data)
        assert ds.get('a/b') == 1
        assert ds.get('c') == 2

    def test_batch_set_with_list(self, ds):
        data = [('a/b', 1), ('c', 2)]
        ds.set(data)
        assert ds.get('a/b') == 1
        assert ds.get('c') == 2


class TestGet:
    @pytest.fixture
    def populated_ds(self):
        ds = DataShare()
        ds.set('simple', 'value')
        ds.set('node', 'node_val')
        ds.set('node/child', 'child_val')
        ds.set('items[]', 'item1')
        ds.set('items[]/name', 'item2')
        return ds

    def test_get_nonexistent(self, ds):
        assert ds.get('nonexistent') is None
        assert ds.get('nonexistent', default='fallback') == 'fallback'

    def test_get_value_mode_0_clean_default(self, populated_ds):
        # Simple value is unwrapped
        assert populated_ds.get('simple') == 'value'

        # Dual value node is partially unwrapped
        expected_node = {'_value': 'node_val', 'child': 'child_val'}
        assert populated_ds.get('node') == expected_node

        # List is unwrapped
        expected_list = ('item1', {'name': 'item2'})
        assert populated_ds.get('items') == expected_list

        # Entire data unwrapped
        entire_data = populated_ds.get('')
        assert entire_data['simple'] == 'value'
        assert entire_data['node'] == expected_node

    def test_get_value_mode_1_raw(self, populated_ds):
        # Simple value remains wrapped
        assert populated_ds.get('simple', get_value=1) == {'_value': 'value'}

        # Dual value node is returned as is
        expected_node = {'_value': 'node_val', 'child': {'_value': 'child_val'}}
        assert populated_ds.get('node', get_value=1) == expected_node

        # List items remain wrapped
        raw_list = populated_ds.get('items', get_value=1)
        assert raw_list[0] == {'_value': 'item1'}
        assert raw_list[1] == {'name': {'_value': 'item2'}}

    def test_get_value_mode_2_value_only(self, populated_ds):
        # Simple value's _value is extracted
        assert populated_ds.get('simple', get_value=2) == 'value'

        # Dual value node's _value is extracted, child is ignored
        assert populated_ds.get('node', get_value=2) == 'node_val'

        # A node without a direct _value returns default
        ds = DataShare()
        ds.set('a/b', 1)
        assert ds.get('a', get_value=2) is None
        assert ds.get('a', get_value=2, default='fallback') == 'fallback'

        # Non-existent node returns default
        assert populated_ds.get('nonexistent', get_value=2, default='fallback') == 'fallback'

    def test_get_invalid_get_value(self, populated_ds):
        with pytest.raises(ValueError):
            populated_ds.get('simple', get_value=3)
        with pytest.raises(ValueError):
            populated_ds.get('simple', get_value='a')


class TestGetk:
    def test_getk_simple(self, ds):
        ds.set('a/b', 1)
        ds.set('a/c', 2)
        result = ds.getk('a')
        assert isinstance(result, tuple)
        assert set(result) == {('a/b', 1), ('a/c', 2)}

    def test_getk_with_list(self, ds):
        ds.set('a/b[]', 'x')
        ds.set('a/b[]', 'y')
        result = ds.getk('a')
        assert set(result) == {('a/b[0]', 'x'), ('a/b[1]', 'y')}

    def test_getk_strip_prefix(self, ds):
        ds.set('config/user/name', 'test')
        ds.set('config/user/role', 'admin')
        result = ds.getk('config/user', strip_prefix=True)
        assert set(result) == {('name', 'test'), ('role', 'admin')}

    def test_getk_nonexistent(self, ds):
        assert ds.getk('nonexistent') == ()

    def test_getk_nonexistent_with_default(self, ds):
        result = ds.getk('nonexistent', default='fallback')
        assert result == (('nonexistent', 'fallback'),)


class TestSubscribe:
    def test_subscribe_and_notify_simple(self, ds):
        mock_callback = Mock()
        ds.subscribe('a', mock_callback)
        ds.set('a', 1)
        mock_callback.assert_called_once_with('a', None, 1)

    def test_subscribe_and_notify_nested_change(self, ds):
        mock_callback = Mock()
        ds.subscribe('a', mock_callback)
        ds.set('a/b', 1)
        mock_callback.assert_called_once_with('a/b', None, 1)

    def test_unsubscribe(self, ds):
        mock_callback = Mock()
        ds.subscribe('a', mock_callback)
        ds.unsubscribe('a', mock_callback)
        ds.set('a', 1)
        mock_callback.assert_not_called()

    def test_batch_update_notification(self, ds):
        mock_callback = Mock()
        ds.subscribe('a', mock_callback)
        with ds.batch_update():
            ds.set('a/b', 1)
            ds.set('a/c', 2)
            mock_callback.assert_not_called()

        # Notifications for batch updates are not guaranteed to be a single call
        # but are guaranteed to happen after the block.
        assert mock_callback.call_count == 2
        mock_callback.assert_any_call('a/b', None, 1)
        mock_callback.assert_any_call('a/c', None, 2)

