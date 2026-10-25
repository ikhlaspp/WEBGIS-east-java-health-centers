<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class RegionResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return ['code' => $this->code, 'name' => $this->name, 'parent_code' => $this->parent_code,
            'level' => $this->level, 'edition' => $this->edition];
    }
}
