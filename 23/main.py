import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from typing import Literal, cast, Callable, Optional
from collections import deque, defaultdict

import graphviz
from graphviz import Digraph

GridSymbol = Literal['.', '#', '>', '<', '^', 'v']
Grid = list[list[GridSymbol]]
Point = tuple[int, int]
NeighborFunc = Callable[[Grid, Point], list[Point]]

NEIGHBORS: dict[GridSymbol, list[Point]] = {
    # can move in any direction
    '.': [(0, 1), (1, 0), (0, -1), (-1, 0)],
    '#': [],
    # can only move right
    '>': [(0, 1)],
    # can only move left
    '<': [(0, -1)],
    # can only move up
    '^': [(-1, 0)],
    # can only move down
    'v': [(1, 0)],
}

@dataclass
class Graph:
    nodes: list[Point]
    edges: list[tuple[Point, Point, int]]
    start: Point
    goal: Point
    id: int = 0
    _memoized_edges: dict[Point, list[tuple[Point, int]]] = None

    def adjacent_nodes(self, node: Point) -> list[tuple[Point, int]]:
        if not self._memoized_edges:
            self._memoized_edges = defaultdict(list)
            for n1, n2, w in self.edges:
                self._memoized_edges[n1].append((n2, w))
        return self._memoized_edges[node]

    def render_graphviz(self, path: list[Point] = None):
        """
        Render graph as a PNG using graphviz library
        :return:
        """

        # add graphviz to path
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

        dot = graphviz.Digraph(comment='Graph')
        for node in self.nodes:
            attrs = {}
            if node == self.start:
                attrs['color'] = 'darkgreen'
                attrs['style'] = 'filled'
            elif node == self.goal:
                attrs['color'] = 'darkred'
                attrs['style'] = 'filled'
            elif path and node in path:
                attrs['color'] = 'cyan'
                attrs['style'] = 'filled'

            dot.node(
                str(node),
                str(node),
                **attrs
            )
        for node1, node2, weight in self.edges:
            dot.edge(str(node1), str(node2), label=str(weight))
        dot.render('graph', view=True, format='png')


def parse(input: str) -> Grid:
    return [cast(list[GridSymbol], list(line)) for line in input.splitlines()]


def longest_walk_graph(graph: Graph, node: Point, goal: Point, length: int, visited: set[Point]) -> int:
    if node == goal:
        return length
    elif node in visited:
        return 0

    neighbors = [(n, w) for n, w in graph.adjacent_nodes(node) if n not in visited]

    if len(neighbors) == 0:
        return 0

    visited.add(node)
    longest = max(
        longest_walk_graph(graph, n, goal, length + w, visited)
        for n, w in neighbors
    )
    visited.remove(node)

    return longest


def longest_walk_dfs(grid: Grid, neighbors: NeighborFunc) -> int:
    start: Point = (0, 1)
    goal: Point = (len(grid) - 1, len(grid[0]) - 2)

    stack: deque[tuple[Point, set[Point]]] = deque()
    stack.append((start, {start}))
    longest = 0

    while len(stack) > 0:
        point, visited = stack.pop()

        for next_point in sorted(neighbors(grid, point), key=lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])):
            if next_point in visited:
                continue

            updated_path = {next_point}.union(visited)

            if next_point == goal and len(updated_path) > longest:
                longest = len(updated_path)
                break
            else:
                stack.append((next_point, updated_path))

    # Subtract 1 to take out start
    return longest - 1

def build_graph(grid: Grid, start: Point, goal: Point, neighbors: NeighborFunc) -> Graph:
    def traverse(point: start, start_branch: Point, branch_points: list[Point]) -> tuple[Optional[Point], Optional[Point], int]:
        assert point not in branch_points

        current = point
        path = [current]

        while True:
            all_neighbors = neighbors(grid, current)
            unvisited_neighbors = [x for x in all_neighbors if x not in path and x != start_branch]

            if len(unvisited_neighbors) == 1:
                current = unvisited_neighbors[0]
                path.append(current)
            elif len(unvisited_neighbors) == 0:
                return None, None, 0
            else:
                assert current in branch_points
                return path[-1], current, len(path)-1

    # find all nodes that have a choice
    branch_points: list[Point] = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if grid[x][y] != '#' and len(neighbors(grid, (x, y))) > 2:
                branch_points.append((x, y))

    # find connections between points
    edges: list[tuple[Point, Point, int]] = []
    branch_nodes = set()
    for point in branch_points:
        next_points = neighbors(grid, point)
        for next_point in next_points:
            if next_point not in branch_points:
                end_point, branch_point, length = traverse(next_point, point, branch_points)
                if end_point and end_point not in branch_point:
                    branch_nodes.add(end_point)
                    branch_nodes.add(next_point)

                    edges.append((point, next_point, 1))
                    edges.append((branch_point, end_point, 1))
                    edges.append((next_point, end_point, length))
                    edges.append((end_point, next_point, length))

            else:
                edges.append((point, next_point, 1))

    nodes = [*branch_points, *branch_nodes, start, goal]
    _, p, w = traverse(start, start, branch_points)
    edges.append((start, p, w))

    _, p, w = traverse(goal, goal, branch_points)
    edges.append((p, goal, w))

    return Graph(
        nodes=nodes,
        edges=edges,
        start=start,
        goal=goal,
    )

def valid_neighbors(grid: Grid, point: Point, deltas: list[Point]) -> list[Point]:
    return [
        (point[0] + d[0], point[1] + d[1])
        for d in deltas
        if (
                0 <= point[0] + d[0] < len(grid)
                and 0 <= point[1] + d[1] < len(grid[0])
                and grid[point[0] + d[0]][point[1] + d[1]] != '#'
        )
    ]

def part2_neighbors(grid: Grid, point: Point) -> list[Point]:
    return valid_neighbors(grid, point, NEIGHBORS['.'])

def part1_neighbors(grid: Grid, point: Point) -> list[Point]:
    return valid_neighbors(grid, point, NEIGHBORS[grid[point[0]][point[1]]])

def solve1(grid: Grid) -> int:
    return longest_walk_dfs(grid, part1_neighbors)

def solve2(grid: Grid) -> int:
    return longest_walk_dfs(grid, part2_neighbors)


@contextmanager
def timed(label: str):
    start = time.perf_counter()

    def checkpoint(message: str):
        nonlocal start
        print(f'{label} - {message}: {end - start:.2f}s\n')

    yield checkpoint

    end = time.perf_counter()
    print(f'{label}: {end - start:.2f}s')

def main():
    # grid = parse(open('example2.txt').read())
    grid = parse(open('input.txt').read())

    start = (0, 1)
    goal = (len(grid) - 1, len(grid[0]) - 2)

    with timed('part 1'):
        print(longest_walk_dfs(grid, part1_neighbors))

    with timed('part 2') as checkpoint:
        part2_graph = build_graph(grid, start, goal, part2_neighbors)
        checkpoint("built graph")
        print(longest_walk_graph(part2_graph, start, goal, 0, set()))

if __name__ == '__main__':
    main()

