<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use RuntimeException;

class ReleaseLifecycleService
{
    public function __construct(private AnalysisRunService $analysis) {}

    public function publish(#[\SensitiveParameter] string $token, string $releaseId, int $expectedVersion, string $operationId, string $reason): array
    {
        return $this->activate($token, $releaseId, $expectedVersion, $operationId, $reason, 'publish');
    }

    public function rollback(#[\SensitiveParameter] string $token, string $releaseId, int $expectedVersion, string $operationId, string $reason): array
    {
        return $this->activate($token, $releaseId, $expectedVersion, $operationId, $reason, 'rollback');
    }

    private function activate(#[\SensitiveParameter] string $token, string $releaseId, int $expectedVersion, string $operationId, string $reason, string $ability): array
    {
        if (! Str::isUuid($releaseId) || ! Str::isUuid($operationId) || $expectedVersion < 0 || mb_strlen(trim($reason)) < 10 || mb_strlen($reason) > 2000) {
            throw new InvalidArgumentException('Release/operation UUIDs, expected pointer version and publication reason are required.');
        }
        $manifest = DB::transaction(function () use ($token, $releaseId, $ability): array {
            DB::statement('SET LOCAL ROLE gis_worker');
            DB::selectOne('SELECT actor_id FROM gis.operator_identity(?,?)', [$token, $ability]);
            $run = DB::selectOne('SELECT a.id,a.parameters,a.code_revision,a.input_hash FROM gis.dataset_releases r JOIN gis.analysis_runs a ON a.id=r.default_analysis_run_id AND a.release_id=r.id WHERE r.id=?', [$releaseId]);
            if ($run === null) {
                throw new RuntimeException('Accepted default analysis required.');
            }
            $parameters = json_decode($run->parameters, true, 512, JSON_THROW_ON_ERROR);
            $fresh = $this->analysis->prepare($releaseId, $run->id, $parameters['T'], $run->code_revision, true);
            if (! hash_equals($run->input_hash, $fresh['input_hash'])) {
                throw new RuntimeException('Frozen analysis input hash mismatch.');
            }

            return $this->analysis->verifyArtifacts($fresh, 'analysis/'.$run->id);
        });

        // Release read locks end before the finalizer acquires pointer then candidate locks.
        return DB::transaction(function () use ($token, $releaseId, $expectedVersion, $operationId, $reason, $manifest, $ability): array {
            DB::statement('SET LOCAL ROLE gis_artifact_verifier');
            $function = $ability === 'publish' ? 'gis.publish_release' : 'gis.rollback_release';
            $result = DB::selectOne('SELECT '.$function.'(?,?::uuid,?::bigint,?::uuid,?,?::jsonb) AS result', [$token, $releaseId, $expectedVersion, $operationId, $reason, json_encode($manifest, JSON_THROW_ON_ERROR)]);
            DB::statement('SET LOCAL ROLE gis_publisher');

            return json_decode($result->result, true, 512, JSON_THROW_ON_ERROR);
        });
    }
}
