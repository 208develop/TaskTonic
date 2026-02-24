from .ttSparkleStack import ttSparkleStack
from .ttLedger import ttLedger
from .ttCatalyst import ttCatalyst

import time

class ttFormula():
    def __init__(self):

        # 1/ INIT, init parameters ----------------------------------------------------------------------------------
        self.ledger = ttLedger()
        sp_stck = ttSparkleStack()

        from .ttLoggers.ttScreenLogger import ttLogService, ttScreenLogService
        from .ttLogger import ttLog
        self.ledger.update_formula((
            # project parameters
            ('tasktonic/project/name', 'tasktonic app'),
            ('tasktonic/project/started@', time.time()),
            ('tasktonic/project/status', 'starting'),

            # default logger is screen, quiet logging
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),

            # set log services
            ('tasktonic/log/service#', 'off'),
            ('tasktonic/log/service./service', ttLogService), # base class, without logging
            ('tasktonic/log/service#', 'screen'),
            ('tasktonic/log/service./service', ttScreenLogService),
            ('tasktonic/log/service./arguments', {}),
        ))

        # 2/ FORMULA, load the user formula -------------------------------------------------------------------------
        app_formula = self.creating_formula()
        if app_formula:
            self.ledger.update_formula(app_formula)

        # make id reservation for main catalyst
        self.ledger.make_reservation(service_name='tt_main_catalyst')

        # 3/ TONIC LOGGER, start the system log function if set -----------------------------------------------------
        log_formula = self.ledger.formula.at('tasktonic/log')
        self._logger = None
        self._log_mode = None
        self._log = None
        log_to = log_formula.get('to', 'off')

        if log_to != 'off':
            from .ttLogger import ttLogService, ttLog
            log_service = None
            services = log_formula.children(prefix='service')
            for service in services:
                if service.v == log_to:
                    s_kwargs = service.get('arguments', {})
                    log_service = service.get('service')(*(), **s_kwargs)  ## startup logger service
                    break
            if log_service is None:
                raise RuntimeError(f'Log to service "{log_to}" not supported.')

        # 4/ CATALYST, start the main catalyst ----------------------------------------------------------------------
        self.creating_main_catalyst()

        main_catalyst = self.ledger.get_tonic_by_name('tt_main_catalyst')
        if not isinstance(main_catalyst, ttCatalyst):
            raise RuntimeError(f'Main catalyst {main_catalyst} in formula is not a ttCatalyst instance')

        # 5/ TONICS, startup the system by creating the starting tonics ---------------------------------------------
        sp_stck.push(self.ledger.get_tonic_by_name('tt_main_catalyst'), '__formula__')
        self.creating_starting_tonics()
        sp_stck.pop()

        # 6/ STARTUP, start created catalysts and them start main catalyst ------------------------------------------
        if not self.ledger.formula.get('tasktonic/testing/dont_start_catalysts', False):

            self.ledger.update_formula('tasktonic/project/status', 'start_catalysts')
            for essence in self.ledger.tonics[1:].copy(): # must be copied, because threads get started and ledger can be changed
                if isinstance(essence, ttCatalyst):
                    essence.start_sparkling()

            self.ledger.update_formula('tasktonic/project/status', 'main_running')
            main_catalyst.start_sparkling()
            self.ledger.update_formula('tasktonic/project/status', 'main_finished')

            # notify unfinished catalysts in ledger records
            for essence in self.ledger.tonics[1:].copy():
                if hasattr(essence, '_ttss__main_catalyst_finished'):
                    essence._ttss__main_catalyst_finished()



    def creating_formula(self):
        return None

    def creating_main_catalyst(self):
        ttCatalyst(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        pass

