import re
from typing import Literal, cast, Callable, TypedDict

EXAMPLE = f"""
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
""".strip()

INPUT_FORMAT = re.compile(r'([LRUD]) (\d+) \(#([^)]+)\)')

Direction = Literal['L', 'R', 'U', 'D']
GridGlyph = Literal['.', '#']
Point = tuple[int, int]

DIRECTIONS: dict[Direction, Point] = {
    'L': (-1, 0),
    'R': (1, 0),
    'U': (0, -1),
    'D': (0, 1),
}

class ParsedProblem(TypedDict):
    path_vertexes: list[Point]
    grid_width: int
    grid_height: int
    path_length: int

def parse_instruction1(instruction: list[str]) -> tuple[Direction, int, str]:
    direction = instruction[0]
    distance = int(instruction[1])
    color = instruction[2]

    return direction, distance, color

def parse_instruction2(instruction: list[str]) -> tuple[Direction, int, str]:
    v = instruction[2]

    # the 6 digit hex "color" is actually the distance (first five hex) and distance (last hex)
    # 0 means R, 1 means D, 2 means L, and 3 means U.
    direction = cast(Direction, 'RDLU'[int(v[5], 16)])
    distance = int(v[:5], 16)

    return direction, distance, ""

def solve1(problem: ParsedProblem) -> int:
    size_x = problem['grid_width']
    size_y = problem['grid_height']

    print("Grid size {}x{} (cells={})".format(size_x, size_y, size_x * size_y))
    grid: list[list[GridGlyph]] = [[cast(GridGlyph, '.')] * (size_x + 1) for _ in range(size_y + 1)]

    # Draw path
    vertexes = problem['path_vertexes']
    start = vertexes[0]

    current_x = start[0]
    current_y = start[1]
    path: list[Point] = list()

    for vertex in vertexes[1:] + [start]:
        for x in range(min(current_x, vertex[0]), max(current_x, vertex[0]) + 1):
            for y in range(min(current_y, vertex[1]), max(current_y, vertex[1]) + 1):
                grid[y][x] = '#'
                path.append((x, y))

        current_x = vertex[0]
        current_y = vertex[1]

    inner = measure_inner(grid, path)

    return len(set(path)) + inner

def solve2(problem: ParsedProblem) -> int:
    """
    Use the shoelace formula to compute the area of the polygon formed by the vertexes.

    :param problem:
    :return:
    """

    vertexes = problem['path_vertexes']
    vertexes.append(vertexes[0])

    area = 0

    for i in range(len(vertexes) - 1):
        area += vertexes[i][0] * vertexes[i + 1][1] - vertexes[i + 1][0] * vertexes[i][1]

    enclosed_area = abs(area) // 2

    return enclosed_area + (problem['path_length'] + 2) // 2
def parse(
        input: str,
        instruction_parser: Callable[[list[str]], tuple[Direction, int, str]]
) -> ParsedProblem:
    # First find bounds of the grid
    instructions = INPUT_FORMAT.findall(input)
    max_x = 0
    max_y = 0
    min_x = 0
    min_y = 0
    current_x = 0
    current_y = 0

    for instruction in instructions:
        direction, distance, color = instruction_parser(instruction)
        delta = DIRECTIONS[direction]

        current_x += delta[0] * distance
        current_y += delta[1] * distance

        max_x = max(max_x, current_x)
        max_y = max(max_y, current_y)
        min_x = min(min_x, current_x)
        min_y = min(min_y, current_y)

    # Create grid
    size_x = max_x - min_x
    size_y = max_y - min_y

    vertexes: list[Point] = [(-min_x, -min_y)]
    current_x = -min_x
    current_y = -min_y
    path_length = 0

    for instruction in instructions:
        direction, distance, color = instruction_parser(instruction)
        delta = DIRECTIONS[direction]

        current_x += delta[0] * distance
        current_y += delta[1] * distance

        vertexes.append((current_x, current_y))
        path_length += distance

    return ParsedProblem(
        path_length=path_length,
        path_vertexes=vertexes,
        grid_width=size_x,
        grid_height=size_y)

def measure_inner(grid: list[list[GridGlyph]], path: list[Point]) -> int:
    visited: set[Point] = set(path)

    def is_border(x: int, y: int) -> bool:
        return x == 0 or x == len(grid[0]) - 1 or y == 0 or y == len(grid) - 1

    def flood_fill(start_x: int, start_y: int) -> set[Point]:
        fringe = [(start_x, start_y)]
        local_visited = set()

        while len(fringe):
            x, y = fringe.pop()
            local_visited.add((x, y))

            for dx, dy in DIRECTIONS.values():
                new_x = x + dx
                new_y = y + dy

                if not (0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid)):
                    continue

                if (new_x, new_y) not in visited and (new_x, new_y) not in local_visited and grid[new_y][new_x] == '.':
                    fringe.append((new_x, new_y))
                    local_visited.add((new_x, new_y))

        return local_visited

    total_inner = 0

    while len(visited) != len(grid) * len(grid[0]):
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == '#':
                    continue
                elif (x, y) not in visited:
                    visited_batch = flood_fill(x, y)

                    if not any(is_border(x, y) for x, y in visited_batch):
                        total_inner += len(visited_batch)

                    visited |= visited_batch

    return total_inner


def main():
    input = open('input.txt').read().strip()
    # input = EXAMPLE.strip()

    problem1 = parse(input, parse_instruction1)

    a1 = solve1(problem1)
    print("part 1 = {}".format(a1))

    problem2 = parse(input, parse_instruction2)

    a2 = solve2(problem2)
    print("part 2 = {}".format(a2))

if __name__ == '__main__':
    main()