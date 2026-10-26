<?php

namespace Tests\Feature;

use App\Services\ReleaseValidationService;
use InvalidArgumentException;
use Tests\TestCase;

class ReleaseValidationInputTest extends TestCase
{
    public function test_invalid_input_is_rejected_before_database_access(): void
    {
        $this->expectException(InvalidArgumentException::class);
        app(ReleaseValidationService::class)->validate('not-a-token', 'invalid', 'invalid', -1, '');
    }

    public function test_cli_requires_explicit_revision_and_private_token(): void
    {
        $this->artisan('gis:validate', ['release' => 'invalid'])->assertFailed();
    }
}
