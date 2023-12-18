"""
will be in the form:
41 48 83 86 17 | 83 86  6 31 17  9 48 53

in the order:
winning_numbers | has_numbers
"""
from typing import Tuple, List


def parse_row(row: str) -> Tuple[List[int], List[int]]:
    winning_numbers, has_numbers = row.split('|')

    # split on multiple spaces
    winning_numbers = winning_numbers.strip().split(' ')
    winning_numbers = [int(n.strip()) for n in winning_numbers if len(n.strip())]

    has_numbers = has_numbers.strip().split(' ')
    has_numbers = [int(n.strip()) for n in has_numbers if len(n.strip())]

    return winning_numbers, has_numbers

def main():
    with open("input.txt") as f:
        lines = f.readlines()

    total_score = 0
    total_scratchers = 0

    # array of 1s equal to length of lines
    num_copies = [1 for _ in range(len(lines))]

    for i in range(len(lines)):
        line = lines[i]

        # split out "Card N: ..."
        card_id, line = line.split(':')
        card_num = int(card_id.split(' ')[-1].strip())

        winning, has = parse_row(line.strip())
        num_matches = len(set(has).intersection(set(winning)))

        # score is 2^(n-1)
        if num_matches > 0:
            total_score += 2 ** (num_matches - 1)

            for x in range(i+1, min(i+num_matches+1, len(lines))):
                num_copies[x] += num_copies[i]


    print("Total score:", total_score)
    print(num_copies)

    # num scratchers is sum of values in num_copies
    total_scratchers = sum(num_copies)
    print(total_scratchers)

if __name__ == "__main__":
    main()