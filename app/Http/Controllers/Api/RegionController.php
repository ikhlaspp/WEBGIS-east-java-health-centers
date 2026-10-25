<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ReferenceApiRequest;
use App\Http\Resources\RegionResource;
use App\Services\ReleaseContext;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class RegionController extends Controller
{
    public function __invoke(ReferenceApiRequest $request, ReleaseContext $resolver): JsonResponse
    {
        $context = $resolver->resolve($request->validated('release_id'), $request->validated('analysis_run_id'));
        $level = $request->validated('level', 'regency');
        $boundary = $context['release']->boundary_set_id;
        if ($level === 'district') {
            $parent = DB::table('gis.regencies')->where('boundary_set_id', $boundary)->where('code', $request->validated('parent_code'))->first(['id', 'code']);
            if ($parent === null) {
                throw ValidationException::withMessages(['parent_code' => 'Parent region is not in this boundary edition.']);
            }
            $rows = DB::table('gis.districts')->where('boundary_set_id', $boundary)->where('regency_id', $parent->id)->orderBy('code')->get(['code', 'name']);
        } else {
            $rows = DB::table('gis.regencies')->where('boundary_set_id', $boundary)->orderBy('code')->get(['code', 'name']);
        }
        $data = [];
        foreach ($rows as $row) {
            $row->parent_code = $level === 'district' ? $parent->code : null;
            $row->level = $level;
            $row->edition = $context['boundary']->version;
            $data[] = (new RegionResource($row))->resolve($request);
        }

        return response()->json(['data' => $data, 'meta' => $resolver->meta($context)]);
    }
}
