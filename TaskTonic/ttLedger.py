from .utils.ttRWLock import RWLock
from .utils.ttDataShare import DataShare


class ttLedger:
    """A thread-safe singleton class that serves as the central registry for all ttEssence instances.

    The Ledger is the authoritative source of truth for the state of the entire
    system. It assigns unique IDs, stores records of all active essences, and
    provides methods to look up essences by ID or name.
    """
    _lock = RWLock()
    _instance = None
    _singleton_init_done = False

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
            self.records = [] # ledger records by id
            self.essences = [] # direct acces to essence instance by id
            self.formula = None
            self._singleton_init_done = True

    def update_formula(self, formula, val=None):
        """Updates the application's formula

        :param formula: The application definition object, typically a DataShare
                        instance containing configuration.
        :type formula: str, Collection[Tuple[str, Any]] or Dict[str, Any]]
        :param val: used if formula is a string to create a key, val pair
        :type val: any, optional
        """
        with self._lock.write_access():
            from TaskTonic.ttEssence import ttEssence
            if self.formula is None:
                self.formula = DataShare()
            self.formula.set(formula, val)

    def update_record(self, ess_id, data):
        if 0 > ess_id >= len(self.records) or self.essences[ess_id] is None:
            raise RuntimeError(f"Essence ID {ess_id} does not exist")
        with self._lock.write_access():
            self.records[ess_id].update(data)

    def register(self, essence):
        from TaskTonic.ttEssence import ttEssence
        """Registers a ttEssence instance and assigns it a unique ID.

        :param essence: The ttEssence instance to be registered.
        :type essence: ttEssence

        :raises TypeError: If `essence` is not a ttEssence instance 
        :return: The unique integer ID assigned to the essence.
        :rtype: int
        """
        if not isinstance(essence, ttEssence):
            raise TypeError('essence must be of type ttEssence')

        with self._lock.write_access():
            try:
                ess_id = self.essences.index(None)
                self.essences[ess_id] = essence
            except ValueError:
                ess_id = len(self.essences)
                self.essences.append(essence)
                self.records.append(essence.my_record)
        return ess_id

    def unregister(self, essence):
        """Unregisters a ttEssence instance from the ledger.

        (Note: This method is not yet implemented).

        :param essence: The ttEssence instance to unregister.
        :type essence: ttEssence
        """
        from TaskTonic import ttEssence
        if isinstance(essence, ttEssence):
            ess_id = essence.id
        elif isinstance(essence, int):
            ess_id = essence
        elif isinstance(essence, str):
            ess_id = self.get_id_by_name(essence)
        else:
            raise TypeError('essence must be of type ttEssence or int or str')
        if ess_id == -1 or ess_id >= len(self.essences) or self.essences[ess_id] is None:
            raise RuntimeError(f"Id '{ess_id}' not found to unregister")
        with self._lock.write_access():
            self.essences[ess_id].id = -1
            self.essences[ess_id] = None
            self.records[ess_id] = None

    def get_id_by_name(self, name):
        """Retrieves the ID of an essence by its registered name.

        :param name: The name of the essence to find.
        :type name: str
        :return: The integer ID of the essence, or -1 if not found.
        :rtype: int
        """
        with self._lock.read_access():
            for record in self.records:
                if record and record.get('name', '') == name:
                    return record['id']
        return -1

    def get_essence_by_name(self, name):
        """Retrieves a ttEssence instance by its registered name.

        :param name: The name of the essence to retrieve.
        :type name: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            for record in self.records:
                if record and record.get('name', '') == name:
                    return self.essences[record['id']]
        return None

    def get_essence_by_id(self, id):
        """Retrieves a ttEssence instance by its unique ID.

        :param id: The unique integer ID of the essence.
        :type id: int
        :return: The ttEssence instance, or None if the ID is out of bounds.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            if id < 0 or id >= len(self.essences): return None
            return self.essences[id]

    def get_service_essence(self, service):
        """Retrieves a ttEssence instance by its service name.

        :param service: The name of the service of the essence to retrieve.
        :type service: str
        :return: The ttEssence instance, or None if not found.
        :rtype: ttEssence or None
        """
        with self._lock.read_access():
            for record in self.records:
                if record and record.get('service', '') == service:
                    return self.essences[record['id']]
        return None
