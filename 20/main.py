import math
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Literal, TypedDict, Optional, Callable, get_args
import os
import graphviz
from graphviz import Digraph

ComponentSymbol = Literal['%', '&', '_']
Observer = Callable[['Component', 'Component', 'Pulse'], None]

class Pulse(Enum):
    HIGH = 1
    LOW = 0

    def invert(self) -> 'Pulse':
        if self == Pulse.HIGH:
            return Pulse.LOW
        else:
            return Pulse.HIGH

    def __repr__(self):
        if self == Pulse.HIGH:
            return 'H'
        else:
            return 'L'

    def __str__(self):
        return self.__repr__()


@dataclass
class Component:
    label: str
    input_signals: list[tuple['Component', Pulse]] = None
    output_signals: list[Pulse] = None
    output_components: list['Component'] = None
    input_components: list['Component'] = None
    observer: Observer = None

    def queue_output(self, pulse: Pulse):
        if self.output_signals is None:
            self.output_signals = []
        self.output_signals.append(pulse)

    def queue_input(self, c: 'Component', pulse: Pulse):
        if self.input_signals is None:
            self.input_signals = []
        self.input_signals.append((c, pulse))

    def send_output(self, pulse: Pulse):
        for output in self.output_components:
            if self.observer:
                self.observer(self, output, pulse)

            output.queue_input(self, pulse)

    def _handle_input(self, input: 'Component', pulse: Pulse) -> None:
        pass

    def tick(self) -> bool:
        # print("ticking " + str(self.label))
        # print("  inputs: " + str([f"{input.label}:{pulse}" for input, pulse in self.input_signals]))
        self.output_signals = []

        for input, pulse in self.input_signals:
            self._handle_input(input, pulse)

        has_output = len(self.output_signals) > 0

        for signal in self.output_signals:
            self.send_output(signal)

        self.input_signals = []
        return has_output

    def __repr__(self):
        return f'{self.label}'

    def __str__(self):
        return self.__repr__()


@dataclass
class FlipFlop(Component):
    state: Pulse = Pulse.LOW
    def _handle_input(self, input: Component, pulse: Pulse) -> None:
        if pulse == Pulse.LOW:
            self.state = self.state.invert()
            self.queue_output(self.state)


@dataclass
class Conjunction(Component):
    input_states: dict[str, Pulse] = None

    def _handle_input(self, input: Component, pulse: Pulse) -> None:
        if not self.input_states:
            self.input_states = {}
            for c in self.input_components:
                self.input_states[c.label] = Pulse.LOW

        self.input_states[input.label] = pulse
        # print("&" + str(self.label))
        # print("  handling input from " + str(input.label) + ":" + str(pulse))
        # print("  states after: " + str(self.input_states))

        if all(state == Pulse.HIGH for state in self.input_states.values()):
            self.queue_output(Pulse.LOW)
        else:
            self.queue_output(Pulse.HIGH)

@dataclass
class Broadcast(Component):
    def _handle_input(self, input: Component, pulse: Pulse) -> None:
        self.queue_output(pulse)

@dataclass
class Sink(Component):
    def _handle_input(self, input: Component, pulse: Pulse) -> None:
        pass


COMPONENT_TYPES: dict[ComponentSymbol, type[Component]] = {
    '%': FlipFlop,
    '&': Conjunction,
    '_': Sink
}

def parse(input: str, observer: Observer) -> dict[str, Component]:
    components: dict[str, Component] = {}

    # first pass to establish topology
    types: dict[str, type[Component]] = {}
    output_connections: dict[str, list[str]] = defaultdict(list)

    for line in input.splitlines():
        parts = line.split('->')
        label = parts[0].strip()
        outputs = parts[1].strip().split(', ') if len(parts) > 1 else []

        if label[0] in COMPONENT_TYPES:
            component_type = COMPONENT_TYPES[label[0]]
            label = label[1:]
        elif label == 'broadcaster':
            component_type = Broadcast
        else:
            raise Exception(f'Unknown component type: {label}')

        types[label] = component_type
        output_connections[label] = outputs

    input_connections: dict[str, list[str]] = defaultdict(list)

    for label, outputs in output_connections.items():
        for output in outputs:
            input_connections[output].append(label)

    # components with no outputs are sinks
    for label in input_connections.keys():
        if label not in output_connections:
            types[label] = Sink

    # create circuit
    for label, component_type in types.items():
        component = component_type(label)
        component.observer = observer

        components[label] = component

    for label, outputs in output_connections.items():
        components[label].output_components = [components[output] for output in outputs]

    for label, inputs in input_connections.items():
        components[label].input_components = [components[input] for input in inputs]

    button = Broadcast('button')
    button.output_components = [components['broadcaster']]
    button.observer = observer
    components['button'] = button

    return components

def resolve(components: dict[str, Component], num_presses: int) -> None:
    for i in range(num_presses):
        components['button'].send_output(Pulse.LOW)
        queue = [components['broadcaster']]

        while len(queue):
            component = queue.pop()
            if component.tick():
                queue.extend(component.output_components)

def generate_graphviz(components: dict[str, Component]) -> Digraph:
    dot = graphviz.Digraph()

    for component in components.values():
        shape = 'ellipse'  # default shape
        if isinstance(component, Conjunction):
            shape = 'box'  # square shape for Conjunction nodes
        elif isinstance(component, FlipFlop):
            shape = 'diamond'  # diamond shape for FlipFlop nodes
        dot.node(component.label, shape=shape)

    for component in components.values():
        if component.output_components:
            for output in component.output_components:
                dot.edge(component.label, output.label)

    return dot
def lcm_of_list(numbers):
    lcm = numbers[0]
    for number in numbers[1:]:
        lcm = lcm * number // math.gcd(lcm, number)
    return lcm

def main():
    input = open('input.txt').read().strip()
    # input = open('example.txt').read().strip()

    counts = defaultdict(int)
    def count_outputs(input: Component, output: Component, pulse: Pulse):
        counts[pulse] += 1

    components = parse(input, count_outputs)
    resolve(components, 1000)

    answer = counts[Pulse.HIGH] * counts[Pulse.LOW]

    print("part 1 =", answer)

    # Used to generate a visualization of the circuit. This made it clear there are several
    # subcomponents feeding into a Conjunction 'hj' which is connected to 'rx'.
    #
    # I verified that these repeat on a regular cadence. Then the answer is just the LCM of
    # the cycle lengths (which happen to be all prime, so this is equivalent to their product).
    #
    # os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
    # dot = generate_graphviz(components)
    # dot.render('circuit_graph', format='png')

    press = 1
    first_high_signals: dict[str, int] = {}

    def output_watcher(input: Component, output: Component, pulse: Pulse):
        if output.label == 'hj' and pulse == Pulse.HIGH and input.label not in first_high_signals:
            first_high_signals[input.label] = press

    components = parse(input, output_watcher)

    while len(first_high_signals) < 4:
        resolve(components, 1)
        press += 1

    print('part 2')

    for label, press in first_high_signals.items():
        print(f'{label}: {press}')

    print('answer =', lcm_of_list(list(first_high_signals.values())))


if __name__ == '__main__':
    main()
