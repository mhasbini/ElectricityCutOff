from datetime import datetime

# 6am-9am, 9am-12pm, 12pm-3pm and 3pm-6pm

ELECTRICITY = "كهرباء"
CUTOFF = "إشتراك"

CUTOFF_RANGES = [
    # 6-10am 2-6pm
    [(6, 10), (14, 18)],
    # 12-6am 10-2pm 6-12pm
    [(0, 6), (10, 14), (18, 24)],
]


class CutOff:
    def __init__(self, cutoff_range_index=0):
        self.range = CUTOFF_RANGES[cutoff_range_index]

    def status(self):
        """return wether it's ELECTRICITY or CUTOFF based on the selected range and current time"""

        current_hour, current_minutes, current_seconds = self.current_time()
        eps_minutes, eps_seconds = self.epsilons()

        for hour_range in self.range:
            start, stop = hour_range

            if current_hour in range(start, stop):
                return CUTOFF

            if current_hour == stop and current_minutes == 0 and current_seconds == 0:
                return CUTOFF

        return ELECTRICITY

    def epsilons(self):
        # minutes, seconds
        return 0, 1

    def current_time(self):
        now = datetime.now()

        current_hour = int(now.strftime("%-H"))
        current_minutes = int(now.strftime("%-M"))
        current_seconds = int(now.strftime("%-S"))

        return current_hour, current_minutes, current_seconds

    def is_electricity(self):
        return self.status() == ELECTRICITY

    def is_cutoff(self):
        return self.status() == CUTOFF
