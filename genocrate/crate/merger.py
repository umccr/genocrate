import os

from genocrate.crate.rocrate import ROCrate

def process_crate(crate_path: str, output_crate: ROCrate) -> ROCrate:
    """Process a single RO-Crate and add its entities to the output graph."""
    sub_crate = ROCrate.from_ro_crate_path(crate_path=crate_path)
    crate_dirname = os.path.dirname(crate_path)

    non_root_datasets = sub_crate.find_non_root_dataset_entity()

    # Build a new crate containing merged entities from sub crate and output crate
    crate_to_merge = ROCrate()

    for dataset in non_root_datasets:
        dataset_id = dataset.get('@id')
        existing_dataset = output_crate.find_entity_by_id(dataset_id)

        if existing_dataset is not None:
            # Dataset exists in root crate - preserve it as base to retain existing links
            # TODO: Add history log for dataset update
            crate_to_merge.add_new_entity(existing_dataset)
        else:
            # New dataset - add from sub crate
            # TODO: Add history log for dataset creation
            crate_to_merge.add_new_entity(dataset)

        # Process collection entities referenced by this dataset
        collection_entities = sub_crate.find_entities_by_has_part(dataset.get("hasPart", []))
        for collection in collection_entities:
            collection_id = collection.get('@id')

            # Link collection to dataset
            crate_to_merge.upsert_has_part_id_to_entity(dataset_id, collection_id)

            # Check if collection exists in output crate (for update vs create)
            existing_collection = output_crate.find_entity_by_id(collection_id)
            if existing_collection is not None:
                # TODO: Add history log for collection update
                pass
            else:
                # TODO: Add history log for collection creation
                pass

            # Merge file entities from both root and sub crates
            # Dictionary uses identifier (filename) as key to deduplicate files
            files_by_identifier = {}

            # Add existing files from root crate collection (if present)
            if existing_collection is not None:
                for file in output_crate.find_entities_by_has_part(existing_collection.get('hasPart', [])):
                    files_by_identifier[file["identifier"]] = file

            # Add/override with files from sub crate (newer takes precedence)
            for file in sub_crate.find_entities_by_has_part(collection.get('hasPart', [])):
                files_by_identifier[file["identifier"]] = file

            # Update file paths and add to crate
            new_files_ids = []
            for identifier, file in files_by_identifier.items():
                file_id = file.get('@id')

                # Update path only for files from sub crate (where @id equals identifier)
                # Files from root crate retain their original paths
                new_file_id = file_id
                if file_id == identifier:
                    new_file_id = f"{crate_dirname}/{file_id}"

                new_files_ids.append({"@id": new_file_id})
                crate_to_merge.add_new_entity({**file, "@id": new_file_id})

            # Update collection with new file references
            collection["hasPart"] = new_files_ids
            crate_to_merge.add_new_entity(collection)

    return crate_to_merge