"""Main CLI entry point for Lambdora."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .repl import repl
from .runner import run_file


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="lambdora",
        description="A minimalist Lisp-inspired functional language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lambdora repl                    # Start interactive REPL
  lambdora run script.lamb         # Execute a Lambdora script
  lambdora --version               # Show version information
        """,
    )
    
    parser.add_argument(
        "--version",
        action="version", 
        version=f"Lambdora {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # REPL subcommand
    repl_parser = subparsers.add_parser("repl", help="Start the interactive REPL")
    
    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Execute a Lambdora script")
    run_parser.add_argument("file", help="Path to the .lamb file to execute")
    
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        if parsed_args.command == "repl":
            repl()
            return 0
        elif parsed_args.command == "run":
            file_path = Path(parsed_args.file)
            if not file_path.exists():
                print(f"Error: File '{file_path}' not found.", file=sys.stderr)
                return 1
            if not file_path.suffix == ".lamb":
                print(f"Warning: File '{file_path}' doesn't have .lamb extension.", file=sys.stderr)
            run_file(file_path)
            return 0
        else:
            # No subcommand provided, show help
            parser.print_help()
            return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 