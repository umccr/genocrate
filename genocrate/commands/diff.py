import click
from typing import TypedDict, List, Literal, Optional

from genocrate.crate.merger import process_crate
from genocrate.crate.rocrate import ROCrate
from genocrate.main import cli


class DiffNode(TypedDict, total=True):
    change_type: Literal["modified", "added", "removed"]
    entity_type: str
    entity_id: str
    old: Optional[str]
    new: Optional[str]
    children: Optional[List['DiffNode']]


@cli.command(name="diff")
@click.argument(
    "root_crate", nargs=1, type=click.Path(exists=False, file_okay=True),
)
@click.argument(
    "new_crate", nargs=1, type=click.Path(exists=True, file_okay=True),
)
def diff(
        root_crate: str,
        new_crate: str,
):
    """
    Diff the RO-Crate metadata between the existing root crate and the new crate, showing changes if the new crate is merged.

    ROOT-CRATE: Path to the root RO-Crate metadata file (local path or S3 URI, e.g., s3://bucket/ro-crate-metadata.json). Requires AWS credentials for S3.
    NEW-CRATE: Path to the new RO-Crate metadata file.
    """
    original_crate = ROCrate.from_ro_crate_path(root_crate)
    draft_crate = ROCrate.from_ro_crate_path(root_crate)
    crate_changes = process_crate(crate_path=new_crate, output_crate=draft_crate)
    draft_crate.merge_ro_crate(crate_changes)

    diff_nodes = calculate_crate_diff(original_crate, draft_crate)

    for diff_node in diff_nodes:
        print_diff(diff_node)


def calculate_crate_diff(old_crate: ROCrate, new_crate: ROCrate) -> List[DiffNode]:
    """
    Compare two RO-Crates and return a list of DiffNode objects describing the differences.
    """
    diff_result: List[DiffNode] = []

    for new_dataset in new_crate.find_non_root_dataset_entity():
        dataset_diffs = []
        dataset_id = new_dataset.get('@id')
        old_dataset = old_crate.find_entity_by_id(dataset_id)

        # Find collections in the new dataset
        new_collections = new_crate.find_entities_by_has_part(new_dataset.get("hasPart", []))

        for new_collection in new_collections:
            collection_diffs = []

            new_collection_id = new_collection.get('@id')
            old_collection = old_crate.find_entity_by_id(new_collection_id)
            new_files = new_crate.find_entities_by_has_part(new_collection.get("hasPart", []))

            if old_collection is None:
                # Entire collection is new
                for file_entity in new_files:
                    collection_diffs.append(DiffNode(
                        change_type="added",
                        entity_type="File",
                        entity_id=file_entity.get('identifier'),
                        old=None,
                        new=file_entity.get('@id'),
                        children=None
                    ))
            else:
                # Compare files in the collection
                old_files = old_crate.find_entities_by_has_part(old_collection.get("hasPart", []))

                # Map: filename (identifier) -> full @id
                new_file_map = {f.get('identifier'): f.get('@id') for f in new_files}
                old_file_map = {f.get('identifier'): f.get('@id') for f in old_files}

                new_filenames = set(new_file_map.keys())
                old_filenames = set(old_file_map.keys())

                added_filenames = new_filenames - old_filenames
                common_filenames = new_filenames & old_filenames

                for filename in added_filenames:
                    collection_diffs.append(DiffNode(
                        change_type="added",
                        entity_type="File",
                        entity_id=filename,
                        old=None,
                        new=new_file_map[filename],
                        children=None
                    ))

                for filename in common_filenames:
                    if old_file_map[filename] == new_file_map[filename]:
                        continue  # No change

                    collection_diffs.append(DiffNode(
                        change_type="modified",
                        entity_type="File",
                        entity_id=filename,
                        old=old_file_map[filename],
                        new=new_file_map[filename],
                        children=None
                    ))

            if collection_diffs:
                collection_id_changed = old_collection is not None and (new_collection_id != old_collection.get('@id'))
                collection_diff_node = DiffNode(
                    change_type="modified" if old_collection else "added",
                    entity_type="Collection",
                    entity_id=new_collection_id,
                    old=old_collection.get('@id') if collection_id_changed else None,
                    new=new_collection_id if collection_id_changed else None,
                    children=collection_diffs
                )
                dataset_diffs.append(collection_diff_node)

        if dataset_diffs:
            dataset_id_changed = old_dataset is not None and (dataset_id != old_dataset.get('@id'))
            dataset_diff_node = DiffNode(
                change_type="modified" if old_dataset else "added",
                entity_type="Dataset",
                entity_id=dataset_id,
                old=old_dataset.get('@id') if dataset_id_changed else None,
                new=dataset_id if dataset_id_changed else None,
                children=dataset_diffs
            )
            diff_result.append(dataset_diff_node)

    return diff_result


def print_diff(node: DiffNode, indent: int = 0):
    prefix = " " * indent
    change_type = str(node.get("change_type", None))
    entity_type = node.get("entity_type", "Entity")
    entity_id = node.get("entity_id")
    old_value = node.get("old")
    new_value = node.get("new")
    children = node.get("children", [])

    if change_type == "modified":
        click.secho(f"{prefix} └─ [~] {entity_type} - {entity_id}:", fg="yellow")
    elif change_type == "added":
        click.secho(f"{prefix} └─ [+] {entity_type} - {entity_id}:", fg="green")
    elif change_type == "removed":
        raise NotImplementedError("TODO: handle removed entities in diff output")

    if old_value is not None:
        click.secho(f"{prefix}     ├─ [-] {old_value}", fg="red")
    if new_value is not None:
        click.secho(f"{prefix}     └─ [+] {new_value}", fg="green")

    for child in children or []:
        print_diff(child, indent=indent + 4)
