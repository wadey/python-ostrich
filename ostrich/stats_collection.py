import threading

from ostrich.stats_provider import StatsProvider
from ostrich.timing import Timing

class StatsCollection(StatsProvider):
    def __init__(self):
        self.counters = {}
        self.timings = {}
        self.counters_lock = threading.Lock()
        self.timings_lock = threading.Lock()
    
    def add_timing(self, name, duration):
        self.get_timing(name).add(duration)
    
    def incr(self, name, count=1):
        self.get_counter(name).incr(count)
    
    def get_counter_stats(self, reset=False):
        with self.counters_lock:
            return dict(map(lambda (k, counter): (k, counter.get(reset)), self.counters.items()))
    
    def get_timing_stats(self, reset=False):
        with self.timings_lock:
            return dict(map(lambda (k, timing): (k, timing.get(reset)), self.timings.items()))
    
    def get_counter(self, name):
        counter = self.counters.get(name, None)
        if counter is None:
            with self.counters_lock:
                counter = self.counters.get(name, None)
                if counter is None:
                    counter = Counter()
                    self.counters[name] = counter
        return counter
            
    
    def get_timing(self, name):
        timing = self.timings.get(name, None)
        if timing is None:
            with self.timings_lock:
                timing = self.timings.get(name, None)
                if timing is None:
                    timing = Timing()
                    self.timings[name] = timing
        return timing
    
    def clear_all(self):
        with self.counters_lock:
            self.counters.clear()
        with self.timings_lock:
            self.timings.clear()

class Counter(object):
    def __init__(self):
        self.value = 0;
        self.lock = threading.Lock()
    
    def incr(self, n=1):
        with self.lock:
            self.value += n
            return self.value
    
    def __call__(self):
        return self.value
    
    def reset(self):
        with self.lock:
            self.value = 0
            return self.value
    
    def get(self, reset=False):
        if reset:
            with self.lock:
                try:
                    return self.value
                finally:
                    self.value = 0
        else:
            return self.value
    
    def __eq__(self, other):
        return self.value == other.value
