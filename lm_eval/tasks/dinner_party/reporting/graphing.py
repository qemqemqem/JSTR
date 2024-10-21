import argparse
import json
import matplotlib.pyplot as plt
from collections import defaultdict

def load_results(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

def create_graph(results, param, y_value):
    param_values = defaultdict(list)
    for result in results:
        param_value = result['scoring_guide']['parameters'][param]
        param_values[param_value].append(result[y_value])

    x_data = sorted(param_values.keys())
    y_data = [sum(param_values[x]) / len(param_values[x]) for x in x_data]

    plt.figure(figsize=(10, 6))
    plt.plot(x_data, y_data, marker='o')
    plt.xlabel(param.replace('_', ' ').title())
    plt.ylabel(f'Average {y_value.replace("_", " ").title()}')
    plt.title(f'{param.replace("_", " ").title()} vs Average {y_value.replace("_", " ").title()}')
    plt.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Create a graph from dinner party evaluation results")
    parser.add_argument("input_file", help="Path to the input JSONL file with evaluation results")
    parser.add_argument("--param", choices=['bimodal_discount', 'set_size', 'num_people', 'num_interests', 'avg_points'], 
                        default='bimodal_discount', help="Parameter to use for x-axis")
    parser.add_argument("--y_value", choices=['dinner_score', 'percentile', 'ranking'], 
                        default='dinner_score', help="Value to use for y-axis")
    args = parser.parse_args()

    results = load_results(args.input_file)
    create_graph(results, args.param, args.y_value)

if __name__ == "__main__":
    main()
