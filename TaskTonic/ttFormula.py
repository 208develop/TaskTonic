from .ttLogger import ttLog
from .ttCatalyst import ttCatalyst
from .ttLedger import ttLedger

import time

class ttFormula():
    def __init__(self):
        self.ledger = ttLedger()

        from .ttLoggers.ttScreenLogger import ttLogService, ttScreenLogService
        self.ledger.update_formula((
            ('tasktonic/project/name', 'tasktonic app'),
            ('tasktonic/project/started@', time.time()),
            ('tasktonic/project/status', 'starting'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),
            ('tasktonic/log/service#', 'off'),
            ('tasktonic/log/service./service', ttLogService), # base class, without logging
            ('tasktonic/log/service#', 'screen'),
            ('tasktonic/log/service./service', ttScreenLogService),
            ('tasktonic/log/service./arguments', {}),
        ))
        self.starting_at = time.time()

        app_formula = self.creating_formula()
        if app_formula: self.ledger.update_formula(app_formula)

        self.creating_main_catalyst()
        main_catalyst = self.ledger.get_essence_by_id(0)
        if not isinstance(main_catalyst, ttCatalyst):
            raise RuntimeError('Main catalyst (ID 0) in formula is not a ttCatalyst instance')

        self.creating_starting_tonics()

        if not self.ledger.formula.get('tasktonic/testing/dont_start_catalysts', False):
            self.ledger.update_formula('tasktonic/project/status', 'start_catalysts')
            for essence in self.ledger.essences[1:].copy(): # must be copied, because threads get started and ledger can be changed
                if isinstance(essence, ttCatalyst):
                    essence.start_sparkling()

            self.ledger.update_formula('tasktonic/project/status', 'main_running')
            main_catalyst.start_sparkling()
            self.ledger.update_formula('tasktonic/project/status', 'main_finished')

            # notify unfinished catalysts in ledger records
            for essence in self.ledger.essences[1:].copy():
                if hasattr(essence, '_ttss__main_catalyst_finished'):
                    essence._ttss__main_catalyst_finished()

    def creating_formula(self):
        return None

    def creating_main_catalyst(self):
        ttCatalyst(name='main_catalyst')

    def creating_starting_tonics(self):
        pass

