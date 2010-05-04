from ostrich.stats_provider import StatsProvider
from ostrich.stats_collection import StatsCollection
from ostrich.timing import TimingStat

class Stats(StatsProvider):
    def __init__(self):
        self.gauges = {}
        self.collection = StatsCollection()
    
    def add_timing(self, name, timing):
        return self.collection.add_timing(name, timing)
    
    def incr(self, name, count=1):
        return self.collection.incr(name, count)
    
    def get_counter_stats(self, reset=False):
        return self.collection.get_counter_stats(reset)
    
    def get_timing_stats(self, reset=False):
        return self.collection.get_timing_stats(reset)
    
    def get_gauge_stats(self):
        return dict(map(lambda (k, gauge): (k, gauge()), self.gauges.items()))
    
    def get_timing(self, name):
        return self.collection.get_timing(name)
    
    def get_counter(self, name):
        return self.collection.get_counter(name)
    
    def stats(self, reset=False):
        d = self.collection.stats(reset) 
        d.update(gauges=self.get_gauge_stats())
        return d
    
    def clear_all(self):
        self.collection.clear_all()
        self.gauges.clear()
    
    def make_gauge(self, name, func):
        self.gauges[name] = func

_stats = Stats()
add_timing = _stats.add_timing
incr = _stats.incr
get_counter_stats = _stats.get_counter_stats
get_timing_stats = _stats.get_timing_stats
get_gauge_stats = _stats.get_gauge_stats
get_timing = _stats.get_timing
get_counter = _stats.get_counter
clear_all = _stats.clear_all
make_gauge = _stats.make_gauge
stats = _stats.stats
time = _stats.time
time_ns = _stats.time_ns

def json_encoder(o):
    if isinstance(o, TimingStat):
        return o.to_dict(raw_histogram=True)
    else:
        raise TypeError(repr(o) + " is not JSON serializable")

def gauge(name):
    def _decorator(func):
        make_gauge(name, func)
        return func
    return _decorator