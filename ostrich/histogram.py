import sys

class Histogram(object):
    BUCKET_OFFSETS = [1, 2, 3, 4, 5, 7, 9, 11, 14, 18, 24, 31, 40, 52, 67, 87, 113, 147, 191, 248,
          322, 418, 543, 706, 918, 1193, 1551, 2016, 2620, 3406, 4428, 5757, 7483,
          9728, 12647, 16441, 21373, 27784, 36119]
    
    @classmethod
    def _binary_search(cls, array, key, low, high):
        if low > high:
            return low
        else:
            mid = (low + high + 1) >> 1
            mid_val = array[mid]
            if mid_val < key:
                return cls._binary_search(array, key, mid + 1, high)
            elif mid_val > key:
                return cls._binary_search(array, key, low, mid - 1)
            else:
                # exactly equal to this bucket's value. but the value is an exclusive max, so bump it up.
                return mid + 1
    
    @classmethod
    def binary_search(cls, key):
        return cls._binary_search(cls.BUCKET_OFFSETS, key, 0, len(cls.BUCKET_OFFSETS) - 1)
    
    def __init__(self, *values):
        self.num_buckets = len(self.BUCKET_OFFSETS) + 1
        self.buckets = [0] * self.num_buckets
        self.total = 0
        if values:
            for val in values:
                self.add(val)
    
    def add(self, n):
        index = self.binary_search(n)
        self.buckets[index] += 1
        self.total += 1
    
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