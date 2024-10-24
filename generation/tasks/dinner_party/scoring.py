import re
import os
import sys

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())

from generation.tasks.dinner_party.dinner_party import DinnerParty

def score_answer(question, answer):
    """
    Score the given answer based on the scoring guide using the DinnerParty class.

    Args:
    scoring_guide (dict): A dictionary containing the scoring guide information.
    answer (str or dict): The model's response to the dinner party question.

    Returns:
    dict: A dictionary containing the score and other relevant information.
    """
    # Extract answer text
    if isinstance(answer, dict):
        answer_text = answer.get('text', '')
    elif isinstance(answer, list) and len(answer) > 0:
        answer_text = str(answer[0])
    else:
        answer_text = str(answer)

    # Remove "Answer:" from the beginning of the answer text
    answer_text = re.sub(r'^Answer:', '', answer_text).strip()

    scoring_guide = question['scoring_guide']

    # Create the DinnerParty object from the scoring guide
    print()
    # print(f"SCORING GUIDE: {scoring_guide}")
    print(f"ANSWER: {answer_text}")
    dinner_party = DinnerParty.from_dict(scoring_guide)

    # Extract names from the answer
    names = re.findall(r'\b[A-Z][a-z]*\b', answer_text)
    selected_set = names[:dinner_party.set_size]  # Take only the required number of names

    # Score the selected set
    score = dinner_party.score_set(selected_set, debug=True)

    # Get the score statistics
    score_stats = dinner_party.get_score_statistics(score)

    return {
        "dinner_score": score,
        "percentile": score_stats['percentile'],
        "ranking": score_stats['ranking'],
        "normalized_score": score_stats['normalized_score'],
        "rank_normalized_score": score_stats['rank_normalized_score'],
        "percent_of_max": score_stats['percent_of_max'],
    }
