from abc import ABC, abstractmethod
from typing import List

class TaskSpecification(ABC):
    def __init__(self, task_description: str, options: List[str], set_size: int):
        self.task_description = task_description
        self.options = options
        self.set_size = set_size

    @abstractmethod
    def score_set(self, selected_set: List[str]) -> float:
        """
        Score the selected set of options.

        Args:
        selected_set (List[str]): The set of options selected by the model.

        Returns:
        float: The score for the selected set.
        """
        pass
