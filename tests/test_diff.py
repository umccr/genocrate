import os
import json
from genocrate.commands.diff import calculate_crate_diff
from genocrate.crate.merger import process_crate
from genocrate.crate.rocrate import ROCrate


def test_diff_crate():
    """
    Test 'diff' command is picking up the changes correctly
    """
    current_dir = os.path.dirname(__file__)
    root_crate = os.path.join(current_dir, "./fixtures/test-batches/ro-crate-metadata.json")
    new_crate = os.path.join(current_dir, "./fixtures/batch-004/data/ro-crate-metadata.json")

    original_crate = ROCrate.from_ro_crate_path(root_crate)
    draft_crate = ROCrate.from_ro_crate_path(root_crate)
    crate_changes = process_crate(crate_path=new_crate, output_crate=draft_crate)
    draft_crate.merge_ro_crate(crate_changes)

    diff_nodes = calculate_crate_diff(original_crate, draft_crate)

    a001 = find_id(diff_nodes, "#A001")
    assert diff_nodes is not None, "A001 dataset not found in diff"
    assert a001['change_type'] == 'modified', "A001 dataset should be marked as modified"

    # assert A001-bam
    a001_bam = find_id(a001['children'], "#A001-bam")
    assert a001_bam is not None, "A001-bam dataset not found in A001"
    assert a001_bam['change_type'] == 'modified', "A001-bam should be marked as added"
    a001_bam_file = find_id(a001_bam['children'], "A001.bam")
    assert a001_bam_file is not None, "A001.bam dataset not found in A001"
    a001_bai_file = find_id(a001_bam['children'], "A001.bam.bai")
    assert a001_bai_file is not None, "A001.bam.bai dataset not found in A001"

    # assert A001-vcf
    a001_vcf = find_id(a001['children'], "#A001-vcf")
    assert a001_vcf is not None, "A001-vcf dataset not found in A001"
    assert a001_vcf['change_type'] == 'modified', "A001-vcf should be marked as modified"
    a001_vcf_file = find_id(a001_vcf['children'], "A001.vcf")
    assert a001_vcf_file is not None, "A001.vcf dataset not found in A001"


def find_id(list_of_dicts, target_id):
    for d in list_of_dicts:
        if d.get('entity_id') == target_id:
            return d
    return None
