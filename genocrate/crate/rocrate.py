import json
import copy
import os

from typing import Optional, Any


class ROCrate:
    def __init__(
            self,
            context: Optional[str] = "https://w3id.org/ro/crate/1.2/context",
            graph: Optional[list] = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            date_published: Optional[str] = None,
            publisher: Optional[str] = None,
            license_: Optional[str] = None,
            output_path: Optional[str] = None):

        if graph is None:
            graph = self._create_minimal_valid_graph()
        if output_path:
            self.output_path = output_path

        self.context = context
        self.graph = graph

        root = self.find_entity_by_id('./')
        if name:
            root['name'] = name
        if description:
            root['description'] = description
        if date_published:
            root['datePublished'] = date_published
        if publisher:
            root['publisher'] = {"@id": publisher}
        if license_:
            root['license'] = license_

    @staticmethod
    def _create_minimal_valid_graph() -> list:
        """Create minimal valid RO-Crate structure per specification."""
        return [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.2"},
                "about": {"@id": "./"}
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "hasPart": []
            }
        ]

    @classmethod
    def from_ro_crate_path(cls, crate_path: str) -> "ROCrate":
        """Read and validate RO-Crate metadata file."""
        with open(crate_path, 'r') as f:
            data = json.load(f)

        if '@context' not in data:
            raise ValueError(f"Invalid RO-Crate at {crate_path}: Missing '@context' key")

        if '@graph' not in data:
            raise ValueError(f"Invalid RO-Crate at {crate_path}: Missing '@graph' key")

        return cls(context=data['@context'], graph=data['@graph'])

    def find_entity_by_id(self, entity_id: str) -> dict[str, Any] | None:
        """Find a single entity by its @id."""
        for entity in self.graph:
            if entity.get('@id') == entity_id:
                return entity
        return None

    def find_non_root_dataset_entity(self) -> list[dict[str, Any]]:
        """Find all Dataset entities that are not the root dataset ('./')."""
        matching_entities = []

        for entity in self.graph:
            entity_type = entity.get('@type')
            entity_id = entity.get('@id')

            if entity_type == 'Dataset' and entity_id != './':
                matching_entities.append(entity)

        return matching_entities

    def find_entities_by_has_part(
            self,
            has_part_list: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        """Find all entities referenced by a hasPart list."""
        result = []

        for has_part_entry in has_part_list:
            entity_id = has_part_entry.get('@id')

            if entity_id:
                entity = self.find_entity_by_id(entity_id)
                if entity:
                    result.append(entity)

        return result

    def add_new_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        """Add a new entity to the RO-Crate graph."""

        new_entity_id = entity.get('@id')

        if self.find_entity_by_id(new_entity_id) is not None:
            raise ValueError(f"Entity with id '{new_entity_id}' already exists")

        entity = copy.deepcopy(entity)
        self.graph.append(copy.deepcopy(entity))
        return entity

    def upsert_has_part_id_to_entity(self, entity_id: str, new_has_part_id: str) -> None:
        """update or insert has_part to include new {"@id"}"""

        entity = self.find_entity_by_id(entity_id)

        if entity is None:
            raise ValueError(f"Entity with id '{entity_id}' does not exist")

        all_has_part_id = [entry["@id"] for entry in entity.get('hasPart', [])]
        unique_id = sorted(list(set(all_has_part_id + [new_has_part_id])))
        entity['hasPart'] = [{"@id": x} for x in unique_id]

    def remove_orphan_files(self) -> None:
        """Remove file entities that are not referenced by any collection's hasPart."""

        referenced_file_ids = set()

        # Collect all referenced file IDs from collections
        for entity in self.graph:
            if entity.get('@type') == 'Collection':
                has_part_list = entity.get('hasPart', [])
                for has_part_entry in has_part_list:
                    referenced_file_ids.add(has_part_entry.get('@id'))

        # Filter out unreferenced file entities
        self.graph = [
            entity for entity in self.graph
            if not (entity.get('@type') == 'File' and entity.get('@id') not in referenced_file_ids)
        ]

    def merge_ro_crate(self, other_crate: "ROCrate") -> None:
        """Merge another RO-Crate into this one."""

        for entity in other_crate.graph:
            entity_id = entity.get('@id')

            # sub-crate root dataset doesn't get merged
            if entity_id == './':
                continue

            # Find index by matching @id
            existing_index = next(
                (i for i, e in enumerate(self.graph) if e.get('@id') == entity_id),
                None
            )

            if existing_index is None:
                self.graph.append(copy.deepcopy(entity))
            else:
                # Override: replace existing entity at found index
                self.graph[existing_index] = copy.deepcopy(entity)

            # Make sure that if the entity is a Dataset, it is linked to the root dataset
            entity_type = entity.get('@type')
            if entity_type == 'Dataset':
                self.upsert_has_part_id_to_entity('./', entity_id)

        self.remove_orphan_files()

    def to_file(self) -> None:
        """Write RO-Crate metadata to a file."""
        if self.output_path is None:
            raise ValueError("Output path is not set for ROCrate")

        data = {
            '@context': self.context,
            '@graph': self.graph
        }
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(data, f, indent=2)
