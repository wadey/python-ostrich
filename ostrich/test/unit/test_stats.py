import sys
import time
import math
import unittest

from ostrich import stats, timing, histogram

class StatsTest(unittest.TestCase):
    def setUp(self):
        stats.clear_all()
    
    def test_counters(self):
        stats.incr("widgets", 1)
        stats.incr("wodgets", 12)
        stats.incr("wodgets")
        self.assertEquals({"widgets": 1, "wodgets": 13}, stats.get_counter_stats())
    
    def test_timings_empty(self):
        stats.add_timing("test", 0)
        test = stats.get_timing("test")
        self.assertEqual(timing.TimingStat(1, 0, 0), test.get(reset=True))
        # the timings list will be empty here:
        self.assertEqual(timing.TimingStat(0, 0, 0), test.get())
    
    def test_timings_basic(self):
        stats.add_timing("test", 1)
        stats.add_timing("test", 2)
        stats.add_timing("test", 3)
        test = stats.get_timing("test")
        self.assertEqual(timing.TimingStat(3, 3, 1, 2.0, 2.0, histogram.Histogram(1, 2, 3)), test.get())
    
    def test_timings_report(self):
        x = 0
        with stats.time("hundred"):
            for i in xrange(100):
                x += i
        timings = stats.get_timing_stats()
        self.assertEquals(["hundred"], timings.keys())
        self.assertEquals(1, timings["hundred"].count)
        self.assertEquals(timings["hundred"].average, timings["hundred"].min)
        self.assertEquals(timings["hundred"].average, timings["hundred"].max)
    
    def test_timings_average(self):
        stats.add_timing("test", 0)
        test = stats.get_timing("test")
        self.assertEquals(timing.TimingStat(1, 0, 0), test.get())
    
    def test_timings_negative(self):
        stats.add_timing("test", 1)
        stats.add_timing("test", -1)
        test = stats.get_timing("test")
        self.assertEquals(timing.TimingStat(1, 1, 1, 1.0, 0.0, histogram.Histogram(1)), test.get())
    
    def test_timing_boundarys(self):
        stats.add_timing("test", sys.maxint)
        stats.add_timing("test", 5)
        sum = 5.0 + sys.maxint
        avg = sum / 2.0
        sumsq = 5.0 * 5.0 + float(sys.maxint) * sys.maxint
        partial = sumsq - sum * avg
        test = stats.get_timing("test")
        self.assertEquals(timing.TimingStat(2, sys.maxint, 5, avg, partial, histogram.Histogram(5, sys.maxint)), test.get())
    
    def test_timing_with(self):
        with stats.time("test"):
            time.sleep(0.01)
        test = stats.get_timing("test")
        self.assertTrue(test.get().average >= 10)
    
    def test_timing_decorator(self):
        @stats.time("test")
        def _test_timing_decorator():
            time.sleep(0.01)
        _test_timing_decorator()
        test = stats.get_timing("test")
        self.assertTrue(test.get().average >= 10)
    
    def test_timing_reset(self):
        x = 0
        
        with stats.time("hundred"):
            for i in xrange(100): x += i
        self.assertEqual(1, stats.get_timing_stats(reset=False)["hundred"].count)
        with stats.time("hundred"):
            for i in xrange(100): x += i
        self.assertEqual(2, stats.get_timing_stats(reset=False)["hundred"].count)
        self.assertEqual(2, stats.get_timing_stats(reset=True)["hundred"].count)
        with stats.time("hundred"):
            for i in xrange(100): x += i
        self.assertEqual(1, stats.get_timing_stats(reset=False)["hundred"].count)
    
    def test_timing_bundle(self):
        timing_stat = timing.TimingStat(3, 20, 10, 15.0, 50.0, histogram.Histogram(10, 15, 20))
        stats.add_timing("test", timing_stat)
        stats.add_timing("test", 25)
        test = stats.get_timing_stats(reset=False)["test"]
        self.assertEqual(4, test.count)
        self.assertEqual(17, test.average)
        self.assertEqual(6, int(test.std_dev))
        
        stats.clear_all()
        
        timing_stat1 = timing.TimingStat(2, 25, 15, 20.0, 50.0, histogram.Histogram(15, 25))
        timing_stat2 = timing.TimingStat(2, 20, 10, 15.0, 50.0, histogram.Histogram(10, 20))
        stats.add_timing("test", timing_stat1)
        stats.add_timing("test", timing_stat2)
        test = stats.get_timing_stats(reset=False)["test"]
        self.assertEqual(4, test.count)
        self.assertEqual(17, test.average)
        self.assertEqual(6, int(test.std_dev))
    
    def test_timing_add(self):
        x = 0
        with stats.time("hundred"):
            for i in xrange(100): x += 1
        self.assertEquals(1, len(stats.get_timing_stats(reset=False)))
        
        stats.add_timing("foobar", timing.TimingStat(1, 0, 0))
        self.assertEquals(2, len(stats.get_timing_stats(reset=False)))
        self.assertEquals(1, stats.get_timing_stats(reset=True)["foobar"].count)
        stats.add_timing("foobar", timing.TimingStat(3, 0, 0))
        self.assertEquals(3, stats.get_timing_stats(reset=False)["foobar"].count)
    
    # TODO: not implemented
    # def test_timing_external(self):
    #     pass
    
    def test_timing_report_sorted(self):
        stats.add_timing("alpha", timing.TimingStat(1, 0, 0))
        string = str(stats.get_timing_stats(reset=False)["alpha"])
        self.assertEquals("(average=0, count=1, maximum=0, minimum=0, p25=0, p50=0, p75=0, p90=0, p99=0, p999=0, p9999=0, standard_deviation=0)", string)
    
    # TODO
    # def test_timing_json_contains_histogram_buckets(self):
    #    pass
    
    def test_gauge_report(self):
        @stats.gauge("pi")
        def _pi():
            return math.pi
        
        stats.make_gauge("e", lambda: math.e)
        self.assertEquals({"e": math.e, "pi": math.pi}, stats.get_gauge_stats())
    
    def test_gauge_update(self):
        potatoes = [100.0]
        @stats.gauge("stew")
        def _stew():
            potatoes[0] += 1.0
            return potatoes[0]
        self.assertEquals({"stew": 101.0}, stats.get_gauge_stats())
        self.assertEquals({"stew": 102.0}, stats.get_gauge_stats())
        self.assertEquals({"stew": 103.0}, stats.get_gauge_stats())

    # TODO
    # def test_gauge_derivative(self):
    #     pass
    
    # TODO
    # def test_fork(self):
    #     pass





