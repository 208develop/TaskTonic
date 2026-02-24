from TaskTonic import ttLiquid, ttCatalyst, ttLog, ttSparkleStack
import queue, threading, time, copy


class ttDistiller(ttCatalyst):
    """
    The TaskTonic Test Harness
       The Distiller is the dedicated testing environment for the TaskTonic framework. Where the Catalyst
       is designed for high-speed, real-time production, the Distiller is its analytical counterpart,
       designed for controlled observation and debugging.
    """

    def __init__(self, name='tt_main_catalyst'):
        super().__init__(name=name, log_mode=ttLog.OFF)

    def start_sparkling(self):
        # print('Distiller is setup and ready for testing')
        sp_stck = ttSparkleStack()
        sp_stck.catalyst = self

        self.thread_id = threading.get_ident()
        sp_stck.catalyst = self

        self.sparkling = True

    def sparkle(self,
                sparkle_count=None,
                timeout=None,
                till_state_in=None,
                till_sparkle_in=None,
                contract=None):

        status={}
        sp_stck = ttSparkleStack()
        if self.sparkling:
            if contract is None: contract = {}

            def ccheck(item, default, ext=None, force_list=False):
                c = ext if ext else contract.get(item, default)
                if force_list and not isinstance(c, list): c=[c]
                contract[item] = c

            ccheck('timeout', 3600, timeout)
            ccheck('till_state_in', [], till_state_in, force_list=True)
            ccheck('till_sparkle_in', [], till_sparkle_in, force_list=True)
            ccheck('probes', [], force_list=True)

            status = {
                'status': 'running',
                'start@': time.time(),
                'sparkle_trace': [],
            }
            ending_at = time.time() + contract['timeout']

            while self.sparkling and not status.get('stop_condition', False):
                reference = time.time()
                next_timer_expire = 0.0
                while next_timer_expire == 0.0:
                    next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60
                if reference+next_timer_expire > ending_at:
                    next_timer_expire = ending_at - reference
                    if next_timer_expire < 0.0: next_timer_expire = 0.0
                try:
                    instance, sparkle, args, kwargs, sp_stck.source = self.catalyst_queue.get(timeout=next_timer_expire)
                    sp_name = sparkle.__name__
                    self.execute_with_testlog(instance, sparkle, args, kwargs, status, contract)
                    if sparkle_count: sparkle_count -= 1
                    while self.extra_sparkles:
                        instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                        self.execute_with_testlog(instance, sparkle, args, kwargs,
                                                  status, contract)
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

    def execute_with_testlog(self, instance, sparkle, args, kwargs, status, contract):
        def _freeze_value(value):
            """
            Maakt een statische snapshot van een variabele.
            Zorgt ervoor dat dynamische objecten (zoals ttLiquid) worden omgezet
            naar hun huidige string-representatie.
            """
            # 1. Specifieke types die we direct als string willen vastleggen
            # Check op type naam is veiliger tegen circulaire imports dan isinstance
            type_name = type(value).__name__
            if type_name == 'ttLiquid':
                return str(value)

            # 2. Dictionaries recursief doorlopen
            if isinstance(value, dict):
                return {k: _freeze_value(v) for k, v in value.items()}

            # 3. Lists en Tuples recursief doorlopen
            if isinstance(value, (list, tuple)):
                return [_freeze_value(v) for v in value]

            # 4. Primitives (int, float, bool, str, None) mogen door
            if isinstance(value, (int, float, bool, str, type(None))):
                return value

            # 5. ttLiquid
            if isinstance(value, ttLiquid):
                return value.__str__()

            # 6. Fallback: probeer deepcopy, anders string representatie
            try:
                return copy.deepcopy(value)
            except:
                return str(value)

        sp_stck = ttSparkleStack()
        status['sparkle_trace'].append({
            'id': instance.id,
            'tonic': instance.name,
            'sparkle': sparkle.__name__,
            'args': args,
            'kwargs': kwargs,
            'source': sp_stck.source,
            'at_enter': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': {
                    p: _freeze_value(getattr(instance, p))
                    for p in contract.get('probes', [])
                    if hasattr(instance, p)
                },
            }
        })
        sp_stck.push(instance, sparkle.__name__)
        instance._execute_sparkle(sparkle, *args, **kwargs)
        sp_stck.pop()
        status['sparkle_trace'][-1].update({
            'at_exit': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': {
                    p: _freeze_value(getattr(instance, p))
                    for p in contract.get('probes', [])
                    if hasattr(instance, p)
                },
                'sparkling': self.sparkling,
            }
        })
        if sparkle.__name__ in contract['till_sparkle_in']:
            status.setdefault('stop_condition', []).append(f'sparkle_trigger: [{sparkle.__name__}]')
        if instance.get_current_state_name() in contract['till_state_in']:
            status.setdefault('stop_condition', []).append(f'state_trigger: [{instance.get_current_state_name()}]')


    def finish_distiller(self, timeout=.5, contract=None):
        for liq in self.ledger.tonics:
            if isinstance(liq, ttLiquid): liq.finish()
            elif isinstance(liq, self.ledger.TonicReservation): self.ledger.unregister(liq)
        stat = self.sparkle(timeout=timeout, contract=contract)
        #todo: reset ledger
        return stat

    def stat_print(self, status, filter=None):
        import time
        print('=== Sparkling ==')

        if isinstance(filter, int):
            filter = [filter]
        elif isinstance(filter, list):
            pass
        elif filter is None:
            pass
        else:
            raise TypeError('filter is not None, a number or a list of numbers')

        for t in status.get('sparkle_trace', []):
            if filter is None or t['id'] in filter:
                e = t['at_enter']
                x = t['at_exit']
                ts = e['@']
                te = x['@']
                l_ts = f'{time.strftime("%H%M%S", time.localtime(ts))}.{int((ts - int(ts)) * 1000):03d}'
                l_te = f'{time.strftime("%H%M%S", time.localtime(te))}.{int((te - int(te)) * 1000):03d}'
                l_duration = f'{(te - ts):2.3f}'
                s = t['source']
                src = (s[0].name if s[0] else 'None') + '.' + s[1]

                print(
                    f"{t['id']:03d} - {t['tonic']}.{t['sparkle']} ( {t['args']}, {t['kwargs']} ) <-- {src}\n"
                    f"   at enter                                 at exit\n"
                    f"   {l_ts}                               {l_te}                               < {l_duration}s\n"
                    f"   {e['state']:.<40} {x['state']:.<40} < state"
                )
                pe = e.get('probes', {})
                px = x.get('probes', {})
                p = sorted(set(pe.keys()) | set(px.keys()))
                for key in p:
                    print(f"   {str(pe.get(key, '-')):.<40} {str(px.get(key, '-')):.<40} < {key}")
                print()
        print(
            f'>> stopped : {status["stop_condition"]}, duration {(status["end@"] - status["start@"]):2.03f}s, Catalyst Status {status["status"]}')
