from TaskTonic import *
from TaskTonic.ttTonicStore.ttTimerScheduled import *

class TimTst(ttTonic):
    def __init__(self, **kwargs):
        super(TimTst, self).__init__(**kwargs)

    def ttse__on_start(self):
        tr = [
            ttTimerEveryYear(month=2, day=3, hour=10),
            ttTimerEveryYear(month="august", day=-1, hour=10),
            ttTimerEveryYear(month="august", day=2, hour=10),
            ttTimerEveryYear(month="february", day="monday", in_week=-1, time_str="9:56:45"),
            ttTimerEveryYear(month="september", day="saturday", in_week=-1, time_str="8:00:00"),
            ttTimerEveryYear(week=1, day="tuesday", hour=8),
            ttTimerEveryYear(week=3, day=6, hour=6),
            ttTimerEveryYear(week=52, day=6, time_str="23:59:59"),
            ttTimerEveryYear(month="december", day=-1, time_str="23:59:59"),

            ttTimerEveryMonth(day="wednesday", in_week=1, hour=10),
            ttTimerEveryMonth(day="wednesday", in_week=2, hour=10),
            ttTimerEveryMonth(day="wednesday", in_week=-1, hour=10),
            ttTimerEveryMonth(day="wednesday", in_week=-6, hour=10),
            ttTimerEveryMonth(day="tuesday", in_week=5, hour=10),
            ttTimerEveryMonth(day="tuesday", in_week=6, hour=10),
            ttTimerEveryMonth(day="monday", in_week=-1, hour=19),
            ttTimerEveryMonth(day=27, time_str="13:00:00"),
            ttTimerEveryMonth(day=-1, time_str="13:00:00"),
            ttTimerEveryMonth(day=-10, time_str="13:00:00"),

            ttTimerEveryWeek(day=0, time_str="23:59:59"),
            ttTimerEveryWeek(day="Tuesday", time_str="23:59:00"),
            ttTimerEveryWeek(day="wednesday", hour=1),
            ttTimerEveryWeek(day="friday", hour=2),
            ttTimerEveryWeek(day="saturday", hour=23),

            ttTimerEveryDay(hour=0),
            ttTimerEveryDay(hour=5),
            ttTimerEveryDay(hour=12),
            ttTimerEveryDay(hour=19),

            ttTimerEveryHour(time_str="59:59", name='tm_start_backup'),

            ttTimerEveryMinute(second=0),
            ttTimerEveryMinute(second=15),
            ttTimerEveryMinute(second=30.8),
            ttTimerEveryMinute(second=45)
        ]

        for t in tr:
            self.log(str(t))

    def ttse__on_timer(self, tinfo):
        self.log(f'{tinfo} >> {self.ledger.get_tonic_by_name(tinfo["name"])}')


class myMixDrink(ttFormula):
    def creating_formula(self):
        return (
            ('tasktonic/project/name', 'DEMO PROJECT'),
            ('tasktonic/log/to', 'screen'),
            ('tasktonic/log/default', ttLog.QUIET),
        )

    def creating_starting_tonics(self):
        TimTst()

myMixDrink()
