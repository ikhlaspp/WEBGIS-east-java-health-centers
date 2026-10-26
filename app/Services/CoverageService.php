<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use RuntimeException;

class CoverageService
{
    public function __construct(private BufferService $buffers) {}

    public function generate(string $releaseId, string $runId, string $codeRevision, bool $lockRelease = true): array
    {
        return DB::transaction(function () use ($releaseId, $runId, $codeRevision, $lockRelease): array {
            $buffer = $this->buffers->generate($releaseId, $runId, $codeRevision, $lockRelease);
            $excluded = array_column($buffer['excluded'], 'reason', 'facility_code');
            $counts = [];
            foreach (DB::table('gis.facility_snapshots')->where('release_id', $releaseId)->get(['facility_code', 'district_id']) as $facility) {
                $counts[$facility->district_id] ??= ['registered_count' => 0, 'eligible_count' => 0, 'excluded_count' => 0, 'exclusion_reasons' => []];
                $counts[$facility->district_id]['registered_count']++;
                if (isset($excluded[$facility->facility_code])) {
                    $counts[$facility->district_id]['excluded_count']++;
                    $reason = $excluded[$facility->facility_code];
                    $counts[$facility->district_id]['exclusion_reasons'][$reason] = ($counts[$facility->district_id]['exclusion_reasons'][$reason] ?? 0) + 1;
                } else {
                    $counts[$facility->district_id]['eligible_count']++;
                }
            }
            $rows = DB::select(file_get_contents(base_path('scripts/analysis/sql/coverage.sql')), [json_encode($buffer['features'], JSON_THROW_ON_ERROR), $releaseId]);
            $results = [];
            $previous = [];
            $hashes = [];
            foreach ($rows as $row) {
                $denominator = (float) $row->geometry_area_m2;
                $numerator = (float) $row->covered_area_m2;
                if (! is_finite($denominator) || $denominator <= 0 || ! is_finite($numerator) || $numerator < 0) {
                    throw new RuntimeException('Invalid geodesic coverage area.');
                }
                $percentage = $numerator / $denominator * 100;
                if ($numerator > $denominator + 1 || $percentage > 100 + 1e-8 || $numerator + 1 < ($previous[$row->district_id] ?? 0)) {
                    throw new RuntimeException('Coverage exceeds the frozen area/percentage/monotonicity tolerance.');
                }
                $previous[$row->district_id] = $numerator;
                $available = $buffer['eligible_count'] > 0;
                $hashes[$row->district_id] = $row->geometry_hash;
                $results[] = [
                    'district_id' => $row->district_id, 'radius_m' => (int) $row->radius_m,
                    'covered_area_m2' => $available ? min($numerator, $denominator) : null,
                    'geometry_area_m2' => $available ? $denominator : null,
                    'coverage_pct' => $available ? min($percentage, 100) : null,
                    'geometry' => $available && $row->geometry !== null ? json_decode($row->geometry, true, 512, JSON_THROW_ON_ERROR) : null,
                    ...($counts[$row->district_id] ?? ['registered_count' => 0, 'eligible_count' => 0, 'excluded_count' => 0, 'exclusion_reasons' => []]),
                    'contributing_count' => (int) $row->contributing_count,
                    'completeness' => ! $available ? 'unavailable' : ($buffer['excluded_count'] > 0 ? 'partial' : 'complete'),
                    'reason' => ! $available ? 'no_eligible_points' : ($buffer['excluded_count'] > 0 ? 'excluded_locations_in_dataset' : ''),
                    'numeric_adjustment_m2' => max(0, $numerator - $denominator),
                ];
            }
            unset($buffer['features']);

            return [...$buffer, 'buffer_method_version' => $buffer['method_version'], 'method_version' => 'postgis-union-clip-geodesic-v1', 'boundary_hash' => hash('sha256', json_encode($hashes, JSON_THROW_ON_ERROR)), 'results' => $results];
        });
    }
}
