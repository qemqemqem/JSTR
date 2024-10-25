import json
import argparse
from pathlib import Path
import itertools
import random
from typing import List, Union

from generation.tasks.dinner_party.dinner_party import DinnerParty


def parse_range(arg: str) -> List[int]:
    """Parse a comma-separated string into a list of integers."""
    return [int(x) for x in arg.split(',')]

def produce_random_dinner_party(num_people: Union[int, List[int]] = 20, num_interests: Union[int, List[int]] = 8, set_size: Union[int, List[int]] = 5, avg_points: Union[int, List[int]] = 20, points_spread: int = 10, min_interests: int = 1, max_interests: int = 5, bimodal_discount: Union[int, List[int]] = 0) -> DinnerParty:
    """
    Produce a random DinnerParty instance.

    Args:
    num_people (int or List[int]): The number of people to generate for the dinner party.
    num_interests (int or List[int]): The number of possible interests to choose from.
    set_size (int or List[int]): The number of people to be selected for the dinner party.
    avg_points (int or List[int]): The average interest points for a person.
    points_spread (int): The plus or minus on a person's total point value.
    min_interests (int): The minimum number of interests a person can have.
    max_interests (int): The maximum number of interests a person can have.
    bimodal_discount (int or List[int]): The discount to apply to 50% of people's points total.

    Returns:
    DinnerParty: A randomly generated DinnerParty instance.
    """
    num_people = random.choice(num_people) if isinstance(num_people, list) else num_people
    num_interests = random.choice(num_interests) if isinstance(num_interests, list) else num_interests
    set_size = random.choice(set_size) if isinstance(set_size, list) else set_size
    avg_points = random.choice(avg_points) if isinstance(avg_points, list) else avg_points
    bimodal_discount = random.choice(bimodal_discount) if isinstance(bimodal_discount, list) else bimodal_discount

    total_points = num_people * avg_points
    return DinnerParty.random_dinner_party(num_people=num_people, num_interests=num_interests, set_size=set_size, total_points=total_points, points_spread=points_spread, min_interests=min_interests, max_interests=max_interests, bimodal_discount=bimodal_discount)

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

    # Open the file in write mode to start with an empty file
    with open(full_output_path, 'w') as f:
        for combo in combinations:
            params = dict(zip(param_names, combo))
            for _ in range(n):
                party = produce_random_dinner_party(**params)
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
    parser.add_argument("--think-through", type=str, default="", help="Optional thinking prompt to add before the answer")
    args = parser.parse_args()

    # Convert args to a dictionary, removing 'num_parties' and 'output'
    params = {k: v for k, v in vars(args).items() if k not in ['num_parties', 'output']}

    # Generate and print one random dinner party
    # Remove think-through from params before passing to produce_random_dinner_party
    think_through = params.pop('think_through')
    random_party = produce_random_dinner_party(**params)
    # Add think-through back to params
    params['think_through'] = think_through
    print("Random Dinner Party:")
    print(random_party.to_prompt())
    print("\nTarget Score:", random_party.target_score)

    produce_and_save_dinner_parties(args.num_parties, args.output, **params)
    print(f"\nDinner parties saved to `{args.output}`")

    # Print the number of dinner parties saved
    with open(args.output, 'r') as f:
        num_lines = sum(1 for line in f)
    print(f"Number of dinner parties saved: {num_lines}")

if __name__ == "__main__":
    main()
