<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ReferenceApiRequest;
use App\Http\Resources\ReleaseResource;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;

class ReleaseController extends Controller
{
    public function __invoke(ReferenceApiRequest $request): JsonResponse
    {
        $active = DB::table('app.active_release')->where('singleton', 1)->value('release_id');
        $page = (int) $request->validated('page', 1);
        $perPage = (int) $request->validated('per_page', 50);
        $releases = DB::table('gis.dataset_releases')->where('status', 'published')->orderByDesc('published_at')->orderBy('id')
            ->paginate($perPage, ['id', 'label', 'boundary_set_id', 'default_analysis_run_id', 'facility_period', 'population_policy', 'area_policy', 'published_at'], 'page', $page);
        $data = [];
        foreach ($releases->items() as $release) {
            $release->active = $release->id === $active;
            $data[] = (new ReleaseResource($release))->resolve($request);
        }

        return response()->json(['data' => $data, 'meta' => ['active_release_id' => $active, 'page' => $page, 'per_page' => $perPage, 'total' => $releases->total(), 'last_page' => $releases->lastPage(), 'generated_at' => Carbon::now('UTC')->toRfc3339String()]]);
    }
}
