<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\MapStatisticsRequest;
use App\Services\PublicMapData;
use App\Services\ReleaseCache;
use App\Services\ReleaseContext;
use Illuminate\Http\JsonResponse;

class MapController extends Controller
{
    public function __invoke(MapStatisticsRequest $request, ReleaseContext $resolver, ReleaseCache $cache, PublicMapData $data): JsonResponse
    {
        $endpoint = match ($request->route()->getName()) {
            'api.v1.map.points' => 'points', 'api.v1.map.regions' => 'regions', 'api.v1.analysis.buffers' => 'buffers',
        };

        return $this->respond($endpoint, $request, $resolver, $cache, $data);
    }

    public function respond(string $endpoint, MapStatisticsRequest $request, ReleaseContext $resolver, ReleaseCache $cache, PublicMapData $data): JsonResponse
    {
        $context = $resolver->resolve($request->validated('release_id'), $request->validated('analysis_run_id'));
        $filters = $request->validated();
        $data->validateRegions($context, $filters);
        $payload = $cache->remember($context, $endpoint, $filters, fn () => $data->$endpoint($context, $filters));
        $payload['meta'] = [...$resolver->meta($context), ...$payload['meta']];

        return response()->json($payload);
    }
}
