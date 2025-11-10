import pytest
import sys
import time
import enum
from unittest.mock import MagicMock, call


# --- Mocks for Dependencies ---
class MockDataShare:
    """Basic mock for DataShare used in formula."""

    def __init__(self, data=None):
        self._data = data or {}

    def get(self, key, default=None):
        # Basic key access, handles simple paths and empty key
        if not key:
            # Return a copy of the whole data for empty key
            return self._data.copy() if default is None else default
        parts = key.split('/')
        current = self._data
        try:
            for part in parts:
                if not part: continue
                if isinstance(current, list) and part.isdigit():
                    current = current[int(part)]
                elif isinstance(current, dict):
                    current = current[part]
                else:
                    return default
            # Return a copy if it's a collection to prevent modification by caller
            if isinstance(current, (dict, list)):
                return current.copy()
            return current
        except (KeyError, IndexError, TypeError):
            return default

    def set(self, key_or_dict, value=None):
        # Simplified set for testing structure
        if isinstance(key_or_dict, dict):
            self._data.update(key_or_dict)
        elif isinstance(key_or_dict, (list, tuple)):
            for k, v in key_or_dict:
                self._set_path(k, v)
        elif value is not None:
            self._set_path(key_or_dict, value)

    def _set_path(self, path, value):
        # Very basic path setting supporting list append '[]' and last '[-1]'
        parts = path.split('/')
        d = self._data
        for i, part in enumerate(parts):
            if not part: continue
            is_last = (i == len(parts) - 1)
            list_append = part.endswith('[]')
            list_last = part.startswith('[-1]')

            if list_append:
                key_part = part[:-2]
                if key_part not in d or not isinstance(d[key_part], list):
                    d[key_part] = []
                if is_last:
                    d[key_part].append(value)  # Append value directly if last part
                else:
                    # Append dict and continue traversal
                    d[key_part].append({})
                    d = d[key_part][-1]

            elif list_last:
                key_part = part[4:]  # If there's something after like /name
                if not d or not isinstance(d, list):
                    raise IndexError("Cannot access [-1] on non-list or empty list")
                if is_last and not key_part:  # Just [-1]
                    d[-1] = value  # Replace last item
                elif is_last and key_part:  # [-1]/name
                    d[-1][key_part] = value
                elif not is_last:
                    d = d[-1]  # Continue traversal into last item
                    if key_part:  # If path continues after [-1]/...
                        d = d.setdefault(key_part, {})


            elif is_last:
                d[part] = value
            else:
                d = d.setdefault(part, {})


class MockLedger:
    """Mock ttLedger for isolated testing."""
    _instance = None
    _singleton_init_done = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._singleton_init_done = False
        return cls._instance

    def __init__(self):
        if self._singleton_init_done: return
        self.reset()
        self._singleton_init_done = True

    def reset(self):
        """Resets the mock ledger state, including default formula."""
        self.records = []
        self.essences = []

        # Define mocks INSIDE reset to ensure they use the correct ttEssence base
        # This requires ttEssence to be defined before MockLedger, or handle imports carefully
        if 'ttEssence' in globals():  # Check if ttEssence is defined
            class MockScreenLoggerService(ttEssence):
                _tt_is_service = "screen"
                put_log = MagicMock()

                def __init__(self,
                             **kwargs): self.id = -1; self.name = "MockScreen"; self.my_record = {}; self._log_mode = ttLog.STEALTH; self.ledger = MockLedger()

                def _init_post_action(self): pass

                def _init_service(self, *args, **kwargs): pass

            class MockDummyLoggerService(ttEssence):
                _tt_is_service = "off"
                put_log = MagicMock()

                def __init__(self,
                             **kwargs): self.id = -1; self.name = "MockDummy"; self.my_record = {}; self._log_mode = ttLog.STEALTH; self.ledger = MockLedger()

                def _init_post_action(self): pass

                def _init_service(self, *args, **kwargs): pass

            # --- FORMULA INITIALIZATION ---
            self.formula = MockDataShare({
                'tasktonic/log/to': 'screen',
                'tasktonic/log/default': 'QUIET',
                'tasktonic/log/services': [
                    {'name': 'screen', 'service': MockScreenLoggerService, 'arguments': {}},
                    {'name': 'off', 'service': MockDummyLoggerService, 'arguments': {}},
                ]
            })
        else:
            # Fallback if ttEssence not yet defined (shouldn't happen with correct file structure)
            self.formula = MockDataShare({'tasktonic/log/to': 'screen', 'tasktonic/log/default': 'QUIET'})

        self.get_service_essence_calls = []
        self.update_record_calls = []
        self.register_calls = []
        self.unregister_calls = []
        self.get_essence_by_id_calls = []
        self._id_counter = -1

    def update_formula(self, formula_update, val=None):
        if self.formula is None:
            self.formula = MockDataShare()
        self.formula.set(formula_update, val)

    def register(self, essence_instance):
        self.register_calls.append(essence_instance)
        self._id_counter += 1
        new_id = self._id_counter
        while len(self.essences) <= new_id:
            self.essences.append(None)
            self.records.append(None)
        self.essences[new_id] = essence_instance
        # Store a copy of the record *as it is* during register
        self.records[new_id] = essence_instance.my_record.copy()
        return new_id

    def unregister(self, essence_id):
        self.unregister_calls.append(essence_id)
        if 0 <= essence_id < len(self.essences):
            if self.essences[essence_id]:
                self.essences[essence_id].id = -1
            self.essences[essence_id] = None
            self.records[essence_id] = None

    def get_essence_by_id(self, ess_id):
        self.get_essence_by_id_calls.append(ess_id)
        if isinstance(ess_id, int) and 0 <= ess_id < len(self.essences):
            return self.essences[ess_id]
        return None

    def get_service_essence(self, service_name):
        print(f"LEDGER: Finding service essence '{service_name}'...")
        self.get_service_essence_calls.append(service_name)
        for i, record in enumerate(self.records):
            if record and record.get('service') == service_name:
                if i < len(self.essences) and self.essences[i] is not None:
                    return self.essences[i]
        return None

    def get_essence_by_name(self, name):
        """Mock method to find essence by name using the stored record."""
        for i, record in enumerate(self.records):
            # Check if record exists and name matches
            if record and record.get('name') == name:
                # Check if essence still exists at that index
                if i < len(self.essences) and self.essences[i] is not None:
                    return self.essences[i]
        return None

    def get_id_by_name(self, name):
        """Mock method to find id by name using the stored record."""
        for i, record in enumerate(self.records):
            if record and record.get('name') == name:
                # Check if essence still exists (consistency check)
                if i < len(self.essences) and self.essences[i] is not None:
                    return i
        return -1

    def update_record(self, ess_id, data):
        """Mock update_record that updates the stored copy."""
        self.update_record_calls.append({'id': ess_id, 'data': data})
        if 0 <= ess_id < len(self.records) and self.records[ess_id] is not None:
            self.records[ess_id].update(data)


# Inject mock ledger
sys.modules['TaskTonic.ttLedger'] = MagicMock(ttLedger=MockLedger, RWLock=MagicMock())


# --- ttLog Enum ---
class ttLog(enum.IntEnum):
    STEALTH = enum.auto()
    OFF = enum.auto()
    QUIET = enum.auto()
    FULL = enum.auto()

    @classmethod
    def from_any(cls, value):
        if isinstance(value, cls): return value
        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                raise ValueError(f"'{value}' invalid name")
        if isinstance(value, int):
            try:
                return cls(value)
            except ValueError:
                raise ValueError(f"'{value}' invalid value")
        raise TypeError(f"Cannot convert {type(value)}")


# --- ttEssence Definition (Simplified for testing, with fixes) ---

class __ttEssenceMeta(type):
    def __call__(cls, *args, **kwargs):
        service_name = kwargs.pop('service', None)
        if service_name is None:
            service_name = getattr(cls, '_tt_is_service', None)
        is_service = service_name is not None

        if not is_service:
            instance = super().__call__(*args, **kwargs)
            # Check if _init_post_action exists before calling
            if hasattr(instance, '_init_post_action'):
                instance._init_post_action()
            return instance

        ledger = MockLedger()
        existing_instance = ledger.get_service_essence(service_name)
        # Inject name from class var ONLY if not passed in kwargs
        if 'name' not in kwargs and (name_from_class := getattr(cls, '_tt_is_service', None)):
            kwargs['name'] = name_from_class
        elif service_name and 'name' not in kwargs:  # Inject name from service kwarg if needed
            kwargs['name'] = service_name

        if existing_instance is None:
            instance = super().__call__(*args, **kwargs)
            ledger.update_record(instance.id, {'service': service_name})
            if hasattr(instance, '_init_post_action'):
                instance._init_post_action()
        else:
            instance = existing_instance

        if hasattr(instance, '_init_service'):
            instance._init_service(*args, **kwargs)

        return instance


class ttEssence(metaclass=__ttEssenceMeta):
    """Simplified ttEssence base class for testing."""

    def __init__(self, name=None, context=None, log_mode=None, **kwargs):
        self.ledger = MockLedger()
        self.my_record = {}  # Initialize BEFORE register
        self.context = context if isinstance(context, ttEssence) else self.ledger.get_essence_by_id(context) if (
                    isinstance(context, int) and context >= 0) else None
        self.bindings = []

        # --- Populate record BEFORE register ---
        # Get preliminary ID (will be overwritten by register)
        temp_id = self.ledger._id_counter + 1 if MockLedger._instance else 0
        prelim_name = name if isinstance(name, str) else f'{temp_id:02d}.{self.__class__.__name__}'

        self.my_record.update({
            # 'id' will be set by register
            'name': prelim_name,  # Use preliminary name for now
            'type': self.__class__.__name__,
            'context_id': self.context.id if self.context else -1,
        })
        # --- End record prep ---

        self.id = self.ledger.register(self)
        # --- Finalize Name AFTER getting ID ---
        self.name = name if isinstance(name, str) else f'{self.id:02d}.{self.__class__.__name__}'
        # Update record with final ID and Name
        self.my_record['id'] = self.id
        self.my_record['name'] = self.name
        # Update ledger's copy *after* name is final
        self.ledger.update_record(self.id, {'name': self.name, 'id': self.id})
        # --- End Name/ID Finalization ---

        print(f"  ttEssence __init__ running for '{self.name}' (ID: {self.id})")

        # --- Logging Setup ---
        self._logger = None
        self._log = None  # Initialize _log attribute

        # Determine initial log mode request, default to STEALTH if invalid
        try:
            initial_log_mode_request = ttLog.from_any(log_mode if log_mode is not None else ttLog.STEALTH)
        except (ValueError, TypeError):
            initial_log_mode_request = ttLog.STEALTH

        log_to = self.ledger.formula.get('tasktonic/log/to', None)

        if getattr(self, '_tt_force_stealth_logging', False) or \
                log_to is None or \
                initial_log_mode_request == ttLog.STEALTH:

            self.set_log_mode(ttLog.STEALTH)
            # Ensure _log_mode is also set correctly even if logger isn't created
            self._log_mode = ttLog.STEALTH
        else:
            services = self.ledger.formula.get('tasktonic/log/services', [])
            ServiceClass = None
            s_kwargs = {}
            for service_def in services:
                if service_def.get('name') == log_to:
                    s_kwargs = service_def.get('arguments', {})
                    ServiceClass = service_def.get('service')
                    break

            if ServiceClass:
                # Add context to arguments for service init
                s_kwargs['context'] = self
                self._logger = ServiceClass(**s_kwargs)
            else:
                # Raise error only if no valid service class was found
                raise RuntimeError(f'Log to service "{log_to}" not found in formula/services.')

            # Determine final log mode
            if log_mode is None:  # Inherit only if not explicitly passed
                log_mode_to_set = self.context._log_mode if self.context and hasattr(self.context, '_log_mode') else \
                    self.ledger.formula.get('tasktonic/log/default', ttLog.STEALTH)
            else:
                log_mode_to_set = initial_log_mode_request  # Use explicit value

            final_log_mode = ttLog.from_any(log_mode_to_set)
            self.set_log_mode(final_log_mode)
            # _log_mode is set inside set_log_mode

        # Call log methods only if 'log' attribute is properly set
        if hasattr(self, 'log') and callable(self.log):
            self.log(system_flags={'created': True})
            self.log(system_flags=self.my_record)

    def _init_post_action(self):
        """Post-init hook."""
        self.my_record.update({
            'name': self.name,  # Ensure name is final
            'context_id': self.context.id if self.context else -1,
        })
        self.ledger.update_record(self.id, self.my_record.copy())  # Update ledger record
        if hasattr(self, 'log') and callable(self.log):
            self.log(system_flags=self.my_record, close_log=True)

    def _init_service(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'TaskTonic {getattr(self, "name", "Unnamed")} in context {getattr(getattr(self, "context", None), "name", -1)}'

    def __repr__(self):
        return self.__str__()

    def __deepcopy__(self, memodict={}):
        return self

    def bind(self, essence, *args, **kwargs):
        if not issubclass(essence, ttEssence): raise TypeError('Expected ttEssence subclass')
        # Ensure context=self is passed correctly
        kwargs['context'] = self
        e = essence(*args, **kwargs)
        if hasattr(e, 'id'):  # Check if child essence initialized correctly
            self.bindings.append(e.id)
        return e

    def unbind(self, ess_id):
        if ess_id in self.bindings: self.bindings.remove(ess_id)

    def binding_finished(self, ess_id):
        self.unbind(ess_id)

    def finish(self):
        # Finish children before finishing self
        # Iterate over a copy because binding_finished modifies self.bindings
        for ess_id in list(self.bindings):
            child = self.ledger.get_essence_by_id(ess_id)
            if child:
                child.finish()
        # If bindings were cleared by children finishing, finish self now
        if not self.bindings:
            self.finished()

    def finished(self):
        """Final cleanup."""
        # Use getattr for safety in case log method removed
        log_method = getattr(self, 'log', None)
        if callable(log_method):
            log_method(system_flags={'finished': True})

        # Notify context only if context exists and method is callable
        if self.context and hasattr(self.context, 'binding_finished') and callable(self.context.binding_finished):
            self.context.binding_finished(self.id)

        # Unregister from ledger
        self.ledger.unregister(self.id)
        # Don't reset id to -1 immediately, might be needed if logs are processed later
        # Mark as finished internally? Maybe add a self._is_finished flag

    # --- Log Methods ---
    # Define actual methods, don't mock them here
    def _log_full(self, line=None, flags=None, system_flags=None, close_log=False):
        if not hasattr(self, '_log') or self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault('sys', {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            self._log_push(self._log)
            self._log = None

    def _log_quiet(self, line=None, flags=None, system_flags=None, close_log=False):
        if not hasattr(self, '_log') or self._log is None: self._log = {'id': self.id, 'start@': time.time(), 'log': []}
        if system_flags: self._log.setdefault('sys', {}).update(system_flags)
        if flags: self._log.update(flags)
        if line: self._log['log'].append(line)
        if close_log:
            if self._log.get('log') or self._log.get('sys'):
                self._log_push(self._log)
            self._log = None

    def _log_off(self, line=None, flags=None, system_flags=None, close_log=False):
        if system_flags:
            if not hasattr(self, '_log') or self._log is None: self._log = {'id': self.id, 'start@': time.time()}
            self._log.setdefault('sys', {}).update(system_flags)
        if close_log and hasattr(self, '_log') and self._log:
            self._log_push(self._log)
            self._log = None

    def _log_stealth(self, line=None, flags=None, system_flags=None, close_log=False):
        pass

    def set_log_mode(self, log_mode):
        """Sets the active log handler method."""
        try:
            log_mode = ttLog.from_any(log_mode)
        except (ValueError, TypeError):
            print(f"Warning: Invalid log_mode '{log_mode}', defaulting to STEALTH.")
            log_mode = ttLog.STEALTH

        handler_map = {
            ttLog.STEALTH: self._log_stealth,
            ttLog.OFF: self._log_off,
            ttLog.QUIET: self._log_quiet,
            ttLog.FULL: self._log_full,
        }
        self.log = handler_map.get(log_mode)
        if self.log is None:
            raise NotImplementedError(f"Log mode {log_mode} not implemented in handler_map")
        # Store the mode that was successfully set
        self._log_mode = log_mode

    def _log_push(self, log):
        """Pushes log if logger exists."""
        if hasattr(self, '_logger') and self._logger:
            self._logger.put_log(log)


# Define mocks needed by MockLedger.reset globally or ensure import order
class MockScreenLoggerService(ttEssence):
    _tt_is_service = "screen"
    put_log = MagicMock()

    def __init__(self,
                 **kwargs): self.id = -1; self.name = "MockScreen"; self.my_record = {}; self._log_mode = ttLog.STEALTH; self.ledger = MockLedger()

    def _init_post_action(self): pass

    def _init_service(self, *args, **kwargs): pass


class MockDummyLoggerService(ttEssence):
    _tt_is_service = "off"
    put_log = MagicMock()

    def __init__(self,
                 **kwargs): self.id = -1; self.name = "MockDummy"; self.my_record = {}; self._log_mode = ttLog.STEALTH; self.ledger = MockLedger()

    def _init_post_action(self): pass

    def _init_service(self, *args, **kwargs): pass


# --- Test Helper ---
def reset_ledger_singleton():
    """Resets the mock ledger's state."""
    if MockLedger._instance:
        MockLedger._instance.reset()


# --- Fixtures ---
@pytest.fixture(autouse=True)
def clean_ledger():
    """Ensures a clean ledger before each test."""
    reset_ledger_singleton()
    yield
    reset_ledger_singleton()


@pytest.fixture
def ledger():
    """Provides the ledger singleton instance."""
    return MockLedger()


# --- Test Classes ---

class TestStandardEssence:
    """Tests for non-service ttEssence behavior."""

    def test_basic_creation(self, ledger):
        e = ttEssence(name="Test1")
        assert isinstance(e, ttEssence)
        assert e.id == 0
        assert e.name == "Test1"
        assert e.context is None
        assert ledger.essences[0] is e
        assert ledger.records[0].get('name') == "Test1"
        assert ledger.records[0].get('type') == 'ttEssence'
        assert 'service' not in ledger.records[0]

    def test_creation_with_context(self, ledger):
        parent = ttEssence(name="Parent")
        child = ttEssence(name="Child", context=parent)
        assert child.id == 1
        assert child.context is parent
        assert ledger.records[child.id].get('context_id') == parent.id

    def test_default_name_generation(self, ledger):
        e = ttEssence()
        assert e.id == 0
        assert e.name == "00.ttEssence"
        assert ledger.records[0].get('name') == "00.ttEssence"

    def test_init_post_action_updates_record(self, ledger):
        e = ttEssence(name="PostActionTest")
        record_after_post_action = ledger.records[e.id]
        assert record_after_post_action.get('name') == "PostActionTest"
        assert record_after_post_action.get('context_id') == -1

    def test_bind_creates_child(self, ledger):
        parent = ttEssence(name="ParentBind")
        assert len(parent.bindings) == 0

        class ChildEssence(ttEssence): pass

        child = parent.bind(ChildEssence, name="BoundChild")
        assert isinstance(child, ChildEssence)
        assert child.name == "BoundChild"
        assert child.context is parent
        assert len(parent.bindings) == 1
        assert parent.bindings[0] == child.id
        assert ledger.get_essence_by_id(child.id) is child
        assert ledger.records[child.id].get('context_id') == parent.id

    def test_finish_unregisters_and_notifies_parent(self, ledger):
        parent = ttEssence(name="ParentFinish")
        child = parent.bind(ttEssence, name="ChildFinish")
        child_id = child.id
        assert ledger.get_essence_by_id(child_id) is child
        assert child_id in parent.bindings
        parent.binding_finished = MagicMock()  # Mock the callback
        child.finish()
        # assert child.id == -1 # Check if necessary
        assert ledger.get_essence_by_id(child_id) is None
        assert ledger.records[child_id] is None
        parent.binding_finished.assert_called_once_with(child_id)


class TestServiceEssence:
    """Tests for service/singleton ttEssence behavior."""

    # --- Test Service Classes (Nested) ---
    class MyService(ttEssence):
        _tt_is_service = "MyServiceName"
        init_run_count = 0
        post_action_run_count = 0

        def __init__(self, srv_param=None, **kwargs):
            cls = self.__class__
            cls.init_run_count += 1
            self.srv_param = srv_param
            super().__init__(**kwargs)

        def _init_post_action(self):
            cls = self.__class__
            cls.post_action_run_count += 1
            super()._init_post_action()

    class MyOtherService(ttEssence):
        _tt_is_service = "OtherService"

    class ServiceWithHook(ttEssence):
        _tt_is_service = "HookService"
        access_log = []

        def __init__(self, **kwargs):
            cls = self.__class__
            cls.access_log = []
            super().__init__(**kwargs)

        def _init_service(self, context=None, ctxt_param=None, **kwargs):
            entry = {'context_id': context.id if context else None, 'param': ctxt_param}
            cls = self.__class__
            cls.access_log.append(entry)

    # --- Tests ---
    def test_service_is_singleton_via_class_var(self, ledger):
        s1 = self.MyService(srv_param=1)
        s2 = self.MyService(srv_param=2)
        assert s1 is s2
        assert s1.name == "MyServiceName"
        assert s1.srv_param == 1
        actual_essences = [e for e in ledger.essences if isinstance(e, self.MyService)]
        assert len(actual_essences) == 1
        assert ledger.get_service_essence_calls.count("MyServiceName") >= 2

    def test_service_is_singleton_via_kwarg(self, ledger):
        class KwargService(ttEssence): pass

        s1 = KwargService(service="KwargServiceName")
        s2 = KwargService(service="KwargServiceName")
        assert s1 is s2
        assert s1.name == "KwargServiceName"
        actual_essences = [e for e in ledger.essences if isinstance(e, KwargService)]
        assert len(actual_essences) == 1
        assert ledger.get_service_essence_calls.count("KwargServiceName") >= 2

    def test_init_and_post_action_run_only_once(self, ledger):
        self.MyService.init_run_count = 0
        self.MyService.post_action_run_count = 0
        s1 = self.MyService()
        assert self.MyService.init_run_count == 1
        assert self.MyService.post_action_run_count == 1
        s2 = self.MyService()
        assert s1 is s2
        assert self.MyService.init_run_count == 1
        assert self.MyService.post_action_run_count == 1

    def test_init_service_runs_every_time_with_args(self, ledger):
        ctx1 = ttEssence(name="Ctx1")
        ctx2 = ttEssence(name="Ctx2")
        self.ServiceWithHook.access_log = []
        s1 = self.ServiceWithHook(context=ctx1, ctxt_param="First")
        assert len(self.ServiceWithHook.access_log) == 1
        assert self.ServiceWithHook.access_log[0] == {'context_id': ctx1.id, 'param': 'First'}
        s2 = self.ServiceWithHook(context=ctx2, ctxt_param="Second")
        assert s1 is s2
        assert len(self.ServiceWithHook.access_log) == 2
        assert self.ServiceWithHook.access_log[1] == {'context_id': ctx2.id, 'param': 'Second'}

    def test_service_is_marked_in_ledger(self, ledger):
        s1 = self.MyService()
        found_call = False
        for call_info in ledger.update_record_calls:
            # Check data *after* name injection by metaclass might update kwargs
            if call_info['id'] == s1.id and call_info['data'].get('service') == 'MyServiceName':
                found_call = True
                break
        assert found_call, "update_record call to mark service not found or incorrect"
        assert ledger.records[s1.id].get('service') == 'MyServiceName'

    def test_get_service_essence_works(self, ledger):
        s1 = self.MyService()
        found_service = ledger.get_service_essence("MyServiceName")
        assert found_service is s1
        not_found = ledger.get_service_essence("NoSuchService")
        assert not_found is None


class TestEssenceLogging:
    """Tests focused on the logging setup in ttEssence."""

    # Fixture needed to ensure mocks are available
    @pytest.fixture
    def ledger(self):
        """Provides the ledger singleton instance."""
        return MockLedger()

    def test_default_logging_uses_formula_to(self, ledger):
        ledger.formula.set('tasktonic/log/to', 'screen')
        MockScreenLoggerService.put_log.reset_mock()
        e = ttEssence()
        assert isinstance(e._logger, MockScreenLoggerService)

    def test_stealth_mode_sets_correct_handler(self, ledger):
        e = ttEssence(log_mode=ttLog.STEALTH)
        # Check the actual method object assigned
        assert e.log == e._log_stealth
        assert e._log_mode == ttLog.STEALTH
        assert e._logger is None

    def test_force_stealth_overrides_formula(self, ledger):
        ledger.formula.set('tasktonic/log/to', 'screen')

        class StealthForcedEssence(ttEssence):
            _tt_force_stealth_logging = True

        e = StealthForcedEssence()
        assert e.log == e._log_stealth
        assert e._log_mode == ttLog.STEALTH
        assert e._logger is None

    def test_log_mode_from_context(self, ledger):
        parent = ttEssence(name="LogParent", log_mode=ttLog.FULL)
        assert parent._log_mode == ttLog.FULL  # Verify parent setting worked
        child = ttEssence(name="LogChild", context=parent)
        assert child._log_mode == ttLog.FULL
        assert child.log == child._log_full  # Check method assignment

    def test_set_log_mode_changes_handler(self, ledger):
        e = ttEssence(log_mode=ttLog.QUIET)
        assert e.log == e._log_quiet
        e.set_log_mode(ttLog.FULL)
        assert e.log == e._log_full
        e.set_log_mode("OFF")
        assert e.log == e._log_off
