<?php

namespace Tests\Feature;

use App\Services\DistrictVerification;
use Tests\TestCase;

class DistrictVerificationTest extends TestCase
{
    public function test_evidence_only_matches_the_reviewed_release_and_unchanged_assignment(): void
    {
        $evidence = json_decode(file_get_contents(resource_path('district-verifications.json')), true, 512, JSON_THROW_ON_ERROR);
        $code = (string) array_key_first($evidence['records']);
        $row = $evidence['records'][$code];
        $service = app(DistrictVerification::class);
        $this->assertTrue($service->matches($evidence['release_id'], $code, $row['district_code'], $row['regency_code'], $row['name'], $row['address']));
        $this->assertFalse($service->matches('another-release', $code, $row['district_code'], $row['regency_code'], $row['name'], $row['address']));
        $this->assertFalse($service->matches($evidence['release_id'], $code, '9999999', $row['regency_code'], $row['name'], $row['address']));
        $this->assertFalse($service->matches($evidence['release_id'], $code, $row['district_code'], $row['regency_code'], $row['name'], 'changed address'));
        foreach ($evidence['held_codes'] as $held) {
            $this->assertFalse($service->matches($evidence['release_id'], $held, $row['district_code'], $row['regency_code'], $row['name'], $row['address']));
        }
    }
}
