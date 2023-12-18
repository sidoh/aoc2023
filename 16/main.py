from typing import Literal, List, Callable, cast

MovementSymbols = Literal["-", "|", "/", "\\", '.']
Direction = Literal["S", "E", "N", "W"]
VisitedObserver = Callable[[tuple[int, int], Direction], None]

DIRECTION_VECTORS: dict[Direction, tuple[int, int]] = {
    "S": (0, 1),
    "E": (1, 0),
    "N": (0, -1),
    "W": (-1, 0),
}


class Ray:
    visited: set[tuple[int, int, Direction]]

    def __init__(self, location: tuple[int, int], direction: Direction, observer: VisitedObserver, has_visited: Callable[[tuple[int, int], Direction], bool]):
        self.location = location
        self.direction = direction
        self.observer = observer
        self.has_visited = has_visited
        observer(location, direction)

    def move(self, symbol: MovementSymbols) -> List['Ray']:
        if symbol == '-':
            if self.direction in ['E', 'W']:
                return self.move_in(self.direction)
            else:
                return [*self.move_in('E'), *self.move_in('W')]
        elif symbol == '|':
            if self.direction in ['N', 'S']:
                return self.move_in(self.direction)
            else:
                return [*self.move_in('N'), *self.move_in('S')]
        elif symbol == '/':
            if self.direction == 'E':
                return self.move_in('N')
            elif self.direction == 'N':
                return self.move_in('E')
            elif self.direction == 'W':
                return self.move_in('S')
            elif self.direction == 'S':
                return self.move_in('W')
        elif symbol == '\\':
            if self.direction == 'E':
                return self.move_in('S')
            elif self.direction == 'S':
                return self.move_in('E')
            elif self.direction == 'W':
                return self.move_in('N')
            elif self.direction == 'N':
                return self.move_in('W')
        elif symbol == '.':
            return self.move_in(self.direction)

    def move_in(self, direction: Direction) -> List['Ray']:
        v = DIRECTION_VECTORS[direction]
        new_location = (self.location[0] + v[0], self.location[1] + v[1])

        if self.has_visited(new_location, direction):
            return []
        else:
            return [Ray(
                new_location,
                direction,
                self.observer,
                self.has_visited
            )]

    def __repr__(self):
        return f'Ray({self.location}, {self.direction})'


class Grid:
    def __init__(self, grid: List[List[MovementSymbols]]):
        self.grid = grid

    def __getitem__(self, location: tuple[int, int]) -> MovementSymbols:
        return self.grid[location[1]][location[0]]

    def trace(self, location: tuple[int, int], direction: Direction) -> set[tuple[int, int]]:
        visited: set[tuple[int, int, direction]] = set()

        def observer(l: tuple[int, int], d: Direction):
            if 0 <= l[0] < len(self.grid[0]) and 0 <= l[1] < len(self.grid):
                visited.add((l[0], l[1], d))

        def has_visited(l: tuple[int, int], d: Direction) -> bool:
            return (l[0], l[1], d) in visited

        rays = [Ray(location, direction, observer, has_visited)]

        while len(rays):
            ray = rays.pop()
            symbol = self[ray.location]

            # filter out rays that have left the grid
            new_rays = [
                r for r in ray.move(symbol)
                if 0 <= r.location[0] < len(self.grid[0]) and 0 <= r.location[1] < len(self.grid)
            ]

            rays.extend(new_rays)

        return {(x, y) for x, y, _ in visited}


def parse_grid(input: str) -> List[List[MovementSymbols]]:
    return [[cast(MovementSymbols, c) for c in row] for row in input.split('\n')]


def solve1(grid: List[List[MovementSymbols]]) -> int:
    g = Grid(grid)
    visited = g.trace((0, 0), 'E')
    return len(visited)


def solve2(grid: List[List[MovementSymbols]]) -> int:
    g = Grid(grid)
    # Try from every edge
    max_visited = 0

    for x in range(len(grid[0])):
        from_top = g.trace((x, 0), 'S')
        from_bottom = g.trace((x, len(grid) - 1), 'N')
        max_visited = max(max_visited, len(from_top), len(from_bottom))

    for y in range(len(grid)):
        from_left = g.trace((0, y), 'E')
        from_right = g.trace((len(grid[0]) - 1, y), 'W')
        max_visited = max(max_visited, len(from_left), len(from_right))

    return max_visited


def main():
    print(solve2(parse_grid(open('input.txt').read().strip())))


if __name__ == '__main__':
    main()
