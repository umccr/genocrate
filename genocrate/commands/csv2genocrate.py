import os
import datetime
import csv
import click
import json
import sys

from genocrate.crate.rocrate import ROCrate
from genocrate.crate.validate_utils import is_ro_crate_valid, compute_hashes
from genocrate.main import cli


@cli.command(name="csv2genocrate")
@click.argument(
    "csv_path", nargs=1, type=click.Path(exists=True, file_okay=True)
)
@click.option(
    '--filename-column',
    type=str,
    default="filename",
    help="The csv column header for the filename within the manifest (default: 'filename')"
)
@click.option(
    '--identifier-column',
    type=str,
    default="identifier",
    help="The csv column header for the identifier within the manifest (default: 'identifier')"
)
@click.option(
    '--checksum-column',
    type=str,
    default="checksum",
    help="The checksum column header for the filename within the manifest (default: 'checksum')"
)
@click.option(
    '--skip-crate-validation',
    is_flag=True,
    default=False,
    help="Skip crate validation after is being created"
)
@click.option(
    '--skip-integrity-validation',
    is_flag=True,
    default=False,
    help="Skip integrity validation"
)
def csv2genocrate(
        csv_path: str,
        filename_column: str,
        identifier_column: str,
        checksum_column: str,
        skip_crate_validation: bool,
        skip_integrity_validation: bool,
):
    """
    Convert a CSV manifest file to an RO-Crate.

    The manifest must contain columns: filename, identifier, md5 checksum

    """

    # Get directory and name for output
    dirname = os.path.dirname(csv_path)
    name = os.path.basename(os.path.dirname(csv_path))
    crate_output = f"{dirname}/ro-crate-metadata.json"

    # Initialize the RO-Crate
    crate = ROCrate(
        output_path=crate_output,
        name=name,
        description=f"batch submission for {name}",
        date_published=datetime.date.today().isoformat(),
        license_="confidential - not for public release."
    )

    # Get the root entity and prepare to add parts to it
    root_entity = crate.find_entity_by_id('./')
    root_entity_has_part = root_entity.get('hasPart', [])

    # dataset: maps identifier to its collections
    dataset = {}
    # collection: maps collection id to its files
    collection = {}

    # filename map to checksum
    filename_to_checksum = {}

    # Read the CSV and process each row
    with open(csv_path, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        for r in rows:
            filename = r[filename_column]
            identifier = r[identifier_column]
            checksum = r[checksum_column]

            filename_to_checksum[filename] = checksum

            # Add file entity to the crate
            file_entity = {
                "@id": filename,
                "@type": "File",
                "identifier": filename
            }
            crate.add_new_entity(file_entity)

            # Determine artifact type (e.g., vcf, bam, fastq, cram)
            artifact_type = get_artifact_type(filename)

            # Group files into collections by identifier and artifact type
            collection_id = f"#{identifier}-{artifact_type}"
            collection_value = collection.get(collection_id, set())
            collection_value.add(file_entity["@id"])
            collection[collection_id] = collection_value

            # Map dataset (identifier) to its collections
            dataset_value = dataset.get(identifier, set())
            dataset_value.add(collection_id)
            dataset[identifier] = dataset_value

    # Add collection entities to the crate
    for key, value in collection.items():
        collection_entity = {
            "@id": key,
            "@type": "Collection",
            "hasPart": [{"@id": fid} for fid in value]
        }
        crate.add_new_entity(collection_entity)

    # Add dataset entities to the crate and link to root
    for key, value in dataset.items():
        dataset_entity = {
            "@id": f"#{key}",
            "@type": "Dataset",
            "identifier": key,
            "hasPart": [{"@id": cid} for cid in value]
        }
        crate.add_new_entity(dataset_entity)
        root_entity_has_part.append({"@id": dataset_entity["@id"]})

    # Write the crate to file and print the graph
    crate.to_file()
    click.echo(f'Successfully created RO-Crate: {crate_output}')

    if not skip_crate_validation:
        if not is_ro_crate_valid(dirname):
            click.echo("RO-Crate metadata is invalid!")
            sys.exit(1)

    if not skip_integrity_validation:
        file_absolute_paths = [os.path.join(
            dirname, fn) for fn in filename_to_checksum.keys()]
        hash_results = compute_hashes(file_absolute_paths, processes=1)
        errors = []
        for filepath, calculated_md5 in hash_results:
            fn = os.path.basename(filepath)

            expected_md5 = filename_to_checksum[fn]
            if calculated_md5 != expected_md5:
                errors.append(
                    f"MD5 mismatch for {fn}: expected {expected_md5}, calculated {calculated_md5}")

        if errors:
            click.echo("Checksum validation errors:")
            click.echo(json.dumps(errors, indent=4))
            sys.exit(1)

    return crate


def get_artifact_type(filename: str) -> str:
    """
    Determine the artifact type based on file extension.
    """
    if filename.endswith((".vcf", ".vcf.gz", ".tbi")):
        return "vcf"
    if filename.endswith((".bam", ".bam.bai")):
        return "bam"
    if filename.endswith((".fastq", ".fastq.gz", ".fq", ".fq.gz")):
        return "fastq"
    if filename.endswith((".cram", ".cram.crai")):
        return "cram"
    raise ValueError(f"Unknown artifact type: {filename}")
