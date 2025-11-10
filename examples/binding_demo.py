from TaskTonic import *
import json


class E(ttEssence):
    pass

class T(ttTonic):
    def ttse__on_start(self):
        self.bind(S)
        pass

    def ttsc__bindings_in_row(self, cnt):
        self.log(f'Create {cnt} bindings as row')
        t = self.bind(T)
        self.log(self.bindings)
        cnt -= 1
        if cnt > 0:
            t.ttsc__bindings_in_row(cnt)

    # def _ttss__on_binding_finished(self, ess_id):
    #     super()._ttss__on_binding_finished(ess_id)


class S(ttTonic):
    _tt_is_service = 'demo_service'
    pass

class Demo(ttTonic):
    def log_ledger(self):
        self.log('== LEDGER ==')
        self.log(json.dumps(self.ledger.records, indent=4))

    def ttse__on_start(self):
        self.bind(S)
        self.log('== Binding at Tonic level ==')
        self.ttsc__4bindings_in_self()

    def ttsc__4bindings_in_self(self):
        self.log('Create 4 bindings in self')
        for i in range(4):
            self.bind(T)
        self.log(self.bindings)
        self.ttsc__bindings_in_row(4)

    def ttsc__bindings_in_row(self, cnt):
        self.log(f'Create {cnt} bindings as row')
        t = self.bind(T)
        t.ttsc__bindings_in_row(cnt-1)
        self.log(self.bindings)
        self.bind(ttTimerSingleShot, 1, sparkle_back=self.ttsc__finish_demo)
        self.log(self.bindings)

    def ttsc__finish_demo(self, timer_info):
        self.log('Finishing demo tonic')
        self.finish()

class MyTonics(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'Binding demo'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

    def creating_starting_tonics(self):
        S()  # starting service
        Demo()

def print_ledger(l):
    print('== LEDGER ==')
    print(json.dumps(l.records, indent=4))



# print('== Binding at Essence level ==')
# l=ttLedger()
# l.update_formula('tasktonic/project/name', 'Binding demo')
#
# e = E()
# print_ledger(l)
#
# print('Create 4 bindings in e')
# for i in range(4):
#
#     e.bind(E)
# print_ledger(l)
# print(e.bindings)
#
# print('Create 4 bindings as row ')
# t = e
# for i in range(4):
#     t = t.bind(E)
# print_ledger(l)
# print(e.bindings)
#
# print('Finish e')
# e.finish()
# print_ledger(l)
# print(e.bindings)


# reset ledger singleton, forcing clean startup
ttLedger._instance = None
ttLedger._singleton_init_done = False

MyTonics()

