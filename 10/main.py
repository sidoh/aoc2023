import os
from typing import List, Tuple, Set, Dict, Literal, Union, Optional, Callable
from termcolor import colored

os.system('color')

EXAMPLES = [x.strip() for x in [
    """
F---S......
L7..L----7.
FJ..F----J.
L---J......
""",

    """
-L|F7
7S-7|
L|7||
-L-J|
L|-JF
""",

    """
7-F7-
.FJ|7
SJLL7
|F--J
LJ.LJ
""",

    """
..........
.F------7.
.|F-S--7|.
.||....||.
.||....||.
.|L-7F-J|.
.|..||..|.
.L--JL--J.
..........
""",

    """
.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ...
""",

    """
FF7F7F7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJS||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
""",
]]

AbsoluteDirection = Literal['W', 'E', 'N', 'S']
RelativeDirection = Literal['L', 'R', 'U', 'D']
AdjacentDirection = Union[AbsoluteDirection, Literal['NW', 'NE', 'SW', 'SE']]
ConnectorType = Literal['-', '|', '7', 'L', 'J', 'F', 'S', '.']

TRANSLATIONS: Dict[AbsoluteDirection, Tuple[int, int]] = {
    'W': (-1, 0),
    'E': (1, 0),
    'N': (0, -1),
    'S': (0, 1),
    'NW': (-1, -1),
    'NE': (1, -1),
    'SW': (-1, 1),
    'SE': (1, 1)
}

DIRECTIONS: Dict[Tuple[int, int], AbsoluteDirection] = dict((v, k) for k, v in TRANSLATIONS.items())

# Connections listed in order that would result in a clockwise turn
CONNECTOR_TYPES: Dict[ConnectorType, List[AbsoluteDirection]] = {
    '-': ['W', 'E'],
    '|': ['S', 'N'],
    '7': ['W', 'S'],
    'L': ['E', 'N'],
    'J': ['N', 'W'],
    'F': ['S', 'E'],
    'S': [],
    '.': [],
}
CORNER_CONNECTOR_TYPES: List[ConnectorType] = ['7', 'L', 'J', 'F']

CONNECTOR_TRANSLATIONS: Dict[chr, List[Tuple[int, int]]] = dict(
    (k, [TRANSLATIONS[x] for x in v])
    for k, v in CONNECTOR_TYPES.items()
)

# More readable symbols
CONNECTOR_SYMBOLS: Dict[ConnectorType, chr] = {
    '-': '─',
    '|': '│',
    '7': '┐',
    'L': '└',
    'J': '┘',
    'F': '┌',
    'S': 'S',
    '.': '.',
    '+': '@'
}

INITIAL_TURN_NUMBERS: Dict[ConnectorType, int] = {
    '-': 1,
    '|': 0,
    '7': 3,
    'L': 2,
    'J': 3,
    'F': 2,
}

INITIAL_MOVE_DIRECTIONS: Dict[ConnectorType, AdjacentDirection] = {
    '-': 'E',
    '|': 'N',
    '7': 'W',
    'L': 'E',
    'J': 'W',
    'F': 'E',
}

# Adjacent directions for each connector type assuming we define 0 turns as northward-moving
#   F-S-7
#   |   |
#   L---J
CONNECTOR_ADJACENCIES: Dict[ConnectorType, Tuple[List[AdjacentDirection], List[AdjacentDirection]]] = {
    '7': ([], ['N', 'E']),
    'J': ([], ['S', 'E']),
    'L': (['S', 'W'], []),
    'F': (['N', 'W'], []),
}

CONNECTOR_MERGED_DIRECTIONS: Dict[ConnectorType, Set[AdjacentDirection]] = {
    '7': {'E', 'N'},
    'J': {'E', 'S'},
    'L': {'W', 'S'},
    'F': {'W', 'N'},
    '|': {'N'},
    '-': {'E'},
}

ADJACENT_DIRECTIONS: List[AbsoluteDirection] = ['N', 'E', 'S', 'W']

#  N   W
# W E S N
#  S   E
# N E S W
# W N E S



class GridCell:
    adjacent_cells: List['GridCell']
    connector_type: ConnectorType
    position: Tuple[int, int]
    is_start: bool

    def __init__(self, connector_type: ConnectorType, position: Tuple[int, int]):
        self.connector_type = connector_type
        self.position = position
        self.adjacent_cells = []
        self.is_start = False

    def connector(self) -> ConnectorType:
        if self.is_start:
            return 'S'
        else:
            return self.connector_type

    def __repr__(self):
        return f'<GridCell {self.position} {self.connector_type}>'

    def __str__(self):
        return CONNECTOR_SYMBOLS[self.connector_type]

    def orientation(self, other_cell: 'GridCell') -> AdjacentDirection:
        dx = self.position[0] - other_cell.position[0]
        dy = self.position[1] - other_cell.position[1]
        if dx > 1 or dx > 1:
            print(dx, dy)
        return DIRECTIONS[(
            self.position[0] - other_cell.position[0],
            self.position[1] - other_cell.position[1]
        )]

    def turn_direction(self, previous_cell: 'GridCell') -> int:
        if self.connector_type in CORNER_CONNECTOR_TYPES:
            previous_cell_location = previous_cell.orientation(self)

            # Connector types is organized so that the first direction is the one that
            # will result in a clockwise turn. If the previous cell is in the first
            # direction, then travelling through this results in a clockwise turn.
            if CONNECTOR_TYPES[self.connector_type][0] == previous_cell_location:
                return 1
            else:
                return -1
        # Straight connector, will not turn
        else:
            return 0


class Grid:
    cells: List[List[GridCell]]
    height: int
    width: int
    start: GridCell

    def __init__(self, grid: str, start_position: Tuple[int, int] = None):
        self.cells = []

        for y, line in enumerate(grid.split('\n')):
            self.cells.append([])

            for x, cell in enumerate(line):
                self.cells[y].append(GridCell(cell, (x, y)))

        self.height = len(self.cells)
        self.width = len(self.cells[0])

        for y, line in enumerate(self.cells):
            for x, cell in enumerate(line):
                if cell.connector_type == 'S' or cell.is_start or start_position == cell.position:
                    self.start = cell
                    self.start.is_start = True

                for dx, dy in CONNECTOR_TRANSLATIONS[cell.connector_type]:
                    new_x = x + dx
                    new_y = y + dy

                    if 0 <= new_x < self.width and 0 <= new_y < self.height:
                        cell.adjacent_cells.append(self.cells[y + dy][x + dx])

        # Find the cells that start is connected to
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                if x == 0 and y == 0:
                    continue

                try:
                    cell = self.cells[self.start.position[1] + y][self.start.position[0] + x]

                    if self.start in cell.adjacent_cells:
                        self.start.adjacent_cells.append(cell)
                except IndexError:
                    pass

        # Determine the type of the start cell
        start_adjacencies = set([
            (
                x.position[0] - self.start.position[0],
                x.position[1] - self.start.position[1]
            )
            for x in self.start.adjacent_cells
        ])

        # find key in CONNECTOR_TRANSLATIONS that matches start_adjacencies
        for k, v in CONNECTOR_TRANSLATIONS.items():
            if set(v) == start_adjacencies:
                self.start.connector_type = k
                break

        # Sort so that we move in direction preferring U R D L
        for cell in self:
            cell.adjacent_cells.sort(key=lambda ac: ac.orientation(cell))

    def __repr__(self):
        return f'<Grid {self.width}x{self.height}>'

    def __str__(self):
        return '\n'.join(''.join(str(cell) for cell in line) for line in self.cells)

    # iterator
    def __iter__(self):
        for line in self.cells:
            for cell in line:
                yield cell

    def get_all_adjacent(self, cell: GridCell, directions: List[AdjacentDirection]) -> Set[GridCell]:
        adjacent_cells = [self.get_adjacent(cell, direction) for direction in directions]
        return set([x for x in adjacent_cells if x is not None])

    def get_adjacent(self, cell: GridCell, direction: AdjacentDirection) -> Optional[GridCell]:
        translation = TRANSLATIONS[direction]
        x = cell.position[0] + translation[0]
        y = cell.position[1] + translation[1]

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        else:
            return self.cells[y][x]

    def traverse_loop(self, start: GridCell) -> Tuple[Set[GridCell], Set[GridCell]]:
        """
        Traverse the loop starting at the given cell. We return two sets of cells. One for
        adjacent cells on the left of the loop, and one for adjacent cells on the right of the loop.
        One of these sets will contain cells on the inside of the loop.

        :param start:
        :return:
        """
        visited = set()
        current_cell = start
        turn_number = INITIAL_TURN_NUMBERS[start.connector_type]
        print("tn ------ ", turn_number)

        partitions: Tuple[Set[GridCell], Set[GridCell]] = (set(), set())

        while True:
            visited.add(current_cell)

            current_cell.turn_number = (turn_number % 4)

            # Travel in a consistent direction
            new_adjacent_cells = [x for x in current_cell.adjacent_cells if x not in visited]

            if len(new_adjacent_cells) == 0:
                break

            next_cell = new_adjacent_cells[0]
            previous_cell = [x for x in current_cell.adjacent_cells if x != next_cell][0]

            p1 = partitions[0]
            p2 = partitions[1]

            left: Set[AbsoluteDirection] = {ADJACENT_DIRECTIONS[(turn_number + 1) % 4]}
            right: Set[AbsoluteDirection] = {ADJACENT_DIRECTIONS[(turn_number + 3) % 4]}

            if left.intersection(CONNECTOR_MERGED_DIRECTIONS[current_cell.connector_type]):
                left = left.union(CONNECTOR_MERGED_DIRECTIONS[current_cell.connector_type])
            if right.intersection(CONNECTOR_MERGED_DIRECTIONS[current_cell.connector_type]):
                right = right.union(CONNECTOR_MERGED_DIRECTIONS[current_cell.connector_type])

            p1 |= self.get_all_adjacent(current_cell, list(left))
            p2 |= self.get_all_adjacent(current_cell, list(right))

            turn_number += current_cell.turn_direction(previous_cell)
            current_cell = next_cell

        # We only care about cells adjacent to loop cells that are not part of the loop
        filtered_partitions = [set([x for x in partition if x not in visited]) for partition in partitions]

        return filtered_partitions[0], filtered_partitions[1]

    def breadth_first_traverse(
            self,
            start: GridCell,
            get_adjacent: Callable[['Grid', GridCell], Set[GridCell]] = lambda g, c: c.adjacent_cells,
            previously_visited: Set[GridCell] = None
    ) ->  Tuple[Set[GridCell], int]:
        """
        Traverse the grid starting at the given cell, returning all visited cells and the maximum distance from the
        start.

        :param start:
        :param previously_visited:
        :return:
        """
        frontier = [(start, 0)]
        visited = set()
        previously_visited = previously_visited or set()
        max_distance = 0

        while frontier:
            cell, distance = frontier.pop(0)
            visited.add(cell)

            for adjacent_cell in get_adjacent(self, cell):
                if (
                        not any([x[0] == adjacent_cell for x in frontier])
                        and adjacent_cell not in visited
                        and adjacent_cell not in previously_visited
                ):
                    frontier.append((adjacent_cell, distance + 1))
                    max_distance = max(max_distance, distance + 1)

        return visited, max_distance

    def is_border(self, cell: GridCell) -> bool:
        return (
                cell.position[0] == 0 or
                cell.position[0] == self.width - 1 or
                cell.position[1] == 0 or
                cell.position[1] == self.height - 1
        )


def solve(grid: str) -> int:
    grid = Grid(grid)
    visited, max_distance = grid.breadth_first_traverse(grid.start)

    all_visited = visited.copy()
    visit_batches = [all_visited.copy()]

    # Until the whole grid has been visited, pick one arbitrarily and batch together
    # all the cells that are reachable from it
    while len(all_visited) < grid.width * grid.height:
        for cell in grid:
            if cell not in all_visited:
                visited, _ = grid.breadth_first_traverse(
                    cell,
                    lambda g, c: g.get_all_adjacent(c, ['N', 'E', 'S', 'W']),
                    all_visited
                )

                all_visited |= visited
                break
        visit_batches += [visited]

    # Find the batches that contain border cells
    border_batches = [batch for batch in visit_batches if any(grid.is_border(x) for x in batch)]

    # Cells which are border cells or are reachable from border cells
    border_cells = set([cell for batch in border_batches for cell in batch])

    # Partition cells adjacent to the loop into two sets. We pick a travel direction arbitrarily, and one
    # set is all the cells on the left while we travel through the loop, the other is cells on the right.
    #
    # One of these partitions will be inside the loop, the other will be outside. We can determine which
    # is which by checking if any of the cells in the partition are contained in the escapable set.
    p1, p2 = grid.traverse_loop(grid.start)

    p1_escapable = len(p1.intersection(border_cells)) > 0
    p2_escapable = len(p2.intersection(border_cells)) > 0

    # This should never happen
    # if p1_escapable == p2_escapable:
    #     print(p1.intersection(border_cells))
    #     print(p2.intersection(border_cells))
    #     raise Exception("Both sets have same escape value: {} {}".format(p1_escapable, p2_escapable))

    # Select the set which is escapable
    loop_adjacent_inside_cells = p2 if p1_escapable else p1

    # Now we have the inside cells which are directly adjacent to the loop. Find all of the
    # cells which are reachable from these cells
    inside_batches = [batch for batch in visit_batches if len(batch.intersection(loop_adjacent_inside_cells)) > 0]
    inside_cells = set([cell for batch in inside_batches for cell in batch])
    num_inside_cells = len(inside_cells)

    loop_cells = visit_batches[0]

    for y, line in enumerate(grid.cells):
        for x, cell in enumerate(line):
            if cell in loop_cells:
                if cell.is_start:
                    print(colored('S', 'white', 'on_green', ['bold']), end='')
                else:
                    color = ['red', 'green', 'blue', 'yellow'][cell.turn_number % 4]
                    print(colored(CONNECTOR_SYMBOLS[cell.connector_type], color), end='')
            elif cell in p1 and cell in p2:
                print(colored('*', 'magenta', 'on_white'), end='')
            elif cell in inside_cells:
                print(colored('@', 'white', 'on_red', ['bold']), end='')
            elif cell in p1:
                print(colored('*', 'blue'), end='')
            elif cell in p2:
                print(colored('*', 'red'), end='')
            else:
                print('.', end='')
        print()

    print()
    print()

    print("Max distance in path: {}".format(max_distance))
    print("Total inside cells: {}".format(num_inside_cells))


def main():
    input = open('input.txt').read().strip()

    # solve(EXAMPLES[5])

    for i in EXAMPLES:
        print("Example:")
        solve(i.strip())
        print()

    solve(input)


if __name__ == '__main__':
    main()
