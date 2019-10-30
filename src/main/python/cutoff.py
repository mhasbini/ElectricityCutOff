from datetime import datetime

# 6am-9am, 9am-12pm, 12pm-3pm and 3pm-6pm

ELECTRICITY = "كهرباء"
CUTOFF = "إشتراك"

CUTOFF_RANGES = [
    [
        # 12-6am 10-2pm 6-12pm
        [(0, 6), (10, 14), (18, 24)],  # odd days
        # 6-10am 2-6pm
        [(6, 10), (14, 18)],  # even days
    ],
    [
        # 6-10am 2-6pm
        [(6, 10), (14, 18)],  # odd days
        # 12-6am 10-2pm 6-12pm
        [(0, 6), (10, 14), (18, 24)],  # even days
    ],
]


class CutOff:
    def __init__(self, cutoff_range_index=0, parity=None):
        self.cutoff_range_index = cutoff_range_index
        self.range = self.get_range(parity)

    def status(self):
        """return wether it's ELECTRICITY or CUTOFF based on the selected range and current time"""

        current_hour, current_minutes, current_seconds = self.current_time()
        time_left = self.get_timeleft(current_hour, current_minutes, current_seconds)
        eps_minutes, eps_seconds = self.epsilons()

        for hour_range in self.range:
            start, stop = hour_range

            if current_hour in range(start, stop):
                return time_left, CUTOFF

            if current_hour == stop and current_minutes == 0 and current_seconds == 0:
                return time_left, CUTOFF

        return ELECTRICITY, time_left

    def get_timeleft(self, current_hour, current_minutes, current_seconds):
        left_hours = 0
        left_minutes = 0

        for hour_range in self.range:
            start, stop = hour_range

            if current_hour in range(start, stop):
                if current_minutes == 0:
                  left_hours = stop - current_hour
                  left_minutes = 0
                else:
                  left_hours = stop - current_hour - 1
                  left_minutes = 60 - current_minutes

                return f"{left_hours}:{left_minutes:02}"

        for hour_range in self.range:
            start, stop = hour_range

            if current_hour <= start:
                if current_minutes == 0:
                  left_hours = start - current_hour
                  left_minutes = 0
                else:
                  left_hours = start - current_hour - 1
                  left_minutes = 60 - current_minutes

                return f"{left_hours}:{left_minutes:02}"


        if current_minutes == 0:
            left_hours = 24 - current_hour
            left_minutes = 0
        else:
            left_hours = 24 - current_hour - 1
            left_minutes = 60 - current_minutes

        return f"{left_hours}:{left_minutes:02}"


    def update_range(self):
        self.range = self.get_range()

    def get_range(self, parity=None):
        if not parity:
            current_day = self.get_current_day()
            if current_day % 2 == 0:
                parity = 1
            else:
                parity = 0

        return CUTOFF_RANGES[self.cutoff_range_index][parity]

    def invert(self):
        """
        This method will invert the order of cut off range, e.g. incase it's consistently showing the wrong status
        """
        new_cutoff_range_index = None
        if self.cutoff_range_index == 0:
            new_cutoff_range_index = 1
        else:
            new_cutoff_range_index = 0

        self.cutoff_range_index = new_cutoff_range_index
        self.range = self.get_range()

    def epsilons(self):
        # minutes, seconds
        return 0, 1

    def get_current_day(self):
        now = datetime.now()

        return int(now.strftime("%-d"))

    def current_time(self):
        now = datetime.now()

        current_hour = int(now.strftime("%-H"))
        current_minutes = int(now.strftime("%-M"))
        current_seconds = int(now.strftime("%-S"))

        return current_hour, current_minutes, current_seconds
