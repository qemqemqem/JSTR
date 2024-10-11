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

    def to_prompt(self) -> str:
        """
        Generate a prompt string for the task.

        Returns:
        str: A string containing the task description, options, and question.
        """
        prompt = f"{self.task_description}\n\nOptions:\n"
        for i, option in enumerate(self.options, 1):
            prompt += f"{i}. {option}\n"
        prompt += f"\nPlease choose {self.set_size} options that best fulfill the task."
        return prompt
