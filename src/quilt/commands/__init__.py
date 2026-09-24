"""quilt.commands — per-command modules for the unified CLI.

Each module exposes:
    def register(subparsers) -> None
        Add this command's subparser to the tree.
    def run(args) -> int
        Run the command; return process exit code.
"""
