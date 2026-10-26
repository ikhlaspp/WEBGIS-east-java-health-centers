<?php

namespace Tests\Feature;

use App\Services\ReleaseLifecycleService;
use InvalidArgumentException;
use Tests\TestCase;

class ReleasePublicationInputTest extends TestCase
{
    public function test_invalid_input_fails_before_database_access(): void
    {
        $this->expectException(InvalidArgumentException::class);
        app(ReleaseLifecycleService::class)->publish('invalid', 'invalid', -1, 'invalid', '');
    }

    public function test_command_requires_explicit_version_and_token(): void
    {
        $this->artisan('gis:publish', ['release' => 'invalid'])->assertFailed();
    }
}
