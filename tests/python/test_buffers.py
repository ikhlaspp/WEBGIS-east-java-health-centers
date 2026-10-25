import copy
import math

import pytest

from gis_pipeline.analysis.buffers import GEOD, RADII, build_buffers, eligibility, radius_check, reference_buffer


def facility(lon=112, lat=-7):
    review = {'review_id': 'review-fixture', 'release_id': 'release-fixture', 'facility_code': '35010100001',
              'source_id': 'source-fixture', 'candidate_lon': lon, 'candidate_lat': lat,
              'result_status': 'accepted', 'precision_level': 'facility', 'centroid_candidate': False,
              'reviewer_id': 'synthetic-reviewer', 'reviewed_at': '2026-01-01T00:00:00Z',
              'decision_reason': 'Synthetic accepted point for testing only', 'evidence_url': 'https://example.test/synthetic'}
    return {'release_id': 'release-fixture', 'facility_code': '35010100001', 'coordinate_status': 'verified',
            'precision_level': 'facility', 'coordinate_source_id': 'source-fixture', 'selected_review_id': 'review-fixture',
            'longitude': lon, 'latitude': lat, 'review': review}


@pytest.mark.parametrize('longitude,latitude', [(112, -7), (113.2, -7), (112.7, -5.8), (115.6, -6.8)])
@pytest.mark.parametrize('radius', RADII)
def test_mainland_madura_bawean_and_remote_island_radius(longitude, latitude, radius):
    polygon = reference_buffer(longitude, latitude, radius)
    check = radius_check(longitude, latitude, polygon, radius)
    assert check['vertices'] == 128
    assert check['midpoints'] == 128
    assert check['max_error_m'] <= max(2, 0.01 * radius)
    area, _ = GEOD.geometry_area_perimeter(polygon)
    assert abs(abs(area) - math.pi * radius**2) <= 0.01 * math.pi * radius**2


@pytest.mark.parametrize('change', ['unverified', 'centroid', 'no_review', 'wrong_source', 'wrong_release', 'wrong_facility', 'wrong_point', 'pending', 'no_evidence', 'no_reviewer', 'missing', 'invalid'])
def test_unverified_or_mismatched_evidence_never_becomes_eligible(change):
    row = facility()
    if change == 'unverified':
        row['coordinate_status'] = 'unverified'
    elif change == 'centroid':
        row['review']['centroid_candidate'] = True
    elif change == 'no_review':
        row['review'] = None
    elif change == 'wrong_source':
        row['review']['source_id'] = 'other'
    elif change == 'wrong_release':
        row['review']['release_id'] = 'other'
    elif change == 'wrong_facility':
        row['review']['facility_code'] = '35010100002'
    elif change == 'wrong_point':
        row['review']['candidate_lon'] += 0.1
    elif change == 'pending':
        row['review']['result_status'] = 'pending'
    elif change == 'no_evidence':
        row['review']['evidence_url'] = None
    elif change == 'no_reviewer':
        row['review']['reviewer_id'] = None
    elif change == 'missing':
        row['longitude'] = row['latitude'] = None
    else:
        row['longitude'] = float('nan')
    assert eligibility(row, 'release-fixture') is not None


def test_snapshot_keeps_every_excluded_identity_and_parameter():
    accepted = facility()
    missing = copy.deepcopy(accepted)
    missing['facility_code'] = '35010100002'
    missing['coordinate_status'] = 'missing'
    document = {'release_id': 'release-fixture', 'analysis_run_id': 'run-fixture', 'code_revision': 'fixture', 'facilities': [accepted, missing]}
    result = build_buffers(document, 'a' * 64)
    assert result['registered_count'] == 2
    assert result['eligible_count'] == 1
    assert result['excluded_count'] == 1
    assert result['excluded'] == [{'facility_code': '35010100002', 'reason': 'not_verified'}]
    assert len(result['features']) == 3
    assert result['parameters']['radii_m'] == [1000, 3000, 5000]
    assert result['input_hash'] == 'a' * 64
    assert result['status'] == 'candidate_artifact'


def test_duplicate_or_mixed_release_snapshot_is_rejected():
    row = facility()
    document = {'release_id': 'release-fixture', 'analysis_run_id': 'run-fixture', 'code_revision': 'fixture', 'facilities': [row, row]}
    with pytest.raises(ValueError, match='duplicate'):
        build_buffers(document, 'a' * 64)
    document['facilities'] = [row]
    row['release_id'] = 'other'
    with pytest.raises(ValueError, match='Mixed release'):
        build_buffers(document, 'a' * 64)


@pytest.mark.parametrize('radius', [0, 1, 1000.0, True, 2000, -1000])
def test_only_frozen_metric_radii_are_allowed(radius):
    with pytest.raises(ValueError):
        reference_buffer(112, -7, radius)


def test_no_eligible_points_is_an_explicit_empty_artifact():
    row = facility()
    row['coordinate_status'] = 'unverified'
    result = build_buffers({'release_id': 'release-fixture', 'analysis_run_id': 'run-fixture', 'code_revision': 'fixture', 'facilities': [row]}, 'a' * 64)
    assert result['features'] == []
    assert result['registered_count'] == result['excluded_count'] == 1
    assert result['eligible_count'] == 0
