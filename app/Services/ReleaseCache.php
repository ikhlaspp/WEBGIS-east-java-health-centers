<?php

namespace App\Services;

use Closure;
use Illuminate\Support\Facades\Cache;

class ReleaseCache
{
    public function remember(array $context, string $endpoint, array $filters, Closure $loader): array
    {
        ksort($filters);
        $generation = Cache::get($this->generationKey($context['release']->id, $context['run']->id), 'initial');
        $key = 'public-map-v2:'.hash('sha256', json_encode([$context['release']->id, $context['run']->id, $context['boundary']->id, $endpoint, $filters, $generation], JSON_THROW_ON_ERROR));

        return Cache::remember($key, 300, $loader);
    }

    public function generationKey(string $releaseId, string $runId): string
    {
        return 'release-cache-generation:'.$releaseId.':'.$runId;
    }
}
