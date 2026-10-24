import copy
import io
import re
import zipfile

import pytest

from gis_pipeline.etl.boundaries import select_hdx_features
from gis_pipeline.etl.sources import RemoteZipReader


def historical_fixture():
    ring = [[0, 0], [1, 0], [1, 1], [0, 0]]
    features = []
    for code, name in [('3501010', 'Synthetic A'), ('3501020', 'Synthetic B'), ('3522888', 'Perairan')]:
        features.append({'type': 'Feature', 'properties': {
            'adm3_pcode': 'ID' + code, 'adm3_name': name, 'adm2_pcode': 'ID' + code[:4],
            'adm1_pcode': 'ID35', 'valid_on': '2020-04-01', 'version': 'v01'},
            'geometry': {'type': 'MultiPolygon', 'coordinates': [[ring], [[[2, 2], [3, 2], [3, 3], [2, 2]]]]}})
    return {'type': 'FeatureCollection', 'crs': {'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
            'features': features}, {'report': {'complete': True}, 'rows': [{'code': '3501010'}, {'code': '3501020'}]}


def test_historical_selection_preserves_islands_water_and_actual_date():
    collection, master = historical_fixture()
    original = copy.deepcopy(collection)
    result = select_hdx_features(collection, master)
    assert result['report']['districts'] == 2
    assert result['report']['excluded_water_objects'] == 1
    assert result['collection']['features'][0]['geometry'] == original['features'][0]['geometry']
    assert result['excluded'][0]['feature'] == original['features'][2]
    assert result['boundary_edition'] == '2020-04-01'
    assert not result['strict_2023_geometry_verified']
    assert not result['ready_for_public_release']
    assert collection == original


@pytest.mark.parametrize('mutation', [
    lambda c: c['features'].pop(0),
    lambda c: c['features'].append(copy.deepcopy(c['features'][0])),
    lambda c: c['features'][0]['properties'].update(valid_on='2026-06-01'),
    lambda c: c['features'][0]['properties'].update(adm2_pcode='ID3502'),
    lambda c: c['features'][2]['properties'].update(adm3_name='Unexpected district'),
    lambda c: c['features'][0].update(geometry=None),
])
def test_historical_mismatch_never_passes(mutation):
    collection, master = historical_fixture()
    mutation(collection)
    with pytest.raises(ValueError):
        select_hdx_features(collection, master)


class RangeResponse(io.BytesIO):
    def __init__(self, data, content_range, etag='synthetic-etag', status=206):
        super().__init__(data)
        self.headers = {'Content-Range': content_range, 'ETag': etag}
        self.status = status


def test_remote_zip_reads_only_selected_member_with_stable_ranges(monkeypatch):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('selected.json', '{"synthetic": true}')
        archive.writestr('unused.txt', 'unused')
    data = buffer.getvalue()
    monkeypatch.setattr('gis_pipeline.etl.sources.validate_url', lambda *args: None)
    class Opener:
        def open(self, request, timeout):
            start, end = map(int, re.fullmatch(r'bytes=(\d+)-(\d+)', request.get_header('Range')).groups())
            return RangeResponse(data[start:end + 1], f'bytes {start}-{end}/{len(data)}')
    reader = RemoteZipReader('https://example.test/archive.zip', len(data), {'example.test'}, Opener())
    with zipfile.ZipFile(reader) as archive:
        assert archive.read('selected.json') == b'{"synthetic": true}'
    assert reader.etag == 'synthetic-etag'


@pytest.mark.parametrize('fault', ['ignored_range', 'wrong_range', 'changed_etag', 'short_read'])
def test_remote_archive_rejects_inconsistent_responses(monkeypatch, fault):
    monkeypatch.setattr('gis_pipeline.etl.sources.validate_url', lambda *args: None)
    class Opener:
        def open(self, request, timeout):
            return RangeResponse(b'ab' if fault != 'short_read' else b'a',
                                 'bytes 0-1/10' if fault != 'wrong_range' else 'bytes 2-3/10',
                                 etag='changed' if fault == 'changed_etag' else 'original',
                                 status=200 if fault == 'ignored_range' else 206)
    reader = RemoteZipReader('https://example.test/archive.zip', 10, {'example.test'}, Opener())
    reader.etag = 'original'
    with pytest.raises(ValueError):
        reader.read(2)
