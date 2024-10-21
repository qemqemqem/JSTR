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

    plt.figure(figsize=(12, 7))  # Slightly larger figure to accommodate legend
    
    # Plot individual data points
    for i, x in enumerate(x_data):
        y = param_values[x]
        plt.scatter([i] * len(y), y, color='#888888', alpha=0.5, s=20, zorder=2)
    
    # Create the point plot with a softer color
    sns.pointplot(x=x_data, y=y_data, capsize=0.1, linestyles='dashed', color='#222222', zorder=3)
    
    # Add error bars with improved visibility
    plt.errorbar(range(len(x_data)), y_data, yerr=confidence_intervals, fmt='none', color='#4444BB', capsize=10, linewidth=2.8, alpha=1.0, capthick=2.0, zorder=4)
    
    plt.xlabel(param.replace('_', ' ').title(), fontsize=11, fontweight='bold')
    plt.ylabel(f'Average {y_value.replace("_", " ").title()}', fontsize=11, fontweight='bold')
    plt.title(f'Impact of {param.replace("_", " ").title()} on {y_value.replace("_", " ").title()}', fontsize=13, fontweight='bold')
    
    plt.xticks(range(len(x_data)), x_data, rotation=0, ha='center', fontsize=9)
    plt.yticks(fontsize=9)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.gca().set_facecolor('#f9f9f9')  # Very light gray background
    
    # Add a subtle border
    for spine in plt.gca().spines.values():
        spine.set_edgecolor('#e0e0e0')
    
    # Add legend to show N for each bin
    legend_labels = [f'{x}: N={len(param_values[x])}' for x in x_data]
    plt.legend(legend_labels, title="Bin Sizes", title_fontsize=10, fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    
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
                        default='ranking', help="Value to use for y-axis")
    parser.add_argument("--display_graph", action="store_true", default=False,
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
