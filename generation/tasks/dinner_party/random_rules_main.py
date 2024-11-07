import random

from generation.tasks.dinner_party.dinner_party import DinnerParty
from generation.tasks.dinner_party.random_scoring_rules import *


def main(verbose: bool = True):
    dinner_party = DinnerParty.random_dinner_party(num_people=10, num_interests=6, set_size=5, points_spread=0, min_interests=2, max_interests=4, avg_points=15)

    points = random.randint(3, 15)
    if verbose:
        print(f"Generating rules with Points: {points}")

    # random_rules = random_scoring_rules(points, dinner_party, target_number_rules=3, weighting_exponent=2.0, verbose=verbose)
    random_rules = one_of_each_scoring_rule(dinner_party)

    if verbose:
        print("Rules:")
        print(random_rules)

    # Create a random set of people to score
    people = random.sample(dinner_party.people, dinner_party.set_size)
    if verbose:
        print("\nPeople:")
        print(", ".join(str(person) for person in people))

    # Score all rounds
    final_scores = random_rules.score_all_rounds(people, verbose=verbose)

    print("Final Scores:")
    print(final_scores)


if __name__ == "__main__":
    main(True)
