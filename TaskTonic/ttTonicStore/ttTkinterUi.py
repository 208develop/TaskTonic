import os
import sys

# Re-route the Tcl/Tk libraries to the base Python installation
base_prefix = getattr(sys, "base_prefix", sys.prefix)
os.environ['TCL_LIBRARY'] = os.path.join(base_prefix, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(base_prefix, 'tcl', 'tk8.6')

import tkinter as tk
import queue
import time
from .. import ttSparkleStack
from ..ttCatalyst import ttCatalyst


class TkinterQueue(queue.SimpleQueue):
    def __init__(self, catalyst_ui):
        super().__init__()
        self.catalyst_ui = catalyst_ui
        self.root = catalyst_ui.root

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        # Genereer een thread-safe virtueel event om de mainloop te triggeren
        self.root.event_generate("<<SparkleEvent>>", when="tail")


class ttTkinterUi(ttCatalyst):
    def __init__(self, name=None):
        self.root = tk.Tk()
        super().__init__(name=name)

        # Koppel het virtuele event aan de custom Sparkle verwerker
        self.root.bind("<<SparkleEvent>>", self.customEvent)
        self._timer_id = None

    def new_catalyst_queue(self):
        return TkinterQueue(catalyst_ui=self)

    def start_sparkling(self):
        if self.id != 0:
            raise RuntimeError(f'{self.__class__.__name__} must be a main catalyst (id==0)')

        self._schedule_next_timer()
        ttSparkleStack().catalyst = self

        self.root.mainloop()
        super().sparkle()  # Verwerk overgebleven TaskTonic calls als het scherm sluit

    def customEvent(self, event=None):
        sp_stck = ttSparkleStack()
        try:
            item = self.catalyst_queue.get_nowait()
            instance, sparkle, args, kwargs, sp_stck.source = item
            sp_name = sparkle.__name__

            sp_stck.push(instance, sp_name)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

            sp_stck.source = (instance, sp_name)
            self._process_extra_sparkles()

        except queue.Empty:
            pass
        except Exception as e:
            print(f"[ttTkinterUi] Error: {e}")
        finally:
            self._schedule_next_timer()

    def _process_extra_sparkles(self):
        sp_stck = ttSparkleStack()
        while self.extra_sparkles:
            payload = self.extra_sparkles.pop(0)
            instance, sparkle, args, kwargs = payload
            sp_stck.push(instance, sparkle.__name__)
            instance._execute_sparkle(sparkle, *args, **kwargs)
            sp_stck.pop()

    def _schedule_next_timer(self):
        reference = time.time()
        next_timer_expire = 0.0
        while next_timer_expire == 0.0:
            next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0

        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

        if next_timer_expire > 0.0:
            ms = max(0, int(next_timer_expire * 1000))
            if ms > 60000: ms = 60000  # Max 1 minuut wachten als er geen timers zijn
            self._timer_id = self.root.after(ms, self._on_tk_timer_timeout)

    def _on_tk_timer_timeout(self):
        self._schedule_next_timer()

        # TaskTonic/ttTonicStore/ttTkinterUi.py

    def ttse__on_finished(self):
        # Als de Catalyst écht klaar is met z'n queues,
        # sluiten we pas het Tkinter fundament af.
        if self.root:
            try:
                self.root.destroy()
            except tk.TclError:
                pass
        super().ttse__on_finished()