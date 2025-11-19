import os
import sys

import click

from genocrate.crate.validate_utils import is_ro_crate_valid, is_valid_bagit, is_md5_checksum_valid
from genocrate.main import cli


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
    is_flag=True,
    default=False,
    help="Skip integrity validation and only validate RO-Crate metadata"
)
@click.option(
    '--data-folder',
    type=click.STRING,
    default="data",
    help="The folder where the data files are located. Defaults to 'data'"
)
def validate_batch(path, validation_type, parallel, skip_integrity_validation, data_folder):
    """
    Validate a batch of files or bags for BagIt or MD5 compliance.


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

    if not is_ro_crate_valid(f"{dir_path}/{data_folder}", profile_id='batch-submission'):
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
        if not is_md5_checksum_valid(manifest_file_path, f'{dir_path}/{data_folder}', processes=parallel):
            click.echo('MD5 checksum validation failed.')
            sys.exit(1)

    click.echo('Validation successful!')
    sys.exit(0)
