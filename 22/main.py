from collections import defaultdict
from dataclasses import dataclass

EXAMPLE1 = ("""
1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9
""").strip()

@dataclass
class Brick:
    label: str
    x_bounds: tuple[int, int]
    y_bounds: tuple[int, int]
    z_bounds: tuple[int, int]

    position: tuple[int, int, int]

    def contains_point(self, point: tuple[int, int, int]) -> bool:
        return all([
            self.x_bounds[0] <= point[0] <= self.x_bounds[1],
            self.y_bounds[0] <= point[1] <= self.y_bounds[1],
            self.z_bounds[0] <= point[2] <= self.z_bounds[1],
        ])

    def is_supporting(self, other: 'Brick') -> bool:
        return (
            other.z_bounds[0] - 1 == self.z_bounds[1] and
            self.intersects_x(other) and
            self.intersects_y(other)
        )

    def intersects_x(self, other: 'Brick') -> bool:
        return not (other.x_bounds[1] < self.x_bounds[0] or other.x_bounds[0] > self.x_bounds[1])

    def intersects_y(self, other: 'Brick') -> bool:
        return not (other.y_bounds[1] < self.y_bounds[0] or other.y_bounds[0] > self.y_bounds[1])

    def __hash__(self):
        return hash((self.x_bounds, self.y_bounds, self.z_bounds))

    def __eq__(self, other):
        return (
            self.x_bounds == other.x_bounds and
            self.y_bounds == other.y_bounds and
            self.z_bounds == other.z_bounds
        )

    def __repr__(self):
        return self.label

    def __str__(self):
        return self.label

    def dump(self) -> str:
        return f'{self.x_bounds[0]},{self.y_bounds[0]},{self.z_bounds[0]}~{self.x_bounds[1]},{self.y_bounds[1]},{self.z_bounds[1]}'


@dataclass
class Container:
    bricks: list[Brick]

    def bounds(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        return (
            (min(b.x_bounds[0] for b in self.bricks), max(b.x_bounds[1] for b in self.bricks)),
            (min(b.y_bounds[0] for b in self.bricks), max(b.y_bounds[1] for b in self.bricks)),
            (min(b.z_bounds[0] for b in self.bricks), max(b.z_bounds[1] for b in self.bricks)),
        )

    def dump(self) -> str:
        return '\n'.join(b.dump() for b in self.bricks)

    def settle2(self):
        # for each block, shift downward until supported. only blocks below can support
        sorted_bricks = sorted(self.bricks, key=lambda b: b.z_bounds[0])

        for b1_i in range(len(sorted_bricks)):
            b1 = sorted_bricks[b1_i]

            if b1.z_bounds[0] == 1:
                continue

            max_z = 0

            for b2_i in range(0, b1_i):
                b2 = sorted_bricks[b2_i]
                if b2.intersects_x(b1) and b2.intersects_y(b1) and b2.z_bounds[1] > max_z:
                    max_z = b2.z_bounds[1]

            if max_z < b1.z_bounds[0] - 1:
                shifted_by = b1.z_bounds[0] - 1 - max_z
                b1.z_bounds = (max_z + 1, b1.z_bounds[1] - shifted_by)


    def settle(self):
        # Consider pairs of bricks b1 and b2. If there is no b2 below b1, shift b1 down.
        # Do this until there are no bricks left to settle.
        shifted = True

        print("settling...")

        sorted_z_min = sorted(self.bricks, key=lambda b: b.z_bounds[0])
        sorted_z_max = sorted(self.bricks, key=lambda b: b.z_bounds[1])

        while shifted:
            shifted = False

            num_settled = 0

            for b1_i in range(len(self.bricks)):
                b1 = sorted_z_min[b1_i]
                b1_supported = False

                # Do not consider bricks which are at the bottom
                if b1.z_bounds[0] == 1:
                    continue

                for b2_i in range(len(self.bricks)):
                    b2 = sorted_z_max[b2_i]

                    if b1 == b2:
                        continue
                    elif b2.z_bounds[1] > b1.z_bounds[0]:
                        break
                    elif b2.z_bounds[1] < b1.z_bounds[0] - 1:
                        continue
                    elif b2.is_supporting(b1):
                        b1_supported = True
                        break

                if not b1_supported:
                    num_settled += 1
                    b1.z_bounds = (b1.z_bounds[0] - 1, b1.z_bounds[1] - 1)
                    shifted = True

        print("done settling")

    def print_layers(self):
        x_bounds, y_bounds, z_bounds = self.bounds()
        for z in range(z_bounds[0], z_bounds[1] + 1):
            print(f'z={z}')
            for y in range(y_bounds[0], y_bounds[1] + 1):
                for x in range(x_bounds[0], x_bounds[1] + 1):
                    for brick in self.bricks:
                        if brick.contains_point((x, y, z)):
                            print(brick.label, end='')
                            break
                    else:
                        print('.', end='')
                print()
            print()

    def print_y(self):
        x_bounds, y_bounds, z_bounds = self.bounds()
        for y in range(y_bounds[0], y_bounds[1] + 1):
            print(f'{y}', end='')
        print()

        for z in range(z_bounds[1], z_bounds[0] - 1, -1):
            for y in range(y_bounds[0], y_bounds[1] + 1):
                x_points = [(x, y, z) for x in range(x_bounds[0], x_bounds[1] + 1)]
                contained_bricks = [brick for brick in self.bricks if any(brick.contains_point(p) for p in x_points)]
                if len(contained_bricks) == 0:
                    print('.', end='')
                elif len(contained_bricks) == 1:
                    print(contained_bricks[0].label, end='')
                else:
                    print('?', end='')

            print(f' {z}')
        print('-'*(y_bounds[1] - y_bounds[0] + 1))

    def print_x(self):
        x_bounds, y_bounds, z_bounds = self.bounds()
        for x in range(x_bounds[0], x_bounds[1] + 1):
            print(f'{x}', end='')
        print()

        for z in range(z_bounds[1], z_bounds[0] - 1, -1):
            for x in range(x_bounds[0], x_bounds[1] + 1):
                y_points = [(x, y, z) for y in range(y_bounds[0], y_bounds[1] + 1)]
                contained_bricks = [brick for brick in self.bricks if any(brick.contains_point(p) for p in y_points)]
                if len(contained_bricks) == 0:
                    print('.', end='')
                elif len(contained_bricks) == 1:
                    print(contained_bricks[0].label, end='')
                else:
                    print('?', end='')

            print(f' {z}')
        print('-'*(x_bounds[1] - x_bounds[0] + 1))


def parse(input: str) -> Container:
    bricks = []
    for line in input.splitlines():
        # lines in format: x1,y1,z1~x2,y2,z2
        points = line.split('~')
        p1 = tuple(int(x) for x in points[0].split(','))
        p2 = tuple(int(x) for x in points[1].split(','))
        bricks.append(Brick(
            label=chr(len(bricks)%26 + 65),
            x_bounds=(p1[0], p2[0]),
            y_bounds=(p1[1], p2[1]),
            z_bounds=(p1[2], p2[2]),
            position=p1,
        ))
    return Container(bricks=bricks)

def get_support_structure(container: Container) -> tuple[dict[Brick, set[Brick]], dict[Brick, set[Brick]]]:
    # compute support relationships in direction x -> y means x supports y
    supports: dict[Brick, set[Brick]] = defaultdict(set)
    supported_by: dict[Brick, set[Brick]] = defaultdict(set)
    for b1 in container.bricks:
        for b2 in container.bricks:
            if b1 == b2:
                continue

            if b1.is_supporting(b2):
                supports[b1].add(b2)
                supported_by[b2].add(b1)

    return supports, supported_by

def measure_removal_chain(brick: Brick, supports: dict[Brick, set[Brick]], supported_by: dict[Brick, set[Brick]]) -> int:
    removed: set[Brick] = {brick}
    to_remove: set[Brick] = supports[brick].copy()

    while to_remove:
        block = to_remove.pop()

        if all(b in removed for b in supported_by[block]):
            removed.add(block)
            to_remove.update(supports[block])

    return len(removed) - 1


def solve2(container: Container) -> int:
    supports, supported_by = get_support_structure(container)

    answer = 0
    for brick in container.bricks:
        answer += measure_removal_chain(brick, supports, supported_by)

    return answer

def solve1(container: Container) -> int:
    # compute support relationships in direction x -> y means x supports y
    supports, supported_by = get_support_structure(container)

    removable = 0

    for brick in container.bricks:
        supported = supports[brick]
        # see if all supported bricks are supported by other bricks
        if all(len(supported_by[b]) > 1 for b in supported) or len(supported) == 0:
            removable += 1

    return removable

if __name__ == "__main__":
    # input_str = EXAMPLE1
    input_str = open('input.txt').read().strip()

    container = parse(input_str)
    container.settle2()

    print(solve1(container))
    print(solve2(container))