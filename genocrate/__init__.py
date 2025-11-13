from genocrate.main import cli
from genocrate.commands.validate import validate_batch
from genocrate.commands.build import build
from genocrate.commands.diff import diff
from genocrate.commands.csv2genocrate import csv2genocrate

# Import all commands to register them with the CLI
__all__ = ["cli", "validate_batch", "build", "diff", "csv2genocrate"]
