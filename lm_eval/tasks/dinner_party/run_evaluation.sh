#!/bin/bash

# Help text function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Run dinner party evaluation with specified parameters."
    echo
    echo "Options:"
    echo "  -m, --model MODEL       Model to use (default: gpt-4-turbo)"
    echo "  -s, --step-by-step     Enable step-by-step mode (default: false)"
    echo "  -p, --path PATH        Path to lm-evaluation-harness directory"
    echo "  -i, --include PATH     Path to include for task definitions"
    echo "  -h, --help            Show this help message"
    echo
    echo "Example:"
    echo "  $0 -m gpt-4-turbo -s true -p /path/to/lm-evaluation-harness"
}

# Default values
MODEL="gpt-4-turbo"
STEP_BY_STEP="false"
EVAL_PATH="/home/keenan/Dev/lm-evaluation-harness/"
INCLUDE_PATH="/home/keenan/Dev/JSTR/"

# Assert that EVAL_PATH is a real directory
if [ ! -d "$EVAL_PATH" ]; then
    echo "Error: $EVAL_PATH is not a valid directory, please rerun with the '--path' option."
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -s|--step-by-step)
            STEP_BY_STEP="$2"
            shift 2
            ;;
        -p|--path)
            EVAL_PATH="$2"
            shift 2
            ;;
        -i|--include)
            INCLUDE_PATH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Export PYTHONPATH if needed
if [ -n "$EVAL_PATH" ]; then
    export PYTHONPATH="${EVAL_PATH}:${PYTHONPATH:+:$PYTHONPATH}"
fi

echo "Configuration:"
echo "  Model: $MODEL"
echo "  Step-by-step mode: $STEP_BY_STEP"
echo "  Evaluation harness path: $EVAL_PATH"
echo "  Include path: $INCLUDE_PATH"

# Set task based on step-by-step mode
TASK="dinner_party_real"
if [ "$STEP_BY_STEP" = "true" ]; then
    TASK="dinner_party_real_step_by_step"
fi

# Run evaluation
lm_eval --model openai-chat-completions \
    --model_args model=$MODEL \
    --include_path "$INCLUDE_PATH" \
    --tasks $TASK \
    --num_fewshot 0 \
    --batch_size 1 \
    --output_path lm_eval/tasks/dinner_party/results \
    --apply_chat_template \
    --log_samples \
    --verbosity DEBUG

# Uncomment to use Anthropic's Claude model instead
#lm_eval --model anthropic-chat-completions \
#    --model_args model=claude-3-5-sonnet-20240620 \
