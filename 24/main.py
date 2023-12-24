import sympy

Point = tuple[int, int, int]
Velocity = Point

def solve_tx(p: Point, v: Velocity, x: float) -> float:
    return (x - p[0])/v[0]

def solve_ty(p: Point, v: Velocity, y: float) -> float:
    return (y - p[1])/v[1]

def get_intersect_x(p1: Point, p2: Point, v1: Velocity, v2: Velocity) -> float:
    try:
        return (p1[1] - p2[1] + (v2[1]/v2[0])*p2[0] - (v1[1]/v1[0])*p1[0])/((v2[1]/v2[0]) - (v1[1]/v1[0]))
    except ZeroDivisionError:
        return -1

def get_intersect_y(p1: Point, p2: Point, v1: Velocity, v2: Velocity) -> float:
    try:
        return (p1[0] - p2[0] - (v1[0]/v1[1])*p1[1] + (v2[0]/v2[1])*p2[1])/((v2[0]/v2[1]) - (v1[0]/v1[1]))
    except ZeroDivisionError:
        return -1

def parse(input: str) -> list[tuple[Point, Velocity]]:
    # ex: 19, 13, 30 @ -2,  1, -2
    # in the format of: x, y, z @ vx, vy, vz

    a = []
    for line in input.splitlines():
        p = line.split('@')[0].strip()
        v = line.split('@')[1].strip()
        p = tuple(map(int, p.split(',')))
        v = tuple(map(int, v.split(',')))
        a.append((p, v))

    return a

values = parse(open('example.txt').read())
test_x = (7, 27)
test_y = test_x

values = parse(open('input.txt').read())
test_x = (200000000000000, 400000000000000)
test_y = test_x

crossed = 0

for i in range(len(values)):
    for j in range(i+1, len(values)):
        p1, v1 = values[i]
        p2, v2 = values[j]

        x = get_intersect_x(p1, p2, v1, v2)
        y = get_intersect_y(p1, p2, v1, v2)

        tx = solve_tx(p1, v1, x)
        ty = solve_ty(p2, v2, y)

        if test_x[0] <= x <= test_x[1] and test_y[0] <= y <= test_y[1] and tx > 0 and ty > 0:
            crossed += 1

print("part 1 =", crossed)

# part two, find where we can place + throw a boulder such that it intersects with all hailstones

bx = sympy.symbols('bx', integer=True)
by = sympy.symbols('by')
bz = sympy.symbols('bz')

vx = sympy.symbols('vx')
vy = sympy.symbols('vy')
vz = sympy.symbols('vz')

bx, by, bz, vx, vy, vz = sympy.symbols('bx by bz vx vy vz', integer=True)

equations = []
variables = [bx, by, bz, vx, vy, vz]

for i in range(len(values)):
    p, v = values[i]
    t = sympy.symbols(f't{i}', integer=True)
    variables.append(t)
    equations.append(
        bx + vx*t - p[0] - v[0]*t
    )
    equations.append(
        by + vy*t - p[1] - v[1]*t
    )
    equations.append(
        bz + vz*t - p[2] - v[2]*t
    )

    if i >= 3:
        break

for answer in sympy.nonlinsolve(equations, variables):
    print("part 2 =", answer[0] + answer[1] + answer[2])