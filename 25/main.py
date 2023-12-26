import os
import random
from collections import defaultdict, deque
from typing import Optional
import networkx

import graphviz

def render(graph: networkx.Graph, name: str):
    dot = graphviz.Graph()
    for node in graph.nodes:
        dot.node(node)
    for edge in graph.edges:
        dot.edge(*edge)
    dot.render(name, view=True, format='png')

def parse(input: str) -> networkx.DiGraph:
    graph = networkx.DiGraph()
    for line in input.splitlines():
        node, edges = line.strip().split(': ')
        for edge in edges.split(' '):
            graph.add_edge(node, edge, capacity=1)
    return graph

def part1(input: str) -> list[set[str]]:
    graph = parse(input)
    graph = graph.to_undirected()

    start = list(graph.nodes)[0]
    components = [{start}, set()]

    for n in graph.nodes:
        if n != start:
            for c in components:
                if all([e in c for e in graph.neighbors(n)]):
                    c.add(n)
                    break
            else:
                flow = networkx.algorithms.flow.edmonds_karp(graph, start, n).graph['flow_value']
                if flow == 3:
                    components[1].add(n)
                else:
                    components[0].add(n)

    return components



if __name__ == '__main__':
    with open('input.txt') as input_file:
        components = part1(input_file.read())
        print([len(c) for c in components])
        print(len(components[0]) * len(components[1]))
