import json
import argparse
from pathlib import Path

from generation.tasks.dinner_party.dinner_party import DinnerParty


def produce_random_dinner_party(num_people: int = 20, num_interests: int = 8, set_size: int = 5) -> DinnerParty:
    """
    Produce a random DinnerParty instance.

    Args:
    num_people (int): The number of people to generate for the dinner party.
    num_interests (int): The number of possible interests to choose from.
    set_size (int): The number of people to be selected for the dinner party.

    Returns:
    DinnerParty: A randomly generated DinnerParty instance.
    """
    return DinnerParty.random_dinner_party(num_people=num_people, num_interests=num_interests, set_size=set_size)

def produce_and_save_dinner_parties(n: int, output_file: str, num_people: int = 20, num_interests: int = 8, set_size: int = 5):
    """
    Produce N dinner parties and append them to a .jsonl file.

    Args:
    n (int): The number of dinner parties to produce.
    output_file (str): The path to the output .jsonl file, relative to the project root.
    num_people (int): The number of people to generate for each dinner party.
    num_interests (int): The number of possible interests to choose from for each dinner party.
    set_size (int): The number of people to be selected for each dinner party.
    """
    full_output_path = Path(output_file)

    # Ensure the directory exists
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_output_path, 'w') as f:
        for _ in range(n):
            party = produce_random_dinner_party(num_people, num_interests, set_size)
            json_obj = {
                "question": party.to_prompt(),
                "target_score": party.target_score,
                "scoring_guide": {
                    "task_description": party.task_description,
                    "people": [
                        {
                            "name": person.name,
                            "interests": {k: v for k, v in person.interests.items() if v is not None}
                        } for person in party.people
                    ],
                    "set_size": party.set_size
                }
            }
            f.write(json.dumps(json_obj) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Generate dinner party scenarios")
    parser.add_argument("-n", "--num_parties", type=int, default=20, help="Number of dinner parties to generate")
    parser.add_argument("-o", "--output", type=str, default="generation/tasks/dinner_party/dinner_party.jsonl", help="Output file path")
    parser.add_argument("--num_people", type=int, default=20, help="Number of people per dinner party")
    parser.add_argument("--num_interests", type=int, default=8, help="Number of interests to choose from")
    parser.add_argument("--set_size", type=int, default=5, help="Number of people to select for each dinner party")
    args = parser.parse_args()

    # Generate and print one random dinner party
    random_party = produce_random_dinner_party(args.num_people, args.num_interests, args.set_size)
    print("Random Dinner Party:")
    print(random_party.to_prompt())
    print("\nTarget Score:", random_party.target_score)

    produce_and_save_dinner_parties(args.num_parties, args.output, args.num_people, args.num_interests, args.set_size)
    print(f"\nDinner parties saved to `{args.output}`")

if __name__ == "__main__":
    main()
