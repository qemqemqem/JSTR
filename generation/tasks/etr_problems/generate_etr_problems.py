import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate Easy-to-Read math problems")
    parser.add_argument("-n", "--num_problems", type=int, default=5, 
                       help="Number of problems to generate")
    args = parser.parse_args()
    print(f"Would generate {args.num_problems} problems")

if __name__ == "__main__":
    main()
