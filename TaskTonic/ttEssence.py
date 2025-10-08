from TaskTonic.ttLedger import ttLedger

class ttEssence:
    """A base class for all active components within the TaskTonic framework.

    Each 'Essence' represents a distinct, addressable entity with its own
    lifecycle, context (parent), and subjects (children). It automatically
    registers itself with the central ttLedger upon creation to receive a unique ID.
    """

    def __init__(self, context, name=None, fixed_id=None):
        """Initializes a new ttEssence instance.

        This constructor establishes the essence's context, registers it with the
        ledger to obtain a unique ID, determines its name, and registers itself
        as a subject of its parent context.

        :param context: The parent context for this essence. Can be another
                        ttEssence instance, an integer ID of an existing
                        essence, or None for a top-level essence.
        :type context: ttEssence or int or None
        :param name: An optional name for this essence. If not provided, a name
                     will be generated based on its ID and class name.
        :type name: str, optional
        :param fixed_id: An optional fixed ID (integer or string name) to assign
                         to this essence. This is used for essences that need a
                         predictable, static identifier.
        :type fixed_id: int or str, optional
        """
        self.ledger = ttLedger()  # is singleton class, so the ledger is shared within the whole project
        self.my_record = {}  # record to add to ledger

        self.context = context if isinstance(context, ttEssence) \
            else self.ledger.get_essence_by_id(context) if (isinstance(context, int) and context >= 0) \
            else None

        self.bindings = []
        self.id = self.ledger.register(self, fixed_id)
        self.name = name if isinstance(name, str) else f'{self.id:02d}.{self.__class__.__name__}'

        self.my_record.update({
            'id': self.id,
            'name': self.name,
            'type': self.__class__.__name__,
            'context_id': self.context.id if self.context else -1,
        })
        if fixed_id is not None:
            self.my_record.update({
                'fixed_id': True
            })

    def __str__(self):
        return f'{self.name} in context {self.context if self.context else -1}'

    def __repr__(self):
        return self.__str__()

    def __deepcopy__(self, memodict={}):
        return self

    # ledger functionality
    def bind(self, essence, *args, **kwargs):
        """Bind a child essence (subject) to this essence.

        Called to bind create, start and bind an essence.

        :param essence: The child ttEssence instance to register.
        :type essence: ttEssence
        """
        if not issubclass(essence, ttEssence):
            raise TypeError('Expected an instance of a ttEssence')
        e = essence(self, *args, **kwargs)
        self.bindings.append(e.id)
        return e

    def unbind(self, ess_id):
        """Unbind a child essence (subject) from this essence.

        This is typically called when a child essence is finished or destroyed,
        allowing the parent to remove it from its list of active bindings.

        :param essence: The child ttEssence instance to unbind.
        :type essence: ttEssence
        """
        if ess_id in self.bindings:
            self.bindings.remove(ess_id)

    def binding_finished(self, ess_id):
        self.unbind(ess_id)

    def main_essence(self, essence, *args, **kwargs):
        if not issubclass(essence, ttEssence):
            raise TypeError('Expected an instance of a ttEssence')
        e = essence(None, *args, **kwargs)
        return e


    # standard essence functionality
    def finish(self):
        if not self.bindings:
            self.finished()
        else:
            for ess_id in self.bindings:
                self.ledger.get_essence_by_id(ess_id).finish()

    def finished(self):
        """Signals that this essence has completed its lifecycle.

        This method should be called when the essence is finished with its work.
        It notifies its parent context to unregister it as an active subject.
        """
        if self.context: self.context.binding_finished(self.id)
        self.ledger.unregister(self)
        self.id = -1  # finished
