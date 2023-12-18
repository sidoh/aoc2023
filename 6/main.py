import math
from typing import List, Tuple

EXAMPLE = """
Time:      7  15   30
Distance:  9  40  200
""".strip()

INPUT = """
Time:        48     87     69     81
Distance:   255   1288   1117   1623
""".strip()

LONG_RACE_TIME = 48876981
LONG_RACE_DISTANCE = 255128811171623

def parse_input(input_string: str) -> List[Tuple[int, int]]:
    lines = input_string.split('\n')
    time_line = list(map(int, lines[0].split(':')[1].split()))
    distance_line = list(map(int, lines[1].split(':')[1].split()))
    return list(zip(time_line, distance_line))

def solve(N, K):
    """
    Given a distance K for race length N, the first distance greater than K will be
    the smallest integer x satisfying:

    (N-x)*x > K

    Turn this into a quadratic equation:

    Nx - x^2 - K > 0
    x^2 - Nx + K < 0

    Solve for x:

    x = N +/- sqrt(N^2 - 4K) / 2

    So the first length that will be greater than K is:

    ceil(N - sqrt(N^2 - 4K) / 2))

    So the number of races that will be greater than K is:

    (N+1) - 2*ceil(N - sqrt(N^2 - 4K) / 2))

    (there are (N+1) because 0 counts)
    """
    val = (N - math.sqrt(N*N - 4*K)) / 2

    # If val is an integer, then we need to add 1 to it because we want the
    # first value greater than K, not the first value greater than or equal to K
    if val == int(val):
        val = int(val) + 1
    else:
        val = math.ceil(val)

    return (N+1) - 2*val

def main():
    input_data = parse_input(INPUT)
    answer = 1

    for N, K in input_data:
        val = solve(N, K)
        answer *= val

    print(answer)

    print(solve(LONG_RACE_TIME, LONG_RACE_DISTANCE))

if __name__ == "__main__":
    main()