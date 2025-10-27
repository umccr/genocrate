from genocrate.main import cli
from genocrate.commands.validate import validate_batch
from genocrate.commands.build import build
from genocrate.commands.diff import diff

# Import all commands to register them with the CLI
__all__ = ["cli", "validate_batch", "build", "diff"]
