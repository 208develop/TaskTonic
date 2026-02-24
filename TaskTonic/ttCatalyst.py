from .ttSparkleStack import ttSparkleStack
from .ttTonic import ttTonic
import queue, threading, time


class ttCatalyst(ttTonic):
    """
    The central executor in the TaskTonic framework, it makes the tonic sparkle. The catalyst itself behaves as
    and can be used as a tonic.

    Only the main catalyst (id==0) is executed from main (from the formula class). It is possible to let all the
    tonic sparkle by one catalyst. However, if a catalyst is created in the tonic chaine, it is launched in its
    own thread.

    A Catalyst is a special type of Tonic that manages the main execution queue
    (the 'catalyst_queue') and controls the lifecycle of other Tonics. It pulls
    'sparkles' from the queue and executes them for the correct tonics
    """

    def __init__(self, name=None, log_mode=None, dont_start_yet=False):
        """
        Initializes the Catalyst and its master queue.

        :param name: An optional name for this Catalyst.
        :param fixed_id: An optional fixed ID for this Catalyst.
        """
        # Initialize the base ttTonic functionality. The Catalyst is also a Tonic.
        super().__init__(name=name, log_mode=log_mode)
        # The master queue that all Tonics managed by this Catalyst will use.
        self.catalyst_queue = self.new_catalyst_queue()
        self.extra_sparkles = []
        self.catalyst = self  # Tonics have to have a catalyst
        # internals
        self.sparkling = False
        self.tonics_sparkling = []
        self.thread_id = -1
        self.timers = []



        if self.id > 0 and not dont_start_yet: # id 0 (main catalyst) will be started in formula
            self.start_sparkling()

    def new_catalyst_queue(self):
        return queue.SimpleQueue()

    def start_sparkling(self):
        """
        Starts the main execution loop of the Catalyst.

        The main Catalyst (id=0) runs its loop in the main thread, blocking
        execution. Other Catalysts will start their loop in a separate thread.
        """
        if self.sparkling: return

        if self.id == 0:
            # If this is the main Catalyst, run its loop in the current thread.
            self.sparkle()
        else:
            # For other Catalysts, spawn a new background thread for the loop or wait when application is starting up
            if self.ledger.formula.get('tasktonic/project/status', 'starting') == 'starting':
                return  # dont startup jet, will be done just before main_catalyst starts sparkling
            threading.Thread(target=self.sparkle).start()

    def sparkle(self):
        """
        The main execution loop of the Catalyst.

        This method continuously pulls work orders (instance, sparkle, args, kwargs)
        from the queue and executes them. It runs until the `self.sparkling` flag
        is set to False.
        """
        self.thread_id = threading.get_ident()
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self
        self.sparkling = True

        # The loop continues as long as the Catalyst is in a sparkling state.
        while self.sparkling:
            reference = time.time()
            next_timer_expire = 0.0
            while next_timer_expire == 0.0:
                next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60
            try:
                instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get(timeout=next_timer_expire)
                sp_name = sparkle.__name__
                sp_stck.push(instance, sp_name)
                instance._execute_sparkle(sparkle, *args, **kwargs)
                sp_stck.pop()

                sp_stck.source = (instance, sp_name)
                while self.extra_sparkles:
                    instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                    sp_stck.push(instance, sparkle.__name__)
                    instance._execute_sparkle(sparkle, *args, **kwargs)
                    sp_stck.pop()
            except queue.Empty: pass

    def _execute_extra_sparkle(self, instance, sparkle, *args, **kwargs):
        if hasattr(sparkle, '__func__'): sparkle = sparkle.__func__ # make an unbound method (without self)
        self.extra_sparkles.append((instance, sparkle, args, kwargs))

    def _ttss__add_tonic_to_catalyst(self, tonic_id):
        """
        A system-level sparkle called by a Tonic during its initialization
        to register itself with the Catalyst.

        :param tonic_id: The Tonic id that is starting up.
        """
        if tonic_id not in self.tonics_sparkling:
            self.tonics_sparkling.append(tonic_id)

    def _ttss__remove_tonic_from_catalyst(self, tonic_id):
        """
        A system-level sparkle called by a Tonic when it has completed its
        lifecycle and is shutting down.

        If this is the last active Tonic, the Catalyst will initiate its own
        shutdown sequence.

        :param tonic_id: The Tonic instance that has finished.
        """
        if tonic_id in self.tonics_sparkling:
            self.tonics_sparkling.remove(tonic_id)
        self.log(f"Tonic {tonic_id} has been removed from Catalyst. (left {self.tonics_sparkling})")

        # If there are no more active tonics, or active tonics used by catalyst, the catalyst's job is done.
        infusion_ids = {i.id for i in self.infusions}
        if set(self.tonics_sparkling).issubset(infusion_ids):
            self.finish()

    def _ttss__main_catalyst_finished(self):
        # Default: Stop when main catalyst is finished. You can override this method for other behavior
        self.log('Finish catalyst')
        self.finish()

    def _ttss__on_completion(self):
        super()._ttss__on_completion()
        # Setting this flag to False will terminate the sparkle loop.
        self.sparkling = False
