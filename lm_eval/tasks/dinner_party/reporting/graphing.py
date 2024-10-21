import argparse
import json
import matplotlib.pyplot as plt

def load_results(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

def create_graph(results):
    dinner_scores = [result['dinner_score'] for result in results]
    percentiles = [result['percentile'] for result in results]

    plt.figure(figsize=(10, 6))
    plt.scatter(dinner_scores, percentiles)
    plt.xlabel('Dinner Score')
    plt.ylabel('Percentile')
    plt.title('Dinner Score vs Percentile')
    plt.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Create a graph from dinner party evaluation results")
    parser.add_argument("input_file", help="Path to the input JSONL file with evaluation results")
    args = parser.parse_args()

    results = load_results(args.input_file)
    create_graph(results)

if __name__ == "__main__":
    main()
