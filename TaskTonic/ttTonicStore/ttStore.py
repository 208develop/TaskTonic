# ------------------------------------------------------------------------------
# Class: ttStore (TaskTonic Service Wrapper)
# ------------------------------------------------------------------------------

from ..ttTonic import ttTonic
from ..internals.Store import Store, Item

class ttStore(ttTonic, Store):
    """
    TaskTonic specific wrapper that integrates Store with the Ledger.
    Defined as a Singleton Service via _tt_is_service.
    """

    # Determines service name in ttEssenceMeta logic
    _tt_is_service = 'store'

    def __init__(self, *args, **kwargs):
        ttTonic.__init__(self, *args, **kwargs)
        Store.__init__(self)

    def _init_service(self, *args, **kwargs):
        """Called every time the service is requested/accessed via ledger."""
        pass

    def ttsc__finish(self):
        super().ttsc__finish()


