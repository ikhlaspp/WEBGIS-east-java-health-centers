<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\MapStatisticsRequest;
use App\Services\PublicMapData;
use App\Services\ReleaseCache;
use App\Services\ReleaseContext;
use Illuminate\Http\JsonResponse;

class StatisticsController extends Controller
{
    public function __invoke(MapStatisticsRequest $request, ReleaseContext $resolver, ReleaseCache $cache, PublicMapData $data): JsonResponse
    {
        return (new MapController)->respond('statistics', $request, $resolver, $cache, $data);
    }
}
