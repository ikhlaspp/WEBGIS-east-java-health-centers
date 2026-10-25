<?php

namespace Tests\Feature;

use App\Http\Middleware\PublicApiContext;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class FacilityApiValidationTest extends TestCase
{
    #[DataProvider('invalidQueries')]
    public function test_invalid_input_is_rejected_before_querying(string $query, int $status): void
    {
        $this->withoutMiddleware(PublicApiContext::class);
        $this->getJson('/api/v1/facilities'.$query)->assertStatus($status)->assertJsonStructure(['error' => ['code', 'message', 'request_id']]);
    }

    public static function invalidQueries(): array
    {
        return [
            ['?unknown=1', 400], ['?per_page=101', 422], ['?page=0', 422], ['?page=99999999999999999999999', 422],
            ['?q='.str_repeat('%C3%A9', 101), 422], ['?q[]=a', 422], ['?sort=name;DROP', 422],
            ['?regency_code=3501010', 422], ['?district_code=3501', 422], ['?coordinate_status=accepted', 422],
            ['?service_type=invalid', 422], ['?area_type=invalid', 422], ['?release_id=bad', 422],
            ['/35010100001?q=not-allowed', 400], ['/bad-code', 404],
        ];
    }
}
