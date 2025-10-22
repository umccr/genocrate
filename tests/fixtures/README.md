This directory contains test fixtures for RO-Crate and BagIt validation.

- `test-batches/batch-001`, `batch-002`, `batch-003`: Used to test generating a root RO-Crate that summarizes datasets across multiple batches.
- `test-batches/ro-crate-metadata.json`: Example of a root RO-Crate metadata file summarizing the batches.
- `batch-004`: Used to test validation of broken RO-Crates.

Directory layout:

./tests/fixtures
├── README.md
├── batch-004
└── test-batches
    ├── batch-001
    ├── batch-002
    ├── batch-003
    └── ro-crate-metadata.json

