<?php

namespace App\Services;

use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;
use RuntimeException;
use stdClass;

class DatasetImportService
{
    private const FIELDS = [
        'data_sources' => 'id publisher title source_url private_path publication_year observation_period retrieved_at sha256 license_note limitations',
        'boundary_sets' => 'id source_id name version code_system reference_year source_crs metadata',
        'regencies' => 'id boundary_set_id code name kind geom geom_display',
        'districts' => 'id boundary_set_id regency_id code name geom geom_display',
        'region_aliases' => 'id source_id boundary_set_id district_id raw_regency raw_district source_code_system source_edition source_code mapping_kind evidence',
        'dataset_releases' => 'id label boundary_set_id facility_period population_policy area_policy source_manifest method_version code_revision',
        'release_sources' => 'release_id source_id purpose',
        'district_indicators' => 'release_id boundary_set_id district_id population population_year population_source_id population_locator population_raw area_km2 area_year area_source_id area_locator area_raw quality_status notes',
        'facility_snapshots' => 'release_id boundary_set_id district_id facility_code name address service_type area_type source_id source_row location coordinate_status precision_level coordinate_source_id',
        'geocode_reviews' => 'id release_id facility_code source_id candidate_location provider query provider_object_id precision_level raw_response_private_path evidence_url evidence_note evidence_sha256',
    ];

    public function read(string $path, string $expectedHash): array
    {
        if (! preg_match('/^[a-f0-9]{64}$/D', $expectedHash) || strtolower(pathinfo($path, PATHINFO_EXTENSION)) !== 'json' || ! is_file($path)) {
            throw new InvalidArgumentException('Provide a local JSON file and its SHA-256.');
        }
        $bytes = file_get_contents($path, false, null, 0, 20 * 1024 * 1024 + 1);
        if ($bytes === false || strlen($bytes) > 20 * 1024 * 1024 || ! hash_equals($expectedHash, hash('sha256', $bytes))) {
            throw new InvalidArgumentException('File exceeds 20 MiB or SHA-256 does not match.');
        }
        $document = json_decode($bytes, false, 64, JSON_THROW_ON_ERROR);
        $this->rejectDuplicateKeys($bytes);
        if (! $document instanceof stdClass || ($document->format ?? null) !== 'gis-import-v1'
            || ! is_array($document->rows ?? null) || count($document->rows) < 1 || count($document->rows) > 50000
            || ! ($document->parameters ?? null) instanceof stdClass
            || ! is_string($document->pipeline_version ?? null) || trim($document->pipeline_version) === '') {
            throw new InvalidArgumentException('Invalid canonical import envelope.');
        }
        foreach (['source_id', 'target_release_id'] as $key) {
            if (! is_string($document->$key ?? null) || ! preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/D', $document->$key)) {
                throw new InvalidArgumentException('Source and target must be canonical UUIDs.');
            }
        }
        $seen = [];
        foreach ($document->rows as $row) {
            if (! $row instanceof stdClass || ! is_int($row->row_no ?? null) || $row->row_no < 1 || isset($seen[$row->row_no])
                || ! is_string($row->source_locator ?? null) || trim($row->source_locator) === ''
                || ! ($row->raw_fields ?? null) instanceof stdClass || ! ($row->normalized_fields ?? null) instanceof stdClass
                || ! is_array($row->errors ?? null) || ! in_array($row->disposition ?? null, ['accepted', 'quarantined', 'aggregate'], true)
                || ! is_string($row->dataset ?? null) || ! isset(self::FIELDS[$row->dataset])) {
                throw new InvalidArgumentException('Invalid row envelope or duplicate row number.');
            }
            $seen[$row->row_no] = true;
            $fields = (array) $row->normalized_fields;
            if (array_diff(array_keys($fields), explode(' ', self::FIELDS[$row->dataset]))) {
                throw new InvalidArgumentException('Unknown or protected field in import row.');
            }
            if ((isset($fields['release_id']) && $fields['release_id'] !== $document->target_release_id)
                || ($row->dataset === 'dataset_releases' && ($fields['id'] ?? null) !== $document->target_release_id)
                || (isset($fields['coordinate_status']) && ! in_array($fields['coordinate_status'], ['missing', 'unverified'], true))
                || ($row->disposition === 'accepted' && $row->errors !== [])) {
                throw new InvalidArgumentException('Row targets another release or asserts a trusted decision.');
            }
            foreach ($fields as $name => $value) {
                if (in_array($name, ['geom', 'geom_display', 'location', 'candidate_location'], true) && $value !== null) {
                    $types = in_array($name, ['geom', 'geom_display'], true) ? ['Polygon', 'MultiPolygon'] : ['Point'];
                    if (! $value instanceof stdClass || isset($value->crs) || ! in_array($value->type ?? null, $types, true) || ! is_array($value->coordinates ?? null)) {
                        throw new InvalidArgumentException('Geometry must be longitude/latitude GeoJSON without a CRS override.');
                    }
                }
            }
        }
        $this->json($document);

        return ['document' => $document, 'file_hash' => $expectedHash, 'parameters_hash' => hash('sha256', $this->json($this->canonical($document->parameters)))];
    }

    public function import(string $path, string $expectedHash, #[\SensitiveParameter] string $token): array
    {
        $input = $this->read($path, $expectedHash);
        if (DB::connection()->getDriverName() !== 'pgsql') {
            throw new RuntimeException('Imports require PostgreSQL/PostGIS.');
        }

        return DB::transaction(function () use ($input, $token): array {
            $document = $input['document'];
            DB::selectOne('SELECT gis.import_actor(?)', [$token]);
            $identity = [$document->source_id, $document->target_release_id, $input['file_hash'], $document->pipeline_version, $input['parameters_hash']];
            $key = DB::selectOne('SELECT gis.import_key(?,?,?,?,?) AS key', $identity)->key;
            DB::selectOne('SELECT pg_advisory_xact_lock(hashtextextended(?,0))', [$key]);
            $existing = DB::table('gis.import_batches')->where('idempotency_key', $key)->first();
            if ($existing !== null) {
                return ['batch_id' => $existing->id, 'status' => $existing->status, 'replayed' => true, 'report' => json_decode($existing->checkpoint, true)];
            }
            $rows = $document->rows;
            $order = array_flip(array_keys(self::FIELDS));
            usort($rows, fn ($a, $b) => [$order[$a->dataset], $a->row_no] <=> [$order[$b->dataset], $b->row_no]);
            foreach ($rows as $row) {
                if ($order[$row->dataset] <= $order['dataset_releases'] && $row->disposition === 'accepted') {
                    $this->insert($row);
                }
            }
            $batch = DB::selectOne('SELECT gis.begin_import(?,?,?,?,?,?,?) AS id', [$token, ...$identity, count($rows)])->id;
            $promoted = 0;
            $failure = null;
            $hasQuarantine = count(array_filter($rows, fn ($row) => $row->disposition === 'quarantined')) > 0;
            if (! $hasQuarantine) {
                $current = null;
                try {
                    DB::transaction(function () use ($rows, $order, &$current, &$promoted): void {
                        DB::statement('SET CONSTRAINTS ALL IMMEDIATE');
                        foreach ($rows as $row) {
                            if ($order[$row->dataset] > $order['dataset_releases'] && $row->disposition === 'accepted') {
                                $current = $row;
                                $this->insert($row);
                                $promoted++;
                            }
                        }
                    });
                } catch (QueryException|RuntimeException $exception) {
                    $promoted = 0;
                    $failure = ['row_no' => $current?->row_no, 'code' => $exception instanceof QueryException ? (string) $exception->getCode() : 'row_conflict'];
                    if ($current !== null) {
                        $current->disposition = 'quarantined';
                        $current->errors[] = $failure;
                    }
                }
            }
            foreach ($rows as $row) {
                DB::insert('INSERT INTO staging.rows(batch_id,row_no,source_locator,raw,normalized,disposition,errors,row_hash) VALUES(?,?,?,?,?,?,?,?)', [
                    $batch, $row->row_no, $row->source_locator, $this->json($row->raw_fields), $this->json($row->normalized_fields), $row->disposition, $this->json($row->errors), hash('sha256', $this->json($row->raw_fields)),
                ]);
            }
            $report = ['promoted_domain_rows' => $promoted, 'failure' => $failure, 'quarantined_input' => $hasQuarantine, 'release_status' => 'draft'];
            $status = DB::selectOne('SELECT gis.finish_import(?,?,?,?::jsonb) AS status', [$token, $batch, $failure === null && ! $hasQuarantine, $this->json($report)])->status;

            return ['batch_id' => $batch, 'status' => $status, 'replayed' => false, 'report' => $report];
        });
    }

    private function insert(stdClass $row): void
    {
        $fields = (array) $row->normalized_fields;
        if ($fields === []) {
            throw new RuntimeException('Empty normalized row.');
        }
        $expressions = [];
        $bindings = [];
        foreach ($fields as $name => $value) {
            $expression = '?';
            if (in_array($name, ['geom', 'geom_display', 'location', 'candidate_location'], true) && $value !== null) {
                $expression = 'extensions.ST_GeomFromGeoJSON(?)';
                if (in_array($name, ['geom', 'geom_display'], true)) {
                    $expression = "extensions.ST_Multi($expression)";
                }
            }
            $expressions[$name] = $expression;
            $bindings[] = is_object($value) || is_array($value) ? $this->json($value) : $value;
        }
        $table = 'gis.'.$row->dataset;
        $columns = implode(',', array_keys($fields));
        $values = implode(',', $expressions);
        $inserted = DB::affectingStatement("INSERT INTO $table ($columns) VALUES ($values) ON CONFLICT DO NOTHING", $bindings);
        if ($inserted === 0) {
            $conditions = [];
            foreach ($expressions as $name => $expression) {
                $conditions[] = in_array($name, ['geom', 'geom_display', 'location', 'candidate_location'], true) && $fields[$name] !== null
                    ? "extensions.ST_OrderingEquals($name,$expression)"
                    : "$name IS NOT DISTINCT FROM $expression";
            }
            if (DB::selectOne("SELECT 1 AS found FROM $table WHERE ".implode(' AND ', $conditions), $bindings) === null) {
                throw new RuntimeException('Existing identity has different input; create a new draft identity.');
            }
        }
    }

    private function json(mixed $value): string
    {
        return json_encode($value, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE | JSON_PRESERVE_ZERO_FRACTION);
    }

    private function canonical(mixed $value): mixed
    {
        if ($value instanceof stdClass) {
            $properties = (array) $value;
            ksort($properties);

            return (object) array_map($this->canonical(...), $properties);
        }

        return is_array($value) ? array_map($this->canonical(...), $value) : $value;
    }

    private function rejectDuplicateKeys(string $json): void
    {
        preg_match_all('/"(?:[^"\\\\]|\\\\.)*"|[{}\\[\\]:]/s', $json, $matches);
        $stack = [];
        foreach ($matches[0] as $index => $token) {
            if ($token === '{' || $token === '[') {
                $stack[] = [];
            } elseif ($token === '}' || $token === ']') {
                array_pop($stack);
            } elseif (str_starts_with($token, '"') && ($matches[0][$index + 1] ?? null) === ':') {
                $key = json_decode($token, true, 64, JSON_THROW_ON_ERROR);
                $level = count($stack) - 1;
                if (isset($stack[$level][$key])) {
                    throw new InvalidArgumentException('Duplicate JSON object key.');
                }
                $stack[$level][$key] = true;
            }
        }
    }
}
