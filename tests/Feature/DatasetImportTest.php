<?php

namespace Tests\Feature;

use App\Services\DatasetImportService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class DatasetImportTest extends GisDatabaseTestCase
{
    private string $token;

    private array $paths = [];

    protected function setUp(): void
    {
        parent::setUp();
        $this->token = str_repeat('synthetic-only-', 4);
        DB::update('UPDATE app.users SET is_admin=true WHERE id=?', [$this->id(1)]);
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,?::jsonb,now()+interval '1 hour')", [$this->id(50), $this->id(1), hash('sha256', $this->token), '["import"]']);
        DB::statement('SET LOCAL ROLE gis_worker');
    }

    protected function tearDown(): void
    {
        foreach ($this->paths as $path) {
            unlink($path);
        }
        parent::tearDown();
    }

    public function test_repeated_import_keeps_one_batch_and_one_domain_row(): void
    {
        [$path, $hash] = $this->file([$this->row(1)]);
        $service = new DatasetImportService;
        $first = $service->import($path, $hash, $this->token);
        $again = $service->import($path, $hash, $this->token);
        $this->assertSame('succeeded', $first['status']);
        $this->assertSame($first['batch_id'], $again['batch_id']);
        $this->assertTrue($again['replayed']);
        $this->assertSame(1, DB::table('gis.import_batches')->count());
        $this->assertSame(1, DB::table('staging.rows')->count());
        $this->assertSame(1, DB::table('gis.district_indicators')->count());
        $this->assertSame('draft', DB::table('gis.dataset_releases')->value('status'));
    }

    public function test_middle_failure_rolls_back_domain_rows_but_preserves_error_partition(): void
    {
        $bad = $this->row(2);
        $bad['normalized_fields']['district_id'] = $this->id(999);
        [$path, $hash] = $this->file([$this->row(1), $bad]);
        $result = (new DatasetImportService)->import($path, $hash, $this->token);
        $this->assertSame('failed', $result['status']);
        $this->assertSame(0, DB::table('gis.district_indicators')->count());
        $this->assertSame(2, DB::table('staging.rows')->count());
        $this->assertSame(1, DB::table('staging.rows')->where('disposition', 'quarantined')->count());
        $this->assertSame(0, $result['report']['promoted_domain_rows']);
        $batch = DB::table('gis.import_batches')->first();
        $this->assertSame(2, (int) $batch->raw_rows);
        $this->assertSame(1, (int) $batch->accepted_rows);
        $this->assertSame(1, (int) $batch->quarantined_rows);
    }

    public function test_invalid_capability_cannot_start_import(): void
    {
        [$path, $hash] = $this->file([$this->row(1)]);
        try {
            (new DatasetImportService)->import($path, $hash, 'invalid');
            $this->fail('Invalid capability was accepted.');
        } catch (QueryException $exception) {
            $this->assertSame('28000', (string) $exception->getCode());
        }
        $this->assertSame(0, DB::table('gis.import_batches')->count());
    }

    public function test_aggregate_rows_are_staged_without_domain_promotion(): void
    {
        $row = $this->row(1);
        $row['disposition'] = 'aggregate';
        [$path, $hash] = $this->file([$row]);
        $result = (new DatasetImportService)->import($path, $hash, $this->token);
        $this->assertSame('succeeded', $result['status']);
        $this->assertSame(0, DB::table('gis.district_indicators')->count());
        $this->assertSame(1, (int) DB::table('gis.import_batches')->value('aggregate_rows'));
    }

    public function test_facility_point_is_imported_unverified_and_repeat_does_not_duplicate_it(): void
    {
        $row = $this->row(1);
        $row['dataset'] = 'facility_snapshots';
        $row['normalized_fields'] = ['release_id' => $this->id(6), 'boundary_set_id' => $this->id(3), 'district_id' => $this->id(5), 'facility_code' => '35010100002', 'name' => 'Synthetic second', 'address' => 'Synthetic', 'service_type' => 'fixture', 'area_type' => 'fixture', 'source_id' => $this->id(2), 'source_row' => 2, 'location' => (object) ['type' => 'Point', 'coordinates' => [112.5, -7.5]], 'coordinate_status' => 'unverified', 'precision_level' => 'unknown'];
        [$path, $hash] = $this->file([$row]);
        $service = new DatasetImportService;
        $this->assertSame('succeeded', $service->import($path, $hash, $this->token)['status']);
        $this->assertTrue($service->import($path, $hash, $this->token)['replayed']);
        $this->assertSame(2, DB::table('gis.facility_snapshots')->count());
        $point = DB::selectOne("SELECT coordinate_status, selected_review_id, extensions.ST_X(location) AS longitude FROM gis.facility_snapshots WHERE facility_code='35010100002'");
        $this->assertSame('unverified', $point->coordinate_status);
        $this->assertNull($point->selected_review_id);
        $this->assertSame(112.5, (float) $point->longitude);
    }

    public function test_pre_quarantined_input_prevents_domain_promotion(): void
    {
        $bad = $this->row(2);
        $bad['disposition'] = 'quarantined';
        $bad['errors'] = ['source_missing'];
        [$path, $hash] = $this->file([$this->row(1), $bad]);
        $result = (new DatasetImportService)->import($path, $hash, $this->token);
        $this->assertSame('failed', $result['status']);
        $this->assertSame(0, DB::table('gis.district_indicators')->count());
        $this->assertSame(2, DB::table('staging.rows')->count());
    }

    public function test_changed_content_cannot_overwrite_existing_identity(): void
    {
        [$path, $hash] = $this->file([$this->row(1)]);
        (new DatasetImportService)->import($path, $hash, $this->token);
        $row = $this->row(1);
        $row['normalized_fields']['notes'] = 'changed';
        [$other, $otherHash] = $this->file([$row]);
        $result = (new DatasetImportService)->import($other, $otherHash, $this->token);
        $this->assertSame('failed', $result['status']);
        $this->assertSame('synthetic', DB::table('gis.district_indicators')->value('notes'));
    }

    private function row(int $number): array
    {
        return ['row_no' => $number, 'source_locator' => 'synthetic:'.$number, 'dataset' => 'district_indicators', 'raw_fields' => (object) ['value' => null], 'normalized_fields' => ['release_id' => $this->id(6), 'boundary_set_id' => $this->id(3), 'district_id' => $this->id(5), 'quality_status' => 'pending', 'notes' => 'synthetic'], 'disposition' => 'accepted', 'errors' => []];
    }

    private function file(array $rows): array
    {
        $path = sys_get_temp_dir().'/gis-import-'.bin2hex(random_bytes(8)).'.json';
        $this->paths[] = $path;
        file_put_contents($path, json_encode(['format' => 'gis-import-v1', 'source_id' => $this->id(2), 'target_release_id' => $this->id(6), 'pipeline_version' => 'fixture', 'parameters' => (object) [], 'rows' => $rows], JSON_THROW_ON_ERROR));

        return [$path, hash_file('sha256', $path)];
    }
}
