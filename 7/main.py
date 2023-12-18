from typing import List, Callable


class Card:
    rank: str
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self, rank: str):
        self.rank = rank

    def __str__(self):
        return self.rank

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return Card.RANKS.index(self.rank) < Card.RANKS.index(other.rank)

    def __eq__(self, other):
        return self.rank == other.rank

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    @staticmethod
    def from_string(s: str) -> 'Card':
        return Card(s)

class Joker(Card):
    def __init__(self):
        super().__init__('J')

    def __lt__(self, other):
        return other.rank != 'J'

    def __eq__(self, other):
        return other.rank == 'J'

    def __gt__(self, other):
        return False

    def __str__(self):
        return '*'

    @staticmethod
    def from_string(s: str) -> Card:
        if s != 'J':
            return Card.from_string(s)
        else:
            return Joker()

class Hand:
    cards: List[Card]
    card_groups: List[List[Card]]
    group_sizes: List[int]
    bid: int

    GROUP_SIZE_RANKS = [
        [5],
        [4, 1],
        [3, 2],
        [3, 1, 1],
        [2, 2, 1],
        [2, 1, 1, 1],
        [1, 1, 1, 1, 1]
    ]

    def __init__(self, cards: List[Card], card_groups: List[List[Card]], bid: int):
        self.bid = bid

        self.cards = cards
        self.card_groups = card_groups

        # Create list of group sizes
        self.group_sizes = list(map(lambda group: len(group), self.card_groups))
        self.group_size_rank = Hand.GROUP_SIZE_RANKS.index(self.group_sizes)

    def __str__(self):
        return "Hand(cards={}, card_groups={}, size_rank={}, bid={})".format(self.cards, self.card_groups, self.group_size_rank, self.bid)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other: 'Hand') -> bool:
        """
        Compare this hand to another hand. Return 1 if this hand is stronger, -1
        if the other hand is stronger, or 0 if they are equal.
        Hand type rankings:
            1. Five of a kind
            2. Four of a kind
            3. Full house
            4. Three of a kind
            5. Two pair
            6. One pair
            7. High card

        If two hands have the same type, a second ordering rule takes effect. Start by comparing the first card in
        each hand. If these cards are different, the hand with the stronger first card is considered stronger.
        If the first card in each hand have the same label, however, then move on to considering the second card in
        each hand. If they differ, the hand with the higher second card wins; otherwise, continue with the third card
        in each hand, then the fourth, then the fifth.

        :param other:
        :return:
        """

        if self.group_size_rank > other.group_size_rank:
            return False
        elif self.group_size_rank < other.group_size_rank:
            return True
        else:
            # Just compare cards in order for tiebreak
            for i in range(len(self.cards)):
                if self.cards[i] > other.cards[i]:
                    return True
                elif self.cards[i] < other.cards[i]:
                    return False

            return False

    def __eq__(self, other):
        return self.cards == other.cards

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    @staticmethod
    def from_string(s: str, card_parser: Callable[[str], Card] = Card.from_string) -> 'Hand':
        s = s.split(' ')
        bid = int(s[1])
        cards = [card_parser(x) for x in s[0]]

        sorted_cards = cards.copy()
        sorted_cards.sort(key=lambda card: Card.RANKS.index(card.rank))

        # Create lists of groups of cards of the same rank
        card_groups = []
        current_group = []
        current_rank = None

        for card in sorted_cards:
            if card.rank != current_rank:
                if current_group:
                    card_groups.append(current_group)
                    current_group = []

                current_rank = card.rank

            current_group.append(card)

        if current_group:
            card_groups.append(current_group)

        # Sort groups by length
        card_groups.sort(key=lambda group: len(group), reverse=True)

        return Hand(cards, card_groups, bid)

class JokerHand(Hand):
    """
    Behaves the same as Hand, except Jokers are wildcards and fit into the group that makes the best hand
    """

    def __init__(self, raw_hand: Hand, card_groups: List[List[Card]]):
        super().__init__(raw_hand.cards, card_groups, raw_hand.bid)
        self.raw_hand = raw_hand

    def __str__(self):
        return "Joker" + super().__str__()

    def __lt__(self, other):
        """
        :param other:
        :return:
        """

        if self.group_size_rank > other.group_size_rank:
            return False
        elif self.group_size_rank < other.group_size_rank:
            return True
        else:
            return super().__lt__(other)

    def __eq__(self, other):
        return self.cards == other.cards

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    @staticmethod
    def from_string(s: str, card_parser: Callable[[str], Card] = Joker.from_string) -> Hand:
        raw_hand = Hand.from_string(s, card_parser)
        joker_group = None

        for i in range(len(raw_hand.card_groups)):
            if raw_hand.card_groups[i][0].rank == 'J':
                joker_group = i
                break

        if joker_group is None:
            return raw_hand
        else:
            # Filter joker out of groups
            joker_group_v = raw_hand.card_groups[joker_group]
            card_groups = raw_hand.card_groups.copy()
            card_groups.remove(joker_group_v)

            # Add jokers to largest group.
            # edge case: whole group is jokers
            if len(card_groups) == 0:
                card_groups = [joker_group_v]
            else:
                card_groups[0] += joker_group_v

            return JokerHand(raw_hand, card_groups)

def main2():
    with open("input.txt") as f:
        hands = []

        while True:
            line = f.readline()

            if not line:
                break

            hand = JokerHand.from_string(line.strip())
            hands.append(hand)

        hands.sort(reverse=True)
        winnings = 0

        for i in range(len(hands)):
            winnings += hands[i].bid * (i + 1)
            print(hands[i])

        print(winnings)

if __name__ == '__main__':
    main2()