# Genocrate Batch Submission Profile

This profile defines the structure and requirements for a **batch submission RO Crate** used to package genomic data for research studies. It is designed to ensure that each batch of genomic files is consistently described, grouped, and validated.

## Purpose

The Genocrate Batch Submission Profile specializes the RO Crate standard for genomic batch submissions. It organizes
files by artifact type and links artifact groups to its identifiers.

## Key Concepts

- **Batch Submission**: Represents a set of genomic files generated or transferred together, typically for one or more participants.
- **Artifact Grouping**: Files are grouped by artifact type (e.g., BAM, VCF, FASTQ) and associated with participant identifiers.
- **Validation**: The profile includes constraints to ensure files are properly described, referenced, and packaged
  according to the RO-Crate profile.

## Structure Overview

The profile is described in [`ro-crate-metadata.json`](./ro-crate-metadata.json), which includes:

- **Context**: Specifies the RO Crate 1.2 context for metadata standardization.
- **Root Dataset**: Defines the main dataset entity representing the batch submission.
- **Constraints**: Includes rules for organizing datasets, grouping artifacts, listing files, and ensuring BagIt packaging compliance.
- **License**: Details the dataset's license information, which may be provided as a string or a reference.
- **Example**: Offers a sample RO Crate structure to illustrate expected organization and metadata.

## Main Entities and Rules

| Entity / Rule       | Description                                                                                                                                                                         |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Root Dataset        | Must use `hasPart` to reference at least one Dataset entity (see `#unique-dataset-rule`).                                                                                           |
| Identifier Dataset  | Each Dataset must include an `identifier` and reference at least one Collection entity.                                                                                             |
| Artifact Collection | Collections group related artifacts and must reference one or more File entities within the same category.                                                                          |
| File Requirement    | Each file entity must have `@type: File` and an identifier (typically the filename). Whether a file is listed in a parent’s `hasPart` property depends on the crate’s organization. |
| Use BAG IT Format   | Submissions should follow the BagIt specification for reliable packaging and transfer, or alternatively use regular md5 checksum files.                                             |
| Hierarchy Guide     | Describes the data hierarchy: Root Dataset → Dataset → Collection → File.                                                                                                           |

## Example Structure

```text
batch-001/
├── bag-info.txt
├── bagit.txt
├── data
│   ├── sample1.bam
│   ├── sample1.vcf
│   └── ro-crate-metadata.json
├── manifest-md5.txt
└── tagmanifest-md5.txt
```
