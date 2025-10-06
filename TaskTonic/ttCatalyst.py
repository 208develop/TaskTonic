from queue import Queue

from TaskTonic.ttTonic import ttTonic
import queue


class ttCatalyst(ttTonic):
    def __init__(self, context, name=None, fixed_id=None):
        self.catalyst_queue = Queue()
        super().__init__(context, name, fixed_id)
        self.sparkling = False
        self.tonics_sparkling = []

    def start_sparkling(self):
        if self.id == 0: # the main catalyst, sparkles in main
            self.sparkle()
        else:
            pass # todo, start thread

    def _ttss__startup_tonic(self, tonic):
        if tonic not in self.tonics_sparkling:
            self.tonics_sparkling.append(tonic)

    def _ttss__tonic_finished(self, tonic):
        if tonic in self.tonics_sparkling:
            self.tonics_sparkling.remove(tonic)

        if not self.tonics_sparkling:
            self.finish()

    def finished(self):
        super().finished()
        self.sparkling = False  # stop catalyst sparkle generation

    def sparkle(self):
        self.sparkling = True
        timeout = 5
        while self.sparkling:
            try:
                instance, sparkle, args, kwargs = self.catalyst_queue.get(timeout=timeout)
                instance._execute_sparkle(sparkle, *args, **kwargs)
            except queue.Empty:
                pass


