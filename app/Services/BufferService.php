<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use InvalidArgumentException;

class BufferService
{
    public function generate(string $releaseId, string $runId, string $codeRevision, bool $lockRelease = true): array
    {
        if ($runId === '' || $codeRevision === '') {
            throw new InvalidArgumentException('Explicit analysis run identity and code revision required.');
        }

        return DB::transaction(function () use ($releaseId, $runId, $codeRevision, $lockRelease): array {
            $release = DB::selectOne('SELECT id,input_revision,boundary_set_id FROM gis.dataset_releases WHERE id=?'.($lockRelease ? ' FOR SHARE' : ''), [$releaseId]);
            if ($release === null) {
                throw new InvalidArgumentException('Unknown candidate release.');
            }
            $rows = DB::select(file_get_contents(base_path('scripts/analysis/sql/buffers.sql')), [$releaseId]);
            $features = [];
            $excluded = [];
            $registered = [];
            $inputs = [];
            foreach ($rows as $row) {
                $registered[$row->facility_code] = true;
                $inputs[$row->facility_code] = [$row->facility_code, $row->longitude, $row->latitude, $row->selected_review_id, $row->coordinate_source_id, $row->exclusion_reason, $row->review_hash];
                if ($row->exclusion_reason !== null) {
                    $excluded[$row->facility_code] = ['facility_code' => $row->facility_code, 'reason' => $row->exclusion_reason];

                    continue;
                }
                $features[] = ['type' => 'Feature', 'properties' => [
                    'facility_code' => $row->facility_code, 'radius_m' => (int) $row->radius_m, 'release_id' => $releaseId,
                    'selected_review_id' => $row->selected_review_id, 'coordinate_source_id' => $row->coordinate_source_id,
                ], 'geometry' => json_decode($row->geometry, true, 512, JSON_THROW_ON_ERROR)];
            }

            return [
                'type' => 'FeatureCollection', 'status' => 'candidate_artifact', 'release_id' => $releaseId,
                'analysis_run_id' => $runId, 'input_revision' => (int) $release->input_revision, 'code_revision' => $codeRevision,
                'boundary_set_id' => $release->boundary_set_id,
                'input_hash' => hash('sha256', json_encode([$release, $inputs], JSON_THROW_ON_ERROR)),
                'method_version' => 'postgis-geography-buffer-v1',
                'parameters' => ['radii_m' => [1000, 3000, 5000], 'quad_segs' => 32, 'storage_crs' => 'EPSG:4326', 'distance_unit' => 'metre'],
                'versions' => ['postgis' => DB::selectOne('SELECT extensions.PostGIS_Full_Version() AS version')->version],
                'registered_count' => count($registered), 'eligible_count' => count($registered) - count($excluded),
                'excluded_count' => count($excluded), 'excluded' => array_values($excluded), 'features' => $features,
                'limitations' => ['Straight-line distance, not travel time or routes', 'Facilities outside the province are not included'],
            ];
        });
    }
}
