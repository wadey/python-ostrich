import unittest
import time

import mock

from ostrich import stats
from ostrich.time_series_collector import TimeSeriesCollector

real_time = time.time

class TimeSeriesCollectorTest(unittest.TestCase):
    def setUp(self):
        stats.clear_all()
        self.collector = TimeSeriesCollector()
    
    @mock.patch("time.time")
    def test_report_basic_stats(self, mock_time):
        my_time = real_time()
        mock_time.return_value = my_time
        
        stats.incr("cats")
        stats.incr("dogs", 3)
        self.collector.collect()
        my_time += 60
        mock_time.return_value = my_time
        stats.incr("dogs")
        self.collector.collect()
        
        data = self.collector.get("counter:dogs")
        self.assertEquals((my_time - (2 * 60), 0), data["counter:dogs"][57])
        self.assertEquals((my_time - 60, 3), data["counter:dogs"][58])
        self.assertEquals((my_time, 1), data["counter:dogs"][59])
    
