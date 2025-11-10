from click.testing import CliRunner
from genocrate.main import cli
from genocrate.crate.rocrate import ROCrate


def test_csv2crate():
    """
    Test for csv2crate command success
    """
    test_dir = "./tests/fixtures/batch-005/data/"

    runner = CliRunner()
    result = runner.invoke(cli, ["csv2crate", f"{test_dir}manifest.txt"])
    assert result.exit_code == 0


    # read the output crate
    output_crate = ROCrate.from_ro_crate_path(f"{test_dir}ro-crate-metadata.json")

    entities = {e['@id']: e for e in output_crate.graph}

    # Test all expected entities exist
    expected_entities = [
        ('./', 'Dataset'),
        ('#A001', 'Dataset'),
        ('#A001-bam', 'Collection'),
        ('#A001-vcf', 'Collection'),
        ('A001.bam', 'File'),
        ('A001.bam.bai', 'File'),
        ('A001.vcf', 'File'),
        ('A001.vcf.tbi', 'File'),
    ]

    for entity_id, entity_type in expected_entities:
        assert entity_id in entities, f"Missing entity: {entity_id}"
        assert entities[entity_id]['@type'] == entity_type