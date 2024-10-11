import json

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

from pathlib import Path

def produce_and_save_dinner_parties(n: int, output_file: str):
    """
    Produce N dinner parties and append them to a .jsonl file.

    Args:
    n (int): The number of dinner parties to produce.
    output_file (str): The path to the output .jsonl file, relative to the project root.
    """
    # project_root = Path(__file__).parent.parent.parent.absolute()
    # full_output_path = project_root / output_file
    full_output_path = Path(output_file)

    # Ensure the directory exists
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_output_path, 'w') as f:
        for _ in range(n):
            party = produce_random_dinner_party()
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

if __name__ == "__main__":
    # Example usage
    random_party = produce_random_dinner_party()
    print(random_party.to_prompt())
    
    print("\nRandom set samples:")
    for i in range(2):
        random_set = random_party.get_random_set()
        print(f"\nSample {i+1}: {random_set}")
        score = random_party.score_set(random_set, debug=True)
        print(f"Final Score: {score}\n")
    
    # Produce and save 5 dinner parties to a file
    produce_and_save_dinner_parties(20, "lm_eval/tasks/dinner_party/dinner_party.jsonl")
    print("Dinner parties saved to dinner_parties.jsonl")
