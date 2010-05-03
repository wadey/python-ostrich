from ostrich.stats_provider import StatsProvider
from ostrich.timing import Timing

class StatsCollection(StatsProvider):
    def __init__(self):
        self.counters = {}
        self.timings = {}
    
    def add_timing(self, name, duration):
        self.get_timing(name).add(duration)
    
    def incr(self, name, count=1):
        self.get_counter(name).incr(count)
    
    def get_counter_stats(self, reset=False):
        return dict(map(lambda (k, counter): (k, counter.get(reset)), self.counters.items()))
    
    def get_timing_stats(self, reset=False):
        return dict(map(lambda (k, timing): (k, timing.get(reset)), self.timings.items()))
    
    def get_counter(self, name):
        counter = self.counters.get(name, None)
        if counter is None:
            counter = Counter()
            self.counters[name] = counter
        return counter
            
    
    def get_timing(self, name):
        timing = self.timings.get(name, None)
        if timing is None:
            timing = Timing()
            self.timings[name] = timing
        return timing
    
    def clear_all(self):
        self.counters.clear()
        self.timings.clear()

class Counter(object):
    def __init__(self):
        self.value = 0;
    
    def incr(self, n=1):
        self.value += n
        return self.value
    
    def __call__(self):
        return self.value
    
    def reset(self):
        self.value = 0
        return self.value
    
    def get(self, reset=False):
        try:
            return self.value
        finally:
            if reset:
                self.reset()
    
    def __eq__(self, other):
        return self.value == other.value