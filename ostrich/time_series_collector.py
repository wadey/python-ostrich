import time

from ostrich import stats

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
            data = map(v.histogram.get().get_percentile, [0.5, 0.75, 0.9, 0.99, 0.999, 0.9999])
            get_or_add("timing:%s" % k, [0, 0, 0, 0, 0, 0], d=self.hourly_timings).add(data)
        
        self.last_collection = time.time()
    
    def get(self, name):
        times = [self.last_collection + ((i - 59) * 60) for i in xrange(60)]
        if name in self.hourly:
            data = zip(times, self.hourly[name].to_list())
            return {name: data}
        else:
            data = zip(times, self.hourly_timings)
    
    def keys(self):
        return self.hourly.keys() + self.hourly_timings.keys()