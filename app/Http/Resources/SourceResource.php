<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class SourceResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return ['source_id' => $this->id, 'publisher' => $this->publisher, 'title' => $this->title,
            'source_url' => $this->source_url, 'publication_year' => $this->publication_year,
            'observation_period' => $this->observation_period, 'license_note' => $this->license_note,
            'limitations' => $this->limitations, 'status' => $this->status];
    }
}
