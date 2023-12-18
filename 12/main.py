from typing import Tuple, List, Dict

EXAMPLE1 = """
?###???????? 3,2,1
""".strip()

EXAMPLE2 = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
""".strip()


def parse_line(l: str) -> Tuple[str, List[int]]:
    parts = l.split()
    return parts[0], [int(x) for x in parts[1].split(',')]


def solve_count(row: str, run_lengths: List[int], dt: Dict[Tuple[chr, int, int], int]) -> int:
    key = (row[0] if len(row) > 0 else None, len(row), len(run_lengths))

    if key in dt:
        return dt[key]

    if len(row) == 0 and len(run_lengths) == 0:
        r = 1
    elif len(run_lengths) == 0:
        r = 1 if '#' not in row else 0
    elif sum(run_lengths) > len(row):
        r = 0
    elif row[0] == '.':
        r = solve_count(row[1:], run_lengths, dt)
    elif row[0] == '#':
        n = run_lengths[0]

        # Run can be satisfied if:
        #   1. There is space for the run
        #   2. The run stops: the character after that is ? or . OR run_lengths[0] == len(row)
        run_fits = all(x == '#' or x == '?' for x in row[:n])
        run_stops = (len(row) == n or row[n] == '.' or row[n] == '?')

        if run_fits and run_stops:
            if len(row) == n:
                r = solve_count('', run_lengths[1:], dt)
            else:
                r = solve_count(row[n+1:], run_lengths[1:], dt)
        else:
            r = 0
    else:
        r = (
                solve_count('#' + row[1:], run_lengths, dt) +
                solve_count('.' + row[1:], run_lengths, dt)
        )

    dt[key] = r
    return r

def solve(row: str, run_lengths: List[int]) -> List[str]:
    if len(row) == 0 and len(run_lengths) == 0:
        return ['']
    elif len(run_lengths) == 0:
        return [''] if '#' not in row else []
    elif sum(run_lengths) > len(row):
        return []

    if row[0] == '.':
        return ['.' + x for x in solve(row[1:], run_lengths)]
    elif row[0] == '#':
        n = run_lengths[0]

        # Run can be satisfied if:
        #   1. There is space for the run
        #   2. The run stops: the character after that is ? or . OR run_lengths[0] == len(row)
        run_fits = all(x == '#' or x == '?' for x in row[:n])
        run_stops = (len(row) == n or row[n] == '.' or row[n] == '?')

        if run_fits and run_stops:
            if len(row) == n:
                return [('#' * n) + x for x in solve('', run_lengths[1:])]
            else:
                return [('#' * n) + '.' + x for x in solve(row[n+1:], run_lengths[1:])]
        else:
            return []
    else:
        return (
            solve('#' + row[1:], run_lengths) +
            solve('.' + row[1:], run_lengths)
        )


def run(input: str, expansion: int = 1):
    total = 0

    for l in input.split('\n'):
        row, run_lengths = parse_line(l)

        expanded_row = '?'.join([row] * expansion)
        total += solve_count(expanded_row, run_lengths*expansion, {})

    print(total)


if __name__ == '__main__':
    run(open('input.txt').read().strip(), 5)