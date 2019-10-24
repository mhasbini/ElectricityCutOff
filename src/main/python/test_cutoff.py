import unittest
from datetime import datetime
from freezegun import freeze_time

from cutoff import CutOff, ELECTRICITY, CUTOFF

class CutOffTest(unittest.TestCase):
    def setUp(self):
        # 6-10am 2-6pm
        self.cutoff = CutOff(cutoff_range_index=0)

    def test_status(self):
        electricity_times = [
          "5:00:00", "5:59:59", "10:00:01", "12:00:01", "13:00:00", "13:30:00", "18:00:01", "19:00:01"
        ]

        cutoff_times = [
          "6:00:00", "6:00:01", "6:30:01", "7:12:34", "10:00:00", "14:00:00", "14:00:01", "17:59:59", "18:00:00"
        ]

        for electricity_time in electricity_times:
          with freeze_time(electricity_time):
            self.assertEqual(self.cutoff.status(), ELECTRICITY, f"{electricity_time} is electricity time")

        for cutoff_time in cutoff_times:
          with freeze_time(cutoff_time):
            self.assertEqual(self.cutoff.status(), CUTOFF, f"{cutoff_time} is cutoff time")

    def test_should_show_notification(self):
        truthy_times = [
          "6:00:00", "6:00:01", "10:00:00", "10:00:01", "14:00:00", "14:00:01", "18:00:00", "18:00:01"
        ]

        falsy_times = [
          "6:00:02", "6:01:01", "11:00:00", "5:00:01", "13:00:00", "19:00:01", "18:1:00", "17:59:59"
        ]

        for truthy_time in truthy_times:
          with freeze_time(truthy_time):
            self.assertTrue(self.cutoff.should_show_notification(), f"{truthy_time} should be true")

        for falsy_time in falsy_times:
          with freeze_time(falsy_time):
            self.assertFalse(self.cutoff.should_show_notification(), f"{falsy_time} should be false")


if __name__ == '__main__':
    unittest.main()
