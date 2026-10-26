<?php

namespace Tests\Feature;

use App\Services\OperatorAnalysisService;
use InvalidArgumentException;
use Tests\TestCase;

class OperatorAnalysisValidationTest extends TestCase
{
    /**
     * A basic feature test example.
     */
    public function test_invalid_analysis_identity_is_rejected_before_database_access(): void
    {
        $uuid = '00000000-0000-4000-8000-000000000001';
        foreach ([['bad', $uuid, 30000, str_repeat('c', 40)], [$uuid, 'bad', 30000, str_repeat('c', 40)], [$uuid, $uuid, 0, str_repeat('c', 40)], [$uuid, $uuid, 30000, 'main']] as $arguments) {
            try {
                app(OperatorAnalysisService::class)->run(str_repeat('A', 43), ...$arguments);
                $this->fail('Invalid analysis identity accepted.');
            } catch (InvalidArgumentException) {
                $this->addToAssertionCount(1);
            }
        }
    }

    public function test_command_requires_a_private_token_file(): void
    {
        $this->artisan('gis:analyze', ['release' => 'invalid', '--token-file' => 'missing.token'])->assertFailed();
    }
}
