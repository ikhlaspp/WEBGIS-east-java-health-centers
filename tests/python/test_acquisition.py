import hashlib
import json

import pytest

from gis_pipeline.etl.acquire import checked_bytes, checked_document_bytes, freeze


def identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


@pytest.fixture
def inputs(tmp_path):
    (tmp_path / 'Archives').mkdir()
    (tmp_path / 'Archives/table.csv').write_bytes(b'name,value\nA,1\n')
    inventory = json.dumps({'files': [{'path': 'Archives/table.csv', **identity(b'name,value\nA,1\n')}]}).encode()
    (tmp_path / 'inventory.json').write_bytes(inventory)
    (tmp_path / 'data/raw/official').mkdir(parents=True)
    (tmp_path / 'data/raw/official/source.bin').write_bytes(b'{"rows":[1]}')
    plan = {'archive_inventory': 'inventory.json', 'archive_inventory_identity': identity(inventory),
            'expected_archive_files': 1, 'expected_external_files': 1,
            'external_receipts': [{'source_id': 'official', 'edition': '2023',
                                   'source_url': 'https://example.org/table',
                                   'raw_path': 'data/raw/official/source.bin', **identity(b'{"rows":[1]}')}]}
    return tmp_path, plan


def test_freeze_preserves_original_and_reuses_content(inputs):
    root, plan = inputs
    first = freeze(root, plan, 'data/raw/manifest.json')
    second = freeze(root, plan, 'data/raw/manifest.json')
    assert first['availability_complete'] is True
    assert first['data_quality_accepted'] is False
    assert first['archive_files'] == first['external_files'] == 1
    assert first['plan_sha256'] == second['plan_sha256']
    assert [e['raw_path'] for e in first['files']] == [e['raw_path'] for e in second['files']]
    assert (root / 'Archives/table.csv').read_bytes() == b'name,value\nA,1\n'


@pytest.mark.parametrize('damage', ['changed', 'missing', 'extra', 'corrupt_download', 'duplicate', 'escape'])
def test_incomplete_or_unsafe_sources_never_publish_manifest(inputs, damage):
    root, plan = inputs
    if damage == 'changed':
        (root / 'Archives/table.csv').write_bytes(b'changed')
    elif damage == 'missing':
        (root / 'Archives/table.csv').unlink()
    elif damage == 'extra':
        (root / 'Archives/unexpected.csv').write_bytes(b'extra')
    elif damage == 'corrupt_download':
        (root / 'data/raw/official/source.bin').write_bytes(b'partial')
    elif damage == 'duplicate':
        plan['external_receipts'] *= 2
        plan['expected_external_files'] = 2
    else:
        plan['external_receipts'][0]['raw_path'] = '../outside.bin'
    with pytest.raises(ValueError):
        freeze(root, plan, 'data/raw/manifest.json')
    assert not (root / 'data/raw/manifest.json').exists()


def test_manifest_cannot_overwrite_archive(inputs):
    root, plan = inputs
    with pytest.raises(ValueError):
        freeze(root, plan, 'Archives/table.csv')


def test_git_newline_conversion_only_applies_to_repository_evidence(tmp_path):
    original = b'{\r\n  "version": 1\r\n}\r\n'
    path = tmp_path / 'evidence.json'
    path.write_bytes(original.replace(b'\r\n', b'\n'))
    assert checked_document_bytes(path, identity(original)) == original
    with pytest.raises(ValueError):
        checked_bytes(path, identity(original))
    path.write_bytes(b'{\n  "version": 2\n}\n')
    with pytest.raises(ValueError):
        checked_document_bytes(path, identity(original))
