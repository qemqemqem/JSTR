import json

def add_question(question, jsonl_file):
    """
    Append a question to a JSONL file.

    Args:
    question (dict): The question to be added, in dictionary format.
    jsonl_file (str): The path to the JSONL file where the question will be appended.
    """
    with open(jsonl_file, 'a') as f:
        json.dump(question, f)
        f.write('\n')
