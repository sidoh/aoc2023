from typing import List, Tuple

EXAMPLE1 = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
""".strip().split("\n")

EXAMPLE2 = """
....#........
.........#...
#............
.............
.............
........#....
.#...........
............#
.............
.............
.........#...
#....#.......
""".strip().split("\n")


def get_expansion_rows(grid: List[str]) -> List[int]:
    return [i for i, row in enumerate(grid) if all(x == '.' for x in row)]


def get_expansion_columns(grid: List[str]) -> List[int]:
    return [i for i in range(len(grid[0])) if all(row[i] == '.' for row in grid)]


def get_galaxy_locations(grid: List[str]) -> List[Tuple[int, int]]:
    return [(i, j) for i, row in enumerate(grid) for j, char in enumerate(row) if char == '#']


def expand_grid(grid: List[str]) -> List[str]:
    # columns that contain only dots
    columns_to_expand = get_expansion_columns(grid)
    rows_to_expand = get_expansion_rows(grid)

    new_grid = []

    for j, row in enumerate(grid):
        new_row = []
        for i, char in enumerate(row):
            if i in columns_to_expand:
                new_row.append('.')
            new_row.append(char)
        new_grid.append(new_row)

        if j in rows_to_expand:
            new_grid.append(['.' for _ in range(len(new_row))])

    return ["".join(row) for row in new_grid]

def solve_naive(grid: List[str]) -> int:
    expanded_grid = expand_grid(grid)
    galaxies = get_galaxy_locations(expanded_grid)

    # Enumerate distinct pairs of galaxies
    galaxy_pairs = [(galaxies[i], galaxies[j]) for i in range(len(galaxies)) for j in range(i+1, len(galaxies))]
    total_distance = 0

    for g1, g2 in galaxy_pairs:
        total_distance += abs(g1[0] - g2[0]) + abs(g1[1] - g2[1])

    return total_distance

def solve(grid: List[str], expansion_factor: int = 1_000_000) -> int:
    galaxies = get_galaxy_locations(grid)
    expanded_rows = get_expansion_rows(grid)
    expanded_cols = get_expansion_columns(grid)

    galaxy_pairs = [(galaxies[i], galaxies[j]) for i in range(len(galaxies)) for j in range(i+1, len(galaxies))]
    total_distance = 0

    for g1, g2 in galaxy_pairs:
        num_expanded_rows_crossed = len([row for row in expanded_rows if min(g1[0], g2[0]) < row < max(g1[0], g2[0])])
        num_expanded_columns_crossed = len([col for col in expanded_cols if min(g1[1], g2[1]) < col < max(g1[1], g2[1])])
        total_distance += abs(g1[0] - g2[0]) + abs(g1[1] - g2[1])
        total_distance += num_expanded_rows_crossed * (expansion_factor - 1)
        total_distance += num_expanded_columns_crossed * (expansion_factor - 1)

    return total_distance

def main():
    input = open('input.txt').read().strip().split("\n")
    # input = EXAMPLE1

    print(solve(input))

if __name__ == '__main__':
    main()