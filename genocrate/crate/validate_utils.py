import json
import os
import hashlib
import multiprocessing

import click
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
            # ignore empty or comment lines
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
    :param data_directory: Directory containing the files to check
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


def is_ro_crate_valid(path: str, profile_id: str) -> bool:

    if profile_id not in ['study-dataset', 'batch-submission']:
        raise ValueError("Profile ID must be one of 'study-dataset' or 'batch-submission'")

    # Create an instance of `ValidationSettings` class to configure the validation
    settings = services.ValidationSettings(
        # Set the path to the RO-Crate root directory
        rocrate_uri=path,
        # Set the identifier of the RO-Crate profile to use for validation.
        # If not set, the system will attempt to automatically determine the appropriate validation profile.
        profile_identifier=profile_id,
        # Set the requirement level for the validation
        requirement_severity=models.Severity.REQUIRED,
        profiles_path=os.path.join(os.path.dirname(__file__), f"../profile/{profile_id}/rules"),
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
