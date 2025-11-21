from ..ttCatalyst import ttCatalyst
import queue, threading, time


class ttDistiller(ttCatalyst):
    """
    The TaskTonic Test Harness
       The Distiller is the dedicated testing environment for the TaskTonic framework. Where the Catalyst
       is designed for high-speed, real-time production, the Distiller is its analytical counterpart,
       designed for controlled observation and debugging.
    """

    def __init__(self):
        super().__init__(-1, log_mode='off')

    def start_sparkling(self):
        print('Distiller is setup and ready for testing')
        self.thread_id = threading.get_ident()
        self.sparkling = True

    def sparkle(self,
                sparkle_count=None,
                timeout=None,
                till_state_in=None,
                till_sparkle_in=None,
                contract=None):

        status={}
        if self.sparkling:
            status = {
                'status': 'running',
                'start@': time.time(),
                'sparkle_trace': [],
            }
            ending_at = time.time()+(timeout if timeout else 3600000)
            till_state_in = till_state_in if isinstance(till_state_in, list) else [till_state_in]
            till_sparkle_in = till_sparkle_in if isinstance(till_sparkle_in, list) else [till_sparkle_in]

            while self.sparkling and not status.get('stop_condition', False):
                reference = time.time()
                next_timer_expire = 0.0
                while next_timer_expire == 0.0:
                    next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60
                if reference+next_timer_expire > ending_at:
                    next_timer_expire = ending_at - reference
                    if next_timer_expire < 0.0: next_timer_expire = 0.0
                try:
                    instance, sparkle, args, kwargs = self.catalyst_queue.get(timeout=next_timer_expire)
                    self.execute_with_testlog(instance, sparkle, args, kwargs, status, till_sparkle_in, till_state_in)
                    if sparkle_count: sparkle_count -= 1
                    while self.extra_sparkles:
                        instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                        self.execute_with_testlog(instance, sparkle, args, kwargs,
                                                  status, till_sparkle_in, till_state_in)
                        if sparkle_count: sparkle_count -= 1
                except queue.Empty:
                    pass

                if time.time() >= ending_at:
                    status.setdefault('stop_condition', []).append('timeout')
                if (sparkle_count is not None and sparkle_count <= 0):
                    status.setdefault('stop_condition', []).append('sparkle_count')

        if not self.sparkling:
            status.update({'status': 'catalyst finished'})
            status.setdefault('stop_condition', []).append('catalyst finished')
        status.update({'end@': time.time()})

        return status

    def execute_with_testlog(self, instance, sparkle, args, kwargs, status, till_sparkle_in, till_state_in):
        status['sparkle_trace'].append({
            'id': instance.id,
            'tonic': instance.name,
            'sparkle': sparkle.__name__,
            'args': args,
            'kwargs': kwargs,
            'at_enter': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
            }
        })
        instance._execute_sparkle(sparkle, *args, **kwargs)
        status['sparkle_trace'][-1].update({
            'at_exit': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'sparkling': self.sparkling,
            }
        })
        if sparkle.__name__ in till_sparkle_in:
            status.setdefault('stop_condition', []).append(f'sparkle_trigger: [{sparkle.__name__}]')
        if instance.get_current_state_name() in till_state_in:
            status.setdefault('stop_condition', []).append(f'state_trigger: [{instance.get_current_state_name()}]')


    def finish_distiller(self, timeout=.5):
        for ess in self.ledger.essences:
            if ess: ess.finish()
        stat = self.sparkle(timeout=timeout)
        #todo: reset ledger
        return stat
