import json
import argparse
from pathlib import Path
from datetime import datetime
import shutil
from typing import List, Dict

from generation.tasks.game_of_set.game_of_set import GameOfSet


def parse_range(arg: str) -> List[int]:
    """Parse a comma-separated string into a list of integers."""
    return [int(x) for x in arg.split(',')]


def produce_and_save_games(n: int, output_file: str, **kwargs):
    """
    Produce N Set game boards with exactly one valid set and save them to a .jsonl file.

    Args:
    n (int): The number of game boards to produce for each combination of parameters.
    output_file (str): The path to the output .jsonl file, relative to the project root.
    **kwargs: Keyword arguments for game parameters
    """
    full_output_path = Path(output_file)

    # Ensure the directory exists
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open the file in write mode to start with an empty file
    with open(full_output_path, 'w') as f:
        for i in range(n):
            # TODO: Implement the actual game board generation algorithm
            game = GameOfSet.random_game(**kwargs)

            json_obj = {
                "question": game.to_prompt(),
                "scoring_guide": {
                    "board": [card.to_dict() for card in game.board],
                    "valid_set": [card.to_dict() for card in game.valid_set],
                    "parameters": kwargs
                }
            }
            f.write(json.dumps(json_obj) + '\n')

    # Create backup directory
    backup_dir = Path("lm_eval/tasks/game_of_set/old_games")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"game_of_set_{timestamp}.jsonl"
    backup_path = backup_dir / backup_filename
    
    # Copy the file
    shutil.copy2(full_output_path, backup_path)


def main():
    parser = argparse.ArgumentParser(description="Generate Set game scenarios")
    parser.add_argument("-n", "--num_games", type=int, default=5, 
                       help="Number of game boards to generate")
    parser.add_argument("-o", "--output", type=str, 
                       default="lm_eval/tasks/game_of_set/game_of_set.jsonl",
                       help="Output file path")
    parser.add_argument("--board_size", type=int, default=12,
                       help="Number of cards to display on the board")
    parser.add_argument("--think_through", type=parse_range, default="0",
                       help="Optional thinking prompt to add before the answer")

    args = parser.parse_args()

    # Convert args to a dictionary, removing 'num_games' and 'output'
    params = {k: v for k, v in vars(args).items() 
             if k not in ['num_games', 'output']}

    produce_and_save_games(args.num_games, args.output, **params)

    print(f"\nSet games saved to `{args.output}`")

    # Print the number of games saved
    with open(args.output, 'r') as f:
        num_lines = sum(1 for line in f)
    print(f"Number of games saved: {num_lines}")


if __name__ == "__main__":
    main()
