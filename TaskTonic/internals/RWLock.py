"""
Tool lib for private classes
"""
import threading


class RWLock:
    """
    Read/Write lock for accessing admin data with version indicator.
    You can read data, until a (or more) writing requests. Then writing is allowed just after all read operations are
    finished. After the last write operation completes, the lock is released and reading is allowed again.
    Every write will increase self.version checking on version will tell you if your data is old. Version wraps to
    zero after 2^31−1 = 2.147.483.647 operations, so use if version != stored_version!!
    """

    # noinspection PyProtectedMember
    class ReadAccessContext:
        def __init__(self, rw_lock_instance):
            self._rw_lock = rw_lock_instance

        def __enter__(self):
            self._rw_lock._acquire_read()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._rw_lock._release_read()
            return False

    # noinspection PyProtectedMember
    class WriteAccessContext:
        def __init__(self, rw_lock_instance):
            self._rw_lock = rw_lock_instance

        def __enter__(self):
            self._rw_lock._acquire_write()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._rw_lock._release_write()
            return False

    def __init__(self):
        self.version = 0
        self._readers_active = 0
        self._writers_waiting = 0
        self._writing = False
        self._lock = threading.Lock()
        self._can_read = threading.Condition(self._lock)
        self._can_write = threading.Condition(self._lock)

    def read_access(self):
        return self.ReadAccessContext(self)

    def write_access(self):
        return self.WriteAccessContext(self)

    def _acquire_read(self):
        with self._lock:
            while self._writing or self._writers_waiting:
                self._can_read.wait()
            self._readers_active += 1

    def _release_read(self):
        with self._lock:
            self._readers_active -= 1
            if not self._readers_active and self._writers_waiting:
                self._can_write.notify_all()

    def _acquire_write(self):
        with self._lock:
            self._writers_waiting += 1
            while self._readers_active > 0 or self._writing:
                self._can_write.wait()
            self._writers_waiting -= 1
            self._writing = True
            self.version = (self.version + 1) & 0b0111_1111_1111_1111_1111_1111_1111_1111

    def _release_write(self):
        with self._lock:
            self._writing = False
            if self._writers_waiting:
                self._can_write.notify_all()
            else:
                self._can_read.notify_all()
