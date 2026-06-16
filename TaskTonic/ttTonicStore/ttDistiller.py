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

        status = {}
        sp_stck = ttSparkleStack()
        if self.sparkling:
            if contract is None:
                contract = {}

            def ccheck(item, default, ext=None, force_list=False):
                c = ext if ext is not None else contract.get(item, default)
                if force_list and not isinstance(c, list):
                    c = [c]
                contract[item] = c

            ccheck('timeout', 3600.0, timeout)
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
                    next_timer_expire = self.timers[0].check_on_expiration(reference) if self.timers else 60.0
                if reference + next_timer_expire > ending_at:
                    next_timer_expire = ending_at - reference
                    if next_timer_expire < 0.0:
                        next_timer_expire = 0.0
                try:
                    item = self.catalyst_queue.get(timeout=next_timer_expire)
                    instance, sparkle, args, kwargs, sp_stck.source = item

                    self.execute_with_testlog(instance, sparkle, args, kwargs, status, contract)

                    if sparkle_count:
                        sparkle_count -= 1

                    # State transitions MOGEN NOOIT onderbroken worden!
                    # Drain de extra_sparkles altijd volledig af.
                    while self.extra_sparkles:
                        instance, sparkle, args, kwargs = self.extra_sparkles.pop(0)
                        self.execute_with_testlog(instance, sparkle, args, kwargs, status, contract)
                        if sparkle_count:
                            sparkle_count -= 1


                except queue.Empty:
                    pass

                if time.time() >= ending_at:
                    status.setdefault('stop_condition', []).append('timeout')
                if sparkle_count is not None and sparkle_count <= 0:
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
            type_name = type(value).__name__
            if type_name == 'ttLiquid':
                return str(value)

            if isinstance(value, dict):
                return {k: _freeze_value(v) for k, v in value.items()}

            if isinstance(value, (list, tuple)):
                return [_freeze_value(v) for v in value]

            if isinstance(value, (int, float, bool, str, type(None))):
                return value

            if isinstance(value, ttLiquid):
                return value.__str__()

            try:
                return copy.deepcopy(value)
            except:
                return str(value)

        # 1. Determine requested probes (tonic specific OR global fallback)
        tonic_contract = contract.get('tonics', {}).get(instance.name, {})
        requested_probes = tonic_contract.get('probes', contract.get('probes', []))

        sp_stck = ttSparkleStack()

        # 2. Freeze probes BEFORE sparkle execution
        probes_at_enter = {
            p: _freeze_value(getattr(instance, p))
            for p in requested_probes
            if hasattr(instance, p)
        }

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
                'probes': probes_at_enter,
            }
        })

        # 3. Execute the Sparkle
        sp_stck.push(instance, sparkle.__name__)
        instance._execute_sparkle(sparkle, *args, **kwargs)
        sp_stck.pop()

        # 4. Freeze probes AFTER sparkle execution
        probes_at_exit = {
            p: _freeze_value(getattr(instance, p))
            for p in requested_probes
            if hasattr(instance, p)
        }

        status['sparkle_trace'][-1].update({
            'at_exit': {
                '@': time.time(),
                'state': instance.get_current_state_name(),
                'probes': probes_at_exit,
                'sparkling': self.sparkling,
            }
        })

        # 5. Evaluate stop conditions
        just_executed = {
            'tonic': instance.name,
            'sparkle': sparkle.__name__
        }
        self._evaluate_contract(contract, status, just_executed)

    def _evaluate_contract(self, contract, status, just_executed):
        """
        Evaluates both global legacy conditions and the new per-tonic conditions.
        """
        # --- Legacy Global Conditions ---
        if just_executed['sparkle'] in contract.get('till_sparkle_in', []):
            status.setdefault('stop_condition', []).append(f"sparkle_trigger: [{just_executed['sparkle']}]")
            return True

        instance = self.ledger.get_tonic_by_name(just_executed['tonic'])
        if instance and instance.get_current_state_name() in contract.get('till_state_in', []):
            status.setdefault('stop_condition', []).append(f"state_trigger: [{instance.get_current_state_name()}]")
            return True

        # --- New Per-Tonic Advanced Conditions ---
        tonics_dict = contract.get('tonics', {})
        if not tonics_dict:
            return False

        matched_tonics = 0

        for tonic_name, rules in tonics_dict.items():
            tonic = self.ledger.get_tonic_by_name(tonic_name)
            if not tonic:
                continue

            is_match = False

            # Condition 1: State Match
            if 'till_state_in' in rules:
                if tonic.get_current_state_name() in rules['till_state_in']:
                    is_match = True

            # Condition 2: Sparkle Match
            if not is_match and 'till_sparkle_in' in rules:
                if tonic_name == just_executed['tonic'] and just_executed['sparkle'] in rules['till_sparkle_in']:
                    is_match = True

            # Condition 3: Probe Match
            if not is_match and 'stop_on_probe' in rules:
                for probe_name, expected_val in rules['stop_on_probe'].items():
                    if hasattr(tonic, probe_name) and getattr(tonic, probe_name) == expected_val:
                        is_match = True
                        break

            if is_match:
                matched_tonics += 1

        # Determine target count (AND vs OR logic)
        target_count = contract.get('stop_match_count', 1)
        if target_count == 'all':
            target_count = len(tonics_dict)

        if matched_tonics >= target_count:
            condition_msg = f'contract_met: {matched_tonics}/{target_count} tonics matched'
            status.setdefault('stop_condition', []).append(condition_msg)
            return True

        return False

    def finish_distiller(self, timeout=0.5, contract=None):
        for liq in self.ledger.tonics:
            if isinstance(liq, ttLiquid):
                liq.finish()
            elif isinstance(liq, self.ledger.TonicReservation):
                self.ledger.unregister(liq)

        stat = self.sparkle(timeout=timeout, contract=contract)

        # Forced reset of the ledger to create a new singleton when distiller is restarted.
        self.ledger._instance = None
        self.ledger._singleton_init_done = False
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

        dur = status["end@"] - status["start@"]
        print(f'>> stopped : {status["stop_condition"]}, duration {dur:2.03f}s, Catalyst Status {status["status"]}')