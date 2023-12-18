from typing import List, Union, Tuple


class SchematicNumber:
    n: int
    symbol_adjacent: bool

    def __init__(self, n: int):
        self.n = n
        self.symbol_adjacent = False

    def add_digit(self, digit: int):
        self.n = self.n * 10 + digit

    def mark_symbol_adjacent(self):
        self.symbol_adjacent = True

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return str(self.n)

"""
# Schematic in this form:
# 467..114..
# ...*......
# ..35..633.
# ......#...
# 617*......
# .....+.58.
# ..592.....
# ......755.
# ...$.*....
# .664.598..
# encode as a NxM array where N is the number of lines, M is the length of each line
"""
def parse_schematic(input: str) -> List[List[str]]:
    lines = input.split('\n')
    schematic = []

    for line in lines:
        schematic.append(list(line))

    return schematic


def process_schematic(matrix: List[List[str]]) -> Tuple[List[List[str]], List[Tuple[int, int]], List[SchematicNumber]]:
    result: List[List[Union[str, SchematicNumber]]] = []
    symbol_positions: List[Tuple[int, int]] = []
    all_numbers: List[SchematicNumber] = []

    for row in range(len(matrix)):
        current_digit = None
        current_row: List[Union[str, SchematicNumber]] = []

        for col in range(len(matrix[row])):
            c = matrix[row][col]

            if c.isdigit():
                if current_digit is None:
                    current_digit = SchematicNumber(int(matrix[row][col]))
                    all_numbers.append(current_digit)
                else:
                    current_digit.add_digit(int(matrix[row][col]))
                current_row.append(current_digit)
            else:
                current_row.append(matrix[row][col])
                current_digit = None

                if c != '.':
                    symbol_positions.append((row, col))

        result.append(current_row)

    return result, symbol_positions, all_numbers

def main():
    # Read the file
    with open("input.txt") as f:
        input = parse_schematic(f.read())
        schemaic, symbol_positions, all_numbers = process_schematic(input)
        sum_ratios = 0

        print(schemaic)
        print(symbol_positions)
        print(all_numbers)

        for row, col in symbol_positions:
            adjacent_numbers = set()

            for rowN in [-1, 0, 1]:
                for colN in [-1, 0, 1]:
                    if rowN == 0 and colN == 0:
                        continue

                    if row + rowN < 0 or row + rowN >= len(schemaic):
                        continue

                    if col + colN < 0 or col + colN >= len(schemaic[row]):
                        continue

                    if isinstance(schemaic[row + rowN][col + colN], SchematicNumber):
                        adjacent_numbers.add(schemaic[row + rowN][col + colN])

            for number in adjacent_numbers:
                number.mark_symbol_adjacent()

            if schemaic[row][col] == '*':
                if len(adjacent_numbers) == 2:
                    g1, g2 = list(adjacent_numbers)
                    ratio = g1.n * g2.n

                    print(g1, g2)

                    sum_ratios += ratio

        sum_adjacent = 0

        for number in all_numbers:
            if number.symbol_adjacent:
                sum_adjacent += number.n

        print(sum_adjacent)
        print(sum_ratios)

if __name__ == '__main__':
    main()