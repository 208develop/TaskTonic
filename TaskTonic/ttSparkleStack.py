import contextvars
"""
The Sparkle stack is used and maintained bij the TaskTonic Framework.
- The stack keeps track of the active sparkles and the calling sparkles.
- The stack is located in the tread local space, so at every moment the stack is accessed you read the
   values of the active stack and therefore the active catalyst

Stack maintenance by TaskTonic:
- With every catalyst that is started the initial context is set at None, '' (no tasktonic context, no sparkle).
   The instance of the catalyst is copied and the calling sparkle is set to None
- Every time a sparkle is called (and putted in the sparkling queue) the active sparkle is also stored in that queue
   as the source sparkle.
- At execution of a sparkle the active sparkle is pushed on stack as a set of instance, sparkle name. Also de source
   sparkle is set. When executing a sparkle you can refer to that source, ie for returning data.
- Every time a ttEssence, or subclass, is initiated the new instance is pushed with sparkle __init__. This is done in 
   the init of ttEssense so only after you call super().__init__() in your subclass. Popping the stack is done by
   TaskTonic after the whole init sequence is completed.
- Every time the ttFormula is executed, before starting tonics are created, the context main_catalyst, "__formula__"
   is pushed.
- Be aware that the calling sparkle is always the executing sparkle even when nested inits are putted on stack


Note on using:    
 Don't create a parameter self.sparkle_stack in your class! At creating the data of the current thread is locked for 
 that parameter. If a method is called from an other thread self.sparkle_stack refers to the first thread!!
 Always use in your method:
    sp_stck = ttSparkleStack()
    sp_stck.push.....
    sp_stck.get_essence...
    etc
    
    or 
    ttSparkleStack().get_essence... # for single use
    
"""

_sparkle_context: contextvars.ContextVar = contextvars.ContextVar("sparkle_context")
class ttSparkleStack:
    """
    Represents the execution context stack for a single thread.

    It tracks the hierarchy of 'Essences' and 'Sparkles' (methods/actions)
    currently being executed, allowing introspection of the caller.
    """
    def __new__(cls):
        try:
            # 1. get thread instance
            instance = _sparkle_context.get()
            return instance
        except LookupError:
            # 2. init if not existing
            instance = super().__new__(cls)
            instance.catalyst = None
            instance.stack = [(None, "")]
            instance.source = (None, "")
            _sparkle_context.set(instance)
            return instance

    def push(self, essence, sparkle):
        """
        Pushes a new execution frame onto the stack.

        Args:
            essence: The object instance context.
            sparkle (str): The name of the action/method being invoked.
        """
        self.stack.append((essence, sparkle))

    def pop(self):
        """Removes the top execution frame from the stack."""
        self.stack.pop()

    def get_stack(self, pos=-1):
        return self.stack[pos]

    def get_tonic(self, pos=-1):
        return self.stack[pos][0]

    def get_tonic_name(self, pos=-1):
        essence = self.stack[pos][0]
        return essence.name if essence else ""

    def get_sparkle_name(self, pos=-1):
        return self.stack[pos][1]

    @property
    def source_tonic(self):
        return self.source[0]

    @property
    def source_tonic_name(self):
        return "" if self.source[0] is None else self.source[0].name

    @property
    def source_sparkle_name(self):
        return self.source[1]
