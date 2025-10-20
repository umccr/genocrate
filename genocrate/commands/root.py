import json
import os
import sys
from typing import Any

import click

from genocrate.commands.utils import ROCrate
from genocrate.main import cli


@cli.command(name="root")
@click.argument(
    'path', type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
def root(path):
    """
    Validate a batch of files or bags for BagIt or MD5 compliance.

    :param PATH: Directory containing batches
    """
    output_crate = ROCrate()

    # Find all RO-Crate metadata files
    crate_paths = find_crate_metadata_files(path)

    # Sort by timestamp order
    sorted_crate_paths = sorted(crate_paths)
    for crate_path in sorted_crate_paths:
        output_crate.merge_ro_crate(process_crate(crate_path=crate_path, output_crate=output_crate))


    print(json.dumps(output_crate.graph, indent=2))

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


def process_crate(crate_path: str, output_crate: ROCrate) -> ROCrate:
    """Process a single RO-Crate and add its entities to the output graph."""
    sub_crate = ROCrate.from_ro_crate_path(crate_path=crate_path)
    crate_dirname = os.path.dirname(crate_path)

    non_root_datasets = sub_crate.find_non_root_dataset_entity()

    # This should list all entities from this particular ro crate from path given
    crate_to_merge = ROCrate()

    for dataset in non_root_datasets:
        # FIXME: Check if collection already exists in output_crate_graph
        # first scenario it is a new create
        # 2nd scenario is an update to existing collection

        dataset_id = dataset.get('@id')
        main_crate_dataset = output_crate.find_entity_by_id(dataset_id)

        if main_crate_dataset is not None:
            # We make sure the existing root crate is added in the to_merge list as the base
            # we do not want to lose existing links from the root crate
            crate_to_merge.add_new_entity(main_crate_dataset)
        else:
            # If none is found, just append the dataset from the sub crate
            crate_to_merge.add_new_entity(dataset)

        # Find collection entities referenced by hasPart
        # We append any new collections found in the sub crate to the output crate graph
        collection_entities = sub_crate.find_entities_by_has_part(dataset.get("hasPart", []))
        for collection in collection_entities:
            collection_id = collection.get('@id')

            # First we upsert this id in the has_part to be part of the dataset
            crate_to_merge.upsert_has_part_id_to_entity(dataset_id, collection_id)

            existing_collection = output_crate.find_entity_by_id(collection_id)
            # crate historical on the dataset based on whether a collection exists or not
            if existing_collection is not None:
                # this is an update to existing collection
                # FIXME: Put update logic here say add history log
                # Find and replace existing collection
                pass
            else:
                # It is a new collection
                # create a new history create crate
                pass

            # Find file entities in this collection
            file_entities = sub_crate.find_entities_by_has_part(
                collection.get('hasPart', [])
            )

            # construct a new file array to have updated @id with crate directory name
            new_files_ids = []
            for file in file_entities:
                new_file_id = f"{crate_dirname}/{file['@id']}"

                new_files_ids.append({"@id": new_file_id})
                crate_to_merge.add_new_entity({**file, "@id": new_file_id})

            # update back the collection hasPart to have updated file ids
            collection["hasPart"] = new_files_ids

            crate_to_merge.add_new_entity(collection)

    return crate_to_merge
