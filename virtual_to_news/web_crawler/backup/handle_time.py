import time
import datetime


class TakeTime:

    def __init__(self):
        pass
    # def __init__(self, years_ago: int = None, days: int = None):
        # self.years_ago = years_ago
        # self.days = days
        # self.__format = '%Y-%m-%d %H:%M:%S'
        # self.__now = time.localtime()

    def timestamp_datetime(value):
        format = '%Y-%m-%d %H:%M:%S'
        struct_time = time.localtime(value)
        datetime = time.strftime(format, struct_time)
        return datetime

    def datetime_timestamp(value):
        format = '%Y-%m-%d %H:%M:%S'
        struct_time = time.strptime(value, format)
        timestamp = time.mktime(struct_time)
        return int(timestamp)

    def now_datetime():
        format = '%Y-%m-%d %H:%M:%S'
        now = time.localtime()
        datetime = time.strftime(format, now)
        return datetime

    def now_timestamp():
        now = time.localtime()
        timestamp = int(time.mktime(now))
        return timestamp

    def now_year():
        __now = time.localtime()
        year = time.strftime('%Y', __now)
        return year

    def hand_year(year):
        now_ayear = year + "-01-01 00:00:00"
        return now_ayear

    def last_year(year):
        now_ayear = year + "-12-31 23:59:59"
        return now_ayear

    def take_now():
        now = TakeTime.now_timestamp()
        return now

    def take_head_day(day):
        format = '%Y-%m-%d %H:%M:%S'
        today = datetime.datetime.now()
        day_ago = (today-datetime.timedelta(days=day))
        day_timestamp = TakeTime.datetime_timestamp(day_ago.strftime(format))
        return day_timestamp

    def take_head_year(ago):
        now_year = str(int(TakeTime.now_year())-ago)
        hand_year = TakeTime.hand_year(now_year)
        year_timestamp = TakeTime.datetime_timestamp(hand_year)
        return year_timestamp

    def take_last_year(ago):
        now_year = str(int(TakeTime.now_year())-ago)
        last_year = TakeTime.last_year(now_year)
        year_timestamp = TakeTime.datetime_timestamp(last_year)
        return year_timestamp

    def take_file_day(value):
        format = '%Y-%m-%d'
        struct_time = time.localtime(value)
        datetime = time.strftime(format, struct_time)
        return datetime

# now=TakeTime.take_now()
# week=TakeTime.take_file_day(now)
# print(week)