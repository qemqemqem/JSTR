import json
import argparse
import inspect
from pathlib import Path
import itertools
import random
from typing import List
from datetime import datetime
import shutil

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

    # Get the first values for parameters we want to duplicate
    first_think_through = next(dict(zip(param_names, combo))["think_through"] for combo in combinations)
    first_percent_chain_of_thought = next(dict(zip(param_names, combo))["percent_chain_of_thought"] for combo in combinations)

    # Open the file in write mode to start with an empty file
    with open(full_output_path, 'w') as f:
        for combo in combinations:
            params = dict(zip(param_names, combo))
            for i in range(n):
                # Check if there's a similar dinner party already in there
                params_dup = params.copy()  # Create a copy of the parameters
                params_dup["index"] = i
                params_dup["think_through"] = first_think_through
                params_dup["percent_chain_of_thought"] = first_percent_chain_of_thought
                params_key: str = json.dumps(params_dup)
                if params_key in dinner_parties_by_param:
                    # Deep copy the existing dinner party and update think_through
                    base_party = dinner_parties_by_param[params_key]
                    party = DinnerParty(
                        task_description=base_party.task_description,
                        people=base_party.people.copy(),
                        set_size=base_party.set_size,
                        stored_scores=base_party.stored_scores,
                        target_score=base_party.target_score,
                        think_through=params["think_through"],
                        full_chain_of_thought=base_party.full_chain_of_thought,
                        percent_chain_of_thought=params["percent_chain_of_thought"],
                    )
                    party.options = base_party.options.copy()
                else:
                    # Create a new random dinner party
                    valid_params = inspect.signature(DinnerParty.random_dinner_party).parameters.keys()
                    filtered_params = {k: v for k, v in params.items() if k in valid_params}
                    party = DinnerParty.random_dinner_party(**filtered_params)

                    # Annotate with the full chain of thought if requested
                    if "llm_for_chain_of_thought" in kwargs:
                        print(f"Getting full chain of thought {i+1}/{n} from {kwargs['llm_for_chain_of_thought']} (this takes 5-20s) ...")
                        party.get_full_chain_of_thought_from_llm(kwargs["llm_for_chain_of_thought"])

                # I know it seems like this could be cleaned up, but it's actually a bit tricky to do so
                params_dup = params.copy()  # Copy again to avoid using the modified "think_through" value
                params_dup["index"] = i  # Edit this here because if it's put into params it will annoy DinnerParty
                dinner_parties_by_param[json.dumps(params_dup)] = party

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

    # Create backup directory
    backup_dir = Path("lm_eval/tasks/dinner_party/old_dinner_parties")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Get parameters with multiple values for filename
    multi_params = [name for name, values in kwargs.items() if isinstance(values, list) and len(values) > 1]
    param_str = '_'.join(f"{p}" for p in multi_params) if multi_params else 'single'
    
    # Create backup filename with timestamp and parameters
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"dinner_party_{timestamp}_{param_str}.jsonl"
    backup_path = backup_dir / backup_filename
    
    # Copy the file
    shutil.copy2(full_output_path, backup_path)

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

    parser.add_argument_group("Pre-generate chain of thought. The purpose of this is to generate chain of thought that can be used to get the answer. We pre-generate it rather than allowing the LLM to do so because we want to see if it makes a difference to use more or less of the same chain of thought trace.")
    parser.add_argument("--pregenerate_chain_of_thought", type=bool, default=False, help="Whether to pre-generate chain of thought")
    parser.add_argument("--llm_for_chain_of_thought", type=str, default="", help="Which LLM to use to generate chain of thought, such as gpt-4-turbo.")
    parser.add_argument("--percent_chain_of_thought", type=parse_range, default="100",
                        help="Percent of pregenerated chain of thought to use (can be a range, e.g., '25,50,75,100')")

    args = parser.parse_args()

    # Convert args to a dictionary, removing 'num_parties' and 'output'. This is necessary, because the rest of the arguments are passed to random_dinner_party as kwargs.
    params = {k: v for k, v in vars(args).items() if k not in ['num_parties', 'output']}

    produce_and_save_dinner_parties(args.num_parties, args.output, **params)

    print(f"\nDinner parties saved to `{args.output}`")

    # Print the number of dinner parties saved
    with open(args.output, 'r') as f:
        num_lines = sum(1 for line in f)
    print(f"Number of dinner parties saved: {num_lines}")

if __name__ == "__main__":
    main()
