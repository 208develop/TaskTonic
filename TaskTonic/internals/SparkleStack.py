import threading
from typing import List, Tuple, Optional, Any


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
    
"""


class ThreadSparkleStack:
    """
    Manages thread-local instances of SparkleStack.

    Use this class as a singleton, or make global reference!!!.
    It ensures that every thread accessing 'sparkle_stack' interacts with its own
    isolated stack of execution context, preventing data race conditions in
    a multi-threaded environment.
    """

    def __init__(self):
        # Create a thread-local storage container.
        # Data assigned to attributes of this object is strictly unique to the current thread.
        self._sparkle_storage = threading.local()

    def init_for_thread(self, catalyst=None):
        """
        Initializes the SparkleStack for the *current* thread.

        This must be called at the start of a thread's lifecycle within the framework.

        Args:
            catalyst: The root context or driver object for this thread.

        Returns:
            The newly created SparkleStack instance.
        """
        if not hasattr(self._sparkle_storage, 'data'):
            self._sparkle_storage.data = SparkleStack(catalyst)
        else:
            if catalyst is not None: self._sparkle_storage.data.catalyst = catalyst
        return self._sparkle_storage.data

    def get(self) -> "SparkleStack":
        """
        Retrieves the SparkleStack instance for the *current* thread.

        IMPORTANT: This assumes init_for_thread() has been called previously
        in this thread. It will raise an AttributeError if accessed before initialization
        (Fail-fast design).
        """
        return self._sparkle_storage.data

class SparkleStack:
    """
    Represents the execution context stack for a single thread.

    It tracks the hierarchy of 'Essences' and 'Sparkles' (methods/actions)
    currently being executed, allowing introspection of the caller.
    """

    def __init__(self, catalyst):
        self.catalyst = catalyst
        # Initialize stack with a base sentinel frame.
        # Structure: List of tuples (Essence Instance, Sparkle Name)
        self.stack = [(None, "")]
        self.source = None

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

    def stack_essence(self, pos=-1):
        """
        Returns the Essence instance of the caller (the frame before the current one).

        WARNING: Assumes the stack depth is at least 2.
        Will raise IndexError if called at the root level (Fail-fast).
        """
        return self.stack[pos][0]

    def stack_essence_name(self, pos=-1):
        """
        Returns the name of the calling Essence.
        Returns an empty string if the caller is the base sentinel.
        """
        essence = self.stack[pos][0]
        return essence.name if essence else ""

    def stack_sparkle_name(self, pos=-1):
        """
        Returns the name of the calling Sparkle (action/method).
        """
        return self.stack[pos][1]

    @property
    def source_essence(self):
        """
        Returns the Essence instance of the caller (the frame before the current one).

        WARNING: Assumes the stack depth is at least 2.
        Will raise IndexError if called at the root level (Fail-fast).
        """
        return None if self.source is None else self.source[0]

    @property
    def source_essence_name(self):
        """
        Returns the name of the calling Essence.
        Returns an empty string if the caller is the base sentinel.
        """
        return "" if self.source is None else self.source[0].name

    @property
    def source_sparkle_name(self):
        """
        Returns the name of the calling Sparkle (action/method).
        """
        return "" if self.source is None else self.source[1]
