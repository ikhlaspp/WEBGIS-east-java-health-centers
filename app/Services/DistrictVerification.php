<?php

namespace App\Services;

class DistrictVerification
{
    private array $evidence;

    public function __construct()
    {
        $this->evidence = json_decode(file_get_contents(resource_path('district-verifications.json')), true, 512, JSON_THROW_ON_ERROR);
    }

    public function matches(string $releaseId, string $code, string $district, string $regency, string $name, string $address): bool
    {
        $record = $this->evidence['records'][$code] ?? null;

        return $releaseId === $this->evidence['release_id'] && $record !== null
            && $record['district_code'] === $district && $record['regency_code'] === $regency
            && $record['name'] === $name && $record['address'] === $address;
    }
}
