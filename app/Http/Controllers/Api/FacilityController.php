<?php

namespace App\Http\Controllers\Api;

use App\Exceptions\ApiException;
use App\Http\Controllers\Controller;
use App\Http\Requests\FacilityFilterRequest;
use App\Http\Resources\FacilityResource;
use App\Http\Resources\SourceResource;
use App\Services\ReleaseContext;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class FacilityController extends Controller
{
    public function index(FacilityFilterRequest $request, ReleaseContext $resolver): JsonResponse
    {
        $context = $resolver->resolve($request->validated('release_id'), $request->validated('analysis_run_id'));
        $boundary = $context['release']->boundary_set_id;
        $regency = $request->validated('regency_code');
        $district = $request->validated('district_code');
        if ($regency !== null && ! DB::table('gis.regencies')->where('boundary_set_id', $boundary)->where('code', $regency)->exists()) {
            throw ValidationException::withMessages(['regency_code' => 'Region is not in this boundary edition.']);
        }
        if ($district !== null) {
            $parent = DB::table('gis.districts as d')->join('gis.regencies as r', 'r.id', '=', 'd.regency_id')->where('d.boundary_set_id', $boundary)->where('d.code', $district)->value('r.code');
            if ($parent === null || ($regency !== null && $regency !== $parent)) {
                throw ValidationException::withMessages(['district_code' => 'District does not match the selected boundary edition or parent.']);
            }
        }
        $query = $this->query($context['release']->id);
        foreach (['service_type', 'area_type', 'coordinate_status'] as $filter) {
            if ($request->validated($filter) !== null) {
                $query->where('f.'.$filter, $request->validated($filter));
            }
        }
        if ($regency !== null) {
            $query->where('r.code', $regency);
        }
        if ($district !== null) {
            $query->where('d.code', $district);
        }
        $search = trim($request->validated('q') ?? '');
        if ($search !== '') {
            $pattern = '%'.strtr($search, ['!' => '!!', '%' => '!%', '_' => '!_']).'%';
            $query->where(function (Builder $nested) use ($pattern): void {
                foreach (['f.name', 'f.facility_code', 'f.address'] as $column) {
                    $nested->orWhereRaw($column." ILIKE ? ESCAPE '!'", [$pattern]);
                }
            });
        }
        $total = (clone $query)->count();
        $sort = $request->validated('sort', 'code');
        $query->orderBy(str_contains($sort, 'name') ? 'f.name' : 'f.facility_code', str_starts_with($sort, '-') ? 'desc' : 'asc')->orderBy('f.facility_code');
        $page = (int) $request->validated('page', 1);
        $perPage = (int) $request->validated('per_page', 50);
        $rows = $query->offset(($page - 1) * $perPage)->limit($perPage)->get();

        return response()->json(['data' => FacilityResource::collection($rows)->resolve($request), 'meta' => [...$resolver->meta($context), 'page' => $page, 'per_page' => $perPage, 'total' => $total]]);
    }

    public function show(FacilityFilterRequest $request, ReleaseContext $resolver, string $code): JsonResponse
    {
        $context = $resolver->resolve($request->validated('release_id'), $request->validated('analysis_run_id'));
        $row = $this->query($context['release']->id)->where('f.facility_code', $code)->addSelect('f.source_id', 'f.coordinate_source_id')->first();
        if ($row === null) {
            throw new ApiException(404, 'NOT_FOUND', 'Facility not found.');
        }
        $sources = collect($resolver->sources($context['release']->id, $context['release']->boundary_set_id))->keyBy('id');
        $data = (new FacilityResource($row))->resolve($request);
        foreach (['source' => $row->source_id, 'coordinate_source' => $row->coordinate_source_id] as $key => $id) {
            $data[$key] = $id !== null && $sources->has($id) ? (new SourceResource($sources->get($id)))->resolve($request) : null;
        }

        return response()->json(['data' => $data, 'meta' => $resolver->meta($context)]);
    }

    private function query(string $releaseId): Builder
    {
        return DB::table('gis.facility_snapshots as f')->join('gis.districts as d', 'd.id', '=', 'f.district_id')->join('gis.regencies as r', 'r.id', '=', 'd.regency_id')
            ->where('f.release_id', $releaseId)->select(['f.facility_code', 'f.name', 'f.address', 'f.service_type', 'f.area_type', 'f.coordinate_status', 'f.precision_level', 'd.code as district_code', 'd.name as district_name', 'r.code as regency_code', 'r.name as regency_name'])
            ->selectRaw('extensions.ST_X(f.location) AS longitude, extensions.ST_Y(f.location) AS latitude');
    }
}
