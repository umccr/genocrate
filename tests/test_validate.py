from click.testing import CliRunner
from genocrate.main import cli
from unittest.mock import patch

def test_validate_batch_valid_bagit():
    """
    Test that the 'validate-batch' command succeeds for a batch conforming to the BagIt specification.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/test-batches/batch-001", "-t", "bagit"])
    assert result.exit_code == 0


def test_validate_batch_invalid_bagit():
    """
    Test that the 'validate-batch' command fails for a batch NOT conforming to the BagIt specification.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-004", "-t", "bagit"])
    assert result.exit_code == 1

def test_validate_batch_valid_md5():
    """
    Test that the 'validate-batch' command succeeds when the manifest is valid and all files are listed in the manifest.
    """
    runner = CliRunner()

    # mock making sure it makes the ro_crate_valid check to True to focus testing on the md5 validation
    with patch('genocrate.commands.validate_batch.is_ro_crate_valid', return_value=True):
        result = runner.invoke(
            cli,
            ["validate-batch", "./tests/fixtures/batch-004/good-manifest-md5.txt", "-t", "md5"]
        )
        print(result.output)
        assert result.exit_code == 0

def test_validate_batch_invalid_md5():
    """
    Test that the 'validate-batch' when the manifest failed (incorrect checksum or files not listed).
    """
    runner = CliRunner()

    with patch('genocrate.commands.validate_batch.is_ro_crate_valid', return_value=True):
        result = runner.invoke(
            cli,
            ["validate-batch", "./tests/fixtures/batch-004/bad-manifest-md5.txt", "-t", "md5"]
        )
        assert result.exit_code == 1

def test_validate_invalid_ro_crate():
    """
    Test that the 'validate-batch' command fails when the RO-Crate metadata does not list all files.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["validate-batch", "./tests/fixtures/batch-004", "--skip-integrity-validation"])
    assert result.exit_code == 1
