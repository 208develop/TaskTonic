from TaskTonic import ttTonic, ttLog

class ttLogBase(ttTonic):
    def __init__(self):
        super().__init__('log_output', log_mode=ttLog.STEALTH, fixed_id='log_output')

    def __call__(self):
        logger = self.ledger.get_essence_by_name('log_output')
        if logger:
            return logger
        else:
            return


class ttScreenLogger(ttTonic):
    def __init__(self):
