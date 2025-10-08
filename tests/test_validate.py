from click.testing import CliRunner
from genocrate.main import cli  # Import the CLI group
import os
from genocrate.commands.validate import validate_batch


def test_validate_batch_valid_bagit():
    """
    Test that the 'validate-batch' command succeeds for a batch conforming to the BagIt specification.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-001", "-t", "bagit"])
    assert result.exit_code == 0


def test_validate_batch_invalid_bagit():
    """
    Test that the 'validate-batch' command fails for a batch NOT conforming to the BagIt specification.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-002", "-t", "bagit"])
    assert result.exit_code == 1

def test_validate_batch_valid_md5():
    """
    Test that the 'validate-batch' command succeeds when the manifest is valid and all files are listed in the manifest.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-002/data/good-manifest-md5.txt", "-t", "md5"])
    assert result.exit_code == 0

# def test_validate_batch_invalid_md5():
#     """
#     Test that the 'validate-batch' when the manifest failed (incorrect checksum or files not listed).
#     """
#     runner = CliRunner()
#     result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-002/data/bad-manifest-md5.txt", "-t", "md5"])
#     assert result.exit_code == 1
