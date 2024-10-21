import argparse
import json
import matplotlib.pyplot as plt
from collections import defaultdict
import os
from pathlib import Path

def get_latest_file(directory):
    return max(
        (os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jsonl')),
        key=os.path.getmtime
    )

def load_results(file_path):
    print(f"Loading results from: {file_path}")
    with open(file_path, 'r') as f:
        results = [json.loads(line) for line in f]
    print(f"Loaded {len(results)} results")
    if results:
        print("First result keys:", results[0].keys())
    return results

def create_graph(results, param, y_value):
    print(f"Creating graph with param: {param}, y_value: {y_value}")
    param_values = defaultdict(list)
    for i, result in enumerate(results):
        print(f"Processing result {i}:")
        # print("  Keys:", result.keys())
        if 'scoring_guide' in result['doc']:
            # print("  Scoring guide keys:", result['doc']['scoring_guide'].keys())
            if 'parameters' in result['doc']['scoring_guide']:
                print("Parameters:", result['doc']['scoring_guide']['parameters'])
        
        try:
            param_value = result['doc']['scoring_guide']['parameters'][param]
            param_values[param_value].append(result[y_value])
        except KeyError as e:
            print(f"  KeyError: {e}")
            print(f"  Result: {result.keys()}")

    x_data = sorted(param_values.keys())
    y_data = [sum(param_values[x]) / len(param_values[x]) for x in x_data]

    plt.figure(figsize=(12, 6))
    plt.bar(x_data, y_data)
    plt.xlabel(param.replace('_', ' ').title())
    plt.ylabel(f'Average {y_value.replace("_", " ").title()}')
    plt.title(f'{param.replace("_", " ").title()} vs Average {y_value.replace("_", " ").title()}')
    plt.xticks(x_data, rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent cutting off labels
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def main():
    default_input_dir = Path(__file__).parents[3] / "tasks" / "dinner_party" / "results" / "gpt-4"
    default_input_file = get_latest_file(default_input_dir)

    parser = argparse.ArgumentParser(description="Create a graph from dinner party evaluation results")
    parser.add_argument("--input_file", default=default_input_file, 
                        help="Path to the input JSONL file with evaluation results")
    parser.add_argument("--param", choices=['bimodal_discount', 'set_size', 'num_people', 'num_interests', 'avg_points'], 
                        default='bimodal_discount', help="Parameter to use for x-axis")
    parser.add_argument("--y_value", choices=['dinner_score', 'percentile', 'ranking'], 
                        default='dinner_score', help="Value to use for y-axis")
    args = parser.parse_args()

    print(f"Input file: {args.input_file}")
    print(f"Param: {args.param}")
    print(f"Y-value: {args.y_value}")

    results = load_results(args.input_file)
    create_graph(results, args.param, args.y_value)

if __name__ == "__main__":
    main()
