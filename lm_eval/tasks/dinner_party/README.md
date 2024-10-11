# Dinner Party Task

This task evaluates a language model's ability to generate appropriate and creative responses to dinner party scenarios.

## Task Description

Given a dinner party scenario or question, the model should generate a response that is evaluated based on its quality, creativity, and appropriateness.

## Dataset

The dataset is a local JSONL file (`dinner_party.jsonl`) where each line contains a JSON object with two fields:
- `question`: A string describing a dinner party scenario or asking a related question.
- `scoring_guide`: An object containing guidelines for scoring the response.

## Metrics

The task uses three main metrics:
1. `answer_quality`: Measures the overall quality of the response.
2. `creativity`: Assesses the creativity and originality of the response.
3. `appropriateness`: Evaluates how well the response fits the given scenario.

All metrics are aggregated using the mean and higher scores are better.

## Usage

To run this task, ensure that the `dinner_party.jsonl` file is in the correct location and that the `scoring.py` file is properly implemented.

## Version History

- v1.0: Initial release
