import os
import datetime
import csv
import click
import json
from typing import TypedDict, List, Literal, Optional

from genocrate.crate.merger import process_crate
from genocrate.crate.rocrate import ROCrate
from genocrate.main import cli

@cli.command(name="csv2crate")
@click.argument(
    "csv_path", nargs=1, type=click.Path(exists=True, file_okay=True)
)
@click.option(
    '--filename-column',
    type=str,
    default="filename",
    help="The csv column header for the filename within the manifest"
)
@click.option(
    '--identifier-column',
    type=str,
    default="identifier",
    help="The csv column header for the identifier within the manifest"
)
@click.option(
    '--checksum-column',
    type=str,
    default="checksum",
    help="The checksum column header for the filename within the manifest"
)
def csv2crate(
        csv_path: str,
        filename_column: str,
        identifier_column: str,
        checksum_column: str
):
    """
    Convert a CSV manifest file to an RO-Crate.
    The manifest should have columns for filename, identifier, and checksum.
    """

    # Get directory and name for output
    dirname = os.path.dirname(csv_path)
    name = os.path.basename(os.path.dirname(csv_path))

    # Initialize the RO-Crate
    crate = ROCrate(
        output_path=f"{dirname}/ro-crate-metadata.json",
        name=name,
        description=f"batch submission for {name}",
        date_published=datetime.date.today().isoformat(),
        license_="confidential - not for public release."
    )

    # Add the manifest CSV file as an entity in the crate
    manifest_file_entity = {
        "@id": os.path.basename(csv_path),
        "@type": "File",
        "identifier": os.path.basename(csv_path)
    }
    crate.add_new_entity(manifest_file_entity)

    # Get the root entity and prepare to add parts to it
    root_entity = crate.find_entity_by_id('./')
    root_entity_has_part = root_entity.get('hasPart', [])
    root_entity_has_part.append({"@id": manifest_file_entity["@id"]})

    # dataset: maps identifier to its collections
    dataset = {}
    # collection: maps collection id to its files
    collection = {}

    # Read the CSV and process each row
    with open(csv_path, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        for r in rows:
            filename = r[filename_column]
            identifier = r[identifier_column]
            checksum = r[checksum_column]

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
            "@id": key,
            "@type": "Dataset",
            "hasPart": [{"@id": cid} for cid in value]
        }
        crate.add_new_entity(dataset_entity)
        root_entity_has_part.append({"@id": dataset_entity["@id"]})

    # Write the crate to file and print the graph
    crate.to_file()
    print(json.dumps(crate.graph, indent=2))

def get_artifact_type(filename: str) -> str:
    """
    Determine the artifact type based on file extension.
    """
    if filename.endswith(".vcf") or filename.endswith(".vcf.gz") or filename.endswith(".tbi"):
        return "vcf"
    if filename.endswith(".bam") or filename.endswith(".bam.bai"):
        return "bam"
    if filename.endswith(".fastq") or filename.endswith(".fastq.gz") or filename.endswith(".fq") or filename.endswith(".fq.gz"):
        return "fastq"
    if filename.endswith('.cram') or filename.endswith('.cram.crai'):
        return "cram"
    raise ValueError(f"Unknown artifact type: {filename}")
