import os
import sys

import click

from genocrate.crate.validate_utils import is_ro_crate_valid, is_valid_bagit, is_md5_checksum_valid
from genocrate.main import cli


@cli.command(name="validate-dataset")
@click.argument(
    'directory', type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True),
)
def validate_dataset(directory):
    """
    Validate RO Crate for the study-dataset profile compliance.

    :param directory: The directory containing the RO-Crate file (ro-crate-metadata.json)

    """

    if not is_ro_crate_valid(directory, profile_id='study-dataset'):
        click.echo("RO-Crate metadata is invalid!")
        sys.exit(1)


    click.echo('Validation successful!')
    sys.exit(0)
