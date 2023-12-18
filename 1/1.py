from typing import List, Dict, Tuple

INPUT_FILE = 'input.txt'

CHAR_DIGITS = {
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9
}

SPELLED_DIGITS = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9
}

DEFAULT_LUT = {**CHAR_DIGITS, **SPELLED_DIGITS}


def extract_digits(l: str, lut: Dict[str, int]) -> Tuple[int, int]:
    first: int = -1
    last: int = -1

    # Find the first digit
    i = 0
    while i < len(l) and first == -1:
        for k, v in lut.items():
            if l[i:].startswith(k):
                first = v

        i += 1

    # Find the last digit by scanning backwards
    i = len(l) - 1

    while i >= 0 and last == -1:
        for k, v in lut.items():
            if l[:i].endswith(k):
                last = v

        i -= 1

    return first, last


def main():
    # Read the file
    total = 0

    with open(INPUT_FILE) as f:
        while True:
            line = f.readline()

            if not line:
                break

            first, last = extract_digits(line, DEFAULT_LUT)

            print(line, first, last)

            total += (first * 10) + last

    print(total)


if __name__ == '__main__':
    main()
