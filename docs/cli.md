# CLI Commands

- `validate-batch`
- `build`
- `diff`
- `csv2genocrate`
- `validate-dataset`

---

## `validate-batch`

```
Usage: genocrate [OPTIONS] PATH

  Validate a batch of files or bags for BagIt or MD5 compliance.

Options:
  -t, --validation-type [bagit|md5]
                                  Type of validation to perform
  -p, --parallel INTEGER          Number of processes to run in parallel
  --skip-integrity-validation     Skip integrity validation and only validate
                                  RO-Crate metadata
  --data-folder TEXT              The folder where the data files are located.
                                  Defaults to 'data'
  --help                          Show this message and exit.
```

## `build`

```
Usage: genocrate [OPTIONS] PATH

  Build a batch of RO-Crate files.

  PATH: Directory containing one or more ro-crate-metadata.json files.

Options:
  -o, --output-path TEXT  Path to the output RO-Crate metadata file (local
                          path or S3 URI, e.g., s3://bucket/ro-crate-
                          metadata.json). Requires AWS credentials for S3.
  --no-preview            Skip the generation of an HTML preview file. (ro-
                          crate-preview.html)
  --name TEXT             Dataset name  [required]
  --description TEXT      Dataset description  [required]
  --date-published TEXT   Publication date (YYYY-MM-DD)
  --publisher TEXT        Publisher ROR ID (e.g., https://ror.org/...)
  --license TEXT          License for the dataset (textual description of how
                          the RO-Crate may be used)
  --help                  Show this message and exit.
```

## `diff`

```
Usage: genocrate [OPTIONS] ROOT_CRATE NEW_CRATE

  Diff the RO-Crate metadata between the existing root crate and the new
  crate, showing changes if the new crate is merged.

  ROOT-CRATE: Path to the root RO-Crate metadata file (local path or S3 URI,
  e.g., s3://bucket/ro-crate-metadata.json). Requires AWS credentials for S3.
  NEW-CRATE: Path to the new RO-Crate metadata file.

Options:
  --help  Show this message and exit.
```

## `csv2genocrate`

```
Usage: genocrate [OPTIONS] CSV_PATH

  Convert a CSV manifest file to an RO-Crate.

  The manifest must contain columns: filename, identifier, md5 checksum

Options:
  --filename-column TEXT       The csv column header for the filename within
                               the manifest (default: 'filename')
  --identifier-column TEXT     The csv column header for the identifier within
                               the manifest (default: 'identifier')
  --checksum-column TEXT       The checksum column header for the filename
                               within the manifest (default: 'checksum')
  --skip-crate-validation      Skip crate validation after is being created
  --skip-integrity-validation  Skip integrity validation
  --help                       Show this message and exit.
```

## `validate-dataset`

```
Usage: genocrate [OPTIONS] DIRECTORY

  Validate RO Crate for the study-dataset profile compliance.

  :param directory: The directory containing the RO-Crate file (ro-crate-
  metadata.json)

Options:
  --help  Show this message and exit.
```

