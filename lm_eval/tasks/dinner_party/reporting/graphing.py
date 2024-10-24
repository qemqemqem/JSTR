import argparse
import json
import matplotlib.pyplot as plt
from collections import defaultdict
import os
from pathlib import Path
import numpy as np
import seaborn as sns
from scipy import stats

def get_latest_file(directory):
    return max(
        (os.path.join(root, f) for root, _, files in os.walk(directory) for f in files if f.endswith('.jsonl')),
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
    
    plt.figure(figsize=(14, 8))  # Larger figure to accommodate additional legend
    
    # Create box plot
    box_plot = plt.boxplot([param_values[x] for x in x_data], patch_artist=True, medianprops={'color': "#D81B60"})
    
    # Customize box plot colors
    for box in box_plot['boxes']:
        box.set(facecolor='#1E88E5', alpha=0.6)
    
    # Plot individual data points with jitter
    all_x = []
    all_y = []
    for i, x in enumerate(x_data):
        y = param_values[x]
        jitter = np.random.normal(0, 0.1, len(y))
        plt.scatter(np.array([i+1] * len(y)) + jitter, y, color='#888888', alpha=0.3, s=30, zorder=2)
        all_x.extend([x] * len(y))
        all_y.extend(y)
    
    # Compute best fit line
    slope, intercept, r_value, p_value, std_err = stats.linregress(all_x, all_y)
    line = slope * np.array(x_data) + intercept
    plt.plot(range(1, len(x_data) + 1), line, color='red', linestyle='--', label=f'Best Fit Line (R² = {r_value**2:.3f})')
    
    plt.xlabel(param.replace('_', ' ').title(), fontsize=11, fontweight='bold')
    plt.ylabel(f'{y_value.replace("_", " ").title()}', fontsize=11, fontweight='bold')
    plt.title(f'Impact of {param.replace("_", " ").title()} on {y_value.replace("_", " ").title()}', fontsize=13, fontweight='bold')
    
    plt.xticks(range(1, len(x_data) + 1), x_data, rotation=0, ha='center', fontsize=9)
    
    # Print median horizontally below the x-axis labels
    for i, x in enumerate(x_data):
        median_value = np.median(param_values[x])
        plt.text(i+1, plt.gca().get_ylim()[0] - 0.03 * (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]),
                 f'Median: {median_value:.2f}', rotation=0, va='top', ha='center', fontsize=8)
    plt.yticks(fontsize=9)
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.gca().set_facecolor('#f9f9f9')  # Very light gray background
    
    # Add a subtle border
    for spine in plt.gca().spines.values():
        spine.set_edgecolor('#e0e0e0')
    
    # Add legend to show N for each bin and best fit line info
    legend_labels = [f'{x}: N={len(param_values[x])}' for x in x_data]
    plt.legend(legend_labels + [f'Best Fit Line (R² = {r_value**2:.3f})'], 
               title="Bin Sizes and Fit", title_fontsize=10, fontsize=8, 
               loc='center left', bbox_to_anchor=(1, 0.5))
    
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
    default_input_dir = Path(__file__).parents[3] / "tasks" / "dinner_party" / "results"
    default_input_file = get_latest_file(default_input_dir)

    parser = argparse.ArgumentParser(description="Create a graph from dinner party evaluation results")
    parser.add_argument("--input_file", default=default_input_file, 
                        help="Path to the input JSONL file with evaluation results")
    parser.add_argument("--param", choices=['all', 'bimodal_discount', 'set_size', 'num_people', 'num_interests', 'avg_points'], 
                        default='set_size', help="Parameter to use for x-axis. Use 'all' to generate graphs for all parameters.")
    parser.add_argument("--y_value", choices=['dinner_score', 'percentile', 'ranking', 'normalized_score', 'rank_normalized_score'], 
                        default='ranking', help="Value to use for y-axis")
    parser.add_argument("--display_graph", action="store_true", default=False,
                        help="Whether to display the graph (default: True)")
    args = parser.parse_args()

    print(f"Input file: {args.input_file}")
    print(f"Param: {args.param}")
    print(f"Y-value: {args.y_value}")
    print(f"Display graph: {args.display_graph}")

    results = load_results(args.input_file)

    if args.param == 'all':
        params = ['bimodal_discount', 'set_size', 'num_people', 'num_interests', 'avg_points']
        for param in params:
            print(f"Creating graph for parameter: {param}")

            # Check to see if all the values are the same
            all_values = set()
            for result in results:
                all_values.add(result['doc']['scoring_guide']['parameters'][param])
            if len(all_values) == 1:
                print(f"  Skipping graph for parameter {param} because all values are the same: {all_values}")
                continue

            create_graph(results, param, args.y_value, args)
    else:
        create_graph(results, args.param, args.y_value, args)

    # print the location where these are all saved
    print(f"Graphs saved in: {default_input_dir}")

if __name__ == "__main__":
    main()
