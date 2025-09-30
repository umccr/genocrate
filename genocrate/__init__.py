from genocrate.main import cli
from genocrate.commands.validate import validate_batch

# Import all commands to register them with the CLI
__all__ = ["cli", "validate_batch"]
