import random


def random_scoring_rules(points: int):
    ...

def main():
    points = random.randint(0, 10)
    print(f"Generating rules with Points: {points}")

    random_rules = random_scoring_rules(points)


if __name__ == "__main__":
    main()