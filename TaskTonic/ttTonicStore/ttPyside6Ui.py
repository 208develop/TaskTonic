# ttPyside6Ui.py
import sys, queue, time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QEvent, QCoreApplication, QTimer

from ..ttCatalyst import ttCatalyst
from .ttPysideWidget import ttPysideMeta


class SparkleEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, payload):
        super().__init__(SparkleEvent.EVENT_TYPE)
        self.payload = payload


class PysideQueue(queue.Queue):
    def __init__(self, catalyst_ui, maxsize=0):
        super().__init__(maxsize)
        self.catalyst_ui = catalyst_ui

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        event = SparkleEvent(item)
        QCoreApplication.postEvent(self.catalyst_ui, event)


class ttPyside6Ui(ttCatalyst, QObject, metaclass=ttPysideMeta):
    def __init__(self, name=None, app_args=None):
        QObject.__init__(self)
        if QApplication.instance():
            self.app = QApplication.instance()
        else:
            self.app = QApplication(app_args or sys.argv)

        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.setSingleShot(True)
        self._heartbeat_timer.timeout.connect(self._on_qt_timer_timeout)
        ttCatalyst.__init__(self, name=name)

    def new_catalyst_queue(self):
        return PysideQueue(catalyst_ui=self)

    def start_sparkling(self):
        if self.id != 0:
            raise RuntimeError(f'{self.__class__.__name__} must be a main catalyst (id==0)')

        self._schedule_next_timer()
        print("[ttPyside6Ui] Starting Qt Event Loop...")
        self.app.exec()
        super().sparkle()  # finish last TaskTonic calls (if any) after ui ended

    def customEvent(self, event):
        if event.type() == SparkleEvent.EVENT_TYPE:
            try:
                item = self.catalyst_queue.get_nowait()
                instance, method, args, kwargs = item

                if hasattr(instance, '_execute_sparkle'):
                    # FIX: Unpack args correctly
                    instance._execute_sparkle(method, *args, **kwargs)

                self._process_extra_sparkles()

            except queue.Empty:
                pass
            except Exception as e:
                print(f"[ttPyside6Ui] Error: {e}")
            finally:
                self._schedule_next_timer()
            event.accept()
        else:
            super().customEvent(event)

    def _process_extra_sparkles(self):
        while self.extra_sparkles:
            payload = self.extra_sparkles.pop(0)
            instance, method, args, kwargs = payload
            if hasattr(instance, '_execute_sparkle'):
                instance._execute_sparkle(method, *args, **kwargs)

    def _schedule_next_timer(self):
        reference = time.time()
        next_timer_expire = 0.0
        while next_timer_expire == 0.0:
            next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60

        self._heartbeat_timer.stop()
        if next_timer_expire > 0.0:
            ms = max(0, int(next_timer_expire * 1000))
            self._heartbeat_timer.start(ms)

    def _on_qt_timer_timeout(self):
        self._schedule_next_timer()