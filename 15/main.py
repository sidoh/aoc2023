EXAMPLE = """
rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7
""".strip()

def hash_token(token: str) -> int:
    v = 0
    for c in token:
        v = ((v + ord(c)) * 17) % 256
    return v

class Box:
    def __init__(self):
        self.lenses = []

    def add_lens(self, label: str, focal_len: int):
        if any(lens[0] == label for lens in self.lenses):
            # update focal length
            self.lenses = [(lens[0], focal_len) if lens[0] == label else lens for lens in self.lenses]
        else:
            self.lenses.append((label, focal_len))

    def remove_lens(self, label: str):
        self.lenses = [lens for lens in self.lenses if lens[0] != label]

    def focusing_power(self):
        return sum((i+1) * focal_len for i, (_, focal_len) in enumerate(self.lenses))

    def __repr__(self):
        return ' '.join(f'[{label} {focal_len}]' for label, focal_len in self.lenses)

class Table:
    def __init__(self):
        self.boxes = [Box() for _ in range(256)]

    def add_lens(self, label: str, focal_len: int):
        self.boxes[hash_token(label)].add_lens(label, focal_len)

    def remove_token(self, label: str):
        self.boxes[hash_token(label)].remove_lens(label)

    def focusing_power(self):
        return sum((i + 1) * box.focusing_power() for i, box in enumerate(self.boxes))

    def __repr__(self):
        return '\n'.join(f'Box {i}: {box}' for i, box in enumerate(self.boxes) if box.lenses)

def solve1(input: str) -> int:
    tokens = input.split(',')

    # Compute the hash of each token
    hashes = [hash_token(token) for token in tokens]

    # Compute the sum of the hashes
    return sum(hashes)

def solve2(input: str) -> int:
    tokens = input.split(',')
    table = Table()

    for token in tokens:
        if token.endswith('-'):
            table.remove_token(token[:-1])
        else:
            label, focal_len = token.split('=')
            table.add_lens(label, int(focal_len))

    # Compute the sum of the hashes
    return table.focusing_power()

def main():
    input = open('input.txt').read().strip()
    # input = EXAMPLE

    print(solve1(input))
    print(solve2(input))

if __name__ == '__main__':
    main()
