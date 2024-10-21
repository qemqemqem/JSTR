import argparse
import json
import matplotlib.pyplot as plt

def load_results(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

def create_graph(results, x_value, y_value):
    x_data = [result[x_value] for result in results]
    y_data = [result[y_value] for result in results]

    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data)
    plt.xlabel(x_value.replace('_', ' ').title())
    plt.ylabel(y_value.replace('_', ' ').title())
    plt.title(f'{x_value.replace("_", " ").title()} vs {y_value.replace("_", " ").title()}')
    plt.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Create a graph from dinner party evaluation results")
    parser.add_argument("input_file", help="Path to the input JSONL file with evaluation results")
    parser.add_argument("--x_value", choices=['dinner_score', 'percentile', 'ranking'], default='dinner_score', help="Value to use for x-axis")
    parser.add_argument("--y_value", choices=['dinner_score', 'percentile', 'ranking'], default='percentile', help="Value to use for y-axis")
    args = parser.parse_args()

    results = load_results(args.input_file)
    create_graph(results, args.x_value, args.y_value)

if __name__ == "__main__":
    main()
