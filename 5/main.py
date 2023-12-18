import re
from typing import List, Dict, TypedDict, Tuple, Optional
from range import RangeMapping, RangeLookupTable, SeedIterator


"""
Input is in the format:

dest_start src_start range_len
"""
def parse_map(input_lines: List[str], title: str, parent: RangeLookupTable = None) -> RangeLookupTable:
    result = []

    for line in input_lines:
        dest_start, src_start, range_len = line.split(' ')
        dest_start = int(dest_start)
        src_start = int(src_start)
        range_len = int(range_len)

        result.append(RangeMapping(dest_start=dest_start, src_start=src_start, range_len=range_len))

    return RangeLookupTable(result, title=title, parent=parent)


def main():
    with open("input.txt") as f:
        # First line is the list of seeds in the form "seeds: 1 2 3 4 5"
        raw_seeds = [int(x) for x in f.readline().split(' ')[1:]]
        seeds = SeedIterator(raw_seeds)

        # Expect a blank line
        f.readline()

        # expect lookup tables to be consecutive
        lookup_tables = []

        while True:
            line = f.readline()

            if not line:
                break

            # Expect first line in block to be a label of the form X-to-Y map
            # (extract X and Y via regex)
            matches = re.match(r'([a-z]+)-to-([a-z]+) map:', line)

            if not matches:
                raise Exception("Invalid input: expected label, line was: {}".format(line))

            source_label = matches.group(1)
            dest_label = matches.group(2)

            # Read until blank line
            buffer = []

            while True:
                line = f.readline()

                if not line or line == '\n':
                    break

                buffer.append(line.strip())

            # Parse the map
            print("buffer for {}-to-{}:".format(source_label, dest_label))
            lut = parse_map(buffer, "{}->{}".format(source_label, dest_label), None if len(lookup_tables) == 0 else lookup_tables[-1])
            lookup_tables.append(lut)

        # Find smallest location that has a seed
        # i = 0
        # while True:
        #     val = lookup_tables[-1].reverse_lookup(i)
        #     has_seed = seeds.includes(val)
        #
        #     if has_seed:
        #         print("works: {}".format(i))
        #         break
        #     else:
        #         i += 1
        print(lookup_tables[-1].reverse_lookup_range(0, 10000))


if __name__ == "__main__":
    main()
