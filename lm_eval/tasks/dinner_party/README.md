# Dinner Party Task

...

## Task Description

...

## Dataset

The dataset is a local JSONL file (`dinner_party.jsonl`) where each line contains a JSON object with ... fields:
- `question`: A string prompt
- `scoring_guide`: An object containing guidelines for scoring the response.

## Metrics

...

## Graphing

Command list:

Generate dinner parties in a jsonl file like this:

```bash
python generation/tasks/dinner_party/generate_dinner_parties.py \
  --avg_points 25 --points_spread 0 --min_interests 2 \
  --max_interests 6 --bimodal_discount=0,15 \
  --num_parties=2 --set_size=3,4,5,7
```

Use lm_eval to run the LLM against those tasks. Make sure the yaml file points to the correct model and the jsonl file you just made.

```bash
lm_eval/tasks/dinner_party/run_evaluation.sh
```

Now, the results will be in the `lm_eval/tasks/dinner_party/results` directory. The `graphing.py` utility will default to using the most recent result there. 

You can make some graphs of your most recent run like this:

```bash
python lm_eval/tasks/dinner_party/reporting/graphing.py
```