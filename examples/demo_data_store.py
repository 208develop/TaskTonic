from TaskTonic import *
from TaskTonic.ttTonicStore import ttStore
import random


class OperatorInterface(ttTonic):

    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.twin = DigitalTwin()

    def ttse__on_start(self):
        self.twin.subscribe("sensors", self.ttse__on_sensor_update)
        ttTimerSingleShot(5, name='parm_update')
        ttTimerSingleShot(10, name='end_program')


    def ttse__on_sensor_update(self, updates):
        for path, new, old, source in updates:
            sensor = self.twin.at(path).list_root
            self.log(f"UPDATE OF SENSOR {sensor.v}: {sensor['value'].v:.3f}{sensor.get('unit', '')}")

    def ttse__on_parm_update(self, tmr):
        self.twin['parameters/update_freq'] = .5

    def ttse__on_end_program(self, tmr):
        self.finish()
        self.catalyst.finish() # stop application

class MyProcess(ttTonic):
    def __init__(self, name=None, log_mode=None, catalyst=None):
        super().__init__(name, log_mode, catalyst)
        self.twin = DigitalTwin()
        self.temp_sens = self.twin.at('sensors/#0')
        self.utmr = None

    def ttse__on_start(self):
        self.twin.subscribe("parameters", self.ttse__on_param_update)
        self.utmr = ttTimerRepeat(seconds=self.twin.get('parameters/update_freq', 5),
                                  name='update_timer')

    def ttse__on_param_update(self, updates):
        for path, new, old, source in updates:
            if path == 'parameters/update_freq':
                self.utmr.change_timer(seconds=new).restart()

    def ttse__on_update_timer(self, tmr):
        self.temp_sens['value'].v += random.uniform(-2, 2)
        # self.log('temp update')


class DigitalTwin(ttStore):
    _tt_is_service = "digital_twin"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _tt_post_init_action(self):
        super()._tt_post_init_action()
        with self.group(notify=False):
            self.set((
                ('parameters/update_freq', 2),
                ('parameters/temp_limit', 10),
                ('sensors/#', 'temp'),
                ('sensors/./value', 15.0),
                ('sensors/./unit', '℃'),
                ('sensors/./high_alarm', False),
                ('sensors/#', 'humidity'),
                ('sensors/./value', -1),
            ))
        self.log(f"Digital Twin is initialized\n{self.dumps()}")


class myApp(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.FULL),
        )

    def creating_main_catalyst(self):
        super().creating_main_catalyst()

    def creating_starting_tonics(self):
        DigitalTwin()
        OperatorInterface()
        MyProcess()




if __name__ == '__main__':
    myApp()