from bisect import bisect
import sys

class Histogram(object):
    BUCKET_OFFSETS = [1, 2, 3, 4, 5, 7, 9, 11, 14, 18, 24, 31, 40, 52, 67, 87, 113, 147, 191, 248,
          322, 418, 543, 706, 918, 1193, 1551, 2016, 2620, 3406, 4428, 5757, 7483,
          9728, 12647, 16441, 21373, 27784, 36119, 46955, 61041, 79354, 103160, 134107,
          174339, 226641, 294633, 383023, 497930, 647308, 841501, 1093951]
    
    def __init__(self, *values):
        self.num_buckets = len(self.BUCKET_OFFSETS) + 1
        self.buckets = [0] * self.num_buckets
        self.total = 0
        if values:
            for val in values:
                self.add(val)

    @classmethod
    def from_list(cls, buckets, bucket_offsets=None):
        """This method will be lossy if the bucket_offsets are different"""
        if not bucket_offsets:
            bucket_offsets = cls.BUCKET_OFFSETS
        h = cls()
        if bucket_offsets == cls.BUCKET_OFFSETS:
            for i, v in enumerate(buckets):
                h.buckets[i] = v
            h.total = sum(buckets)
        else:
            for i, v in enumerate(buckets):
                # hack because binary_search does an exclusive max
                h.add(bucket_offsets[i]-1, v)
        return h
    
    def add(self, n, count=1):
        index = bisect(self.BUCKET_OFFSETS, n)
        self.buckets[index] += count
        self.total += count
    
    def clear(self):
        for i in range(self.num_buckets):
            self.buckets[i] = 0
        self.total = 0

    def get_percentile(self, percentile):
        sum = 0
        index = 0
        while sum < percentile * self.total:
            sum += self.buckets[index]
            index += 1
        
        if index == 0:
            return 0
        elif index - 1 >= len(self.BUCKET_OFFSETS):
            return sys.maxint
        else:
            return self.BUCKET_OFFSETS[index - 1] - 1
    
    def merge(self, other):
        for i in range(self.num_buckets):
            self.buckets[i] += other.buckets[i]
        self.total += other.total
    
    def clone(self):
        new = Histogram()
        new.merge(self)
        return new
