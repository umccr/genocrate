import json
import os
import sys
import hashlib
import multiprocessing

import click
from genocrate.main import cli
import bagit

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


def list_files_exclude_manifest(manifest_path: str) -> list:
    """
    List all files in the manifest's directory, excluding the manifest itself.

    :param manifest_path: Path to the manifest file
    :return: List of file paths
    """
    directory = os.path.dirname(manifest_path)
    manifest_file = os.path.basename(manifest_path)
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f != manifest_file
    ]


def is_md5_checksum_valid(manifest_file_path: str, processes: int = 1) -> bool:
    """
    Validate MD5 checksums of files against a manifest.

    :param manifest_file_path: Path to the manifest file
    :param processes: Number of parallel processes to use
    :return: True if all checksums match, False otherwise
    """
    errors = []
    files = list_files_exclude_manifest(manifest_file_path)
    hash_results = compute_hashes(files, processes=processes)
    manifest = read_manifest(manifest_file_path)

    for filepath, md5 in hash_results:
        filename = os.path.basename(filepath)
        expected_md5 = manifest.get(filename)
        if expected_md5 is None:
            errors.append(f"File {filename} not found in manifest")
        elif md5 != expected_md5:
            errors.append(f"MD5 mismatch for {filename}: expected {expected_md5}, calculated {md5}")

    print(json.dumps(errors, indent=4))
    return not errors


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
def validate_batch(path, validation_type, parallel):
    """
    Validate a batch of files or bags for BagIt or MD5 compliance.

    :param PATH: Directory containing a BagIt-compliant batch (for 'bagit' type) or a manifest file with MD5 checksums (for 'md5' type)"

    """
    if validation_type == 'bagit':
        click.echo(f'Validating for bagIt compliance ({path})')
        is_valid = is_valid_bagit(path, processes=parallel)
        if not is_valid:
            click.echo('Bag validation failed.')
            sys.exit(1)
    elif validation_type == 'md5':
        click.echo(f'Validating files from md5sum ({path})')
        is_valid = is_md5_checksum_valid(path, processes=parallel)
        if not is_valid:
            click.echo('MD5 checksum validation failed.')
            sys.exit(1)

    click.echo('Validation successful.')
    sys.exit(0)
