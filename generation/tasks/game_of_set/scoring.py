import re
import os
import sys

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())

from generation.tasks.game_of_set.game_of_set import GameOfSet, Card


def score_answer(question, answer):
    """
    Score the given answer based on whether it identifies a valid set.

    Args:
    question (dict): A dictionary containing the game board and scoring information.
    answer (str or dict): The model's response to the Set game question.

    Returns:
    dict: A dictionary containing the score and other relevant information.
    """
    # Extract answer text
    print()
    print(f"Raw Answer: {answer[:100]}...")
    if isinstance(answer, dict):
        answer_text = answer.get('text', '')
    elif isinstance(answer, list) and len(answer) > 0:
        answer_text = str(answer[0])
    else:
        answer_text = str(answer)

    # Find the "Answer:" part in the response
    match = re.search(r'Answer:\s*([^"\n]+)', answer_text)
    if match:
        answer_text = match.group(1).strip()
    else:
        # If no "Answer:" found, try to find card codes at the end
        lines = answer_text.split('\n')
        answer_text = lines[-1].strip()

    # Parse the selected cards from the answer
    try:
        selected_cards = [Card.from_code(code.strip()) for code in answer_text.split(',')]
    except Exception as e:
        print(f"Error parsing cards: {e}")
        selected_cards = []

    scoring_guide = question['scoring_guide']
    board = [Card(**card_dict) for card_dict in scoring_guide['board']]
    valid_set = [Card(**card_dict) for card_dict in scoring_guide['valid_set']]
    game = GameOfSet(board, valid_set)

    # Check if the selected cards form a valid set
    is_valid = len(selected_cards) == 3 and game.is_valid_set(selected_cards)

    # Calculate score: 1.0 if they found the valid set, 0.5 if they found a different valid set, 0.0 otherwise
    score = 1.0 if selected_cards == valid_set else (0.5 if is_valid else 0.0)

    return {
        "set_score": score,
        "valid_set": float(is_valid),  # Convert bool to float for metrics
        "len_response": len(str(answer)),
    }
