<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ReferenceApiRequest;
use App\Http\Resources\SourceResource;
use App\Services\ReleaseContext;
use Illuminate\Http\JsonResponse;

class SourceController extends Controller
{
    public function __invoke(ReferenceApiRequest $request, ReleaseContext $resolver): JsonResponse
    {
        $context = $resolver->resolve($request->validated('release_id'), $request->validated('analysis_run_id'));
        $data = array_map(fn ($source) => (new SourceResource($source))->resolve($request), $resolver->sources($context['release']->id, $context['release']->boundary_set_id));

        return response()->json(['data' => $data, 'meta' => $resolver->meta($context)]);
    }
}
