from generation.tasks.dinner_party import DinnerParty
import re

def score_answer(scoring_guide, answer):
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

    # Create the DinnerParty object from the scoring guide
    dinner_party = from_dict(data_class=DinnerParty, data=scoring_guide)

    # Extract names from the answer
    names = re.findall(r'\b[A-Z][a-z]*\b', answer_text)
    selected_set = names[:dinner_party.set_size]  # Take only the required number of names

    # Score the selected set
    score = dinner_party.score_set(selected_set)

    return {
        "score": score,
        "selected_set": selected_set,
        "target_score": scoring_guide.get('target_score', None)
    }
