from TaskTonic.ttCatalyst import ttCatalyst
from TaskTonic.ttLedger import ttLedger
import time

class ttFormula():
    def __init__(self):
        self.ledger = ttLedger()
        self.ledger.update_formula({
            'tasktonic/fixed-id[]/name': 'main_catalyst',  # main_catalyst has always id 0
            'tasktonic/log/to': 'screen',
        })
        self.starting_at = time.time()

        self.update_formula(self.creating_formula())
        self.creating_main_catalyst()
        main_catalyst = self.ledger.get_essence_by_id(0)
        if not isinstance(main_catalyst, ttCatalyst):
            raise RuntimeError('Main catalyst (ID 0) in formula is not a ttCatalyst instance')

        self.creating_starting_tonics()

        main_catalyst.start_sparkling()

    def update_formula(self, formula):
        self.ledger.update_formula(formula)

    def creating_formula(self):
        return None

    def creating_main_catalyst(self):
        ttCatalyst(-1,'main_catalyst', fixed_id=0)

    def creating_starting_tonics(self):
        pass

