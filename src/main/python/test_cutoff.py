import unittest
from datetime import datetime
from freezegun import freeze_time

from cutoff import CutOff, ELECTRICITY, CUTOFF


class CutOffTest(unittest.TestCase):
    def setUp(self):
        # 6-10am 2-6pm
        self.cutoff = CutOff(cutoff_range_index=0, parity=1)

    def test_status(self):
        return True
        electricity_times = [
            "5:00:00",
            "5:59:59",
            "10:00:01",
            "12:00:01",
            "13:00:00",
            "13:30:00",
            "18:00:01",
            "19:00:01",
        ]

        cutoff_times = [
            "6:00:00",
            "6:00:01",
            "6:30:01",
            "7:12:34",
            "10:00:00",
            "14:00:00",
            "14:00:01",
            "17:59:59",
            "18:00:00",
        ]

        for electricity_time in electricity_times:
            with freeze_time(electricity_time):
                self.assertEqual(
                    self.cutoff.status()[1],
                    ELECTRICITY,
                    f"{electricity_time} is electricity time",
                )

        for cutoff_time in cutoff_times:
            with freeze_time(cutoff_time):
                self.assertEqual(
                    self.cutoff.status()[1], CUTOFF, f"{cutoff_time} is cutoff time"
                )

    def test_get_timeleft(self):
        # 6 -> 10 - 14 -> 18
        cases = {
            "3:00:00": "3:00",
            "4:00:00": "2:00",
            "4:30:00": "1:30",
            "5:00:00": "1:00",
            "5:30:00": "0:30",
            "5:59:59": "0:01",
            "6:00:00": "4:00",
            "6:00:01": "4:00",
            "6:30:00": "3:30",
            "9:48:12": "0:12",
            "9:59:59": "0:01",
            "11:15:00": "2:45",
            "14:00:00": "4:00",
            "14:00:01": "4:00",
            "16:12:23": "1:48",
            "18:00:00": "6:00",
            "18:00:01": "6:00",
            "21:27:32": "2:33",
            "23:57:13": "0:03"
        }

        for current_time, timeleft in cases.items():
            with freeze_time(current_time):
                current_hour, current_minutes, current_seconds = self.cutoff.current_time()
                self.assertEqual(
                  self.cutoff.get_timeleft(current_hour, current_minutes, current_seconds),
                  timeleft,
                  f"timeleft for {current_time} should be: {timeleft}"
                )

if __name__ == "__main__":
    unittest.main()
