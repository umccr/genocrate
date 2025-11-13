import os
import sys
import datetime
import click

from genocrate.crate.merger import process_crate
from genocrate.crate.rocrate import ROCrate
from genocrate.main import cli


@cli.command(name="build")
@click.argument(
    "path", type=click.Path(exists=True, dir_okay=True, file_okay=False)
)
@click.option(
    "--output-path", "-o",
    help="Path to the output RO-Crate metadata file (local path or S3 URI, e.g., s3://bucket/ro-crate-metadata.json). Requires AWS credentials for S3.",
    default="./ro-crate-metadata.json"
)
@click.option("--name", help="Dataset name", required=True)
@click.option("--description", help="Dataset description", required=True)
@click.option("--date-published", help="Publication date (YYYY-MM-DD)", default=datetime.date.today())
@click.option("--publisher", help="Publisher ROR ID (e.g., https://ror.org/...)")
@click.option("--license", help="License for the dataset (textual description of how the RO-Crate may be used)",
              default="Confidential - Not for Public Release.")
def build(
        path: str,
        output_path: str,
        name: str,
        description: str,
        date_published: str,
        publisher: str,
        license: str
):
    """
    Build and validate a batch of RO-Crate files.

    PATH: Directory containing one or more ro-crate-metadata.json files.
    """
    output_crate = ROCrate(
        output_path=output_path,
        name=name,
        description=description,
        date_published=date_published,
        publisher=publisher,
        # TODO: Ability for referencing contextual entity license
        license_=license
    )

    # Find all RO-Crate metadata files
    crate_paths = find_crate_metadata_files(path)

    # Sort by timestamp order
    sorted_crate_paths = sorted(crate_paths)
    for crate_path in sorted_crate_paths:
        replacement_crate = process_crate(crate_path=crate_path, output_crate=output_crate)
        output_crate.merge_ro_crate(replacement_crate)

    output_crate.to_file()

    click.echo('Crate created/updated!')
    sys.exit(0)


def find_crate_metadata_files(base_path: str) -> list[str]:
    """Find all ro-crate-metadata.json files in directory tree."""
    crate_paths = []

    for dirpath, dirnames, filenames in os.walk(base_path):
        if 'ro-crate-metadata.json' in filenames:
            metadata_path = os.path.join(dirpath, 'ro-crate-metadata.json')
            crate_paths.append(metadata_path)

    return crate_paths
