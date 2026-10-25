<?php

namespace App\Services;

use App\Exceptions\ApiException;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use stdClass;

class ReleaseContext
{
    public function resolve(?string $releaseId, ?string $runId): array
    {
        if ($releaseId === null) {
            $pointer = DB::table('app.active_release')->where('singleton', 1)->first(['release_id']);
            if ($pointer === null || $pointer->release_id === null) {
                throw new ApiException(503, 'NO_PUBLISHED_RELEASE', 'No published release is available.');
            }
            $releaseId = $pointer->release_id;
        }
        $release = DB::table('gis.dataset_releases')->where('id', $releaseId)->where('status', 'published')->first([
            'id', 'label', 'boundary_set_id', 'facility_period', 'population_policy', 'area_policy', 'default_analysis_run_id', 'published_at',
        ]);
        if ($release === null) {
            throw new ApiException(404, 'NOT_FOUND', 'Release not found.');
        }
        $runId ??= $release->default_analysis_run_id;
        $run = DB::table('gis.analysis_runs')->where('id', $runId)->where('release_id', $releaseId)->where('status', 'succeeded')->first(['id', 'method_version', 'parameters']);
        if ($run === null) {
            throw new ApiException(404, 'NOT_FOUND', 'Analysis run not found for this release.');
        }
        $boundary = DB::table('gis.boundary_sets')->where('id', $release->boundary_set_id)->first(['id', 'name', 'version', 'code_system', 'reference_year']);
        if ($boundary === null) {
            throw new ApiException(404, 'NOT_FOUND', 'Boundary edition not found.');
        }

        return ['release' => $release, 'run' => $run, 'boundary' => $boundary];
    }

    public function sources(string $releaseId, string $boundaryId): array
    {
        return DB::table('gis.data_sources as s')->where(function ($query) use ($releaseId, $boundaryId): void {
            $query->whereExists(function ($query) use ($releaseId): void {
                $query->selectRaw('1')->from('gis.release_sources as rs')->whereColumn('rs.source_id', 's.id')->where('rs.release_id', $releaseId);
            })->orWhereExists(function ($query) use ($boundaryId): void {
                $query->selectRaw('1')->from('gis.boundary_sets as b')->whereColumn('b.source_id', 's.id')->where('b.id', $boundaryId);
            });
        })->orderBy('s.publisher')->orderBy('s.title')->orderBy('s.id')->get(['s.id', 's.publisher', 's.title', 's.source_url', 's.publication_year', 's.observation_period', 's.license_note', 's.limitations', 's.status'])->all();
    }

    public function meta(array $context): array
    {
        $release = $context['release'];
        $counts = DB::selectOne("SELECT count(*) AS registered,count(location) AS mapped,count(*) FILTER(WHERE location IS NULL) AS missing,count(*) FILTER(WHERE coordinate_status='verified') AS verified FROM gis.facility_snapshots WHERE release_id=?", [$release->id]);
        $eligible = DB::table('gis.coverage_results')->where('run_id', $context['run']->id)->where('release_id', $release->id)->where('radius_m', 1000)->selectRaw('sum(eligible_count) AS eligible')->first();
        $years = DB::table('gis.district_indicators')->where('release_id', $release->id)->distinct()->orderBy('population_year')->orderBy('area_year')->get(['population_year', 'area_year']);
        $sources = $this->sources($release->id, $release->boundary_set_id);

        return [
            'release_id' => $release->id, 'analysis_run_id' => $context['run']->id, 'boundary_set_id' => $release->boundary_set_id,
            'source_periods' => ['facilities' => $release->facility_period, 'population_years' => $years->pluck('population_year')->unique()->values()->all(), 'area_years' => $years->pluck('area_year')->unique()->values()->all(), 'population_policy' => $release->population_policy, 'area_policy' => $release->area_policy],
            'boundary_edition' => ['name' => $context['boundary']->name, 'version' => $context['boundary']->version, 'code_system' => $context['boundary']->code_system, 'reference_year' => $context['boundary']->reference_year],
            'coordinate_coverage' => ['registered' => (int) $counts->registered, 'mapped' => (int) $counts->mapped, 'missing' => (int) $counts->missing, 'verified' => (int) $counts->verified, 'eligible' => $eligible?->eligible === null ? null : (int) $eligible->eligible],
            'warnings' => array_values(array_unique(array_filter(array_map(fn (stdClass $source) => $source->limitations, $sources)))),
            'generated_at' => Carbon::now('UTC')->toRfc3339String(),
        ];
    }
}
