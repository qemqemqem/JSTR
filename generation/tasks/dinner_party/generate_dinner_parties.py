import json
import argparse
from pathlib import Path
import itertools
import random
from typing import List

from generation.tasks.dinner_party.dinner_party import DinnerParty


def parse_range(arg: str) -> List[int]:
    """Parse a comma-separated string into a list of integers."""
    return [int(x) for x in arg.split(',')]


def produce_and_save_dinner_parties(n: int, output_file: str, **kwargs):
    """
    Produce N dinner parties for each combination of parameters and save them to a .jsonl file.

    Args:
    n (int): The number of dinner parties to produce for each combination of parameters.
    output_file (str): The path to the output .jsonl file, relative to the project root.
    **kwargs: Keyword arguments for dinner party parameters, which can be integers or lists of integers.
    """
    full_output_path = Path(output_file)

    # Ensure the directory exists
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate all combinations of parameters
    param_names = list(kwargs.keys())
    param_values = [kwargs[name] if isinstance(kwargs[name], list) else [kwargs[name]] for name in param_names]
    combinations = list(itertools.product(*param_values))

    dinner_parties_by_param: dict[str, DinnerParty] = {}

    # Open the file in write mode to start with an empty file
    with open(full_output_path, 'w') as f:
        for combo in combinations:
            params = dict(zip(param_names, combo))
            for _ in range(n):
                # Check if there's a similar dinner party already in there
                params_dup = params.copy()  # Create a copy of the parameters
                params_dup["think_through"] = 0
                params_key = json.dumps(params_dup)
                if params_key in dinner_parties_by_param:
                    # Deep copy the existing dinner party and update think_through
                    party = DinnerParty(
                        task_description=dinner_parties_by_param[params_key].task_description,
                        people=dinner_parties_by_param[params_key].people.copy(),
                        set_size=dinner_parties_by_param[params_key].set_size,
                        think_through=params["think_through"]
                    )
                else:
                    party = DinnerParty.random_dinner_party(**params)

                party = DinnerParty.random_dinner_party(**params)
                dinner_parties_by_param[json.dumps(params)] = party
                json_obj = {
                    "question": party.to_prompt(),
                    "scoring_guide": {
                        "task_description": party.task_description,
                        "people": [
                            {
                                "name": person.name,
                                "interests": {k: v for k, v in person.interests.items() if v is not None}
                            } for person in party.people
                        ],
                        "set_size": party.set_size,
                        "parameters": params,
                        "stored_scores": party.stored_scores,
                        "target_score": party.target_score,
                    }
                }
                f.write(json.dumps(json_obj) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Generate dinner party scenarios")
    parser.add_argument("-n", "--num_parties", type=int, default=5, help="Number of dinner parties to generate for each combination of parameters")
    parser.add_argument("-o", "--output", type=str, default="lm_eval/tasks/dinner_party/dinner_party.jsonl", help="Output file path")
    parser.add_argument("--num_people", type=parse_range, default="20", help="Number of people per dinner party (can be a range, e.g., '18,20,22')")
    parser.add_argument("--num_interests", type=parse_range, default="12", help="Number of interests to choose from (can be a range)")
    parser.add_argument("--set_size", type=parse_range, default="5", help="Number of people to select for each dinner party (can be a range, e.g., '3,4,5,7')")
    parser.add_argument("--avg_points", type=parse_range, default="25", help="Average interest points for a person (can be a range)")
    parser.add_argument("--points_spread", type=int, default=5, help="Plus or minus on a person's total point value")
    parser.add_argument("--min_interests", type=int, default=2, help="Minimum number of interests a person can have")
    parser.add_argument("--max_interests", type=int, default=5, help="Maximum number of interests a person can have")
    parser.add_argument("--bimodal_discount", type=parse_range, default="0", help="Discount to apply to 50% of people's points total (can be a range)")
    parser.add_argument("--think_through", type=parse_range, default="0", help="Optional thinking prompt to add before the answer")
    args = parser.parse_args()

    # Convert args to a dictionary, removing 'num_parties' and 'output'
    params = {k: v for k, v in vars(args).items() if k not in ['num_parties', 'output']}

    produce_and_save_dinner_parties(args.num_parties, args.output, **params)
    print(f"\nDinner parties saved to `{args.output}`")

    # Print the number of dinner parties saved
    with open(args.output, 'r') as f:
        num_lines = sum(1 for line in f)
    print(f"Number of dinner parties saved: {num_lines}")

if __name__ == "__main__":
    main()
