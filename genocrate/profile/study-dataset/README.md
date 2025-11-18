# Genocrate Study Dataset Profile

This profile defines the structure and requirements for a **study-level RO Crate** that summarizes and organizes genomic
datasets across multiple batch submissions. It is designed to aggregate genomic files and metadata from individual batch
submission RO Crates, providing a an overview of all data within a study dataset.

## Purpose

The Genocrate Study Dataset Profile specializes the RO Crate standard for genomic datasets. It enables researchers to aggregate multiple batch RO Crates, providing a unified overview and management of all genomic data within a study.

## Key Concepts

- **Study Dataset**: Represents the complete set of genomic data for a research study, composed of multiple batch submissions.
- **Batch Submission**: Each batch is described by its own RO Crate, conforming to the batch submission profile.
- **Hierarchy**: Data is organized in a hierarchy—Root Dataset → Dataset → Collection → File.
- **Constraints**: Rules ensure proper structure, uniqueness, artifact grouping, and history tracking.

## Structure Overview

The profile is described in [`ro-crate-metadata.json`](./ro-crate-metadata.json), which includes:

- **Context**: Specifies the RO Crate 1.2 context for metadata standardization.
- **Root Dataset**: Defines the main dataset entity representing the study.
- **Constraints**: Includes rules for organizing datasets, enforcing uniqueness, grouping artifacts, tracking update history, and listing files.
- **License**: Details the dataset's license information, which may be provided as a string or a reference.
- **Example**: Offers a sample RO Crate structure to illustrate expected organization and metadata.

## Main Entities and Rules

| Entity / Rule                | Description                                                                                   |
|------------------------------|----------------------------------------------------------------------------------------------|
| Root Dataset                 | Must use `hasPart` to reference one or more unique Dataset entities (see `#unique-dataset-rule`). |
| Identifier Dataset           | Each Dataset must have an `identifier`, reference at least one Collection, and mention update history entities. |
| Dataset History              | Each history entity records the type of change, result, summary, end time, and action status for each batch update. |
| Artifact Collection          | Collections group related artifacts and must reference one or more File entities within the same category. |
| File Requirement             | Only files specifically referenced from individual batch RO Crates are included, not all files present in the study directory. |
| Hierarchy Guide              | Describes the data hierarchy: Root Dataset → Dataset → Collection → File.                    |

## Example Structure

```text
study-dataset/
├── ro-crate-metadata.json
├── ro-crate-preview.html
├── batch-001/
│   └── ro-crate-metadata.json
├── batch-002/
│   └── ro-crate-metadata.json
└── ...
```
