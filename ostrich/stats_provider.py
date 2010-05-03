import time

from decorator import decorator

class StatsProvider(object):
    def time(self, name):
        """Returns a Timer that logs the duration, in milliseconds, with the given name."""
        return Timer(self, name)
    
    def time_ns(self, name):
        """Returns a Timer that logs the duration, in nanoseconds, with the given name.
        
        When using nanoseconds, be sure to encode your field with that fact. Consider
        using the suffix `_ns` in your field.
        """
        return Timer(self, name)
    
    def stats(self, reset=False):
        return dict(counters=self.get_counter_stats(reset), timings=self.get_timing_stats(reset))

    ##
    ##
    ##

    def add_timing(self, name, timing):
        return 0
    
    def incr(self, name, count=1):
        return count
    
    def get_counter_stats(self, reset=False):
        return {}
    
    def get_timing_stats(self, reset=False):
        return {}
    
    def clear_all(self):
        pass

class Timer(object):
    def __init__(self, provider, key, nano=False):
        self.provider = provider
        self.key = key
        self.nano = nano

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, tb):
        self.end = time.time()
        if self.nano:
            self.provider.add_timing(self.key, int(self.duration() * 1000000000))
        else:
            self.provider.add_timing(self.key, int(self.duration() * 1000))

    def duration(self):
        return self.end - self.start

    def __call__(self, f):
        def _decorator(func, *args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return decorator(_decorator, f)