from typing import List

POSSILBE_GAME_FILTER = {
    'red': lambda x: x <= 12,
    'green': lambda x: x <= 13,
    'blue': lambda x: x <= 14
}

# Game will be in format:
# X1 green, Y1 red, Z1 blue; X2 green, X2 red, X2 blue; ...
def parse_game(line: str) -> List[List[int]]:
    max_seen = { 'green': 0, 'red': 0, 'blue': 0 }
    samples = line.split(';')

    for sample in samples:
        counts = sample.strip().split(',')

        for count in counts:
            num, color = count.strip().split(' ')
            num = int(num)

            if num > max_seen[color]:
                max_seen[color] = num

    return max_seen

def main():
    # Read the file
    with open("input.txt") as f:
        lines = f.readlines()

    sum_possible = 0
    sum_powers = 0

    for line in lines:

        # game line in format:
        # Game N: (game data)
        # extract N and (game data)
        game_num, game_data = line.split(':')
        game_num = int(game_num.split(' ')[1].strip())

        # print(game_num, game_data.strip())

        max_seen = parse_game(game_data)
        # print(max_seen)
        # print(max_seen['green'], max_seen['red'], max_seen['blue'])

        game_possible = True
        game_power = 1

        for color, max_num in max_seen.items():
            if not POSSILBE_GAME_FILTER[color](max_num):
                print(f'Game {game_num} is not possible')
                game_possible = False
            game_power *= max_num

        if game_possible:
            print(f'Game {game_num} is possible')
            sum_possible += game_num

        sum_powers += game_power

    print("Sum of possible games:", sum_possible)
    print("Sum of powers:", sum_powers)

if __name__ == '__main__':
    main()