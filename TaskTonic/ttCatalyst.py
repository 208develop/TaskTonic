from TaskTonic.ttTonic import ttTonic
import queue
import threading


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

    def __init__(self, context, name=None, fixed_id=None):
        """
        Initializes the Catalyst and its master queue.

        :param context: The context in which this Catalyst operates.
                        For the main Catalyst, this could be a top-level object.
        :param name: An optional name for this Catalyst.
        :param fixed_id: An optional fixed ID for this Catalyst.
        """
        # The master queue that all Tonics managed by this Catalyst will use.
        self.catalyst_queue = queue.Queue()
        self.catalyst = self  # Tonics have to have a catalyst
        # internals
        self.sparkling = False
        self.tonics_sparkling = []
        self.thread_id = -1

        # Initialize the base ttTonic functionality. The Catalyst is also a Tonic.
        super().__init__(context, name, fixed_id)



    def start_sparkling(self):
        """
        Starts the main execution loop of the Catalyst.

        The main Catalyst (id=0) runs its loop in the main thread, blocking
        execution. Other Catalysts will start their loop in a separate thread.
        """
        if self.id == 0:
            # If this is the main Catalyst, run its loop in the current thread.
            self.sparkle()
        else:
            # For other Catalysts, spawn a new background thread for the loop.
            # todo, TESTING of threaded mode is required.
            threading.Thread(target=self.sparkle).start()

    def sparkle(self):
        """
        The main execution loop of the Catalyst.

        This method continuously pulls work orders (instance, sparkle, args, kwargs)
        from the queue and executes them. It runs until the `self.sparkling` flag
        is set to False.
        """
        self.thread_id = threading.get_ident()
        self.sparkling = True
        timeout = 5  # seconds

        # The loop continues as long as the Catalyst is in a sparkling state.
        while self.sparkling:
            try:
                # Wait for a work order to appear on the queue.
                # A timeout is used to prevent blocking forever, allowing the
                # loop to periodically check the `self.sparkling` flag.
                instance, sparkle, args, kwargs = self.catalyst_queue.get(timeout=timeout)

                # Call the central executor on the target tonic instance.
                instance._execute_sparkle(sparkle, *args, **kwargs)
            except queue.Empty:
                # If the queue is empty for the duration of the timeout,
                # do nothing and let the loop continue. This is normal.
                pass

    def _ttss__startup_tonic(self, tonic_id):
        """
        A system-level sparkle called by a Tonic during its initialization
        to register itself with the Catalyst.

        :param tonic_id: The Tonic id that is starting up.
        """
        if tonic_id not in self.tonics_sparkling:
            self.tonics_sparkling.append(tonic_id)

    def _ttss__tonic_finished(self, tonic_id):
        """
        A system-level sparkle called by a Tonic when it has completed its
        lifecycle and is shutting down.

        If this is the last active Tonic, the Catalyst will initiate its own
        shutdown sequence.

        :param tonic_id: The Tonic instance that has finished.
        """
        if tonic_id in self.tonics_sparkling:
            self.tonics_sparkling.remove(tonic_id)

        # If there are no more active tonics, the catalyst's job is done.
        if not self.tonics_sparkling:
            self.finish()

    def finished(self):
        """
        Overrides the base method to stop the Catalyst's execution loop
        after the standard shutdown procedure is complete.
        """
        super().finished()
        # Setting this flag to False will cause the `sparkle` loop to terminate.
        self.sparkling = False

