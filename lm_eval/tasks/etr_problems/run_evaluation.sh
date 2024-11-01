#!/bin/bash

MODEL="gpt-4-turbo"
TASK="etr_problems"

lm_eval --model openai-chat-completions \
    --model_args model=$MODEL \
    --tasks $TASK \
    --num_fewshot 0 \
    --batch_size 1 \
    --apply_chat_template \
    --verbosity DEBUG
