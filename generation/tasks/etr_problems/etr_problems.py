from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ETRProblem:
    """Represents an Easy-to-Read (ETR) math problem"""
    question: str
    answer: float
    explanation: str
    difficulty: int  # 1-5 scale
    topic: str      # e.g., "addition", "multiplication", etc.
