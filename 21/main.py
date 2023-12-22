import hashlib
import json
import math
import pickle
import sys
from collections import deque
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal, cast, Optional, Iterable, Deque

from termcolor import colored

EXAMPLE1 = ("""
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........
""")

GridSymbol = Literal['.', '#', 'S']
Edge = Literal['left', 'right', 'top', 'bottom']
Grid = list[list[GridSymbol]]
Point = tuple[int, int]

def parse(input: str) -> tuple[Grid, Point]:
    grid = [[cast(GridSymbol, char) for char in line.strip()] for line in input.strip().split('\n')]
    start_point = None

    for i, row in enumerate(grid):
        for j, char in enumerate(row):
            if char == 'S':
                start_point = (i, j)

    return grid, start_point

def solve1(input: str, steps: int, *, starts: list[Point] = None, infinite: bool = False, verbose: bool = False) -> tuple[int, dict[int, dict[int, int]]]:
    grid, _start = parse(input)

    queue: Deque[tuple[Point, int]] = deque()
    reachable: dict[Point, set[int]] = defaultdict(set)

    def log(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    if starts is None:
        starts = [_start]

    queue.extend((start, 0) for start in starts)
    max_distance = 0

    while queue:
        (i, j), distance = queue.popleft()

        if distance > max_distance:
            max_distance = distance
            log("new max distance:", max_distance)

        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_i = i + di
            new_j = j + dj
            new_point = (new_i, new_j)

            if not infinite and not (0 <= new_i < len(grid) and 0 <= new_j < len(grid[0])):
                continue

            if grid[new_i % len(grid)][new_j % len(grid[0])] == '#':
                continue

            if distance < steps and (distance + 1) not in reachable[new_point]:
                queue.append((new_point, distance + 1))
                reachable[new_point].add(distance + 1)

    i_bounds = (min(point[0] for point in reachable), max(point[0] for point in reachable))
    j_bounds = (min(point[1] for point in reachable), max(point[1] for point in reachable))

    # for i in range(i_bounds[0], i_bounds[1] + 1):
    #     if i % len(grid) == 0:
    #         super_coord = f'({str(i // len(grid))})'
    #
    #         for j in range(j_bounds[0], j_bounds[1] + 1):
    #             ix = j % len(grid[0])
    #
    #             if ix == 0:
    #                 log('-+', end='')
    #             elif ix == (len(grid[0]) // 2):
    #                 if len(super_coord) % 2 == 0:
    #                     log('-', end='')
    #                 log(super_coord, end='')
    #             elif abs(ix - (len(grid[0]) // 2)) > (len(super_coord) // 2):
    #                 log('-', end='')
    #         log()
    #
    #     total = 0
    #     for j in range(j_bounds[0], j_bounds[1] + 1):
    #         cell = grid[i%len(grid)][j%len(grid[0])]
    #
    #         if j % len(grid[0]) == 0:
    #             log('|', end='')
    #
    #         if cell == '#':
    #             log('#', end='')
    #         elif cell == 'S':
    #             log(colored('S', 'white', on_color='on_green', attrs=['bold']), end='')
    #         elif not reachable[(i, j)]:
    #             log('.', end='')
    #         else:
    #             total += 1
    #             if steps in reachable[(i, j)]:
    #                 log(colored('O', 'red'), end='')
    #             else:
    #                 log(colored('*', 'blue'), end='')
    #
    #     log('|', total)
    #
    # log("[", colored("*", 'blue'), "] reachable in fewer but not exactly", steps, "steps")
    # log("[", colored("@", 'red'), "] reachable in exactly", steps, "steps")

    # reachable by supercoord row
    row_counts = defaultdict(int)
    for i in range(i_bounds[0], i_bounds[1] + 1):
        row_counts[i // len(grid)] += len([j for j in range(j_bounds[0], j_bounds[1] + 1) if steps in reachable[(i, j)]])

    # reachable by supercoord column
    col_counts = defaultdict(int)
    for j in range(j_bounds[0], j_bounds[1] + 1):
        col_counts[j // len(grid[0])] += len([i for i in range(i_bounds[0], i_bounds[1] + 1) if steps in reachable[(i, j)]])

    log("row counts:", row_counts)
    log("col counts:", col_counts)

    cell_counts = defaultdict(lambda: defaultdict(int))
    for i in range(i_bounds[0], i_bounds[1] + 1):
        for j in range(j_bounds[0], j_bounds[1] + 1):
            cell_counts[i // len(grid)][j // len(grid[0])] += 1 if steps in reachable[(i, j)] else 0

    log("cell counts:", cell_counts)
    for x in sorted(cell_counts.keys()):
        log('|', end='')
        total = 0
        for y in sorted(cell_counts[x].keys()):
            c = cell_counts[x][y]
            s = ("" if c == 0 else str(c)).center(10)
            s = colored(s, 'red') if c in [39, 42] else s
            total += c

            log(f'{s}|', end='')
        log(' ', total)
        log('-' * (10 * (len(cell_counts[x]) + 1)))

    return sum(1 for point, distances in reachable.items() if steps in distances), cell_counts

def flood_fill_partitions(grid: Grid) -> list[set[Point]]:
    visited: set[Point] = set()
    partitions: list[set[Point]] = []

    def flood_fill(start_x: int, start_y: int) -> set[Point]:
        fringe = [(start_x, start_y)]
        local_visited = set()

        while len(fringe):
            x, y = fringe.pop()
            local_visited.add((x, y))

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x = x + dx
                new_y = y + dy

                if not (0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid)):
                    continue

                if grid[new_y][new_x] == '#':
                    continue

                if (new_x, new_y) not in visited and (new_x, new_y) not in local_visited:
                    fringe.append((new_x, new_y))
                    local_visited.add((new_x, new_y))

        return local_visited

    while len(visited) != len(grid) * len(grid[0]):
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == '#':
                    visited.add((x, y))
                    continue
                elif (x, y) not in visited:
                    visited_batch = flood_fill(x, y)

                    if visited_batch:
                        partitions.append(visited_batch)

                    visited |= visited_batch

    return partitions

def all_points_shortest_path(grid: Grid, start: Point) -> dict[Point, int]:
    queue: list[tuple[Point, int]] = [(start, 0)]
    shortest_distance: dict[Point, int] = {}

    while queue:
        (i, j), distance = queue.pop(0)

        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_i = i + di
            new_j = j + dj
            new_point = (new_i, new_j)

            if not (0 <= new_i < len(grid) and 0 <= new_j < len(grid[0])):
                continue

            if grid[new_i][new_j] == '#':
                continue

            if new_point not in shortest_distance:
                shortest_distance[new_point] = distance + 1
                queue.append((new_point, distance + 1))

    return shortest_distance

@dataclass
class GridStats:
    # number of blank cells reachable from the start point after N steps. this will be filled out for every
    # step count up until the cycle starts
    reachable_counts: dict[int, int]

    # shortest paths from start
    distances_from_start: dict[Point, int]

    # points unreachable after any number of steps
    unreachable_points: set[Point]

    # step cycle when starting from each corner
    corner_step_counts: dict[Point, dict[int, int]]

    # step cycle when starting from both corners in each edge
    edge_step_counts: dict[Edge, dict[int, int]]

    # all edge points
    left_edges: list[Point]
    right_edges: list[Point]
    top_edges: list[Point]
    bottom_edges: list[Point]
    edges: list[Point]

    # shortest paths when starting from each edge point
    shortest_paths_from_edges: dict[Point, dict[Point, int]]

def find_step_cycle(input: str, start_points: Optional[list[Point]] = None) -> dict[int, int]:
    step_counts: dict[int, int] = {}
    num_steps = 1

    while True:
        print("computing step", num_steps)

        step_count = solve1(input, num_steps, starts=start_points)
        step_counts[num_steps] = step_count
        num_steps += 1

        # cycle detection: [-4, -3] == [-2, -1]
        if len(step_counts) >= 4 and list(step_counts.values())[-4:-2] == list(step_counts.values())[-2:]:
            print("found cycle at", num_steps, "steps")
            break

    return step_counts

@dataclass
class InfiniteGridState:
    center_row_sum: int
    above_row_sum: int
    above_row_len: int
    below_row_sum: int
    below_row_len: int

    bottom_residue: int
    bottom_residue_len: int

    top_residue: int
    top_residue_len: int

    grid_values: dict[int, dict[int, int]]

def non_zero_len(l: Iterable[int]) -> int:
    return len(list(filter(lambda x: x != 0, l)))

def compute_grid_states(input: str, compute_values: list[int]) -> tuple[dict[int, InfiniteGridState], list[int]]:
    v = {}
    for i in compute_values:
        _, d = solve1(input, i, infinite=True)
        v[i] = d

    cycle_values = [v[compute_values[0]][0][0], v[compute_values[0]][0][1]]
    states = {}

    for i in compute_values:
        top_residue = 0
        top_residue_len = 0

        for j in sorted(v[i].keys()):
            # residue is when either cycle value is not present
            if any(x not in v[i][j].values() for x in cycle_values):
                top_residue += sum(v[i][j].values())
                top_residue_len = max(top_residue_len, non_zero_len(v[i][j].values()))
            else:
                break

        bottom_residue = 0
        bottom_residue_len = 0

        for j in sorted(v[i].keys(), reverse=True):
            # residue is when either cycle value is not present
            if any(x not in v[i][j].values() for x in cycle_values):
                bottom_residue += sum(v[i][j].values())
                bottom_residue_len = max(bottom_residue_len, non_zero_len(v[i][j].values()))
            else:
                break

        states[i] = InfiniteGridState(
            center_row_sum=sum(v[i][0].values()),
            above_row_sum=sum(v[i][-1].values()),
            below_row_sum=sum(v[i][1].values()),
            above_row_len=non_zero_len(v[i][-1].values()),
            below_row_len=non_zero_len(v[i][1].values()),
            bottom_residue=bottom_residue,
            bottom_residue_len=bottom_residue_len,
            top_residue=top_residue,
            top_residue_len=top_residue_len,
            grid_values=v[i]
        )

    return states, cycle_values


def compute_grid_stats(input: str) -> GridStats:
    """
    I ended up not using this, but it was useful for learning

    Find the following:
        - How many steps you need to reach any point in the grid except those that are unreachable
        - smallest number of steps to reach every edge position of the grid

    :param input:
    :return:
    """
    grid, start = parse(input)

    # return pickled results if they exist
    input_hash = hashlib.md5(input.encode('utf-8')).hexdigest()
    filename = f"{len(grid[0])}x{len(grid)}-{input_hash}.pickle"

    try:
        # md5 hash input string to get the filename
        return pickle.load(open(filename, 'rb'))
        pass
    except FileNotFoundError:
        pass

    # find step counts until there are repeats for start point
    step_counts = find_step_cycle(input)

    # find step counts when starting at each of the corners
    corners = [(0, 0), (0, len(grid[0]) - 1), (len(grid) - 1, 0), (len(grid) - 1, len(grid[0]) - 1)]
    corner_step_counts: dict[Point, dict[int, int]] = {p: find_step_cycle(input, start_points=[p]) for p in corners}

    # find step counts when starting from two corners on the same edge
    edge_corners: dict[Literal['left', 'right', 'top', 'bottom'], list[Point]] = {
        'left': [(0, 0), (len(grid) - 1, 0)],
        'right': [(0, len(grid[0]) - 1), (len(grid) - 1, len(grid[0]) - 1)],
        'top': [(0, 0), (0, len(grid[0]) - 1)],
        'bottom': [(len(grid) - 1, 0), (len(grid) - 1, len(grid[0]) - 1)]
    }
    edge_step_counts: dict[Edge, dict[int, int]] = {
        edge: find_step_cycle(input, start_points=edge_corners[edge])
        for edge in edge_corners
    }

    # any partitions that don't contain the start point are unreachable
    partitions = flood_fill_partitions(grid)
    unreachable_points = set().union(*[partition for partition in partitions if start not in partition])
    total_blank_cells = sum(1 for row in grid for cell in row if cell == '.')

    shortest_distance = all_points_shortest_path(grid, start)

    # shortest min
    shortest_max = max(shortest_distance.values())
    print("longest point:", shortest_max, "steps")

    # edges
    top_edges = [(0, i) for i in range(len(grid))]
    bottom_edges = [(len(grid) - 1, i) for i in range(len(grid))]
    left_edges = [(i, 0) for i in range(len(grid[0]))]
    right_edges = [(i, len(grid[0]) - 1) for i in range(len(grid[0]))]

    edges = {
        'left': left_edges,
        'right': right_edges,
        'top': top_edges,
        'bottom': bottom_edges
    }

    # print all edge lengths
    print("--- edge lengths stats ---")
    edge_distances = {}
    for edge_name, edge in edges.items():
        edge_lengths = [shortest_distance[point] for point in edge]
        print(edge_name)
        print("  min:", min(edge_lengths), "at", edge[edge_lengths.index(min(edge_lengths))])
        print("  max:", max(edge_lengths), "at", edge[edge_lengths.index(max(edge_lengths))])

        min_distance = math.inf
        min_point = None
        best_edge_distances = None

        # what happens when we start at the edge?
        for point in edge:
            distances = all_points_shortest_path(grid, point)
            edge_distances[point] = distances
            d = max(distances.values())

            if d < min_distance:
                min_distance = d
                min_point = point
                best_edge_distances = distances

        print("  best starting point:", min_distance, "steps at", min_point)
        print("  other edge distances:")

        for other_edge_name, other_edge in edges.items():
            if other_edge_name == edge_name:
                continue

            other_edge_lengths = [best_edge_distances[point] for point in other_edge]
            print("    ", other_edge_name)
            print("      min:", min(other_edge_lengths), "at", other_edge[other_edge_lengths.index(min(other_edge_lengths))])
            print("      max:", max(other_edge_lengths), "at", other_edge[other_edge_lengths.index(max(other_edge_lengths))])

    stats = GridStats(
        reachable_counts=step_counts,
        distances_from_start=shortest_distance,
        left_edges=left_edges,
        right_edges=right_edges,
        top_edges=top_edges,
        bottom_edges=bottom_edges,
        edges=[point for edge in edges.values() for point in edge],
        edge_step_counts=edge_step_counts,
        corner_step_counts=corner_step_counts,
        shortest_paths_from_edges=edge_distances,
        unreachable_points=unreachable_points
    )

    pickle.dump(stats, open(filename, 'wb'))
    return stats

def solve2(input: str, steps: int) -> int:
    grid, start = parse(input)
    stats = compute_grid_stats(input)

    # will take this many steps to start cycling
    cycle_start = len(stats.reachable_counts) - 2
    cycle_parity = cycle_start % 2

    # start grid will have this many reachable
    main_grid_reachable = stats.reachable_counts[cycle_start + ((cycle_parity + steps) % 2)]

    # how many grids 1 step away? find the first point on each edge to be reached
    shortest_left = min(stats.distances_from_start[point] for point in stats.left_edges)
    shortest_right = min(stats.distances_from_start[point] for point in stats.right_edges)
    shortest_top = min(stats.distances_from_start[point] for point in stats.top_edges)
    shortest_bottom = min(stats.distances_from_start[point] for point in stats.bottom_edges)

    # print corner step counts
    print("--- corner step counts ---")
    for corner, step_counts in stats.corner_step_counts.items():
        print(corner)
        print(" ".join([str(x).rjust(4) for x in list(step_counts.values())[:20]]))
    # print edge step counts
    print("--- edge step counts ---")
    for edge, step_counts in stats.edge_step_counts.items():
        print(edge)
        print(" ".join([str(x).rjust(4) for x in list(step_counts.values())[:20]]))

    return main_grid_reachable
    pass

def expand_infinite_grid_state(
        steps: int,
        start: int,
        cycle_length: int,
        cycle_values: list[int],
        ec_state: InfiniteGridState
) -> int:
    """
    Takes in the state of the infinite grid after a number of steps equivalent to the # of steps % cycle_length and
    expands it to match the number of steps given.

    Example:
        |          |          |          |    1     |    4     |    1     |          |          |          |  6
        ----------------------------------------------------------------------------------------------------
        |          |          |    1     |    21    |    39    |    25    |    1     |          |          |  87
        ----------------------------------------------------------------------------------------------------
        |          |    1     |    21    |    42    |    39    |    42    |    25    |    1     |          |  171
        ----------------------------------------------------------------------------------------------------
        |    1     |    21    |    42    |    39    |    42    |    39    |    42    |    25    |    1     |  252
        ----------------------------------------------------------------------------------------------------
        |    4     |    35    |    39    |    42    |    39    |    42    |    39    |    33    |    2     |  275
        ----------------------------------------------------------------------------------------------------
        |    1     |    21    |    42    |    39    |    42    |    39    |    41    |    12    |          |  237
        ----------------------------------------------------------------------------------------------------
        |          |    1     |    21    |    42    |    39    |    41    |    12    |          |          |  156
        ----------------------------------------------------------------------------------------------------
        |          |          |    1     |    21    |    35    |    12    |          |          |          |  69
        ----------------------------------------------------------------------------------------------------
        |          |          |          |    1     |    2     |          |          |          |          |  3
        ----------------------------------------------------------------------------------------------------
    Each cell above corresponds to a full copy of the input grid. The number in the cell is the number of
    positions in that grid reachable in the given number of steps.

    After each increase in step count, the values 39/42 swap (these are cycle_values). The other numbers will
    change, but the edges will revert to the same numbers after cycle_length steps.

    We expand this grid to steps by adding multiples of 39+42 to the center row, above row, and below row.
    The top and bottom rows which do not have both 39 and 42 are added as "residue" to the total.

    :param steps:
    :param start:
    :param cycle_length:
    :param cycle_values:
    :param ec_state:
    :return:
    """
    iters = (steps - start) // cycle_length
    extra_values = sum(cycle_values) * iters
    center_row = ec_state.center_row_sum + extra_values
    above_row = ec_state.above_row_sum + extra_values
    below_row = ec_state.below_row_sum + extra_values

    total = center_row + above_row + below_row

    l = (ec_state.above_row_len + 2*iters - 2)
    a = above_row

    while l > ec_state.top_residue_len:
        a -= sum(cycle_values)
        l -= 2
        total += a

    l = (ec_state.below_row_len + 2*iters - 2)
    b = below_row

    while l > ec_state.bottom_residue_len:
        b -= sum(cycle_values)
        l -= 2
        total += b

    total += ec_state.top_residue + ec_state.bottom_residue

    return total



def main():
    input = open('input.txt').read().strip()
    # input = EXAMPLE1.strip()

    # print(solve1(input, 50, infinite=True))
    # print(solve1(input, 5002))

    # if CLI argument exists, use that as number of steps. otherwise default to 50
    # steps = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    # print(solve2(input, steps))

    answer, _ = solve1(input, 64)
    print("part 1 =", answer)

    part2_steps = 26_501_365
    grid, _ = parse(input)
    cycle_start = len(grid[0])*4
    cycle_length = len(grid[0])

    equivalent_n = cycle_start + (part2_steps % cycle_length)
    states, cycle_values = compute_grid_states(input, [equivalent_n])
    cell_counts = states[equivalent_n].grid_values

    for x in sorted(cell_counts.keys()):
        print('|', end='')
        total = 0
        for y in sorted(cell_counts[x].keys()):
            c = cell_counts[x][y]
            st = ("" if c == 0 else str(c)).center(10)
            st = colored(st, 'red') if c in cycle_values else st
            total += c

            print(f'{st}|', end='')
        print(' ', total)
        print('-' * (10 * (len(cell_counts[x]) + 1)))

    answer = expand_infinite_grid_state(part2_steps, cycle_start, cycle_length, cycle_values, states[equivalent_n])
    print("part 2 =", answer)

if __name__ == '__main__':
    main()