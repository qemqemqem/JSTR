from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
import itertools
from abc import ABC

@dataclass
class Card:
    """A card in the game of Set has 4 attributes"""
    color: str      # red, green, or purple
    shape: str      # oval, squiggle, or diamond  
    number: int     # 1, 2, or 3
    shading: str    # solid, striped, or open

    @classmethod
    def from_code(cls, code: str) -> 'Card':
        """Create a card from a code string like 'R-O-1-S' """
        color, shape, number, shading = code.split('-')
        return cls(color, shape, int(number), shading)
    
    def to_code(self) -> str:
        """Convert card to code string"""
        return f"{self.color}-{self.shape}-{self.number}-{self.shading}"

class GameOfSet:
    """Represents a game of Set with a board of cards and methods to find valid sets"""
    
    COLORS = ['R', 'G', 'P']  # Red, Green, Purple
    SHAPES = ['O', 'S', 'D']  # Oval, Squiggle, Diamond
    NUMBERS = [1, 2, 3]
    SHADINGS = ['S', 'H', 'O']  # Solid, sHaded, Open

    def __init__(self, board: List[Card], valid_set: Optional[List[Card]] = None, think_through: bool = False):
        """Initialize with a board of cards and optionally a known valid set"""
        self.board = board
        self.valid_set = valid_set
        self.think_through = think_through
        
    @classmethod
    def random_game(cls, board_size: int = 12, think_through: bool = False) -> 'GameOfSet':
        """Generate a random game board with exactly one valid set"""
        while True:
            # Generate all possible cards
            all_cards = [
                Card(c, s, n, h)
                for c, s, n, h in itertools.product(
                    cls.COLORS, cls.SHAPES, cls.NUMBERS, cls.SHADINGS
                )
            ]
            
            # Randomly select cards for the board
            board = random.sample(all_cards, board_size)
            
            # Find all valid sets on the board
            valid_sets = cls.find_all_sets(board)
            
            # If we found exactly one valid set, we're done
            # print(f"Found {len(valid_sets)} valid sets")  # This seems to happen on average 5-10 times or something, which is not too bad
            if len(valid_sets) == 1:
                return cls(board, valid_sets[0], think_through=think_through)
    
    @staticmethod
    def is_valid_set(cards: List[Card]) -> bool:
        """Check if three cards form a valid set"""
        if len(cards) != 3:
            return False
            
        # For each attribute, all cards must be either all same or all different
        for attr in ['color', 'shape', 'number', 'shading']:
            values = [getattr(card, attr) for card in cards]
            if len(set(values)) == 2:  # If 2 same and 1 different
                return False
        return True
    
    @classmethod
    def find_all_sets(cls, board: List[Card]) -> List[List[Card]]:
        """Find all valid sets on the board"""
        valid_sets = []
        for combo in itertools.combinations(board, 3):
            if cls.is_valid_set(list(combo)):
                valid_sets.append(list(combo))
        return valid_sets

    def to_prompt(self) -> str:
        """Convert the game board to a prompt string"""
        card_strs = [card.to_code() for card in self.board]
        cards_formatted = '\n'.join(card_strs)
        
        prompt = (
            f"Here is a game board with {len(self.board)} cards for the game of Set:\n\n"
            f"{cards_formatted}\n\n"
            "Find a valid set of three cards. Remember, in a valid set, for each attribute "
            "(color, shape, number, shading), the cards must either all match or all differ.\n\n"
            "Express your answer as three card codes separated by commas."
        )

        if self.think_through:
            prompt += "\n\nThink through your answer by considering many different possible sets until you find the right one, then answer in this format: \n\nAnswer: R-O-1-S, G-S-2-H, P-D-3-O"
        else:
            prompt += "\n\nDo not think through your answer. Answer immediately in this format: \n\nAnswer: R-O-1-S, G-S-2-H, P-D-3-O"

        return prompt

if __name__ == "__main__":
    game = GameOfSet.random_game()
    print(game.to_prompt())

    print("Valid set:")
    card_strs = [card.to_code() for card in game.valid_set]
    cards_formatted = '\n'.join(card_strs)
    print(cards_formatted)
