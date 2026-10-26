<?php

namespace App\Services;

use App\Exceptions\ApiException;
use Illuminate\Database\Query\Builder;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class PublicMapData
{
    public function validateRegions(array $context, array $filters): void
    {
        $boundary = $context['boundary']->id;
        $parent = $filters['regency_code'] ?? $filters['parent_code'] ?? null;
        if ($parent !== null && ! DB::table('gis.regencies')->where('boundary_set_id', $boundary)->where('code', $parent)->exists()) {
            throw ValidationException::withMessages(['regency_code' => 'Region is not in this boundary edition.']);
        }
        if (isset($filters['district_code'])) {
            $actual = DB::table('gis.districts as d')->join('gis.regencies as r', 'r.id', '=', 'd.regency_id')->where('d.boundary_set_id', $boundary)->where('d.code', $filters['district_code'])->value('r.code');
            if ($actual === null || ($parent !== null && $parent !== $actual)) {
                throw ValidationException::withMessages(['district_code' => 'District does not match the boundary edition or parent.']);
            }
        }
    }

    private function scope(Builder $query, array $filters): Builder
    {
        if (isset($filters['regency_code']) || isset($filters['parent_code'])) {
            $query->where('r.code', $filters['regency_code'] ?? $filters['parent_code']);
        }
        if (isset($filters['district_code'])) {
            $query->where('d.code', $filters['district_code']);
        }

        return $query;
    }

    public function points(array $context, array $filters): array
    {
        $query = $this->scope(DB::table('gis.facility_snapshots as f')->join('gis.districts as d', 'd.id', '=', 'f.district_id')->join('gis.regencies as r', 'r.id', '=', 'd.regency_id')->where('f.release_id', $context['release']->id), $filters);
        foreach (['service_type', 'area_type', 'coordinate_status'] as $key) {
            if (isset($filters[$key])) {
                $query->where('f.'.$key, $filters[$key]);
            }
        }
        $search = trim($filters['q'] ?? '');
        if ($search !== '') {
            $pattern = '%'.strtr($search, ['!' => '!!', '%' => '!%', '_' => '!_']).'%';
            $query->where(function (Builder $nested) use ($pattern): void {
                foreach (['f.name', 'f.facility_code', 'f.address'] as $column) {
                    $nested->orWhereRaw($column." ILIKE ? ESCAPE '!'", [$pattern]);
                }
            });
        }
        $counts = (clone $query)->selectRaw("count(*) AS registered,count(f.location) AS mapped,count(*) FILTER(WHERE f.location IS NULL) AS missing,count(*) FILTER(WHERE f.coordinate_status='verified') AS verified")->first();
        $query->whereNotNull('f.location');
        if (isset($filters['bbox'])) {
            $query->whereRaw('extensions.ST_Intersects(f.location,extensions.ST_MakeEnvelope(?,?,?,?,4326))', array_map('floatval', explode(',', $filters['bbox'])));
        }
        $rows = $query->orderBy('f.facility_code')->get(['f.facility_code', 'f.name', 'f.coordinate_status', 'd.code as district_code', 'r.code as regency_code', DB::raw('extensions.ST_AsGeoJSON(f.location) AS geometry')]);
        $features = $rows->map(fn ($row) => ['type' => 'Feature', 'id' => $row->facility_code, 'geometry' => json_decode($row->geometry, true, 512, JSON_THROW_ON_ERROR), 'properties' => ['code' => $row->facility_code, 'name' => $row->name, 'coordinate_status' => $row->coordinate_status, 'district_code' => $row->district_code, 'regency_code' => $row->regency_code]])->all();

        return ['type' => 'FeatureCollection', 'features' => $features, 'meta' => ['filtered_registered' => (int) $counts->registered, 'filtered_mapped' => (int) $counts->mapped, 'filtered_missing' => (int) $counts->missing, 'filtered_verified' => (int) $counts->verified, 'filter_count' => (int) $counts->registered, 'view_count' => count($features)]];
    }

    private function indicators(array $context, array $filters): array
    {
        $rows = $this->scope(DB::table('gis.districts as d')->join('gis.regencies as r', 'r.id', '=', 'd.regency_id')
            ->leftJoin('gis.indicator_results as i', function ($join) use ($context): void {
                $join->on('i.district_id', '=', 'd.id')->where('i.run_id', $context['run']->id)->where('i.release_id', $context['release']->id);
            })->leftJoin('gis.district_indicators as s', function ($join) use ($context): void {
                $join->on('s.district_id', '=', 'd.id')->where('s.release_id', $context['release']->id);
            })->where('d.boundary_set_id', $context['boundary']->id), $filters)
            ->orderBy('d.code')->get(['d.id', 'd.code', 'd.name', 'r.code as regency_code', 'i.run_id', 'i.population', 'i.facility_count', 'i.density', 'i.population_per_facility', 'i.indicative_deficit', 'i.completeness', 'i.reason', 's.area_km2'])->all();
        foreach ($rows as $row) {
            if ($row->run_id === null) {
                throw new ApiException(503, 'INCOMPLETE_ANALYSIS', 'Stored analysis results are incomplete.');
            }
        }

        return $rows;
    }

    private function aggregate(array $rows): array
    {
        $facilities = array_sum(array_map(fn ($r) => (int) $r->facility_count, $rows));
        $completePopulation = count(array_filter($rows, fn ($r) => $r->population === null)) === 0 && count($rows) > 0;
        $completeArea = count(array_filter($rows, fn ($r) => $r->area_km2 === null)) === 0 && count($rows) > 0;
        $population = $completePopulation ? array_sum(array_map(fn ($r) => (int) $r->population, $rows)) : null;
        $area = $completeArea ? array_sum(array_map(fn ($r) => (float) $r->area_km2, $rows)) : null;
        $deficitComplete = count(array_filter($rows, fn ($r) => $r->indicative_deficit === null)) === 0 && count($rows) > 0;

        return ['facility_count' => $facilities, 'population' => $population, 'area_km2' => $area,
            'population_per_facility' => $population !== null && $facilities > 0 ? $population / $facilities : null,
            'density' => $population !== null && $area > 0 ? $population / $area : null,
            'facilities_per_30000' => $population > 0 ? $facilities * 30000 / $population : null,
            'indicative_deficit' => $deficitComplete ? array_sum(array_map(fn ($r) => (int) $r->indicative_deficit, $rows)) : null,
            'without_facility' => $facilities === 0, 'district_count' => count($rows),
            'completeness' => $completePopulation && $completeArea ? 'complete' : 'partial',
            'reason' => $completePopulation && $completeArea ? null : 'MISSING_SOURCE_DATA'];
    }

    public function statistics(array $context, array $filters): array
    {
        $parameters = json_decode($context['run']->parameters, true, 512, JSON_THROW_ON_ERROR);

        return ['data' => [...$this->aggregate($this->indicators($context, $filters)), 'T' => $parameters['T'] ?? null], 'meta' => []];
    }

    public function regions(array $context, array $filters): array
    {
        $level = $filters['level'] ?? 'regency';
        $metric = ($filters['metric'] ?? 'count') === 'count' ? 'facility_count' : $filters['metric'];
        $detail = $filters['geometry_detail'] ?? 'display';
        $rows = $this->indicators($context, $filters);
        $query = DB::table($level === 'district' ? 'gis.districts' : 'gis.regencies')->where('boundary_set_id', $context['boundary']->id);
        if ($level === 'district') {
            $query->whereIn('id', array_map(fn ($r) => $r->id, $rows));
        }
        $geometry = $detail === 'full' ? 'geom' : 'COALESCE(geom_display,geom)';
        $boundaries = $query->orderBy('code')->get(['code', 'name', DB::raw('extensions.ST_AsGeoJSON('.$geometry.') AS geometry'), DB::raw('geom_display IS NULL AS display_fallback')]);
        $legend = json_decode(file_get_contents(resource_path('analysis-legends.json')), true, 512, JSON_THROW_ON_ERROR)[$metric];
        $features = [];
        foreach ($boundaries as $boundary) {
            $members = array_values(array_filter($rows, fn ($r) => ($level === 'district' ? $r->code : $r->regency_code) === $boundary->code));
            $values = $this->aggregate($members);
            $value = $values[$metric];
            if ($level === 'district' && count($members) === 1) {
                $stored = $members[0]->$metric;
                $value = $stored === null ? null : (in_array($metric, ['facility_count', 'indicative_deficit'], true) ? (int) $stored : (float) $stored);
            }
            $class = 'no_data';
            if ($value !== null) {
                $class = count($legend['upper_bounds']);
                foreach ($legend['upper_bounds'] as $index => $upper) {
                    if ($value <= $upper) {
                        $class = $index;
                        break;
                    }
                }
            }
            $features[] = ['type' => 'Feature', 'id' => $boundary->code, 'geometry' => json_decode($boundary->geometry, true, 512, JSON_THROW_ON_ERROR), 'properties' => ['code' => $boundary->code, 'name' => $boundary->name, 'value' => $value, 'metric' => $metric, 'class' => $class, 'without_facility' => $values['without_facility'], 'completeness' => $values['completeness'], 'reason' => $values['reason'], 'geometry_detail_used' => $detail === 'full' || $boundary->display_fallback ? 'full' : 'display']];
        }

        return ['type' => 'FeatureCollection', 'features' => $features, 'meta' => ['level' => $level, 'metric' => $metric, 'geometry_detail' => $detail, 'legend' => $legend]];
    }

    public function buffers(array $context, array $filters): array
    {
        $rows = $this->scope(DB::table('gis.coverage_results as c')->join('gis.districts as d', 'd.id', '=', 'c.district_id')->join('gis.regencies as r', 'r.id', '=', 'd.regency_id')->where('c.release_id', $context['release']->id)->where('c.run_id', $context['run']->id)->where('c.radius_m', $filters['radius_m']), $filters)
            ->orderBy('d.code')->get(['d.code', 'd.name', 'c.radius_m', 'c.covered_area_m2', 'c.geometry_area_m2', 'c.coverage_pct', 'c.registered_count', 'c.eligible_count', 'c.excluded_count', 'c.contributing_count', 'c.completeness', 'c.reason', DB::raw('extensions.ST_AsGeoJSON(c.geom) AS geometry')]);
        $expected = count($this->indicators($context, $filters));
        if ($rows->count() !== $expected) {
            throw new ApiException(503, 'INCOMPLETE_ANALYSIS', 'Stored coverage results are incomplete.');
        }
        $features = [];
        foreach ($rows as $row) {
            $properties = ['code' => $row->code, 'name' => $row->name, 'completeness' => $row->completeness, 'reason' => $row->reason];
            foreach (['radius_m', 'registered_count', 'eligible_count', 'excluded_count', 'contributing_count'] as $key) {
                $properties[$key] = (int) $row->$key;
            }
            foreach (['covered_area_m2', 'geometry_area_m2', 'coverage_pct'] as $key) {
                $properties[$key] = $row->$key === null ? null : (float) $row->$key;
            }
            $features[] = ['type' => 'Feature', 'id' => $row->code, 'geometry' => $row->geometry === null ? null : json_decode($row->geometry, true, 512, JSON_THROW_ON_ERROR), 'properties' => $properties];
        }

        return ['type' => 'FeatureCollection', 'features' => $features, 'meta' => ['radius_m' => (int) $filters['radius_m'], 'geometry_detail' => $filters['geometry_detail'] ?? 'display', 'geometry_detail_used' => 'full', 'geometry_note' => 'Stored full coverage geometry; no request-time simplification.']];
    }
}
