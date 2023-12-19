import heapq
import math
from collections import defaultdict
from typing import List, Literal

from termcolor import colored

EXAMPLE1 = """
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
""".strip()

Point = tuple[int, int]
Direction = Literal['N', 'S', 'W', 'E']
DIRECTIONS: dict[Direction, Point] = {
    'E': (1, 0),
    'W': (-1, 0),
    'N': (0, -1),
    'S': (0, 1),
}
ALLOWED_DIRECTIONS: dict[Direction, set[Direction]] = {
    'E': {'N', 'S', 'E'},
    'W': {'N', 'S', 'W'},
    'S': {'W', 'S', 'E'},
    'N': {'N', 'W', 'E'},
}

DIRECTION_POINTERS = {
    'N': '↑',
    'S': '↓',
    'E': '→',
    'W': '←',
}

def parse_grid(input: str) -> List[List[int]]:
    return [[int(c) for c in row] for row in input.split('\n')]

def solve2(grid: List[List[int]], start: Point, end: Point) -> int:
    score: dict[tuple[Point, str], int] = defaultdict(lambda: math.inf)

    def h(r: int, c: int) -> int:
        # return 0
        return abs(r - end[1]) + abs(c - end[0])

    frontier = [(h(*start), 0, (start[1], start[0]), [start], [])]
    seen_distances = {}

    while len(frontier):
        _, cost, p, path, directions = heapq.heappop(frontier)
        row, col = p

        if row == end[1] and col == end[0]:
            return path, directions, cost

        move_directions = ALLOWED_DIRECTIONS[directions[-1]] if len(directions) > 0 else DIRECTIONS.keys()

        for direction in move_directions:
            (colN, rowN) = DIRECTIONS[direction]
            move_factor = 1

            if directions and directions[-1] != direction:
                move_factor = 4

            new_row = row + rowN * move_factor
            new_col = col + colN * move_factor

            if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])):
                continue

            new_directions = directions + [direction]*move_factor

            new_cost = cost
            new_path = path.copy()

            d = h(new_row, new_col)
            if d not in seen_distances:
                print(h(new_row, new_col), cost)
                seen_distances[d] = True

            for i in range(1, move_factor+1):
                new_cost += grid[row + rowN*i][col + colN*i]
                new_path.append((row + rowN*i, col + colN*i))

            key = ((new_row, new_col), "".join(new_directions[-10:]))

            if (
                    (len(directions) < 10 or any(x != direction for x in directions[-10:]))
                    and new_cost < (score[key])
            ):
                score[key] = new_cost

                heapq.heappush(
                    frontier,
                    (
                        new_cost + h(new_row, new_col),
                        new_cost,
                        (new_row, new_col),
                        new_path,
                        new_directions
                    ))

def solve1(grid: List[List[int]], start: Point, end: Point) -> int:
    score: dict[tuple[Point, str], int] = defaultdict(lambda: math.inf)

    def h(r: int, c: int) -> int:
        # return 0
        return abs(r - end[1]) + abs(c - end[0])

    frontier = [(h(*start), 0, (start[1], start[0]), [start], [])]

    while len(frontier):
        _, cost, p, path, directions = heapq.heappop(frontier)
        row, col = p

        if row == end[1] and col == end[0]:
            print(path)
            print(directions)
            return path, directions, cost

        move_directions = ALLOWED_DIRECTIONS[directions[-1]] if len(directions) > 0 else DIRECTIONS.keys()

        for direction in move_directions:
            (colN, rowN) = DIRECTIONS[direction]
            new_row = row + rowN
            new_col = col + colN

            if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])):
                continue

            new_directions = directions + [direction]
            new_cost = cost + grid[new_row][new_col]
            new_path = path + [(new_row, new_col)]
            num_repeats = 0

            for i in range(len(new_directions) - 1, -1, -1):
                if new_directions[i] == new_directions[-1]:
                    num_repeats += 1
                else:
                    break

            # key = ((new_row, new_col), "".join(new_directions[-3:]))
            key = ((new_row, new_col), direction + "," + str(num_repeats))

            if (
                    (len(directions) < 3 or any(x != direction for x in directions[-3:]))
                    and new_cost < (score[key])
            ):
                score[key] = new_cost

                heapq.heappush(
                    frontier,
                    (
                        new_cost + h(new_row, new_col),
                        new_cost,
                        (new_row, new_col),
                        new_path,
                        new_directions
                    ))

def main():
    input = open('input.txt').read().strip()
    # input = EXAMPLE1
    grid = parse_grid(input)
    start = (0, 0)
    end = (len(grid) - 1, len(grid[0]) - 1)
    path, directions, cost = solve2(grid, start, end)
    d = dict(zip(path, directions))
    t = 0

    for i, row in enumerate(grid):
        for j, col in enumerate(row):
            if (i, j) in d:
                print(colored(DIRECTION_POINTERS[d[(i, j)]], 'red'), end='')
                t += col
            else:
                print(col, end='')
        print()


    print(cost, t)

if __name__ == '__main__':
    main()