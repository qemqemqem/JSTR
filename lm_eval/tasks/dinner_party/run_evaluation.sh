#!/bin/bash

# TODO Try `--include_path .` instead

lm_eval --model openai-chat-completions \
    --model_args model=gpt-4-turbo \
    --include_path /home/keenan/Dev/JSTR/ \
    --tasks dinner_party_real \
    --num_fewshot 0 \
    --batch_size 1 \
    --output_path lm_eval/tasks/dinner_party/results \
    --apply_chat_template \
    --log_samples \
    --verbosity DEBUG



#lm_eval --model anthropic-chat-completions \
#    --model_args model=claude-3-5-sonnet-20240620 \