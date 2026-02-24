from . import ttLiquid, ttTonic
from .internals.RWLock import RWLock
from .internals.Store import Store

class ttLedger:
    """A thread-safe singleton class that serves as the central registry for all ttEssence instances.

    The Ledger is the authoritative source of truth for the state of the entire
    system. It assigns unique IDs, stores records of all active essences, and
    provides methods to look up essences by ID or name.
    """
    _lock = RWLock()
    _instance = None
    _singleton_init_done = False

    class TonicReservation(object):
        def __init__(self, tid, name):
            self.id = tid
            self.name = name

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock.write_access():
                if cls._instance is None:
                    cls._instance = super().__new__(cls, *args, **kwargs)
                    cls._singleton_init_done = False
        return cls._instance

    def __init__(self):
        if self._singleton_init_done: return
        with self._lock.write_access():
            if self._singleton_init_done: return
            self.tonics = [] # direct acces to liquid instance by id
            self.tonic_by_name = {}
            self.tonic_by_service = {}
            self.formula = Store()
            # init thread data, a data structure depending on active thread.
            self._singleton_init_done = True

    def update_formula(self, formula, val=None):
        """Updates the application's formula

        :param formula: The application definition object, typically a DataShare
                        instance containing configuration.
        :type formula: str, Collection[Tuple[str, Any]] or Dict[str, Any]]
        :param val: used if formula is a string to create a key, val pair
        :type val: any, optional
        """
        self.formula.set(formula, val)

    def make_reservation(self, service_name=None):
        with self._lock.write_access():
            try:
                tid = self.tonics.index(None)
                self.tonics[tid] = self.TonicReservation(tid, None)
            except ValueError:
                tid = len(self.tonics)
                self.tonics.append(self.TonicReservation(tid, None))

            if service_name is not None:
                self.tonic_by_name[service_name] = self.TonicReservation(tid, service_name)
        return tid

    def check_reservation(self, reservation, raise_on_err=False):
        if isinstance(reservation, str):
            reservation = self.tonic_by_name.get(reservation, None)
            if reservation is not None and isinstance(reservation, self.TonicReservation):
                return reservation.id
        elif isinstance(reservation, int) and reservation >= 0:
            if 0 <= reservation < len(self.tonics) \
            and isinstance(self.tonics[reservation], self.TonicReservation):
                return reservation

        if raise_on_err: raise RuntimeError(f'ID "{reservation}" is not a reservation')
        return None

    def register(self, essence, reservation=None):
        """Registers a ttEssence instance and assigns it a unique ID.

        :param essence: The ttEssence instance to be registered.
        :type essence: ttEssence

        :raises TypeError: If `essence` is not a ttEssence instance
        :return: The unique integer ID assigned to the essence.
        :rtype: int
        """
        from TaskTonic.ttLiquid import ttLiquid
        if not isinstance(essence, ttLiquid):
            raise TypeError('essence must be of type ttEssence')

        if reservation is not None:
            ess_id = self.check_reservation(reservation, raise_on_err=True)
            self.tonics[ess_id] = essence
            self.tonic_by_name[essence.name] = essence

        else: # no reservation, find or create space in list
            with self._lock.write_access():
                try:
                    ess_id = self.tonics.index(None)
                    self.tonics[ess_id] = essence
                    self.tonic_by_name[essence.name] = essence
                except ValueError:
                    ess_id = len(self.tonics)
                    self.tonics.append(essence)
                    self.tonic_by_name[essence.name] = essence
        return ess_id

    def unregister(self, liquid):
        """Unregisters a ttEssence instance from the ledger.

        (Note: This method is not yet implemented).

        :param liquid: The ttEssence instance to unregister.
        :type liquid: ttEssence
        """
        from TaskTonic import ttLiquid
        if isinstance(liquid, (ttLiquid, self.TonicReservation)):
            pass
        elif isinstance(liquid, int):

            if liquid == -1 or liquid >= len(self.tonics) or self.tonics[liquid] is None:
                raise RuntimeError(f"Id '{liquid}' not found to unregister")
            liquid = self.tonics[liquid]
        elif isinstance(liquid, str):
            liquid = self.tonic_by_name[liquid]
        else:
            raise TypeError('essence must be of type ttEssence or int or str')

        with self._lock.write_access():
            self.tonics[liquid.id] = None
            self.tonic_by_name.pop(liquid.name, None)
            liquid.id = -1

    def get_id_by_name(self, name):
        """Retrieves the ID of an essence by its registered name.

        :param name: The name of the essence to find.
        :type name: str
        :return: The integer ID of the essence, or -1 if not found.
        :rtype: int
        """
        with self._lock.read_access():
            ess = self.tonic_by_name.get(name, None)
            return ess.id if ess is not None else -1

    def get_tonic_by_name(self, name):
        """Retrieves a ttEssence instance by its registered name.

        :param name: The name of the essence to retrieve.
        :type name: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            return self.tonic_by_name.get(name, None)


    def get_tonic_by_id(self, id):
        """Retrieves a ttEssence instance by its unique ID.

        :param id: The unique integer ID of the essence.
        :type id: int
        :return: The ttEssence instance, or None if the ID is out of bounds.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            if 0 <= id < len(self.tonics): return self.tonics[id]
            return None

    def get_service_essence(self, service):
        """Retrieves a ttEssence instance by its service name.

        :param service: The name of the service of the essence to retrieve.
        :type service: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            return self.tonic_by_name.get(service, None)

    def sdump(self):
        def sdumptonic(t, b, indent):
            s = f'\n{indent}{"F! " if t.finishing else ""} {t.id:02d}[{t.name}] <{t.__class__.__name__}>'
            if hasattr(t, 'tonics_sparkling'): s+=f' cat:{t.tonics_sparkling} '
            if t.finishing: s+=' FINISHING '
            if hasattr(t, 'service_bases'):
                if t.base != b: return s+' SERVICE COPY'
                for sb in t.service_bases:
                    s+=f'\n{indent}  sb: {sb.id:02d}[{sb.name}]'
            for i in t.infusions:
                s += sdumptonic(i, t, ' | '+indent)
            return s

        from .ttTonic import ttTonic
        s = 'Ledger dump'
        for t in self.tonics:
            if isinstance(t, ttTonic):
                if t.base is None:
                    s += sdumptonic(t, None, ' - ')
            elif isinstance(t, self.TonicReservation):
                s += f'\n - {t.id:20d}[{t.name}] <RESERVATION>'

        return s+'\n'