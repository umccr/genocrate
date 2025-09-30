from click.testing import CliRunner
from genocrate.main import cli  # Import the CLI group
import os
from genocrate.commands.validate import validate_batch

#
def test_validate_batch():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-001"])
    assert result.exit_code == 0

