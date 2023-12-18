import math
import re
from typing import Dict, List, Tuple, Callable


class Node:
    label: str
    left: 'Node'
    right: 'Node'

    def __init__(self, label: str, left: 'Node' = None, right: 'Node' = None):
        self.label = label
        self.left = left
        self.right = right

class Tree:
    root: Node
    nodes: Dict[str, Node]

    def __init__(self, nodes: List[Tuple[str, str, str]]):
        self.nodes = {}

        for node in nodes:
            label, left, right = node
            self.nodes[label] = Node(label)

        for node in nodes:
            label, left, right = node
            self.nodes[label].left = self.nodes[left]
            self.nodes[label].right = self.nodes[right]

        self.root = self.nodes['AAA']

    def traverse(self, path: str, source: str, times: int = 1) -> str:
        """Traverse the tree, returning the label of the node reached"""
        current = self.nodes[source]

        for i in range(times):
            for step in path:
                if step == 'L':
                    next = current.left
                elif step == 'R':
                    next = current.right
                else:
                    raise Exception("Invalid step: {}".format(step))

                current = next

        return current.label

    def navigate(self, path: str, source: str, destination_filter: Callable[[str], bool]) -> int:
        """Navigate the tree, returning the number of steps taken to reach the destination"""
        current = source

        steps = 0

        while not destination_filter(current) or steps == 0:
            current = self.traverse(path, current)
            steps += len(path)

        return steps

    def parallel_navigate(self, path: str, sources: List[str], destination_filter: Callable[[str], bool]) -> int:
        steps = 0
        current_nodes = sources.copy()

        while not all(destination_filter(node) for node in current_nodes):
            current_nodes = [self.traverse(path, node) for node in current_nodes]
            steps += len(path)
            print("Current nodes: {}".format([destination_filter(node) for node in current_nodes]))

        return steps


def parse(input_path: str) -> (str, Tree):
    nodes = []

    with open(input_path, 'r') as f:
        path = f.readline().strip()

        # skip blank line
        f.readline()

        while True:
            line = f.readline().strip()

            if not line:
                break

            matches = re.match(r'(\w+) = \((\w+), (\w+)\)', line)
            label, left, right = matches.groups()
            nodes.append((label, left, right))

    return path, Tree(nodes)


def lcm_of_list(numbers):
    lcm = numbers[0]
    for number in numbers[1:]:
        lcm = lcm * number // math.gcd(lcm, number)
    return lcm


def part1(path: str, tree: Tree) -> None:
    print(tree.navigate(path, 'AAA', lambda x: x == 'ZZZ'))


def part2(path: str, tree: Tree) -> None:
    # all nodes that end with A
    start_nodes = [node for node in tree.nodes if node.endswith('A')]

    # For each start node, compute:
    #   1. The number of iterations to reach a node that ends with Z
    #   2. The number of iterations to end back at the start node
    distances: Dict[str, Tuple[List[int], int, int]] = {}

    for n in start_nodes:
        i = 0
        current_node = n
        visited_nodes = set()

        while i == 0 or current_node not in visited_nodes:
            visited_nodes.add(current_node)
            current_node = tree.traverse(path, current_node)

            i += 1

        steps_to_start_loop = i
        z_locations = []

        i = 0
        loop_start = current_node
        while i == 0 or current_node != loop_start:
            if current_node.endswith('Z'):
                z_locations.append(i)
            current_node = tree.traverse(path, current_node)
            i += 1

        distances[n] = (z_locations, steps_to_start_loop, i)

    loop_lengths = [loop_length for _, (_, _, loop_length) in distances.items()]
    answer = lcm_of_list(loop_lengths) * len(path)

    print(answer)

    pass


if __name__ == '__main__':
    path, tree = parse("input.txt")
    part1(path, tree)
    part2(path, tree)