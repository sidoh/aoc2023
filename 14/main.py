from typing import List

EXAMPLES = [x.strip().split("\n") for x in [
"""
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....
"""
]]

def rotate(grid: List[str]) -> List[str]:
    return [''.join(x) for x in zip(*grid[::-1])]

def slide_rocks_north(grid: List[str]) -> List[str]:
    new_grid = []
    num_rocks = [0 for _ in range(len(grid[0]))]

    # Work backwards from the bottom row
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        new_row = []

        for j, char in enumerate(row):
            if char == 'O':
                num_rocks[j] += 1
            elif char == '#':
                for n in range(num_rocks[j]):
                    new_grid[n][j] = 'O'
                num_rocks[j] = 0

        for j, char in enumerate(row):
            if char == 'O':
                new_row.append('.')
            elif char == '#':
                new_row.append('#')
            else:
                new_row.append(char)

        new_grid = [new_row] + new_grid

    for i, n in enumerate(num_rocks):
        for j in range(n):
            new_grid[j][i] = 'O'

    return [''.join(row) for row in new_grid]

def compress_state(grid: List[str]) -> str:
    return "\n".join(grid)

def cycle_once(grid: List[str]) -> List[str]:
    for i in range(4):
        grid = slide_rocks_north(grid)
        grid = rotate(grid)
    return grid

def cycle(grid: List[str], times: int = 1) -> List[str]:
    state_map = {}
    current_state = compress_state(grid)

    for n in range(times):
        if current_state in state_map:
            state, n_loc = state_map[current_state]
            cycle_length = n - n_loc
            remaining = times - n

            for _ in range(remaining % cycle_length):
                grid = cycle_once(grid)

            return grid

        grid = cycle_once(grid)

        next_state = compress_state(grid)
        state_map[current_state] = (next_state, n)
        current_state = next_state
    return grid

def calculate_score(grid: List[str]) -> int:
    return sum(len(grid)-row_num for row_num, row in enumerate(grid) for char in row if char == 'O')

def solve1(grid: List[str]) -> int:
    return calculate_score(slide_rocks_north(grid))

def solve2(grid: List[str]) -> int:
    return calculate_score(cycle(grid, 1_000_000_000))

def main():
    input = open("input.txt").read().strip().split("\n")
    # input = EXAMPLES[0]

    print(solve1(input))
    print(solve2(input))

if __name__ == '__main__':
    main()