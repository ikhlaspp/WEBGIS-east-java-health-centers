<?php

namespace App\Services;

use Closure;
use Illuminate\Support\Facades\Cache;

class ReleaseCache
{
    public function remember(array $context, string $endpoint, array $filters, Closure $loader): array
    {
        ksort($filters);
        $key = 'public-map-v1:'.hash('sha256', json_encode([$context['release']->id, $context['run']->id, $context['boundary']->id, $endpoint, $filters], JSON_THROW_ON_ERROR));

        return Cache::remember($key, 300, $loader);
    }
}
