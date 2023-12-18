from typing import List, Optional, Tuple

EXAMPLE1 = """
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
""".strip()

def find_mirrored_row(grid: List[str], n: int = 0):
    for i in range(1, len(grid)):
        # Length of the mirror given we start at this location. Will be the shorter of moving back to the
        # start or ahead to the end
        half_length = min(i, len(grid)-i)

        p1 = grid[i - half_length:i]
        # Reverse to make it easy to compare
        p2 = grid[i:i+half_length][::-1]

        if num_smudges(p1, p2) == n:
            return i

    return 0

def transpose(grid: List[str]) -> List[str]:
    return [''.join(x) for x in zip(*grid)]

def num_smudges(p1: List[str], p2: List[str]) -> int:
    return sum(1 if p1[i][j] != p2[i][j] else 0 for i in range(len(p1)) for j in range(len(p1[0])))

def solve(grid: List[str], n: int) -> int:
    if len(grid) == 0:
        return 0

    # Find the mirrored row and column
    mirrored_row = find_mirrored_row(grid, n)
    mirrored_column = find_mirrored_row(transpose(grid), n)

    return 100*(mirrored_row) + mirrored_column


def main(input: str, n: int) -> int:
    lines = input.strip().split("\n")
    grid = []
    total = 0

    for l in lines:
        if len(l) > 0:
            grid.append(l)
        else:
            total += solve(grid, n)
            grid = []

    total += solve(grid, n)

    return total

if __name__ == '__main__':
    input = open('input.txt').read().strip()
    # input = EXAMPLE1
    print("Part 1:", main(input, 0))
    print("Part 2:", main(input, 1))
