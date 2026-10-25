<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class DatabaseIndicatorReferenceTest extends GisDatabaseTestCase
{
    public function test_postgresql_numeric_matches_the_frozen_independent_examples(): void
    {
        $fixtures = json_decode(file_get_contents(base_path('docs/pekerjaan/WF-049/formula-fixtures.json')), true, 512, JSON_THROW_ON_ERROR);
        foreach ($fixtures['cases'] as $case) {
            $input = $case['input'];
            $result = DB::selectOne(<<<'SQL'
WITH input AS (SELECT ?::numeric AS p, ?::numeric AS f, ?::numeric AS a, ?::numeric AS t)
SELECT p/a AS density,p/nullif(f,0) AS ratio,ceil(p/t) AS need,
CASE WHEN p IS NULL THEN NULL ELSE greatest(0,ceil(p/t)-f) END AS deficit,
f=0 AS without_facility FROM input
SQL, [$input['P'], $input['F'], $input['A'], $input['T']]);
            foreach ($case['expected'] as $name => $expected) {
                if ($expected === null) {
                    $this->assertNull($result->$name, $case['id'].':'.$name);
                } elseif (is_bool($expected)) {
                    $this->assertSame($expected, $result->$name, $case['id'].':'.$name);
                } else {
                    $this->assertEqualsWithDelta((float) $expected, (float) $result->$name, 1e-9, $case['id'].':'.$name);
                }
            }
        }
    }
}
