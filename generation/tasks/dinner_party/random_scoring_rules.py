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
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from generation.tasks.dinner_party.dinner_party import Person, DinnerParty  # DO NOT UNCOMMENT. This causes a circular import error


class ScoringRule(ABC):
    def __init__(self, dinner_party: "DinnerParty"):
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party: "DinnerParty") -> "ScoringRule":
        pass

    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
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

    def _select_host_from_available(self, people: List["Person"], game_scoring: "GameScoring", key_func) -> "Person":
        """
        Select a host from available people using the given key function for sorting.
        Handles host rotation tracking.
        
        Args:
            people: List of all people
            game_scoring: GameScoring object containing previous_hosts
            key_func: Function to use for selecting host (e.g., lambda x: (len(x.interests), x.name))
        
        Returns:
            Selected host "Person" object
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

    def _calculate_scores_for_interest(self, people: List["Person"], interest: str) -> Dict[str, float]:
        """
        Calculate scores for all people based on a single interest.
        
        Args:
            people: List of all people
            interest: Interest to score
        
        Returns:
            Dictionary mapping person names to their scores
        """
        return {person.name: person.interests.get(interest, 0) for person in people}

    def _count_interests_per_person(self, people: List["Person"]) -> Dict[str, int]:
        """
        Count number of interests for each person.
        
        Args:
            people: List of people to count interests for
        
        Returns:
            Dictionary mapping person names to their interest counts
        """
        return {person.name: len(person.interests) for person in people}

class FewestInterestsLargestValueRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "FewestInterestsLargestValueRule"
            # Add any specific attributes for this rule if needed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "FewestInterestsLargestValueRule":
        # Extract attributes from data and create an instance
        return cls(dinner_party=dinner_party)
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
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
        return "[Focused Host Interest] In this round, one guest is chosen as the host. The host is the guest with the fewest number of interests (breaking ties alphabetically, and skipping people who have previously hosted a round). That host's largest interest (again, breaking ties alphabetically) is chosen as the topic for the round. Then, each guest gets points equal to their value in that topic."

class FewestInterestsHostRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)
        self.points_per_interest = random.randint(2, 5)  # Both inclusive

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "FewestInterestsHostRule",
            "points_per_interest": self.points_per_interest
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "FewestInterestsHostRule":
        instance = cls(dinner_party=dinner_party)  # Replace with actual initialization logic
        instance.points_per_interest = data["points_per_interest"]
        return instance
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
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
        return f"[Focused Host] In this round, the host is chosen as the guest with the fewest number of interests (breaking ties alphabetically, and skipping guests who have previously hosted a round). Then, each guest gets {self.points_per_interest} points for each interest they share with the host."


class NicheInterestsRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)
        self.bonus_points = random.randint(3, 7)  # Random bonus points per niche interest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "NicheInterestsRule",
            "bonus_points": self.bonus_points
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "NicheInterestsRule":
        instance = cls(dinner_party=dinner_party)  # Replace with actual initialization logic
        instance.bonus_points = data["bonus_points"]
        return instance
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Get all interests and their total values across all guests
        interest_totals = {}
        for person in people:
            for interest, level in person.interests.items():
                if interest not in interest_totals:
                    interest_totals[interest] = 0
                interest_totals[interest] += level
        
        # Find the three lowest-valued interests
        niche_interests = sorted(interest_totals.items(), key=lambda x: (x[1], x[0]))[:3]
        niche_interest_names = [interest for interest, _ in niche_interests]
        
        # Award bonus points to guests who have these interests
        scores = {}
        for person in people:
            score = 0
            for interest in niche_interest_names:
                if interest in person.interests:
                    score += self.bonus_points
            scores[person.name] = score
            
        return scores, {"niche_interests": niche_interest_names}

    @classmethod
    def get_cr(cls) -> int:
        return 2
    
    def get_description(self) -> str:
        return f"[Niche Interests] In this round, we find the three interests with lowest total values across all guests, meaning the lowest sum of interest among all guests, breaking ties alphabetically. Then, we award {self.bonus_points} bonus points to each guest for each of these niche interests they have."

class WellRoundedInterestsRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WellRoundedInterestsRule"
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "WellRoundedInterestsRule":
        return cls(dinner_party=dinner_party)
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        scores = {}
        for person in people:
            if not person.interests:
                scores[person.name] = 0
                continue
                
            # Find highest and lowest interest levels
            highest = max(person.interests.values())
            lowest = min(person.interests.values())
            
            # Calculate gap - smaller gaps get more points
            gap = highest - lowest
            
            # Award points inversely proportional to the gap
            scores[person.name] = max(0, 10 - gap)
            
        return scores, {}

    @classmethod
    def get_cr(cls) -> int:
        return 1
    
    def get_description(self) -> str:
        return "[Well-Rounded Interests] In this round, each guest gets points based on how close their highest and lowest interest levels are. Each person gets points based on this formula: `max(0, 10 - (highest_score - lowest_score))`, ignoring 0s. A smaller gap means more points, encouraging well-rounded conversationalists."

class AlphabeticHostInterestRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "AlphabeticHostInterestRule"
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "AlphabeticHostInterestRule":
        return cls(dinner_party=dinner_party)
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
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
        return "[First Host] In this round, the alphabetically lowest guest is chosen as the host, excluding guests who have previously hosted a round. Then, each guest gets 2 points for each interest they share with the host."


class LargestInterestValueRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "LargestInterestValueRule"
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "LargestInterestValueRule":
        return cls(dinner_party=dinner_party)
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
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
        return "[Loudest Interest] In this round, we find the interest with the highest value among all guests which has not yet been discussed. This is the highest single value in a single interest that one person has. Break ties alphabetically by interest name. Then, each person is awarded their value in that interest in points."


class EachPersonSpeaksRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "EachPersonSpeaksRule"
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "EachPersonSpeaksRule":
        return cls(dinner_party=dinner_party)
    
    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
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
        return "[Each Person Speaks] In this round, each person is awarded points equal to their highest interest in any topic which has not yet been discussed by the full group. If a person has no undiscussed interests, they get 0 points."


class SingleInterestRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)
        self.interest = random.choice(dinner_party.all_interests)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "SingleInterestRule",
            "interest": self.interest
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "SingleInterestRule":
        instance = cls(dinner_party=dinner_party)  # Replace with actual initialization logic
        instance.interest = data["interest"]
        return instance

    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        scores = {}
        for person in people:
            # Award points for the specific interest if they have it
            scores[person.name] = person.interests.get(self.interest, 0)
        return scores, {"interest": self.interest}

    @classmethod
    def get_cr(cls) -> int:
        return 1

    def get_description(self) -> str:
        return f"[Talk about {self.interest.title()}] This round is simple. Award each person their value in {self.interest} in points. (Or 0 if they don't have it)"


class MostCommonInterestRule(ScoringRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)
        self.ignore_previous_interests = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "MostCommonInterestRule",
            "ignore_previous_interests": self.ignore_previous_interests
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "MostCommonInterestRule":
        instance = cls(dinner_party=dinner_party)  # Replace with actual initialization logic
        instance.ignore_previous_interests = data["ignore_previous_interests"]
        return instance

    def score_round(self, people: List["Person"], game_scoring: "GameScoring") -> tuple[Dict[str, float], Dict[str, Any]]:
        # Count how many people have each interest, excluding previously discussed interests if needed
        interest_counts = {}
        for person in people:
            for interest in person.interests:
                if person.interests[interest] is not None and person.interests[interest] > 0:
                    if not self.ignore_previous_interests or interest not in game_scoring.discussed_interests:
                        interest_counts[interest] = interest_counts.get(interest, 0) + 1

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
        return f"[Most Common Interest] First, find the most commonly shared interest by number of people with any value in the interest{ignore_previous} (breaking ties alphabetically), and make it the topic for the round. Then, award each person their value in that interest in points."

class MostCommonInterestExceptPrevious(MostCommonInterestRule):
    def __init__(self, dinner_party: "DinnerParty"):
        super().__init__(dinner_party)
        self.ignore_previous_interests = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "MostCommonInterestExceptPrevious",
            "ignore_previous_interests": self.ignore_previous_interests
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party) -> "MostCommonInterestExceptPrevious":
        instance = cls(dinner_party=dinner_party)  # Replace with actual initialization logic
        instance.ignore_previous_interests = data["ignore_previous_interests"]
        return instance

    @classmethod
    def get_cr(self) -> int:
        return MostCommonInterestRule.get_cr()  # + 1


@dataclass
class GameScoring:
    scoring_complexity: int
    rules: List[ScoringRule]
    discussed_interests: List[str] = None
    previous_hosts: List[str] = None
    current_round: int = 0
    scores: Dict[str, float] = field(default_factory=dict)

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
        if total_complexity != self.scoring_complexity:
            # TODO This is an error
            print(
                f"Rules complexity ({total_complexity}) "
                f"doesn't match target ({self.scoring_complexity})"
            )

    def reset(self):
        """Reset the scoring state to allow for a new round of scoring."""
        self.discussed_interests = []
        self.previous_hosts = []
        self.scores = {}
        self.current_round = 0

    def score_all_rounds(self, people: List["Person"], verbose: bool = False) -> float:
        """Score all rounds and return final scores"""
        self.reset()
        
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
            print(f"Total score: {sum(self.scores.values())}")

        total_score = sum(self.scores.values())
        self.reset()
        
        return total_score
    
    def get_final_scores(self) -> Dict[str, float]:
        return self.scores.copy()

    def to_prompt(self) -> str:
        prompt = f"The game is split into {len(self.rules)} rounds. Each round is different, and provides a way for each participant in the dinner party to score points.\n"
        prompt += f"At the end of the game, each participant's points are added together to score the dinner party as a whole.\n"
        prompt += f"\nHere are the rules for each round:\n\n"
        for i, rule in enumerate(self.rules, 1):
            prompt += f"Round {i}: {rule.get_description()}\n\n"
        prompt += f"\nThe final score is the sum of all interest levels for these top 3 interests.\n"
        prompt += f"In all cases, if there is a tie between valid options, it goes to the interest or person with the name closest to the beginning of the alphabet.\n"
        prompt += f"Your goal is to maximize the total score of the dinner party, by choosing just the right group of people.\n"
        return prompt

    def to_dict(self) -> Dict[str, Any]:
        """Convert the GameScoring object to a dictionary for JSON serialization."""
        return {
            "scoring_complexity": self.scoring_complexity,
            "rules": [rule.to_dict() for rule in self.rules],
            "discussed_interests": self.discussed_interests,
            "previous_hosts": self.previous_hosts,
            "current_round": self.current_round,
            "scores": self.scores,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], dinner_party: "DinnerParty") -> "GameScoring":
        """Create a GameScoring instance from a dictionary."""
        rules = [scoring_rule_from_dict(rule_data, dinner_party=dinner_party) for rule_data in data['rules']]
        return cls(
            scoring_complexity=data['scoring_complexity'],
            rules=rules,
            discussed_interests=data.get('discussed_interests', []),
            previous_hosts=data.get('previous_hosts', []),
            current_round=data.get('current_round', 0),
            scores=data.get('scores', {})
        )


ALL_RULES: List[type[ScoringRule]] = [
    EachPersonSpeaksRule,
    MostCommonInterestRule,
    SingleInterestRule,
    MostCommonInterestExceptPrevious,
    LargestInterestValueRule,
    AlphabeticHostInterestRule,
    FewestInterestsHostRule,
    FewestInterestsLargestValueRule,
    WellRoundedInterestsRule,
    NicheInterestsRule,
]

def scoring_rule_from_dict(data: Dict[str, Any], verbose: bool = False, dinner_party: "DinnerParty" = None, points: int = 0, target_number_rules: int = 0, weighting_exponent: Optional[float] = None) -> ScoringRule:
    rule_type = data.get("type")
    if rule_type == "FewestInterestsLargestValueRule":
        return FewestInterestsLargestValueRule.from_dict(data, dinner_party)
    elif rule_type == "FewestInterestsHostRule":
        return FewestInterestsHostRule.from_dict(data, dinner_party)
    elif rule_type == "NicheInterestsRule":
        return NicheInterestsRule.from_dict(data, dinner_party)
    elif rule_type == "WellRoundedInterestsRule":
        return WellRoundedInterestsRule.from_dict(data, dinner_party)
    elif rule_type == "AlphabeticHostInterestRule":
        return AlphabeticHostInterestRule.from_dict(data, dinner_party)
    elif rule_type == "LargestInterestValueRule":
        return LargestInterestValueRule.from_dict(data, dinner_party)
    elif rule_type == "EachPersonSpeaksRule":
        return EachPersonSpeaksRule.from_dict(data, dinner_party)
    elif rule_type == "SingleInterestRule":
        return SingleInterestRule.from_dict(data, dinner_party)
    elif rule_type == "MostCommonInterestRule":
        return MostCommonInterestRule.from_dict(data, dinner_party)
    elif rule_type == "MostCommonInterestExceptPrevious":
        return MostCommonInterestExceptPrevious.from_dict(data, dinner_party)
    else:
        raise ValueError(f"Unknown rule type: {rule_type}")


def random_scoring_rules(points: int, dinner_party: "DinnerParty", target_number_rules: int = 3,
                         weighting_exponent: Optional[float] = 2.0, verbose: bool = False) -> GameScoring:
    """Generate random scoring rules totaling the given complexity points"""

    if verbose:
        print("Possible Rules:")
        for rule in ALL_RULES:
            print(f" * {rule.__name__} (CR {rule.get_cr()}): {rule(dinner_party).get_description()}")

    rules = []
    remaining_points = points

    while remaining_points > 0:
        # Calculate ideal points per remaining rule
        remaining_rules = target_number_rules - len(rules)

        # Get possible rules we could add
        possible_rules = [rule for rule in ALL_RULES if rule.get_cr() <= remaining_points]
        if len(rules) == 0:
            possible_rules = [rule for rule in possible_rules if rule not in [MostCommonInterestExceptPrevious]]

        if not possible_rules:
            break

        # Weight rules by how close their CR is to the ideal points per rule
        if remaining_rules > 0:
            ideal_points_per_rule = remaining_points / remaining_rules
        else:
            ideal_points_per_rule = max(
                rule.get_cr() for rule in possible_rules)  # Prefer largest rules once we hit our target
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

    return GameScoring(scoring_complexity=points, rules=rules)

def default_scoring_rules(dinner_party: "DinnerParty") -> GameScoring:
    """Generate default scoring rules"""
    return GameScoring(scoring_complexity=25, rules=[
        MostCommonInterestExceptPrevious(dinner_party),
        MostCommonInterestExceptPrevious(dinner_party),
        MostCommonInterestExceptPrevious(dinner_party),
    ])


def one_of_each_scoring_rule(dinner_party: "DinnerParty") -> GameScoring:
    """Generate scoring rules that include one of each type"""
    return GameScoring(scoring_complexity=9, rules=[r(dinner_party) for r in ALL_RULES])
