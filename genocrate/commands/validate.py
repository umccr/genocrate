import json
import os
import sys
import hashlib
import multiprocessing

import click
from genocrate.main import cli
import bagit
from rocrate_validator import services, models

# Block size used when reading files for hashing
HASH_BLOCK_SIZE = 512 * 1024


def is_valid_bagit(path: str, processes: int = 1) -> bool:
    """
    Validate all bags in a directory using bagit-python.

    :param path: Path to the directory containing bags
    :param processes: Number of parallel processes to use
    :return: True if valid, False otherwise
    """
    bag = bagit.Bag(path)
    return bag.is_valid(processes=processes)


def _calc_hashes(filename: str) -> tuple:
    """
    Calculate the MD5 hash of a file.

    :param filename: Path to the file
    :return: Tuple of (filename, md5 hash)
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while chunk := f.read(HASH_BLOCK_SIZE):
            md5.update(chunk)
    return filename, md5.hexdigest()


def read_manifest(manifest_path: str) -> dict:
    """
    Read a manifest file and return a dict mapping filenames to checksums.

    :param manifest_path: Path to the manifest file
    :return: Dict of {filename: checksum}
    """
    expected = {}
    with open(manifest_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            checksum, filename = parts[0], parts[-1]
            expected[filename] = checksum
    return expected


def worker_init():
    """Initializer for multiprocessing workers (placeholder)."""
    pass


def compute_hashes(file_list, processes: int = 1) -> list:
    """
    Compute hashes for a list of files, optionally in parallel.

    :param file_list: List of file paths
    :param processes: Number of parallel processes to use
    :return: List of (filename, hash) tuples
    """
    if processes == 1:
        return [_calc_hashes(f) for f in file_list]
    with multiprocessing.Pool(processes, initializer=worker_init) as pool:
        return pool.map(_calc_hashes, file_list)


def is_md5_checksum_valid(manifest_file_path: str, data_directory: str, processes: int = 1) -> bool:
    """
    Validate MD5 checksums of files against a manifest.

    :param manifest_file_path: Path to the manifest file
    :param processes: Number of parallel processes to use
    :return: True if all checksums match, False otherwise
    """
    errors = []
    files = [
        os.path.join(data_directory, f)
        for f in os.listdir(data_directory)
        if os.path.isfile(os.path.join(data_directory, f))
    ]

    hash_results = compute_hashes(files, processes=processes)
    manifest = read_manifest(manifest_file_path)

    for filepath, md5 in hash_results:
        # Convert absolute path to relative path matching manifest format
        relative_path = os.path.relpath(filepath, start=os.path.dirname(data_directory))
        expected_md5 = manifest.get(relative_path)
        if expected_md5 is None:
            errors.append(f"File {relative_path} not found in manifest")
        elif md5 != expected_md5:
            errors.append(f"MD5 mismatch for {relative_path}: expected {expected_md5}, calculated {md5}")

    if errors:
        click.echo(json.dumps(errors, indent=4))

    return not errors

def is_ro_crate_valid(path: str) -> bool:
    # Create an instance of `ValidationSettings` class to configure the validation
    settings = services.ValidationSettings(
        # Set the path to the RO-Crate root directory
        rocrate_uri=path,
        # Set the identifier of the RO-Crate profile to use for validation.
        # If not set, the system will attempt to automatically determine the appropriate validation profile.
        profile_identifier='genocrate-batch-submission',
        # Set the requirement level for the validation
        requirement_severity=models.Severity.REQUIRED,
        profiles_path=os.path.join(os.path.dirname(__file__), "../profile/genocrate-batch-submission/rules"),

    )
    # Call the validation service with the settings
    result = services.validate(settings)

    # Check if the validation was successful
    if not result.has_issues():
        return True
    else:
        for issue in result.get_issues():
            # Every issue object has a reference to the check that failed, the severity of the issue, and a message describing the issue.
            click.echo(
                f"Detected issue of severity {issue.severity.name} with check \"{issue.check.identifier}\": {issue.message}"
            )
        return False


@cli.command(name="validate-batch")
@click.argument(
    'path', type=click.Path(exists=True, dir_okay=True, file_okay=True, readable=True),
)
@click.option(
    '--validation-type', '-t',
    type=click.Choice(['bagit', 'md5'], case_sensitive=False),
    default='bagit',
    help="Type of validation to perform"
)
@click.option(
    '--parallel', '-p',
    type=click.INT,
    default=1,
    help="Number of processes to run in parallel"
)
@click.option(
    '--skip-integrity-validation',
    is_flag=False)
def validate_batch(path, validation_type, parallel, skip_integrity_validation):
    """
    Validate a batch of files or bags for BagIt or MD5 compliance.

    :param PATH: Directory containing a BagIt-compliant batch (for 'bagit' type) or a manifest file with MD5 checksums (for 'md5' type)"

    """
    dir_path = path
    manifest_file_path = ''

    # if path is a file, ignore cd to the data directory
    if os.path.isfile(path):
        if validation_type != 'md5':
            click.echo("When providing a file, the validation type must be 'md5'")
            sys.exit(1)
        manifest_file_path = path
        dir_path = os.path.dirname(path)

    if not is_ro_crate_valid(f"{dir_path}/data"):
        click.echo("RO-Crate metadata is invalid!")
        sys.exit(1)

    click.echo("RO-Crate metadata is valid!")

    # Skip integrity validation if requested
    if skip_integrity_validation:
        click.echo('Skipping integrity validation as requested.')
        click.echo('Validation successful!')
        sys.exit(0)

    # Integrity validation
    if validation_type == 'bagit':
        click.echo(f'Validating for BagIt compliance ({dir_path})')
        if not is_valid_bagit(dir_path, processes=parallel):
            click.echo('Bag validation failed.')
            sys.exit(1)
    elif validation_type == 'md5':
        click.echo(f'Validating files from md5sum ({manifest_file_path})')
        if not is_md5_checksum_valid(manifest_file_path, f'{dir_path}/data', processes=parallel):
            click.echo('MD5 checksum validation failed.')
            sys.exit(1)

    click.echo('Validation successful!')
    sys.exit(0)
