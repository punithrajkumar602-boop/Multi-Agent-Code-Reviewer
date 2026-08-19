"""
Simple CLI demo: runs the multi-agent reviewer against the sample
buggy file (or any file you point it at) without needing GitHub
credentials or a live PR. This is the easiest way to test the project
locally and generate screenshots.

Usage:
    py -m src.demo
    py -m src.demo path/to/your_file.py
"""
import sys
import json

from src.orchestrator import review_files


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "sample_code/buggy_example.py"

    with open(filepath, "r") as f:
        code = f.read()

    print(f"Reviewing: {filepath}\n{'=' * 60}\n")

    result = review_files([{"filename": filepath, "code": code}])

    print(result["consolidated_comment"])

    print("\n" + "=" * 60)
    print(f"Files reviewed: {result['files_reviewed']}")


if __name__ == "__main__":
    main()
