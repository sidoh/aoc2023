from typing import List, Dict, TypedDict, Tuple, Optional

class RangeMapping:
    dest_start: int
    src_start: int
    range_len: int

    def __init__(self, dest_start: int, src_start: int, range_len: int):
        self.dest_start = dest_start
        self.src_start = src_start
        self.range_len = range_len
        self.dest_end = dest_start + range_len

    def in_range(self, n: int) -> bool:
        return self.src_start <= n < self.src_start + self.range_len

    def dest_in_range(self, n: int) -> bool:
        return self.dest_start <= n < self.dest_start + self.range_len

    def map(self, n: int) -> int:
        return self.dest_start + (n - self.src_start)

    def reverse_map(self, n: int) -> int:
        return self.src_start + (n - self.dest_start)

class MappedRange:
    """
    Represents a range of values from a domain B that have been mapped from a
    range of values in a domain A
    """
    start: int
    length: int
    source_ranges: List['MappedRange']

    def __init__(self, start: int, length: int):
        self.start = start
        self.length = length
        self.source_ranges = []

    def push_source_range(self, start: int, length: int) -> 'MappedRange':
        """
        Push a new source range onto the list of source ranges
        """
        new_range = MappedRange(start, length)
        self.source_ranges.append(new_range)
        return new_range

    def __str__(self):
        return "MappedRange(start={}, length={}, source_ranges={})".format(self.start, self.length, self.source_ranges)

    def __repr__(self):
        return self.__str__()

class RangeLookupTable:
    title: str
    ranges: List[RangeMapping]
    parent: Optional['RangeLookupTable']

    def __init__(self, ranges: List[RangeMapping], title: str, parent: Optional['RangeLookupTable'] = None):
        self.title = title
        self.ranges = ranges
        self.parent = parent

    def __getitem__(self, key: int) -> int:
        for range in self.ranges:
            if range.in_range(key):
                return range.map(key)

        return None

    def reverse_lookup(self, key: int) -> int:
        """
        Given a value, search for the input value that corresponds to it
        """
        # Default to identity
        mapped_value = key

        for range in self.ranges:
            if range.dest_in_range(key):
                mapped_value = range.reverse_map(key)
                break

        if self.parent is None:
            return mapped_value
        else:
            v = self.parent.reverse_lookup(mapped_value)
            return v

    def reverse_lookup_range(self, start: int, length: int) -> MappedRange:
        """
        Given a range of values, search for the input range that corresponds to it

        :param start:
        :param length:
        :return:
        """
        current_value = start
        end = start + length
        result = MappedRange(start, length)

        print("Looking for range {}-{} in {}".format(start, end, self.title))

        while current_value < end:
            # Find the range that contains current_value
            for range in self.ranges:
                if range.dest_in_range(current_value):
                    # Map the range
                    mapped_range_start = range.reverse_map(current_value)
                    # See how much of the remaining range will fit
                    mapped_range_end = min(range.dest_end, end)

                    # Push the range onto the result
                    result.push_source_range(mapped_range_start, mapped_range_end - mapped_range_start)

                    # Advance current_value to the end of the range
                    current_value = mapped_range_end

        # Now recurse on each of the source ranges if this isn't a root table
        if self.parent:
            for source_range in result.source_ranges:
                source_range.source_ranges = self.parent.reverse_lookup_range(source_range.start, source_range.length).source_ranges

        return result


class SeedIterator:
    seeds: List[int]
    current_index: int
    current_pair: int

    def __init__(self, seeds: List[int]):
        # These will come in pairs of the form (range_start, range_len)
        # Parse into pairs
        self.range_pairs = []

        for i in range(0, len(seeds), 2):
            self.range_pairs.append((seeds[i], seeds[i + 1]))

        self.current_pair = 0

    def __iter__(self):
        while self.current_pair < len(self.range_pairs):
            print("Processing pair {} of {}".format(self.current_pair, len(self.range_pairs)))
            yield self.range_pairs[self.current_pair]
            self.current_pair += 1

    def includes(self, n: int) -> bool:
        for range_start, range_len in self.range_pairs:
            if range_start <= n < range_start + range_len:
                return True

        return False
