# Test Fixtures

This directory contains test fixtures for RO-Crate and BagIt validation.

- `test-batches/batch-001`, `batch-002`, `batch-003`: Used to test generating a root RO-Crate that summarizes datasets across multiple batches.
- `test-batches/ro-crate-metadata.json`: Example of a root RO-Crate metadata file summarizing the batches.
- `batch-004`: Used to test validation of broken RO-Crates.

Directory layout:

```text
./tests/fixtures
├── README.md
├── batch-004
└── test-batches
    ├── batch-001
    ├── batch-002
    ├── batch-003
    └── ro-crate-metadata.json
```

## Summary of `test-batches` Fixture

- **batch-001**: Submits BAM and VCF files for study participant A001.
- **batch-002**:  
  - Submits FASTQ files for A001.
  - Submits BAM, VCF, and one FASTQ file for A002.
- **batch-003**:  
  - Submits missing FASTQ files for A002.
  - Replaces BAM file for A002.
  - Submits VCF, FASTQ, and BAM files for A003.
  