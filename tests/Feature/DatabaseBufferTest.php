<?php

namespace Tests\Feature;

use App\Services\BufferService;
use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class DatabaseBufferTest extends GisDatabaseTestCase
{
    public function test_postgis_radius_and_area_match_independent_geodesic_reference(): void
    {
        $fixtures = json_decode(file_get_contents(base_path('tests/data/wf-079/reference-areas.json')), true, 512, JSON_THROW_ON_ERROR);
        foreach ($fixtures['cases'] as $case) {
            $result = DB::selectOne(<<<'SQL'
WITH centre AS (SELECT extensions.ST_SetSRID(extensions.ST_MakePoint(?,?),4326) AS p),
buffer AS (SELECT p,extensions.ST_Buffer(p::extensions.geography,?,'quad_segs=32')::extensions.geometry AS g FROM centre),
dumped AS (SELECT extensions.ST_DumpPoints(extensions.ST_ExteriorRing(g)) AS point FROM buffer),
vertices AS (SELECT (point).geom AS v,(point).path AS path FROM dumped),
edges AS (SELECT v,lag(v) OVER (ORDER BY path) AS previous FROM vertices),
samples AS (SELECT v FROM vertices UNION ALL SELECT extensions.ST_LineInterpolatePoint(extensions.ST_MakeLine(previous,v),0.5) FROM edges WHERE previous IS NOT NULL)
SELECT max(abs(extensions.ST_Distance(p::extensions.geography,v::extensions.geography)-?)) AS max_error,
(SELECT extensions.ST_Area(g::extensions.geography,true) FROM buffer) AS area,
(SELECT extensions.ST_NPoints(g) FROM buffer) AS vertices FROM samples CROSS JOIN centre
SQL, [$case['longitude'], $case['latitude'], $case['radius_m'], $case['radius_m']]);
            $this->assertLessThanOrEqual(max(2, 0.01 * $case['radius_m']), (float) $result->max_error, $case['name']);
            $this->assertEqualsWithDelta($case['python_geodesic_area_m2'], (float) $result->area, max(1, 0.01 * $case['python_geodesic_area_m2']), $case['name']);
            $this->assertSame(129, (int) $result->vertices);
        }
    }

    public function test_worker_service_excludes_missing_and_keeps_exact_review_identity(): void
    {
        DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason,reviewed_by,reviewed_at) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic query','facility','accepted','https://example.test/evidence','synthetic','fixture evidence',?,now())", [$this->id(7), $this->id(6), $this->id(2), $this->id(1)]);
        DB::update("UPDATE gis.facility_snapshots SET coordinate_status='verified',precision_level='facility',location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),coordinate_source_id=?,selected_review_id=?", [$this->id(2), $this->id(7)]);
        DB::insert("INSERT INTO gis.facility_snapshots(release_id,boundary_set_id,district_id,facility_code,name,address,service_type,area_type,source_id,source_row,coordinate_status,precision_level) SELECT release_id,boundary_set_id,district_id,'35010100002',name,address,service_type,area_type,source_id,2,'missing','unknown' FROM gis.facility_snapshots WHERE facility_code='35010100001'");
        DB::statement('SET CONSTRAINTS ALL IMMEDIATE');
        DB::statement('SET LOCAL ROLE gis_worker');
        $result = (new BufferService)->generate($this->id(6), $this->id(80), 'synthetic-test');
        $this->assertSame(2, $result['registered_count']);
        $this->assertSame(1, $result['eligible_count']);
        $this->assertSame(1, $result['excluded_count']);
        $this->assertCount(3, $result['features']);
        $this->assertSame($this->id(7), $result['features'][0]['properties']['selected_review_id']);
        $this->assertSame([1000, 3000, 5000], array_column(array_column($result['features'], 'properties'), 'radius_m'));
        $this->assertSame('35010100002', $result['excluded'][0]['facility_code']);
        $this->assertSame('candidate_artifact', $result['status']);
        $this->assertSame(0, DB::table('gis.analysis_runs')->count());
    }

    public function test_zero_eligible_is_reported_without_fabricated_buffers(): void
    {
        DB::statement('SET LOCAL ROLE gis_worker');
        $result = (new BufferService)->generate($this->id(6), $this->id(80), 'synthetic-test');
        $this->assertSame([], $result['features']);
        $this->assertSame(0, $result['eligible_count']);
        $this->assertSame(1, $result['excluded_count']);
    }
}
