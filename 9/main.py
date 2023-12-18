from typing import List, Tuple

EXAMPLE = """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
""".strip()

def extend_sequence(sequence: List[int]) -> Tuple[int, int]:
    # Base case
    if all(0 == x for x in sequence):
        return 0, 0

    # Compute differences in elements
    differences = [sequence[i+1] - sequence[i] for i in range(len(sequence) - 1)]

    # Recurse
    prev_diff, next_diff = extend_sequence(differences)

    return sequence[0] - prev_diff, sequence[-1] + next_diff

def solve_sequences(sequences: str) -> List[int]:
    sequences = [list(map(int, line.split())) for line in sequences.split('\n') if line]
    next_values = [extend_sequence(sequence) for sequence in sequences]

    print(next_values)

    return [sum(x[i] for x in next_values) for i in range(2)]

def main():
    input = open('input.txt').read().strip()
    # input = EXAMPLE

    print(solve_sequences(input))

if __name__ == '__main__':
    main()