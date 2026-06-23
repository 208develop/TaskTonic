from TaskTonic.ttLogger import ttLogService, ttLog
from TaskTonic.ttTonicStore.ttNetworking import TcpDictSocketHandler

class ttIpLogService(ttLogService):
    """
    Intercepts the real TaskTonic log stream, formats the data,
    and forwards it to the visual LogCenter instead of the terminal.
    """
    _tt_force_stealth_logging = False

    def __init__(self, name=None):
        super().__init__(name=name, log_mode=ttLog.QUIET)
        self.net = None
        self.counter = None

        prj = self.ledger.formula.at('tasktonic/project')
        target = self.ledger.formula.get('tasktonic/log/target', 'localhost:1767')
        self.log_bucket = [{
            'start_new_session': True,
            'project': prj['name'].v,
            'start@': prj['started@'].v,
            'target': target,
            'logger_version': 0,
        }]


    def put_log(self, log):
        self.ttsc__add_log(log)

    def ttse__on_start(self):
        self.counter = 0

        # Start the IP client connecting to our Visual Logger
        target = self.ledger.formula.get('tasktonic/log/to/target', 'localhost:1767')
        target = self.ledger.formula.get('app_data/startup_args/target', target)

        if isinstance(target, int):
            target_host = 'localhost'
            target_port = target
        elif isinstance(target, str):
            s = target.split(':')
            target_host = s[0] if len(s) == 2 else 'localhost'
            target_port = int(s[-1])
        else:
            raise TypeError(f'Logger target [{target}] has wrong type')
        self.net = TcpDictSocketHandler(as_client=True, host=target_host, port=target_port)
        self.log(f'Connecting to log service at {target_host}:{target_port}')
        self.to_state('wait_for_connection')

    def ttse__on_socket_status(self, status, info=None):
        self.log(f"Network status changed: {status}")

    def ttse__on_socket_connected(self, addr):
        self.to_state('connected')
        self.log(f"Connected to log service at {addr}")

    def ttsc_wait_for_connection__add_log(self, log):
        self.log_bucket.append(log)

    def ttse_connected__on_enter(self):
        for log in self.log_bucket:
            self.net.ttsc__send_data(log)
        self.log_bucket = []

    def ttsc_connected__add_log(self, log):
        self.net.ttsc__send_data(log)

    def ttse_connected__on_disconnected(self):
        self.to_state('disconnected')
        self.log('Log server disconnected')

    def ttsc_disconnected__add_log(self, log):
        pass

    def ttse__on_service_base_completed(self, tonic, srv_left, _=0):
        super().ttse__on_service_base_completed(tonic, srv_left, finish_on_count=2) # using socket and selector
