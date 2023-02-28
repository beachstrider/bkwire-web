import re
import json
import base64
import requests
from datetime import datetime, timedelta, date


class BkwDateTime:
    def __init__(self):
        self.date_today = date.today()

    def get_timestamp_now(self):
        return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

    def get_timestamp_day_now(self):
        return datetime.now().strftime(("%Y-%m-%d"))

    def get_timestamp_day_now_month_day(self):
        return datetime.now().strftime(("%m-%d"))        

    def get_timestamp_day_now_entry(self):
        return datetime.now().strftime(("%m/%d/%Y"))

    def get_timestamp_day_monday_of_week(self):
        now = datetime.now()
        monday = now - timedelta(days = now.weekday())
        return(monday)

    def get_daily_time_w_month_day(self):
        if self.date_today.weekday() == 0:
            date_previous = self.date_today - timedelta(days = 3)
        else:
            date_previous = self.date_today - timedelta(days = 1)

        today_month = datetime.now().strftime(("%b"))
        today_day = datetime.now().strftime(("%d"))
        return(self.date_today, date_previous, today_month, today_day)

    def get_news_length(self):
        date_previous = self.date_today - timedelta(days = 3)
        return(self.date_today, date_previous)

    def get_weekly_time(self):
        date_previous = self.date_today - timedelta(days = 7)
        return(self.date_today, date_previous)

    def get_bi_weekly_time(self):
        date_previous = self.date_today - timedelta(days = 14)
        return(self.date_today, date_previous)

    def get_thirty_day_time(self,passed_date):
        date_previous = passed_date + timedelta(days = 30)
        return(datetime.now(), date_previous)


# MAIN
if __name__ == '__main__':
    main()
