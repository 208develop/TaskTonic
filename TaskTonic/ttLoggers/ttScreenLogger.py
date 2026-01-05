from ..ttLogger import ttLogService
import time

class ttScreenLogService(ttLogService):

    def __init__(self, name=None, context=None, log_mode=None):
        super().__init__(name, context, log_mode)
        self.log_records = []

    def __init_service__(self, *args, **kwargs):
        pass

    def put_log(self, log):
        self.ttsc__add_log(log)

    def ttsc__add_log(self, log):
        """
        Formats and prints the collected log entry for an event, then resets it.
        """
        l_id = log.get('id', -1)
        if l_id < 0:
            raise RuntimeError(f'Error in log entry {log}')

        if log.get('sys',{}).get('created', False):

            while len(self.log_records) <= l_id:
                self.log_records.append(None)
            self.log_records[l_id] = log.copy()

        sparkle_name = log.get('sparkle', '')
        sparkle_state_idx = log.get('state', -1)

        if sparkle_name == '_ttinternal_state_change_to':
            sparkle_name = f" TO STATE [{self.log_records[l_id]['sys']['states'][log['sys']['new_state']]}]"

        ts = log['start@']
        lt = time.localtime(ts)
        l_time_start = f'{time.strftime("%H%M%S", lt)}.{int((ts - int(ts)) * 1000):03d}'

        header = f"{self.log_records[l_id]['sys']['name']}"
        if sparkle_state_idx >= 0:
            header += f"[{self.log_records[l_id]['sys']['states'][sparkle_state_idx]}]"
        header += f".{sparkle_name}"

        dont_print_flags = ['id', 'start@', 'log', 'sparkle', 'state', 'sparkles', 'states', 'duration']
        flags_to_print = {k: v for k, v in log.items() if k not in dont_print_flags}

        du = log.get('duration',0.0)
        l_du = '' if du <= .15 else f'DURATION: {du:1.3f} sec !!! '

        print(f"[{l_time_start}] {l_id:02d} - {header:.<65} {l_du}{flags_to_print}")
        if l_states := log.get('states'):
            print(f"{16 * ' '}== STATES: |", end='')
            for state in l_states: print(f" {state} |", end='')
            print()
        if l_sparkles := log.get('sparkles'):
            print(f"{16 * ' '}== SPARKLES: |", end='')
            for sparkle in l_sparkles:
                if not sparkle.startswith('_ttss'): print(f" {sparkle} |", end='')
            print()

        if log.get('log'):
            for line in log['log']:
                print(f"{16 * ' '}- {line}")
