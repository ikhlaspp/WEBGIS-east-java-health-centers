<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\Carbon;

class ReleaseResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return ['release_id' => $this->id, 'label' => $this->label, 'boundary_set_id' => $this->boundary_set_id,
            'analysis_run_id' => $this->default_analysis_run_id, 'facility_period' => $this->facility_period,
            'population_policy' => $this->population_policy, 'area_policy' => $this->area_policy,
            'published_at' => Carbon::parse($this->published_at)->utc()->toRfc3339String(), 'active' => $this->active];
    }
}
