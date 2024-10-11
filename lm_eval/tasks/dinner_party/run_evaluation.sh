#!/bin/bash

lm_eval --model openai-chat-completions \
    --model_args model=gpt-4 \
    --tasks generation/tasks/dinner_party/dinner_party.yaml \
    --num_fewshot 0 \
    --batch_size 1 \
    --output_path lm_eval/tasks/dinner_party/results \
    --apply_chat_template \
    --log_samples \
    --verbosity DEBUG
