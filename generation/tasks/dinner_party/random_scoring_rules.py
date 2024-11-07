"""
A utility for generating random scoring rules for a dinner party game.

In this game, the player must choose 5 dinner party guests from a list of 10. Each guest has some set of interests, like a level 4 interest in cooking, or a level 7 interest in gardening.

The scoring for this game can be randomized, and this file contains utilities for generating random scoring rules.

Typically, scoring rules are applied in multiple rounds of scoring. Different scoring rules can be more or less complex.

Each rule has some selection mechanism for choosing which interests are involved in the scoring. A simple rule might be to always choose sports and cooking, while a more complex rule might choose the top 3 interests of each guest.

Each rule has some scoring mechanism for determining how many points a guest gets. A simple rule might be to add up the interest values for the chosen interest, while a more complex rule might give 1 point for each interest, plus 1 point for each interest that is shared with the host.

Here are some examples of scoring rules:

- (CR1) Each guest gets their top interest value.
- (CR1) Each guest gets their value in cooking interest.
- (CR2) Each guest gets the sum of their top 3 interests.
- (CR2) Each guest gets their second-highest interest value.
- (CR3) The most common interest is chosen among all guests, and each guest gets their value in that interest.
- (CR3) The largest interest value is chosen among all guests, and each guest gets their value in that interest.
- (CR4) The host is chosen as the alphabetically lowest guest, and each guest gets 2 points for each interest they share with the host.
- (CR4) The most common interest is chosen among all guests, excluding interests which have been chosen in previous rounds, and each guest gets their value in that interest. (Round 2 and later only)
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from generation.tasks.dinner_party.dinner_party import Person, DinnerParty


class ScoringRule(ABC):
    def __init__(self, dinner_party: DinnerParty):
        pass
    
    @abstractmethod
    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        """Returns a tuple of (scores dict mapping person names to their scores, metadata dict with 'interest' and/or 'host')"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Returns a human-readable description of how the rule works"""
        pass

    @classmethod
    @abstractmethod
    def get_cr(cls) -> int:
        pass

    def __str__(self) -> str:
        return f"CR{self.get_cr()}: {self.get_description()}"

    def _select_host_from_available(self, people: List[Person], game_scoring: "GameScoring", key_func) -> Person:
        """
        Select a host from available people using the given key function for sorting.
        Handles host rotation tracking.
        
        Args:
            people: List of all people
            game_scoring: GameScoring object containing previous_hosts
            key_func: Function to use for selecting host (e.g., lambda x: (len(x.interests), x.name))
        
        Returns:
            Selected host Person object
        """
        # Initialize previous_hosts if needed
        if game_scoring.previous_hosts is None:
            game_scoring.previous_hosts = []
            
        # Filter to people who haven't been host yet
        available_hosts = [p for p in people if p.name not in game_scoring.previous_hosts]
        
        # If everyone has been host, reset the list
        if not available_hosts:
            game_scoring.previous_hosts = []
            available_hosts = people
            
        # Choose host using provided key function
        host = min(available_hosts, key=key_func)
        game_scoring.previous_hosts.append(host.name)
        
        return host

    def _find_largest_interest(self, interests: Dict[str, int]) -> Optional[tuple[str, int]]:
        """
        Find the interest with largest value, breaking ties alphabetically.
        
        Args:
            interests: Dictionary mapping interest names to values
        
        Returns:
            Tuple of (interest_name, value) or None if no interests
        """
        if not interests:
            return None
            
        return max(interests.items(), key=lambda x: (x[1], -ord(x[0][0])))

    def _calculate_scores_for_interest(self, people: List[Person], interest: str) -> Dict[str, float]:
        """
        Calculate scores for all people based on a single interest.
        
        Args:
            people: List of all people
            interest: Interest to score
        
        Returns:
            Dictionary mapping person names to their scores
        """
        return {person.name: person.interests.get(interest, 0) for person in people}

    def _count_interests_per_person(self, people: List[Person]) -> Dict[str, int]:
        """
        Count number of interests for each person.
        
        Args:
            people: List of people to count interests for
        
        Returns:
            Dictionary mapping person names to their interest counts
        """
        return {person.name: len(person.interests) for person in people}

class FewestInterestsLargestValueRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
    
    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Select host with fewest interests
        host = self._select_host_from_available(
            people, 
            game_scoring,
            key_func=lambda x: (len(x.interests), x.name)
        )
        
        # Find host's largest interest
        max_interest = self._find_largest_interest(host.interests)
        if not max_interest:
            return {person.name: 0 for person in people}, {}
        
        chosen_interest = max_interest[0]
        scores = self._calculate_scores_for_interest(people, chosen_interest)
        
        return scores, {"interest": chosen_interest, "host": host.name}

    @classmethod
    def get_cr(cls) -> int:
        return 4
    
    def get_description(self) -> str:
        return "[Focused Host Interest] The host is chosen as the guest with the fewest number of interests (breaking ties alphabetically), and each guest gets points equal to their value in the host's largest interest."

class FewestInterestsHostRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
        self.points_per_interest = random.randint(2, 5)  # Both inclusive
    
    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Initialize previous_hosts if needed
        if game_scoring.previous_hosts is None:
            game_scoring.previous_hosts = []
            
        # Filter to people who haven't been host yet
        available_hosts = [p for p in people if p.name not in game_scoring.previous_hosts]
        
        # If everyone has been host, reset the list
        if not available_hosts:
            game_scoring.previous_hosts = []
            available_hosts = people
            
        # Calculate number of interests for available hosts
        person_interests = {
            person.name: len(person.interests)
            for person in available_hosts
        }
        
        # Choose host as person with fewest interests among available hosts (breaking ties alphabetically)
        host = min(available_hosts, key=lambda x: (person_interests[x.name], x.name))
        game_scoring.previous_hosts.append(host.name)
        
        host_interests = set(host.interests.keys())
        
        # Score each guest based on shared interests with host
        scores = {}
        for person in people:
            shared_interests = set(person.interests.keys()) & host_interests
            scores[person.name] = self.points_per_interest * len(shared_interests)
        
        return scores, {"host": host.name}

    @classmethod
    def get_cr(cls) -> int:
        return 4
    
    def get_description(self) -> str:
        return f"[Focused Host] The host is chosen as the guest with the fewest number of interests (breaking ties alphabetically), and each guest gets {self.points_per_interest} points for each interest they share with the host."

class AlphabeticHostInterestRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
    
    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Initialize previous_hosts if needed
        if game_scoring.previous_hosts is None:
            game_scoring.previous_hosts = []
            
        # Filter to people who haven't been host yet
        available_hosts = [p for p in people if p.name not in game_scoring.previous_hosts]
        
        # If everyone has been host, reset the list
        if not available_hosts:
            game_scoring.previous_hosts = []
            available_hosts = people
            
        # Choose host as alphabetically lowest guest among available hosts
        host = min(available_hosts, key=lambda x: x.name)
        game_scoring.previous_hosts.append(host.name)
        
        host_interests = set(host.interests.keys())
        
        # Score each guest based on shared interests with host
        scores = {}
        for person in people:
            shared_interests = set(person.interests.keys()) & host_interests
            scores[person.name] = 2 * len(shared_interests)
        
        return scores, {"host": host.name}

    @classmethod
    def get_cr(cls) -> int:
        return 3
    
    def get_description(self) -> str:
        return "[First Host] The host is chosen as the alphabetically lowest guest, and each guest gets 2 points for each interest they share with the host."


class LargestInterestValueRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
    
    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Get all undiscussed interests
        discussed = set(game_scoring.discussed_interests if game_scoring.discussed_interests else [])
        
        # Collect all interests and their values
        interest_values = {}
        for person in people:
            for interest, value in person.interests.items():
                if interest not in discussed:
                    if value > interest_values.get(interest, 0):
                        interest_values[interest] = value
        
        # Find highest value interest, breaking ties alphabetically
        if not interest_values:
            return {person.name: 0 for person in people}, {}
            
        max_interest = max(interest_values.items(), key=lambda x: (x[1], -ord(x[0][0])))
        chosen_interest = max_interest[0]
        
        # Score each person based on their value in that interest
        scores = {}
        for person in people:
            scores[person.name] = person.interests.get(chosen_interest, 0)
        
        return scores, {"interest": chosen_interest}

    @classmethod
    def get_cr(cls) -> int:
        return 3
    
    def get_description(self) -> str:
        return "[Loudest Interest] First, find the interest with the highest value among all guests. Then, award each person their value in that interest in points."


class EachPersonSpeaksRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
    
    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        scores = {}
        interests_used = []
        
        # Get all undiscussed interests
        discussed = set(game_scoring.discussed_interests if game_scoring.discussed_interests else [])
        
        for person in people:
            # Filter to only undiscussed interests
            available_interests = {k: v for k, v in person.interests.items() if k not in discussed}
            
            if available_interests:
                # Get the highest value undiscussed interest, breaking ties alphabetically
                top_interest = max(available_interests.items(), key=lambda x: (x[1], -ord(x[0][0])))
                scores[person.name] = top_interest[1]
                interests_used.append(top_interest[0])
            else:
                # No undiscussed interests available
                scores[person.name] = 0
                
        if interests_used:
            return scores, {}
        return scores, {}

    @classmethod
    def get_cr(cls) -> int:
        return 1
    
    def get_description(self) -> str:
        return "[Each Person Speaks] Each person is awarded points equal to their highest interest in any topic which has not yet been discussed by the full group. If a person has no undiscussed interests, they get 0 points."


class SingleInterestRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
        self.interest = random.choice(dinner_party.all_interests)

    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        scores = {}
        for person in people:
            # Award points for the specific interest if they have it
            scores[person.name] = person.interests.get(self.interest, 0)
        return scores, {"interest": self.interest}

    @classmethod
    def get_cr(cls) -> int:
        return 1

    def get_description(self) -> str:
        return f"[Talk about {self.interest.title()}] Award each person their value in {self.interest} in points."


class MostCommonInterestRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
        self.ignore_previous_interests = False

    def score_round(self, people: List[Person], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Count how many people have each interest, excluding previously discussed interests if needed
        interest_counts = {}
        for person in people:
            for interest in person.interests:
                if person.interests[interest] is not None and person.interests[interest] > 0:
                    if not self.ignore_previous_interests or interest not in game_scoring.discussed_interests:
                        interest_counts[interest] = interest_counts.get(interest, 0) + 1

        print("Interest counts:", interest_counts)
        
        if not interest_counts:
            # If no valid interests found (all were previously discussed), return 0 scores
            return {person.name: 0 for person in people}, {}
            
        # Find the most common interest (breaking ties alphabetically)
        most_common = max(interest_counts.items(), key=lambda x: (x[1], -ord(x[0][0])))
        most_common_interest = most_common[0]
        
        # Award points for the most common interest
        scores = {}
        for person in people:
            scores[person.name] = person.interests.get(most_common_interest, 0)
        return scores, {"interest": most_common_interest}

    @classmethod
    def get_cr(cls) -> int:
        return 3

    def get_description(self) -> str:
        ignore_previous = ", excluding interests which have been chosen in previous rounds" if self.ignore_previous_interests else ""
        return f"[Most Common Interest] First, find the most commonly shared interest by number of people with the interest{ignore_previous} (breaking ties alphabetically). Then, award each person their value in that interest in points."

class MostCommonInterestExceptPrevious(MostCommonInterestRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
        self.ignore_previous_interests = True

    @classmethod
    def get_cr(self) -> int:
        return MostCommonInterestRule.get_cr()  # + 1


@dataclass
class GameScoring:
    target_complexity: int
    rules: List[ScoringRule]
    discussed_interests: List[str] = None
    previous_hosts: List[str] = None

    def __str__(self) -> str:
        header = f"GameScoring (Total Complexity: CR{sum(rule.get_cr() for rule in self.rules)})"
        rounds = []
        for i, rule in enumerate(self.rules, 1):
            assert isinstance(rule, ScoringRule), f"Got {rule}, a {rule.__class__.__name__}"  # For IDE type hinting
            round_desc = f"Round {i}: CR{rule.get_cr()}-{rule.__class__.__name__}: {rule.get_description()}"
            rounds.append(round_desc)
        return f"{header}\n" + "\n".join(rounds)
    
    def __post_init__(self):
        # Validate that rules sum to target complexity
        total_complexity = sum(rule.get_cr() for rule in self.rules)
        if total_complexity != self.target_complexity:
            # TODO This is an error
            print(
                f"Rules complexity ({total_complexity}) "
                f"doesn't match target ({self.target_complexity})"
            )
        self.current_round = 0
        self.scores: Dict[str, float] = {}
    
    def score_all_rounds(self, people: List[Person], verbose: bool = True) -> Dict[str, float]:
        """Score all rounds and return final scores"""
        self.discussed_interests = []
        self.previous_hosts = []
        
        if verbose:
            print("\nScoring all rounds:")
        for round_num, rule in enumerate(self.rules, 1):
            if verbose:
                print(f"\nRound {round_num}:")
                print(rule)
            # Get scores and interests for this round
            round_scores, notes = rule.score_round(people, self)
            if verbose:
                print(notes)
            
            # Process what happened this round
            assert isinstance(notes, dict)
            if notes:
                if "interest" in notes:
                    if verbose:
                        print(f"Discussed Interest: {notes['interest']}")
                    self.discussed_interests.append(notes["interest"])
                if "host" in notes:
                    if verbose:
                        print(f"Host: {notes['host']}")
                    self.previous_hosts.append(notes["host"])
            if verbose:
                print("Scores this round:")
                for name, score in round_scores.items():
                    print(f"  {name}: {score}")
            
            # Update cumulative scores
            for name, score in round_scores.items():
                if name not in self.scores:
                    self.scores[name] = 0
                self.scores[name] += score

        if verbose:
            print("\nFinal cumulative scores:")
            for name, score in sorted(self.scores.items(), key=lambda x: (-x[1], x[0])):
                print(f"  {name}: {score}")
            print(f"\nAll interests discussed: {', '.join(sorted(set(self.discussed_interests)))}")
        
        return self.scores.copy()
    
    def get_final_scores(self) -> Dict[str, float]:
        return self.scores.copy()

def random_scoring_rules(points: int, dinner_party: DinnerParty, target_number_rules: int = 3, weighting_exponent: Optional[float] = 1.0, verbose: bool = True) -> GameScoring:
    """Generate random scoring rules totaling the given complexity points"""
    available_rules = [
        EachPersonSpeaksRule,
        MostCommonInterestRule,
        SingleInterestRule,
        MostCommonInterestExceptPrevious,
        LargestInterestValueRule,
        AlphabeticHostInterestRule,
        FewestInterestsHostRule,
        FewestInterestsLargestValueRule,
    ]

    if verbose:
        print("Possible Rules:")
        for rule in available_rules:
            print(f" * {rule.__name__} (CR {rule.get_cr()}): {rule(dinner_party).get_description()}")
    
    rules = []
    remaining_points = points
    
    while remaining_points > 0:
        # Calculate ideal points per remaining rule
        remaining_rules = target_number_rules - len(rules)

        # Get possible rules we could add
        possible_rules = [rule for rule in available_rules if rule.get_cr() <= remaining_points]
        if len(rules) == 0:
            possible_rules = [rule for rule in possible_rules if rule not in [MostCommonInterestExceptPrevious]]
        
        if not possible_rules:
            break
            
        # Weight rules by how close their CR is to the ideal points per rule
        if remaining_rules > 0:
            ideal_points_per_rule = remaining_points / remaining_rules
        else:
            ideal_points_per_rule = max(rule.get_cr() for rule in possible_rules)  # Prefer largest rules once we hit our target
        weights = [1 / (abs(rule.get_cr() - ideal_points_per_rule) + 1) for rule in possible_rules]
        if weighting_exponent is not None:
            weights = [weight ** weighting_exponent for weight in weights]
        else:
            # If none, no weighting
            weights = [1 for _ in weights]

        if verbose:
            print("Weights")
            print(f"Ideal points per rule: {ideal_points_per_rule}")
            print([rule.get_cr() for rule in possible_rules])
            print(weights)
            print()
        
        # Choose a rule using the weights
        chosen_rule = random.choices(possible_rules, weights=weights, k=1)[0](dinner_party)
        rules.append(chosen_rule)
        remaining_points -= chosen_rule.get_cr()
    
    return GameScoring(target_complexity=points, rules=rules)

def main(verbose: bool = True):
    dinner_party = DinnerParty.random_dinner_party(num_people=10, num_interests=6, set_size=5, points_spread=0, min_interests=2, max_interests=4, avg_points=15)

    points = random.randint(3, 15)
    if verbose:
        print(f"Generating rules with Points: {points}")

    random_rules = random_scoring_rules(points, dinner_party, target_number_rules=3, weighting_exponent=2.0, verbose=verbose)

    if verbose:
        print("Rules:")
        print(random_rules)

    # Create a random set of people to score
    people = random.sample(dinner_party.people, dinner_party.set_size)
    if verbose:
        print("\nPeople:")
        print(", ".join(str(person) for person in people))

    # Score all rounds
    random_rules.score_all_rounds(people, verbose=verbose)


if __name__ == "__main__":
    main()
