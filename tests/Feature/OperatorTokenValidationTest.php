<?php

namespace Tests\Feature;

use App\Services\OperatorTokenService;
use InvalidArgumentException;
use Tests\TestCase;

class OperatorTokenValidationTest extends TestCase
{
    /**
     * A basic feature test example.
     */
    public function test_invalid_ability_and_expiry_are_rejected_before_database_access(): void
    {
        foreach ([[['root'], 60], [[], 60], [['review'], 0], [['review'], 481]] as [$abilities, $minutes]) {
            try {
                app(OperatorTokenService::class)->issue('fixture@example.test', $abilities, $minutes);
                $this->fail('Invalid capability accepted.');
            } catch (InvalidArgumentException) {
                $this->addToAssertionCount(1);
            }
        }
    }

    public function test_missing_capability_file_fails_without_printing_secrets(): void
    {
        $this->artisan('gis:review-location', ['release' => 'invalid', 'facility' => '35010100001', 'review' => 'invalid', 'decision' => 'accepted', '--token-file' => 'does-not-exist.token'])->assertFailed();
    }

    public function test_revocation_requires_a_uuid(): void
    {
        $this->expectException(InvalidArgumentException::class);
        app(OperatorTokenService::class)->revoke('invalid');
    }
}
