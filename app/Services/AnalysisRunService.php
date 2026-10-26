<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use RuntimeException;

class AnalysisRunService
{
    public function __construct(private CoverageService $coverage) {}

    public function prepare(string $releaseId, string $runId, int $threshold, string $codeRevision, bool $verifyFrozen = false): array
    {
        if ($threshold < 1 || ! Str::isUuid($runId) || ! preg_match('/^[0-9a-f]{40}$/D', $codeRevision)) {
            throw new InvalidArgumentException('A positive threshold, run UUID and code commit are required.');
        }

        return DB::transaction(function () use ($releaseId, $runId, $threshold, $codeRevision, $verifyFrozen): array {
            $release = DB::selectOne('SELECT id,boundary_set_id,input_revision,status,facility_period,population_policy,area_policy FROM gis.dataset_releases WHERE id=?'.($verifyFrozen ? '' : ' FOR SHARE'), [$releaseId]);
            if ($release === null || ! in_array($release->status, $verifyFrozen ? ['validated', 'published'] : ['draft'], true)) {
                throw new InvalidArgumentException($verifyFrozen ? 'Frozen verification requires a validated or published release.' : 'Analysis preparation requires a draft release.');
            }
            $coverage = $this->coverage->generate($releaseId, $runId, $codeRevision, ! $verifyFrozen);
            $records = DB::select(file_get_contents(base_path('scripts/analysis/sql/indicators.sql')), [$releaseId, $releaseId, $threshold]);
            if ($records === []) {
                throw new RuntimeException('Analysis requires a nonempty administrative master.');
            }
            $indicators = [];
            $boundaries = [];
            $sources = [];
            foreach ($records as $record) {
                $sourceIds = array_values(array_unique(array_filter([...json_decode($record->facility_sources, true, 512, JSON_THROW_ON_ERROR), $record->population_source_id, $record->area_source_id])));
                sort($sourceIds);
                $row = [
                    'district_id' => $record->district_id, 'code' => $record->code, 'parent_code' => $record->parent_code, 'name' => $record->name,
                    'population' => $record->population === null ? null : (int) $record->population,
                    'facility_count' => (int) $record->facility_count, 'area_km2' => $record->area_km2,
                    'density' => $record->density, 'population_per_facility' => $record->population_per_facility,
                    'facilities_per_30000' => $record->facilities_per_30000,
                    'indicative_need' => $record->indicative_need === null ? null : (int) $record->indicative_need,
                    'indicative_deficit' => $record->indicative_deficit === null ? null : (int) $record->indicative_deficit,
                    'without_facility' => $record->without_facility, 'source_ids' => $sourceIds,
                    'source_periods' => ['facilities' => $release->facility_period, 'population' => $record->population_year === null ? null : (string) $record->population_year, 'area' => $record->area_year === null ? null : (string) $record->area_year],
                ];
                $indicators[] = $row;
                $sources[] = array_intersect_key($row, array_flip(['district_id', 'code', 'population', 'facility_count', 'area_km2', 'source_ids', 'source_periods']));
                $boundaries[] = ['district_id' => $record->district_id, 'full' => json_decode($record->full_geometry, true, 512, JSON_THROW_ON_ERROR)];
            }

            return [
                'schema_version' => 'analysis-bundle-v1', 'release_id' => $releaseId, 'analysis_run_id' => $runId,
                'boundary_set_id' => $release->boundary_set_id, 'input_revision' => (int) $release->input_revision,
                'input_hash' => hash('sha256', json_encode([$coverage['input_hash'], $coverage['boundary_hash'], $sources], JSON_THROW_ON_ERROR)),
                'boundary_hash' => $coverage['boundary_hash'], 'method_version' => 'postgis-analysis-v1', 'code_revision' => $codeRevision,
                'parameters' => ['T' => $threshold, 'radii_m' => [1000, 3000, 5000], 'quad_segs' => 32, 'legend_version' => 'fixed-v1', 'buffer_method' => 'postgis-geography-buffer-v1', 'area_method' => 'WGS84-spheroid'],
                'source_periods' => ['facilities' => $release->facility_period, 'population_policy' => $release->population_policy, 'area_policy' => $release->area_policy],
                'eligibility_counts' => ['registered' => $coverage['registered_count'], 'eligible' => $coverage['eligible_count'], 'excluded' => $coverage['excluded_count']],
                'environment' => $coverage['versions'], 'warnings' => $coverage['limitations'],
                'indicators' => $indicators, 'boundaries' => $boundaries, 'coverage' => $coverage['results'],
            ];
        });
    }

    /** Trusted internal persistence; worker/runtime have no direct write grants. Operator entry points belong to the lifecycle service. */
    public function persist(array $prepared, string $actorId, string $relativeDirectory, #[\SensitiveParameter] ?string $operatorToken = null): array
    {
        return DB::transaction(function () use ($prepared, $actorId, $relativeDirectory, $operatorToken): array {
            $actor = $operatorToken === null
                ? DB::selectOne('SELECT id FROM app.users WHERE id=? AND is_admin AND is_active', [$actorId])
                : DB::selectOne("SELECT actor_id AS id FROM gis.operator_identity(?,'analyze')", [$operatorToken]);
            if ($actor === null || $actor->id !== $actorId) {
                throw new InvalidArgumentException('An active internal administrator is required.');
            }
            DB::selectOne('SELECT id FROM gis.dataset_releases WHERE id=? FOR UPDATE', [$prepared['release_id']]);
            $fresh = $this->prepare($prepared['release_id'], $prepared['analysis_run_id'], $prepared['parameters']['T'], $prepared['code_revision']);
            if ($prepared['input_hash'] !== $fresh['input_hash'] || $prepared['input_revision'] !== $fresh['input_revision']) {
                throw new RuntimeException('Analysis input changed after preparation.');
            }
            $parametersHash = hash('sha256', json_encode($fresh['parameters'], JSON_THROW_ON_ERROR));
            $key = hash('sha256', json_encode([$fresh['release_id'], $fresh['input_hash'], $fresh['method_version'], $fresh['code_revision'], $parametersHash], JSON_THROW_ON_ERROR));
            if ($operatorToken !== null) {
                $key = DB::selectOne('SELECT gis.analysis_identity(?::jsonb) AS identity', [json_encode($fresh, JSON_THROW_ON_ERROR)])->identity;
            }
            $existing = DB::table('gis.analysis_runs')->where('idempotency_key', $key)->first();
            if ($existing !== null) {
                if ($existing->status !== 'succeeded') {
                    throw new RuntimeException('Existing analysis identity is not successful.');
                }
                $replayed = $fresh;
                $replayed['analysis_run_id'] = $existing->id;
                $this->verifyArtifacts($replayed, 'analysis/'.$existing->id);

                return ['analysis_run_id' => $existing->id, 'status' => $existing->status, 'replayed' => true];
            }
            $manifest = $this->verifyArtifacts($fresh, $relativeDirectory);
            if ($operatorToken !== null) {
                $result = DB::selectOne('SELECT gis.persist_operator_analysis(?,?::jsonb,?::jsonb) AS result', [$operatorToken, json_encode($fresh, JSON_THROW_ON_ERROR), json_encode($manifest, JSON_THROW_ON_ERROR)]);

                return json_decode($result->result, true, 512, JSON_THROW_ON_ERROR);
            }
            $runId = $fresh['analysis_run_id'];
            DB::table('gis.analysis_runs')->insert([
                'id' => $runId, 'release_id' => $fresh['release_id'], 'method_version' => $fresh['method_version'], 'code_revision' => $fresh['code_revision'],
                'input_hash' => $fresh['input_hash'], 'parameters_hash' => $parametersHash, 'input_revision' => $fresh['input_revision'],
                'parameters' => json_encode($fresh['parameters'], JSON_THROW_ON_ERROR), 'status' => 'running', 'idempotency_key' => $key, 'started_at' => now(), 'started_by' => $actorId,
            ]);
            foreach ($fresh['indicators'] as $row) {
                DB::table('gis.indicator_results')->insert([
                    'run_id' => $runId, 'release_id' => $fresh['release_id'], 'boundary_set_id' => $fresh['boundary_set_id'], 'district_id' => $row['district_id'],
                    ...array_intersect_key($row, array_flip(['population', 'facility_count', 'density', 'population_per_facility', 'facilities_per_30000', 'indicative_need', 'indicative_deficit', 'without_facility'])),
                    'completeness' => $row['population'] !== null && $row['area_km2'] !== null ? 'complete' : 'partial',
                    'reason' => $row['population'] === null ? 'missing_population' : ($row['area_km2'] === null ? 'missing_area' : ''),
                ]);
            }
            foreach ($fresh['coverage'] as $row) {
                DB::insert('INSERT INTO gis.coverage_results(run_id,release_id,boundary_set_id,district_id,radius_m,covered_area_m2,geometry_area_m2,coverage_pct,geom,registered_count,eligible_count,excluded_count,contributing_count,exclusion_reasons,completeness,reason) VALUES(?,?,?,?,?,?,?,?,extensions.ST_GeomFromGeoJSON(?),?,?,?,?,?::jsonb,?,?)', [
                    $runId, $fresh['release_id'], $fresh['boundary_set_id'], $row['district_id'], $row['radius_m'], $row['covered_area_m2'], $row['geometry_area_m2'], $row['coverage_pct'],
                    $row['geometry'] === null ? null : json_encode($row['geometry'], JSON_THROW_ON_ERROR),
                    $row['registered_count'], $row['eligible_count'], $row['excluded_count'], $row['contributing_count'], json_encode((object) $row['exclusion_reasons'], JSON_THROW_ON_ERROR), $row['completeness'], $row['reason'],
                ]);
            }
            foreach ($manifest['artifacts'] as $artifact) {
                DB::table('gis.artifacts')->insert(['id' => (string) Str::uuid(), 'release_id' => $fresh['release_id'], 'analysis_run_id' => $runId, 'kind' => $artifact['kind'], 'private_path' => $relativeDirectory.'/'.$artifact['path'], 'sha256' => $artifact['sha256'], 'bytes' => $artifact['bytes'], 'generated_at' => $manifest['generated_at'], 'sanitized' => $artifact['kind'] !== 'analysis_results']);
            }
            DB::table('gis.analysis_runs')->where('id', $runId)->update(['status' => 'succeeded', 'finished_at' => now(), 'output_manifest' => json_encode($manifest, JSON_THROW_ON_ERROR)]);

            return ['analysis_run_id' => $runId, 'status' => 'succeeded', 'replayed' => false];
        });
    }

    public function verifyArtifacts(array $fresh, string $directory): array
    {
        if (! preg_match('~^analysis/[0-9a-f-]{36}$~D', $directory)) {
            throw new InvalidArgumentException('Artifacts must be inside a private analysis UUID directory.');
        }
        if ($directory !== 'analysis/'.$fresh['analysis_run_id']) {
            throw new InvalidArgumentException('Artifact directory must match the run identity.');
        }
        $root = realpath(storage_path('app/private'));
        $folder = realpath(storage_path('app/private/'.$directory));
        if ($root === false || $folder === false || ! str_starts_with($folder.DIRECTORY_SEPARATOR, $root.DIRECTORY_SEPARATOR)) {
            throw new RuntimeException('Artifact directory escapes private storage.');
        }
        $manifest = json_decode(file_get_contents($folder.'/manifest.json'), true, 512, JSON_THROW_ON_ERROR);
        if (($manifest['schema_version'] ?? null) !== 'analysis-manifest-v1' || ($manifest['validation_status'] ?? null) !== 'passed') {
            throw new RuntimeException('Successful validator manifest required.');
        }
        $content = $manifest;
        unset($content['content_hash'], $content['generated_at']);
        if (! hash_equals(hash('sha256', $this->canonical($content)), $manifest['content_hash'] ?? '')) {
            throw new RuntimeException('Manifest content hash mismatch.');
        }
        foreach (['release_id', 'analysis_run_id', 'boundary_set_id', 'input_revision', 'input_hash', 'boundary_hash', 'method_version', 'code_revision', 'parameters'] as $field) {
            if ($this->canonical($manifest[$field] ?? null) !== $this->canonical($fresh[$field])) {
                throw new RuntimeException('Artifact manifest does not match this analysis input.');
            }
        }
        $expected = ['analysis_results' => 'results.json', 'thematic_density' => 'density.geojson', 'thematic_facility_count' => 'facility_count.geojson', 'thematic_population_per_facility' => 'population_per_facility.geojson', 'thematic_indicative_deficit' => 'indicative_deficit.geojson'];
        $seen = [];
        $rows = array_column($fresh['indicators'], null, 'code');
        $geometries = array_column($fresh['boundaries'], 'full', 'district_id');
        $legends = json_decode(file_get_contents(resource_path('analysis-legends.json')), true, 512, JSON_THROW_ON_ERROR);
        foreach ($manifest['artifacts'] ?? [] as $artifact) {
            $kind = $artifact['kind'] ?? '';
            if (! isset($expected[$kind]) || isset($seen[$kind]) || ($artifact['path'] ?? null) !== $expected[$kind]) {
                throw new RuntimeException('Unexpected artifact registry entry.');
            }
            $seen[$kind] = true;
            $path = realpath($folder.'/'.$artifact['path']);
            if ($path === false || ! str_starts_with($path, $folder.DIRECTORY_SEPARATOR) || filesize($path) !== $artifact['bytes'] || ! hash_equals(hash_file('sha256', $path), $artifact['sha256'])) {
                throw new RuntimeException('Artifact path, size or digest failed verification.');
            }
            $data = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
            if ($kind === 'analysis_results') {
                if (($data['input_hash'] ?? null) !== $fresh['input_hash'] || ($data['analysis_run_id'] ?? null) !== $fresh['analysis_run_id']) {
                    throw new RuntimeException('Results artifact identity mismatch.');
                }
                if ($this->canonical($data['indicators'] ?? null) !== $this->canonical($fresh['indicators'])
                    || ($data['boundaries'] ?? null) != $fresh['boundaries'] || ($data['coverage'] ?? null) != $fresh['coverage']) {
                    throw new RuntimeException('Results artifact differs from the recomputed database snapshot.');
                }

                continue;
            }
            $metric = substr($kind, strlen('thematic_'));
            if (($data['type'] ?? null) !== 'FeatureCollection' || array_diff(array_keys($data), ['type', 'features', 'meta'])) {
                throw new RuntimeException('Unexpected thematic document fields.');
            }
            foreach (['release_id', 'analysis_run_id', 'boundary_set_id', 'input_revision', 'input_hash', 'boundary_hash', 'method_version', 'code_revision'] as $field) {
                if (($data['meta'][$field] ?? null) !== $fresh[$field]) {
                    throw new RuntimeException('Thematic metadata identity mismatch.');
                }
            }
            if (($data['meta']['warnings'] ?? null) !== $fresh['warnings'] || array_diff(array_keys($data['meta']), ['release_id', 'analysis_run_id', 'boundary_set_id', 'input_revision', 'input_hash', 'boundary_hash', 'method_version', 'code_revision', 'metric', 'unit', 'legend', 'geometry_detail', 'display_policy', 'source_periods', 'coordinate_coverage', 'warnings'])) {
                throw new RuntimeException('Unexpected thematic metadata.');
            }
            if ($this->canonical($data['meta']['legend'] ?? null) !== $this->canonical($legends[$metric])
                || $this->canonical($data['meta']['source_periods'] ?? null) !== $this->canonical($fresh['source_periods'])
                || $this->canonical($data['meta']['coordinate_coverage'] ?? null) !== $this->canonical($fresh['eligibility_counts'])) {
                throw new RuntimeException('Thematic legend or provenance mismatch.');
            }
            if (($data['meta']['metric'] ?? null) !== $metric || ($data['meta']['unit'] ?? null) !== $legends[$metric]['unit']
                || ($data['meta']['geometry_detail'] ?? null) !== 'display' || ($data['meta']['display_policy'] ?? null) !== 'full_geometry_fallback') {
                throw new RuntimeException('Thematic display policy mismatch.');
            }
            $codes = [];
            foreach ($data['features'] ?? [] as $feature) {
                $code = $feature['id'] ?? '';
                $properties = $feature['properties'] ?? [];
                if (! isset($rows[$code]) || isset($codes[$code]) || ($properties['release_id'] ?? null) !== $fresh['release_id'] || ($properties['analysis_run_id'] ?? null) !== $fresh['analysis_run_id'] || ($properties['metric'] ?? null) !== $metric || ($feature['geometry'] ?? null) != $geometries[$rows[$code]['district_id']]) {
                    throw new RuntimeException('Thematic layer membership/identity/geometry mismatch.');
                }
                if (array_diff(array_keys($feature), ['type', 'id', 'geometry', 'properties']) || array_diff(array_keys($properties), ['code', 'parent_code', 'name', 'metric', 'value', 'value_exact', 'unit', 'completeness', 'reason', 'without_facility', 'source_ids', 'source_periods', 'release_id', 'analysis_run_id', 'class', 'color', 'label'])) {
                    throw new RuntimeException('Unexpected public layer fields.');
                }
                foreach (['code', 'parent_code', 'name', 'without_facility', 'source_ids', 'source_periods'] as $field) {
                    if ($this->canonical($properties[$field] ?? null) !== $this->canonical($rows[$code][$field])) {
                        throw new RuntimeException('Thematic source metadata mismatch.');
                    }
                }
                $actual = $properties['value_exact'] ?? null;
                $value = $rows[$code][$metric];
                if (($actual === null) !== ($value === null) || ($actual !== null && DB::selectOne('SELECT ?::numeric = ?::numeric AS same', [$actual, $value])->same !== true)) {
                    throw new RuntimeException('Thematic value differs from the recomputed database result.');
                }
                $display = $properties['value'] ?? null;
                if (($display === null) !== ($value === null) || ($display !== null && ((! is_float($display) && ! is_int($display)) || ! is_finite((float) $display) || (float) $display !== (float) $value))) {
                    throw new RuntimeException('Thematic numeric display value mismatch.');
                }
                $style = $this->style($metric, $value, $rows[$code], $legends[$metric]);
                foreach ($style as $field => $expectedValue) {
                    if (($properties[$field] ?? null) !== $expectedValue) {
                        throw new RuntimeException('Thematic class differs from the frozen legend.');
                    }
                }
                $reason = $value === null ? ($style['class'] === 'without_facility' ? 'no_facilities' : 'missing_input') : '';
                if (($feature['type'] ?? null) !== 'Feature' || ($properties['reason'] ?? null) !== $reason
                    || ($properties['completeness'] ?? null) !== ($value === null ? 'unavailable' : 'complete')) {
                    throw new RuntimeException('Thematic completeness mismatch.');
                }
                $codes[$code] = true;
            }
            if (count($codes) !== count($rows)) {
                throw new RuntimeException('Incomplete thematic district layer.');
            }
        }
        if (count($seen) !== count($expected)) {
            throw new RuntimeException('Incomplete artifact registry.');
        }

        return $manifest;
    }

    private function canonical(mixed $value): string
    {
        $sort = function (mixed $item) use (&$sort): mixed {
            if (is_array($item)) {
                if (! array_is_list($item)) {
                    ksort($item);
                }

                return array_map($sort, $item);
            }

            return $item;
        };

        return json_encode($sort($value), JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_LINE_TERMINATORS | JSON_PRESERVE_ZERO_FRACTION);
    }

    private function style(string $metric, mixed $value, array $row, array $legend): array
    {
        if ($value === null) {
            $class = $metric === 'population_per_facility' && $row['population'] !== null && $row['without_facility'] ? 'without_facility' : 'no_data';

            return ['class' => $class, ...$legend['special'][$class], 'unit' => $legend['unit']];
        }
        $parts = explode('.', (string) $value, 2);
        $whole = (int) $parts[0];
        $fraction = rtrim($parts[1] ?? '', '0');
        $index = 0;
        foreach ($legend['upper_bounds'] as $limit) {
            if ($whole < $limit || ($whole === $limit && $fraction === '')) {
                break;
            }
            $index++;
        }

        return ['class' => 'class_'.$index, 'color' => $legend['colors'][$index], 'label' => $legend['labels'][$index], 'unit' => $legend['unit']];
    }
}
