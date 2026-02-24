# ------------------------------------------------------------------------------
# Class: ttStore (TaskTonic Service Wrapper)
# ------------------------------------------------------------------------------
from ..ttLiquid import ttLiquid
from ..internals.Store import Store, Item

class ttStore(ttLiquid, Store):
    """
    TaskTonic specific wrapper that integrates Store with the Ledger.
    Defined as a Singleton Service via _tt_is_service.
    """

    # Determines service name in ttEssenceMeta logic
    _tt_is_service = 'store'

    def __init__(self, *args, **kwargs):
        # 1. Init ttEssence (Registers in Ledger)
        # Note: ttEssenceMeta ensures this runs only once for the singleton
        ttLiquid.__init__(self, *args, **kwargs)

        # 2. Init Store (Setup locks and storage)
        Store.__init__(self)

    def _init_service(self, *args, **kwargs):
        """Called every time the service is requested/accessed via ledger."""
        pass