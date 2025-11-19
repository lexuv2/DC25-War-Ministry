#!/usr/bin/env python3
import sys


def check_if_in_env() -> None:
    if sys.prefix == sys.base_prefix:
        print("❌ Please activate your virtual environment first!")
        print("   (e.g., 'source venv/bin/activate' or 'venv\\Scripts\\activate')")
        sys.exit(1)


check_if_in_env()

import argparse
from src.parser import Parser
import json
import os


def main() -> None:
    args_parser = argparse.ArgumentParser(
        description="Extract text from a PDF using PyMuPDF."
    )
    args_parser.add_argument(
        "--api-mock",
        action="store_true",
        help="Run in API mock mode (no real processing).",
    )
    args_parser.add_argument(
        "--input", default="test/pdf/basic-sample.pdf", help="Path to input PDF file."
    )
    args_parser.add_argument(
        "--output", default="output.json", help="Path to output text file."
    )
    args = args_parser.parse_args()

    parser = Parser()

    if args.api_mock:
        mock = parser.create_mock()
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(mock.model_dump_json(indent=2, ensure_ascii=False))
        return

    cv = parser.parse_file(
        args.input, enable_log=True, log_output=os.path.dirname(args.output)
    )
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(cv.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
