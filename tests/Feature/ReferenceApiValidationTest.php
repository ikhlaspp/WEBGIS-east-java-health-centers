<?php

namespace Tests\Feature;

use App\Http\Middleware\PublicApiContext;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class ReferenceApiValidationTest extends TestCase
{
    #[DataProvider('invalidQueries')]
    public function test_invalid_queries_have_the_versioned_error_envelope(string $url, int $status, string $code): void
    {
        $this->withoutMiddleware(PublicApiContext::class);
        $response = $this->getJson($url)->assertStatus($status)->assertJsonPath('error.code', $code)->assertJsonStructure(['error' => ['message', 'request_id']]);
        $this->assertStringContainsString('no-cache', $response->headers->get('Cache-Control'));
    }

    public static function invalidQueries(): array
    {
        return [
            ['/api/v1/regions?unknown=1', 400, 'UNKNOWN_PARAMETER'],
            ['/api/v1/regions?level=district', 422, 'VALIDATION_FAILED'],
            ['/api/v1/regions?release_id=not-a-uuid', 422, 'VALIDATION_FAILED'],
            ['/api/v1/regions?level=regency&parent_code=3501', 422, 'VALIDATION_FAILED'],
            ['/api/v1/releases?per_page=101', 422, 'VALIDATION_FAILED'],
            ['/api/v1/releases?page=0', 422, 'VALIDATION_FAILED'],
            ['/api/v1/sources?private_path=1', 400, 'UNKNOWN_PARAMETER'],
            ['/api/v1/unknown', 404, 'NOT_FOUND'],
        ];
    }
}
