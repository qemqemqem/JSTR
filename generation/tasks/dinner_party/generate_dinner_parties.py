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
    When only think_through differs, reuse the same dinner party with a different prompt.

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

    # Function to create a deep copy of a dinner party's JSON representation
    def copy_party_json(json_obj, new_params):
        import copy
        new_obj = copy.deepcopy(json_obj)
        new_obj["scoring_guide"]["parameters"] = new_params
        # Create a new DinnerParty instance to get the updated prompt
        party = DinnerParty.from_dict(new_obj["scoring_guide"])
        new_obj["question"] = party.to_prompt()
        return new_obj

    # Find the position of think_through in parameters
    think_through_idx = param_names.index('think_through') if 'think_through' in param_names else -1
    
    # Track the base parties (ones with same params except think_through)
    base_parties = {}  # Key: tuple of non-think_through params, Value: list of json objects

    # Open the file in write mode to start with an empty file
    with open(full_output_path, 'w') as f:
        for combo_idx, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))
            
            # Create a key tuple excluding think_through
            if think_through_idx >= 0:
                base_key = tuple(v for i, v in enumerate(combo) if i != think_through_idx)
            else:
                base_key = combo

            for iteration in range(n):
                if think_through_idx >= 0 and combo[think_through_idx] > 0:
                    # This is a variation that only differs by think_through
                    # Find the corresponding base party (with think_through=0)
                    base_key_with_iteration = (base_key, iteration)
                    if base_key_with_iteration in base_parties:
                        # Duplicate the base party with new parameters
                        json_obj = copy_party_json(base_parties[base_key_with_iteration], params)
                    else:
                        # Fallback to creating a new party if base not found
                        party = DinnerParty.random_dinner_party(**params)
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
                else:
                    # Create a new base party
                    party = DinnerParty.random_dinner_party(**params)
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
                    if think_through_idx >= 0:
                        base_parties[(base_key, iteration)] = json_obj

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
