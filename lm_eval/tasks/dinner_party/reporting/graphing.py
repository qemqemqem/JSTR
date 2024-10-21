import argparse
import json
import matplotlib.pyplot as plt
from collections import defaultdict
import os
from pathlib import Path
import numpy as np
from scipy import stats
import seaborn as sns

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

def create_graph(results, param, y_value, args):
    print(f"Creating graph with param: {param}, y_value: {y_value}")
    param_values = defaultdict(list)
    for i, result in enumerate(results):
        try:
            param_value = result['doc']['scoring_guide']['parameters'][param]
            param_values[param_value].append(result[y_value])
        except KeyError as e:
            print(f"  KeyError: {e}")

    x_data = list(param_values.keys())
    y_data = [np.mean(param_values[x]) for x in x_data]
    
    confidence_intervals = [stats.sem(param_values[x]) * stats.t.ppf((1 + 0.95) / 2, len(param_values[x])-1)
                            for x in x_data]

    plt.figure(figsize=(12, 7))  # 16:9 aspect ratio
    
    # Create the point plot
    sns.pointplot(x=x_data, y=y_data, capsize=0.2, join=False, color='darkblue', scale=1.5)
    
    # Add error bars
    plt.errorbar(range(len(x_data)), y_data, yerr=confidence_intervals, fmt='none', color='darkblue', capsize=5, linewidth=1.5, alpha=0.7)
    
    plt.xlabel(param.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    plt.ylabel(f'Average {y_value.replace("_", " ").title()}', fontsize=12, fontweight='bold')
    plt.title(f'Impact of {param.replace("_", " ").title()} on {y_value.replace("_", " ").title()}', fontsize=14, fontweight='bold')
    plt.suptitle('With 95% Confidence Intervals', fontsize=10, y=0.95)
    
    plt.xticks(range(len(x_data)), x_data, rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    
    # Add value labels
    for i, v in enumerate(y_data):
        plt.text(i, v, f'{v:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.gca().set_facecolor('#f8f8f8')  # Light gray background
    
    # Save the graph as an image
    output_dir = Path(args.input_file).parent / Path(args.input_file).stem
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{param}_{y_value}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph saved as: {output_file}")

    # Show it to the user if display_graph is True
    if args.display_graph:
        plt.show()
    
    plt.close()

def main():
    default_input_dir = Path(__file__).parents[3] / "tasks" / "dinner_party" / "results" / "gpt-4"
    default_input_file = get_latest_file(default_input_dir)

    parser = argparse.ArgumentParser(description="Create a graph from dinner party evaluation results")
    parser.add_argument("--input_file", default=default_input_file, 
                        help="Path to the input JSONL file with evaluation results")
    parser.add_argument("--param", choices=['bimodal_discount', 'set_size', 'num_people', 'num_interests', 'avg_points'], 
                        default='set_size', help="Parameter to use for x-axis")
    parser.add_argument("--y_value", choices=['dinner_score', 'percentile', 'ranking'], 
                        default='dinner_score', help="Value to use for y-axis")
    parser.add_argument("--display_graph", action="store_true", default=True,
                        help="Whether to display the graph (default: True)")
    args = parser.parse_args()

    print(f"Input file: {args.input_file}")
    print(f"Param: {args.param}")
    print(f"Y-value: {args.y_value}")
    print(f"Display graph: {args.display_graph}")

    results = load_results(args.input_file)
    create_graph(results, args.param, args.y_value, args)

if __name__ == "__main__":
    main()
