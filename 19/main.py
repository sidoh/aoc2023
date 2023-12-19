import re
from enum import Enum
from typing import Literal, TypedDict, Optional, Callable, get_args

Operation = Enum('Operation', ['LESS_THAN', 'GREATER_THAN', 'PASSTHROUGH'])
Variable = Literal['x', 'm', 'a', 's']

# example: qqz{s>2770:qs,m<1801:hdj,R}
WORKFLOW = re.compile(r'(\w+)\{([^]]+)}')


class Part(TypedDict):
    rankings: dict[Variable, int]


class WorkflowOperation:
    operation: Operation
    workflow: str
    value: int
    variable: Optional[Variable]

    def __init__(self, operation: Operation, workflow: str, value: int = None, variable: Optional[Variable] = None):
        self.operation = operation
        self.workflow = workflow
        self.value = value
        self.variable = variable

    def passes(self, part: Part) -> bool:
        if not self.variable:
            return self.get_operation_fn()(0)
        else:
            return self.get_operation_fn()(part['rankings'][self.variable])

    def get_operation_fn(self) -> Callable[[int], bool]:
        if self.operation == Operation.LESS_THAN:
            return lambda x: x < self.value
        elif self.operation == Operation.GREATER_THAN:
            return lambda x: x > self.value
        elif self.operation == Operation.PASSTHROUGH:
            return lambda x: True
        else:
            raise Exception(f'Unknown operation: {self.operation}')

    def __repr__(self):
        if self.operation == Operation.PASSTHROUGH:
            return 'PASSTHROUGH'
        elif self.operation == Operation.LESS_THAN:
            return f'{self.variable} < {self.value}'
        elif self.operation == Operation.GREATER_THAN:
            return f'{self.variable} > {self.value}'
        else:
            return f'{self.operation.name} {self.variable} {self.value} {self.workflow}'


class Workflow(TypedDict):
    label: str
    operations: list[WorkflowOperation]


class Constraints:
    min_values: dict[Variable, int]
    max_values: dict[Variable, int]

    def __init__(self, min_values: Optional[dict[Variable, int]] = None,
                 max_values: Optional[dict[Variable, int]] = None):
        self.min_values = min_values or {k: 1 for k in get_args(Variable)}
        self.max_values = max_values or {k: 4000 for k in get_args(Variable)}

    def constrain(self, op: WorkflowOperation) -> 'Constraints':
        if op.operation == Operation.PASSTHROUGH:
            return Constraints(self.min_values.copy(), self.max_values.copy())

        if op.operation == Operation.LESS_THAN:
            new_max_values = self.max_values.copy()
            new_max_values[op.variable] = min(self.max_values[op.variable], op.value - 1)
            return Constraints(self.min_values.copy(), new_max_values)
        elif op.operation == Operation.GREATER_THAN:
            new_min_values = self.min_values.copy()
            new_min_values[op.variable] = max(self.min_values[op.variable], op.value + 1)
            return Constraints(new_min_values, self.max_values.copy())
        else:
            raise Exception(f'Unknown operation: {op.operation}')

    def inverted_constrain(self, op: WorkflowOperation) -> 'Constraints':
        if op.operation == Operation.PASSTHROUGH:
            return self.constrain(op)
        elif op.operation == Operation.LESS_THAN:
            return self.constrain(WorkflowOperation(Operation.GREATER_THAN, op.workflow, op.value - 1, op.variable))
        elif op.operation == Operation.GREATER_THAN:
            return self.constrain(WorkflowOperation(Operation.LESS_THAN, op.workflow, op.value + 1, op.variable))
        else:
            raise Exception(f'Unknown operation: {op.operation}')

    def total_valid_parts(self) -> int:
        total = 1

        for variable in get_args(Variable):
            total *= self.max_values[variable] - self.min_values[variable] + 1

        return total

    def __repr__(self):
        return " & ".join([f'{str(self.min_values[v]).rjust(4)} <= {v} <= {str(self.max_values[v]).ljust(4)}' for v in
                           get_args(Variable)])


def parse_operation(operation: str) -> WorkflowOperation:
    parts = re.match(r'([xmas])([<>=])(\w+):(\w+)', operation)

    if not parts:
        return WorkflowOperation(
            operation=Operation.PASSTHROUGH,
            variable=None,
            workflow=operation,
        )

    variable = parts.group(1)
    operator = parts.group(2)
    value = parts.group(3)
    workflow = parts.group(4)

    if operator == '<':
        operator = 'LESS_THAN'
    elif operator == '>':
        operator = 'GREATER_THAN'

    return WorkflowOperation(
        operation=Operation[operator],
        variable=variable,
        value=int(value),
        workflow=workflow)


def parse_workflow(workflow: str) -> Workflow:
    parts = WORKFLOW.match(workflow)

    if not parts:
        raise Exception(f'Failed to parse workflow: {workflow}')

    label = parts.group(1)
    operations = parts.group(2)

    return {
        'label': label,
        'operations': [
            parse_operation(operation)
            for operation in operations.split(',')
        ]
    }


def parse_part(part: str) -> Part:
    """
    example: {x=1679,m=44,a=2067,s=496}
    """
    parts = re.match(r'{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}', part)

    return {
        'rankings': {
            'x': int(parts.group(1)),
            'm': int(parts.group(2)),
            'a': int(parts.group(3)),
            's': int(parts.group(4)),
        }
    }


def find_accepted_parts(start_workflow: Workflow, workflows: dict[str, Workflow], parts: list[Part]) -> list[Part]:
    accepted_parts = []

    for part in parts:
        current_workflow = start_workflow

        while current_workflow['label'] not in ['A', 'R']:
            for operation in current_workflow['operations']:
                if operation.passes(part):
                    current_workflow = workflows[operation.workflow]
                    break

        if current_workflow['label'] == 'A':
            accepted_parts.append(part)

    return accepted_parts


def get_valid_constraints(workflow: Workflow, workflows: dict[str, Workflow], constraints: Constraints) -> list[
    Constraints]:
    if workflow['label'] == 'A':
        return [constraints]
    elif workflow['label'] == 'R':
        return []

    valid_constraints = []

    for operation in workflow['operations']:
        new_constraints = constraints.constrain(operation)
        valid_constraints += get_valid_constraints(workflows[operation.workflow], workflows, new_constraints)
        constraints = constraints.inverted_constrain(operation)

    return valid_constraints


def main():
    input = open('input.txt').read().strip()
    # input = open('example.txt').read().strip()
    # input = EXAMPLE

    input_workflows, input_parts = input.split('\n\n')

    workflows: dict[str, Workflow] = {}
    parts: list[Part] = []

    workflows['A'] = {
        'label': 'A',
        'operations': []
    }
    workflows['R'] = {
        'label': 'R',
        'operations': []
    }

    for line in input_workflows.split('\n'):
        workflow = parse_workflow(line)
        workflows[workflow['label']] = workflow

    for line in input_parts.split('\n'):
        part = parse_part(line)
        parts.append(part)

    accepted_parts = find_accepted_parts(workflows['in'], workflows, parts)

    # sum all x m a s values for every accepted part
    answer = sum([
        sum(part['rankings'].values())
        for part in accepted_parts
    ])

    print("part 1 =", answer)

    valid_constraints = get_valid_constraints(workflows['in'], workflows, Constraints())
    answer = sum([
        constraints.total_valid_parts()
        for constraints in valid_constraints
    ])

    print("part 2 =", answer)


if __name__ == '__main__':
    main()
