<?php

namespace Tests\Feature;

use App\Http\Middleware\PublicApiContext;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class MapStatisticsValidationTest extends TestCase
{
    #[DataProvider('invalidQueries')]
    public function test_invalid_queries_are_rejected(string $path, int $status): void
    {
        $this->withoutMiddleware(PublicApiContext::class);
        $this->getJson('/api/v1/'.$path)->assertStatus($status)->assertJsonStructure(['error' => ['code', 'request_id']]);
    }

    public static function invalidQueries(): array
    {
        return [
            ['map/points?page=1', 400], ['map/points?bbox=1,2,3', 422], ['map/points?bbox=1,2,NaN,4', 422],
            ['map/points?bbox=1,2,1,4', 422], ['map/points?bbox=170,-10,-170,10', 422], ['map/points?bbox=-181,-10,180,10', 422],
            ['map/points?bbox=0,-91,1,1', 422], ['map/points?bbox=0,0,1e999,1', 422], ['map/points?q[]=bad', 422],
            ['statistics?service_type=Rawat%20Inap', 400], ['statistics?coordinate_status=verified', 400],
            ['map/regions?metric=secret', 422], ['map/regions?geometry_detail=raw', 422], ['map/regions?level=district', 422],
            ['analysis/buffers?radius_m=2000', 422], ['analysis/buffers', 422], ['analysis/buffers?radius_m=1000&analysis_run_id=bad', 422],
        ];
    }
}
