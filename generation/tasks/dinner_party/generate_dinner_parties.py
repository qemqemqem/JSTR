import json
import argparse
from pathlib import Path

from generation.tasks.dinner_party.dinner_party import DinnerParty


def produce_random_dinner_party(num_people: int = 20, num_interests: int = 8, set_size: int = 5, avg_points: int = 20, points_spread: int = 10, min_interests: int = 1, max_interests: int = 5, bimodal_discount: int = 0) -> DinnerParty:
    """
    Produce a random DinnerParty instance.

    Args:
    num_people (int): The number of people to generate for the dinner party.
    num_interests (int): The number of possible interests to choose from.
    set_size (int): The number of people to be selected for the dinner party.
    avg_points (int): The average interest points for a person.
    points_spread (int): The plus or minus on a person's total point value.
    min_interests (int): The minimum number of interests a person can have.
    max_interests (int): The maximum number of interests a person can have.
    bimodal_discount (int): The discount to apply to 50% of people's points total.

    Returns:
    DinnerParty: A randomly generated DinnerParty instance.
    """
    total_points = num_people * avg_points
    return DinnerParty.random_dinner_party(num_people=num_people, num_interests=num_interests, set_size=set_size, total_points=total_points, points_spread=points_spread, min_interests=min_interests, max_interests=max_interests, bimodal_discount=bimodal_discount)

def produce_and_save_dinner_parties(n: int, output_file: str, num_people: int = 20, num_interests: int = 8, set_size: int = 5, avg_points: int = 20, points_spread: int = 10, min_interests: int = 1, max_interests: int = 5, bimodal_discount: int = 0):
    """
    Produce N dinner parties and append them to a .jsonl file.

    Args:
    n (int): The number of dinner parties to produce.
    output_file (str): The path to the output .jsonl file, relative to the project root.
    num_people (int): The number of people to generate for each dinner party.
    num_interests (int): The number of possible interests to choose from for each dinner party.
    set_size (int): The number of people to be selected for each dinner party.
    avg_points (int): The average interest points for a person.
    points_spread (int): The plus or minus on a person's total point value.
    min_interests (int): The minimum number of interests a person can have.
    max_interests (int): The maximum number of interests a person can have.
    bimodal_discount (int): The discount to apply to 50% of people's points total.
    """
    full_output_path = Path(output_file)

    # Ensure the directory exists
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_output_path, 'w') as f:
        for _ in range(n):
            party = produce_random_dinner_party(num_people, num_interests, set_size, avg_points, points_spread, min_interests, max_interests, bimodal_discount)
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
                    "parameters": {
                        "num_people": num_people,
                        "num_interests": num_interests,
                        "set_size": set_size,
                        "avg_points": avg_points,
                        "points_spread": points_spread,
                        "min_interests": min_interests,
                        "max_interests": max_interests,
                        "bimodal_discount": bimodal_discount
                    },
                    "stored_scores": party.stored_scores,
                    "target_score": party.target_score,
                }
            }
            f.write(json.dumps(json_obj) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Generate dinner party scenarios")
    parser.add_argument("-n", "--num_parties", type=int, default=20, help="Number of dinner parties to generate")
    parser.add_argument("-o", "--output", type=str, default="generation/tasks/dinner_party/dinner_party.jsonl", help="Output file path")
    parser.add_argument("--num_people", type=int, default=20, help="Number of people per dinner party")
    parser.add_argument("--num_interests", type=int, default=12, help="Number of interests to choose from")
    parser.add_argument("--set_size", type=int, default=5, help="Number of people to select for each dinner party")
    parser.add_argument("--avg_points", type=int, default=25, help="Average interest points for a person")
    parser.add_argument("--points_spread", type=int, default=5, help="Plus or minus on a person's total point value")
    parser.add_argument("--min_interests", type=int, default=2, help="Minimum number of interests a person can have")
    parser.add_argument("--max_interests", type=int, default=6, help="Maximum number of interests a person can have")
    parser.add_argument("--bimodal_discount", type=int, default=15, help="Discount to apply to 50% of people's points total")
    args = parser.parse_args()

    # Generate and print one random dinner party
    random_party = produce_random_dinner_party(args.num_people, args.num_interests, args.set_size, args.avg_points, args.points_spread, args.min_interests, args.max_interests, args.bimodal_discount)
    print("Random Dinner Party:")
    print(random_party.to_prompt())
    print("\nTarget Score:", random_party.target_score)

    produce_and_save_dinner_parties(args.num_parties, args.output, args.num_people, args.num_interests, args.set_size, args.avg_points, args.points_spread, args.min_interests, args.max_interests, args.bimodal_discount)
    print(f"\nDinner parties saved to `{args.output}`")

if __name__ == "__main__":
    main()
