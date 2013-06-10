from __future__ import absolute_import

import time

from ostrich import stats
from ostrich.timing import Timing, TimingStat
from ostrich.histogram import Histogram

class TimeSeries(object):
    def __init__(self, size, empty=0):
        self.data = [empty] * size
        self.size = size
        self.index = 0
    
    def add(self, n):
        self.data[self.index] = n
        self.index = (self.index + 1) % self.size
    
    def to_list(self):
        return self.data[self.index:] + self.data[:self.index]

class TimeSeriesCollector(object):
    def __init__(self):
        self.hourly = {}
        self.hourly_timings = {}
        self.last_collection = time.time()
        self.stats = stats.fork()
    
    def collect(self):
        def get_or_add(key, new=0, d=self.hourly):
            value = d.get(key)
            if value is None:
                value = TimeSeries(60, new)
                d[key] = value
            return value
        
        for k, v in stats.get_gauge_stats().items():
            get_or_add("gauge:%s" % k).add(v)
        
        for k, v in self.stats.get_counter_stats(reset=True).items():
            get_or_add("counter:%s" % k).add(v)
        
        for k, v in self.stats.get_timing_stats(reset=True).items():
            get_or_add("timing:%s" % k, None, d=self.hourly_timings).add(v)
        
        self.last_collection = time.time()
    
    def start_twisted(self, collect_every=60):
        from twisted.internet import task
        self.task = task.LoopingCall(self.collect)
        self.task.start(collect_every)
        return self.task
    
    def stop_twisted(self):
        self.task.stop()

    def get_combined(self, name, series=False):
        if name.startswith("counter:"):
            if series:
                return self.get(name)
            else:
                counter = self.stats.get_counter(name[8:]).get()
                if name in self.hourly:
                    counter += sum(self.hourly[name].to_list())
                return counter
        elif name.startswith("timing:"):
            timing = Timing()
            timing.add(self.stats.get_timing(name[7:]).get())
            if name in self.hourly_timings:
                for v in self.hourly_timings[name].to_list():
                    if v:
                        timing.add(v)
            return timing.get()
        else:
            raise NotImplemented("Only counters and timings supported")
    
    def get(self, name):
        times = [int(self.last_collection + ((i - 59) * 60)) for i in xrange(60)]
        if name.startswith("counter:"):
            return zip(times, self.hourly.get(name, TimeSeries(60, 0)).to_list()) \
                    + [(time.time(), self.stats.get_counter(name[8:]).get())]
        elif name.startswith("timing:"):
            return zip(times, [v or TimingStat(histogram=Histogram()) for v in self.hourly_timings.get(name, TimeSeries(60, None)).to_list()]) \
                    + [(time.time(), self.stats.get_timing(name[7:]).get())]
        else:
            raise NotImplemented("Only counters and timings supported")
    
    def keys(self):
        return self.hourly.keys() + self.hourly_timings.keys()
