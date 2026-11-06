<?php

namespace App\Http\Resources;

use App\Services\DistrictVerification;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class FacilityResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'code' => $this->facility_code, 'name' => $this->name, 'address' => $this->address,
            'service_type' => $this->service_type, 'area_type' => $this->area_type,
            'regency_code' => $this->regency_code, 'regency_name' => $this->regency_name,
            'district_code' => $this->district_code, 'district_name' => $this->district_name,
            'coordinate_status' => $this->coordinate_status, 'precision_level' => $this->precision_level,
            'location' => $this->longitude === null ? null : ['type' => 'Point', 'coordinates' => [(float) $this->longitude, (float) $this->latitude]],
            'estimated_location' => $this->estimated_location === null ? null : json_decode($this->estimated_location, true, 512, JSON_THROW_ON_ERROR),
            'location_kind' => $this->estimated_location === null ? 'source' : 'district_estimate',
            'district_verified' => $this->estimated_location !== null && app(DistrictVerification::class)->matches($this->release_id, $this->facility_code, $this->district_code, $this->regency_code, $this->name, $this->address),
        ];
    }
}
