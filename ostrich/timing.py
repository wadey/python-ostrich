import sys
import math
import threading

from ostrich.histogram import Histogram

class Timing(object):
    def __init__(self):
        self.max = 0
        self.min = sys.maxint
        self.count = 0
        self.histogram = Histogram()
        self.mean = 0.0
        self.partial_variance = 0.0
        self.lock = threading.Lock()
    
    def clear(self):
        """Resets the state of this Timing. Clears the durations and counts
        collected so far.
        """
        with self.lock:
            self.max = 0
            self.min = sys.maxint
            self.count = 0
            self.histogram.clear()

    def add(self, n):
        if isinstance(n, TimingStat):
            return self.add_timing_stat(n)
        else:
            return self.add_duration(n)
    
    def add_duration(self, n):
        """Adds a duration to our current Timing."""
        with self.lock:
            if n > -1:
                self.max = max(self.max, n)
                self.min = min(self.min, n)
                self.count += 1
                self.histogram.add(n)
                if self.count == 1:
                    self.mean = float(n)
                    self.partial_variance = 0.0
                else:
                    new_mean = self.mean + (n - self.mean) / self.count
                    self.partial_variance += (n - self.mean) * (n - new_mean)
                    self.mean = new_mean
            else:
                # TODO: warning?
                pass
            return self.count
    
    def add_timing_stat(self, timing_stat):
        """Add a summarized set of timings."""
        with self.lock:
            if timing_stat.count > 0:
                # (comment from Scala ostrich) these equations end up using the sum again, and may be lossy. i couldn't find or think of
                # a better way.
                new_mean = (self.mean * self.count + timing_stat.mean * timing_stat.count) / (self.count + timing_stat.count)
                self.partial_variance = self.partial_variance + timing_stat.partial_variance + \
                                        (self.mean - new_mean) * self.mean * self.count + \
                                        (timing_stat.mean - new_mean) * timing_stat.mean * timing_stat.count
                self.mean = new_mean
                self.count += timing_stat.count
                self.max = max(self.max, timing_stat.max)
                self.min = min(self.min, timing_stat.min)
                if timing_stat.histogram is not None:
                    self.histogram.merge(timing_stat.histogram)
    
    def get(self, reset=False):
        """Returns a TimingStat for the measured event."""
        with self.lock:
            try:
                return TimingStat(self.count, self.max, self.min, self.mean, self.partial_variance, self.histogram.clone())
            finally:
                if reset:
                    self.max = 0
                    self.min = sys.maxint
                    self.count = 0
                    self.histogram.clear()

class TimingStat(object):
    """A pre-calculated timing. If you have timing stats from an external source but
    still want to report them via the Stats interface, use this.
       
    Partial variance is `(count - 1)(s^2)`, or `sum(x^2) - sum(x) * mean`.
    """
    def __init__(self, count=0, max=0, min=0, mean=0.0, partial_variance=0.0, histogram=None):
        self.count = count
        self.min = min if count > 0 else 0
        self.max = max if count > 0 else 0
        self.average = int(mean) if count > 0 else 0
        self.mean = mean if count > 0 else 0.0
        self.partial_variance = partial_variance if count > 1 else 0.0
        self.variance = (partial_variance / (count - 1)) if count > 1 else 0.0
        self.std_dev = round(math.sqrt(self.variance))
        self.histogram = histogram
    
    def __eq__(self, other):
        return self.count == other.count and self.max == other.max and \
               self.min == other.min and self.average == other.average and self.variance == other.variance

    def to_raw_dict(self, histogram=False):
        d = dict(count=self.count, max=self.max, min=self.min,
                 mean=self.mean, partial_variance=self.partial_variance)
        if histogram and self.histogram:
            # strip off all the zeros at the end of the histogram
            histogram = list(self.histogram.buckets)
            while histogram and histogram[-1] == 0:
                histogram = histogram[:-1]
            d['histogram'] = histogram
        return d
    
    def to_dict_no_histogram(self):
        return dict(count=self.count, maximum=self.max, minimum=self.min,
                    average=self.average, standard_deviation=long(self.std_dev))
    
    def to_dict(self, percentiles=True, raw_histogram=False):
        d = self.to_dict_no_histogram()
        if self.histogram:
            h = self.histogram
            d.update(p25=h.get_percentile(0.25),
                     p50=h.get_percentile(0.50),
                     p75=h.get_percentile(0.75),
                     p90=h.get_percentile(0.90),
                     p99=h.get_percentile(0.99),
                     p999=h.get_percentile(0.999),
                     p9999=h.get_percentile(0.9999))
            if raw_histogram:
                # strip off all the zeros at the end of the histogram
                histogram = list(h.buckets)
                while histogram and histogram[-1] == 0:
                    histogram = histogram[:-1]
                d.update(histogram=histogram)
        return d

    @classmethod
    def from_raw_dict(cls, d, bucket_offsets=None):
        histogram = None
        if d.has_key('histogram'):
            histogram = Histogram.from_list(d['histogram'], bucket_offsets)
        return TimingStat(d['count'], d['max'], d['min'], d['mean'], d['partial_variance'], histogram)

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "(" + ", ".join(["%s=%d" % (k, v) for k, v in sorted(self.to_dict().items())]) + ")"
