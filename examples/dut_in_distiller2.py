from TaskTonic import *
from TaskTonic.ttTonicStore import ttDistiller


class MyTonic(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)

    def ttse__on_start(self):
        self.log(self.ledger.sdump())
        ttTimerSingleShot(name='tm_finish', seconds=.5)
        ttTimerSingleShot(name='tm_new', seconds=.2)
        self.log(self.ledger.sdump())

    def ttse__on_tm_finish(self, tinfo):
        self.log(self.ledger.sdump())
        self.finish()

    def ttse__on_tm_new(self, tinfo):
        MyTonic()
        pass

    def ttse__on_finished(self):
        self.log(self.ledger.sdump())


class App(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'TEST PROJECT'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        self.main = ttDistiller(name='tt_main_catalyst')

    def creating_starting_tonics(self):
        self.dut = MyTonic()


app = App()
distiller = app.main
dut = app.dut

distiller.stat_print(distiller.sparkle(timeout=5, contract={'probes': ['tonics_sparkling', 'infusions', 'finishing']}))
print(ttLedger().sdump())
