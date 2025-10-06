from utils.ttRWLock import RWLock
from utils.ttDataShare import DataShare


class ttLedger:
    """A thread-safe singleton class that serves as the central registry for all ttEssence instances.

    The Ledger is the authoritative source of truth for the state of the entire
    system. It assigns unique IDs, stores records of all active essences, and
    provides methods to look up essences by ID or name.
    """
    _lock = RWLock()
    _instance = None
    _singleton_init_done = False

    class __FIXED_ID(object):  # used to temperately fill up fixed id instance
        pass

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
            self.logger = None
            self._singleton_init_done = True

    def update_formula(self, formula, val=None):
        """Updates the application's formula and pre-allocates fixed ID slots.


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

            for i, fixed_id in enumerate(self.formula.get('tasktonic/fixed-id')):
                l = len(self.records)
                if l > i:
                    fixed_essence = self.records[i]
                    if not isinstance(fixed_essence, self.__FIXED_ID) \
                            and not (
                            isinstance(fixed_essence, ttEssence) and fixed_essence.my_record.get('fixed_id', False)):
                        raise RuntimeError(f'Ledger record {i}, is already occupied by none fixed id essence')
                elif l == i:
                    self.records.append(None)
                    self.essences.append(self.__FIXED_ID())  # fill temperately with empty FixedId object)
                    self.records[i] = {
                        'id': i,
                        'fixed_id': True,
                        'name': self.formula.get(f'tasktonic/fixed-id[{i}]/name'),
                        'type': 'TEMP_OBJECT',
                        'context_id': -1,
                    }

    def register(self, essence, fixed_id=None):
        from TaskTonic.ttEssence import ttEssence
        """Registers a ttEssence instance and assigns it a unique ID.

        This method handles both dynamic ID assignment (finding the next available
        slot) and fixed ID assignment based on the provided `fixed_id`.

        :param essence: The ttEssence instance to be registered.
        :type essence: ttEssence
        :param fixed_id: An optional fixed identifier. Can be an integer for a
                         specific ID slot or a string name defined in the formula.
        :type fixed_id: int or str, optional
        :raises TypeError: If `essence` is not a ttEssence instance or `fixed_id`
                           is of an invalid type.
        :raises RuntimeError: If a fixed ID is requested that is already taken by
                              a non-fixed ID essence, or if a named fixed ID is not found.
        :return: The unique integer ID assigned to the essence.
        :rtype: int
        """
        if not isinstance(essence, ttEssence):
            raise TypeError('essence must be of type ttEssence')

        if fixed_id is not None:
            if isinstance(fixed_id, int):
                ess_id = fixed_id
            elif isinstance(fixed_id, str):
                ess_id = self.get_id_by_name(fixed_id)
                if ess_id == -1:
                    raise RuntimeError(f"Fixed id '{fixed_id}' not found")
            else:
                raise TypeError('fixed_id must be int or str')

            if not isinstance(self.essences[ess_id], self.__FIXED_ID):
                raise RuntimeError(f'Fixed id {ess_id} has ben taken bij record {self.essences[ess_id].ledger_record}')
            with self._lock.write_access():
                self.essences[ess_id] = essence
                self.records[ess_id] = essence.my_record
        else:
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
        ess_id = essence.id
        if ess_id == -1 or ess_id >= len(self.essences) or self.essences[ess_id] is None:
            raise RuntimeError(f"Id '{ess_id}' not found to unregister")
        essence.id = -1
        with self._lock.write_access():
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
                if record['name'] == name:
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
                if record['name'] == name:
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
            if id >= len(self.essences): return None
            return self.essences[id]
