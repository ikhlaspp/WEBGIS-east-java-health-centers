<?php

namespace Tests\Feature;

use App\Services\BufferService;
use App\Services\CoverageService;
use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class DatabaseCoverageTest extends GisDatabaseTestCase
{
    public function test_postgis_union_clip_matches_python_and_includes_neighbouring_facilities(): void
    {
        $fixture = json_decode(file_get_contents(base_path('tests/data/wf-080/reference-coverage.json')), true, 512, JSON_THROW_ON_ERROR);
        $regions = $fixture['boundaries']['features'];
        DB::update('UPDATE gis.districts SET geom=extensions.ST_GeomFromGeoJSON(?) WHERE id=?', [json_encode($regions[0]['geometry'], JSON_THROW_ON_ERROR), $this->id(5)]);
        DB::insert("INSERT INTO gis.districts(id,boundary_set_id,regency_id,code,name,geom) VALUES(?,?,?,'3501020','Neighbour',extensions.ST_Multi(extensions.ST_GeomFromGeoJSON(?)))", [$this->id(55), $this->id(3), $this->id(4), json_encode($regions[1]['geometry'], JSON_THROW_ON_ERROR)]);
        DB::insert("INSERT INTO gis.districts(id,boundary_set_id,regency_id,code,name,geom) VALUES(?,?,?,'3501030','Far away',extensions.ST_GeomFromText('MULTIPOLYGON(((115 -8,115.1 -8,115.1 -7.9,115 -7.9,115 -8)))',4326))", [$this->id(56), $this->id(3), $this->id(4)]);
        DB::update('UPDATE gis.facility_snapshots SET district_id=?', [$this->id(55)]);
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) SELECT release_id,boundary_set_id,district_id,'35010100002',name,address,service_type,area_type,source_id,2,'missing','unknown' FROM gis.facility_snapshots WHERE facility_code='35010100001'");
        foreach ([1 => 112, 2 => 112.005] as $number => $longitude) {
            $code = '3501010000'.$number;
            DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason,reviewed_by,reviewed_at) VALUES(?,?,?,?,extensions.ST_SetSRID(extensions.ST_MakePoint(?,-7),4326),'fixture','synthetic','facility','accepted','https://example.test/evidence','synthetic','fixture evidence',?,now())", [$this->id(70 + $number), $this->id(6), $code, $this->id(2), $longitude, $this->id(1)]);
            DB::update("UPDATE gis.facility_snapshots SET coordinate_status='verified',precision_level='facility',location=extensions.ST_SetSRID(extensions.ST_MakePoint(?,-7),4326),coordinate_source_id=?,selected_review_id=? WHERE facility_code=?", [$longitude, $this->id(2), $this->id(70 + $number), $code]);
        }
        DB::statement('SET CONSTRAINTS ALL IMMEDIATE');
        DB::statement('SET LOCAL ROLE gis_worker');
        $output = (new CoverageService(new BufferService))->generate($this->id(6), $this->id(80), 'synthetic-test');
        $this->assertCount(9, $output['results']);
        foreach ($output['results'] as $row) {
            if ($row['district_id'] === $this->id(56)) {
                $this->assertSame(0.0, $row['coverage_pct']);
                $this->assertNull($row['geometry']);
                $this->assertGreaterThan(0, $row['geometry_area_m2']);

                continue;
            }
            $name = $row['district_id'] === $this->id(5) ? 'target' : 'neighbour';
            $reference = array_values(array_filter($fixture['reference']['results'], fn ($item) => $item['district_id'] === $name && $item['radius_m'] === $row['radius_m']))[0];
            $this->assertEqualsWithDelta($reference['covered_area_m2'], $row['covered_area_m2'], max(1, 0.01 * $reference['covered_area_m2']));
            $this->assertEqualsWithDelta($reference['geometry_area_m2'], $row['geometry_area_m2'], max(1, 0.01 * $reference['geometry_area_m2']));
            $this->assertSame($reference['registered_count'], $row['registered_count']);
            $this->assertSame(2, $row['contributing_count']);
            $this->assertLessThanOrEqual(100, $row['coverage_pct']);
            $this->assertSame('complete', $row['completeness']);
        }
    }

    public function test_no_eligible_points_return_unavailable_not_zero(): void
    {
        DB::statement('SET LOCAL ROLE gis_worker');
        $result = (new CoverageService(new BufferService))->generate($this->id(6), $this->id(80), 'synthetic-test');
        $this->assertCount(3, $result['results']);
        foreach ($result['results'] as $row) {
            $this->assertNull($row['coverage_pct']);
            $this->assertNull($row['covered_area_m2']);
            $this->assertNull($row['geometry_area_m2']);
            $this->assertSame('unavailable', $row['completeness']);
            $this->assertSame(1, $row['registered_count']);
            $this->assertSame(1, $row['excluded_count']);
        }
    }
}
