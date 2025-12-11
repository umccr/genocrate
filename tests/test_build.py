from click.testing import CliRunner
from genocrate.main import cli
from genocrate.crate.rocrate import ROCrate
import os


def test_build_root_ro_crate():
    """
    Validates that the 'build' command generates a correct RO-Crate
    """
    runner = CliRunner()
    output_path = "./output/ro-crate-metadata.json"
    output_preview_path = "./output/ro-crate-preview.html"
    batch_dir = "./tests/fixtures/test-batches/"

    result = runner.invoke(
        cli,
        [
            "build",
            batch_dir,
            "--name", "test-dataset",
            "--description", "A test dataset",
            "-o", output_path
        ]
    )
    assert result.exit_code == 0, f"CLI exited with code {result.exit_code}: {result.output}"

    ro_crate = ROCrate.from_ro_crate_path(output_path)

    # Check uniqueness of @id values
    entity_ids = [entity.get('@id') for entity in ro_crate.graph if '@id' in entity]
    assert len(entity_ids) == len(set(entity_ids)), "Duplicate @id values found in RO-Crate graph"

    # Check A001 fastq links
    a001_fastq = ro_crate.find_entity_by_id("#A001-fastq")
    expected_a001_fastqs = {
        f"{batch_dir}batch-002/data/A001_R1.fastq",
        f"{batch_dir}batch-002/data/A001_R2.fastq"
    }
    actual_a001_fastqs = {item["@id"] for item in a001_fastq.get("hasPart", [])}
    assert actual_a001_fastqs == expected_a001_fastqs, f"A001 fastq hasPart mismatch: {actual_a001_fastqs} != {expected_a001_fastqs}"

    # check if A002 fastq is complete where the R1 in batch-002 and R2 in batch-003
    a002_fastq = ro_crate.find_entity_by_id("#A002-fastq")
    expected_a002_fastqs = {
        f"{batch_dir}batch-002/data/A002_R1.fastq",
        f"{batch_dir}batch-003/data/A002_R2.fastq"
    }
    actual_a002_fastqs = {item["@id"] for item in a002_fastq.get("hasPart", [])}
    assert actual_a002_fastqs == expected_a002_fastqs, f"A002 fastq hasPart mismatch: {actual_a002_fastqs} != {expected_a002_fastqs}"

    # Check if A002 bam is replaced with the one in batch-003
    a002_bam = ro_crate.find_entity_by_id("#A002-bam")
    expected_a002_bams = {
        f"{batch_dir}batch-003/data/A002.bam",
        f"{batch_dir}batch-003/data/A002.bam.bai"
    }
    actual_a002_bams = {item["@id"] for item in a002_bam.get("hasPart", [])}
    assert actual_a002_bams == expected_a002_bams, f"A002 bam hasPart mismatch: {actual_a002_bams} != {expected_a002_bams}"

    # check if old A002.bam and A002.bam.bai from batch-002 are removed
    removed_bam = ro_crate.find_entity_by_id(f"{batch_dir}batch-002/data/A002.bam")
    assert removed_bam is None, "Old A002.bam file from batch-002 should have been removed"
    removed_bam_bai = ro_crate.find_entity_by_id(f"{batch_dir}batch-002/data/A002.bam.bai")
    assert removed_bam_bai is None, "Old A002.bam.bai file from batch-002 should have been removed"

    # clean up output file
    output_dir = os.path.dirname(output_path)
    if os.path.isdir(output_dir):
        if os.path.exists(output_path):
            os.remove(output_path)
        if os.path.exists(output_preview_path):
            os.remove(output_preview_path)
        os.rmdir(output_dir)
