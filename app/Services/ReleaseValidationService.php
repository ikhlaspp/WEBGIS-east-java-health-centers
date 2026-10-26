<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use RuntimeException;

class ReleaseValidationService
{
    public function __construct(private AnalysisRunService $analysis) {}

    public function validate(#[\SensitiveParameter] string $token, string $releaseId, string $runId, int $revision, string $reason, bool $allowPartial = false): array
    {
        if (! Str::isUuid($releaseId) || ! Str::isUuid($runId) || $revision < 0 || mb_strlen(trim($reason)) < 10 || mb_strlen($reason) > 2000) {
            throw new InvalidArgumentException('Release/run UUIDs and a nonnegative expected revision are required.');
        }

        return DB::transaction(function () use ($token, $releaseId, $runId, $revision, $reason, $allowPartial): array {
            DB::statement('SET LOCAL ROLE gis_worker');
            DB::selectOne("SELECT actor_id FROM gis.operator_identity(?,'validate')", [$token]);
            $release = DB::selectOne('SELECT status,input_revision FROM gis.dataset_releases WHERE id=? FOR UPDATE', [$releaseId]);
            $run = DB::selectOne('SELECT status,input_revision,input_hash,parameters,code_revision FROM gis.analysis_runs WHERE id=? AND release_id=?', [$runId, $releaseId]);
            if ($release === null || $release->status !== 'draft' || (int) $release->input_revision !== $revision
                || $run === null || $run->status !== 'succeeded' || (int) $run->input_revision !== $revision) {
                throw new RuntimeException('Validation requires a current successful run belonging to this draft.');
            }
            $parameters = json_decode($run->parameters, true, 512, JSON_THROW_ON_ERROR);
            $fresh = $this->analysis->prepare($releaseId, $runId, $parameters['T'], $run->code_revision);
            if (! hash_equals($run->input_hash, $fresh['input_hash'])) {
                throw new RuntimeException('Analysis input hash is stale.');
            }
            $manifest = $this->analysis->verifyArtifacts($fresh, 'analysis/'.$runId);
            // Only the trusted CLI connection may assume this role after checking actual private files.
            DB::statement('SET LOCAL ROLE gis_artifact_verifier');
            $result = DB::selectOne('SELECT gis.validate_release(?,?::uuid,?::uuid,?::bigint,?::jsonb,?::boolean,?) AS result', [$token, $releaseId, $runId, $revision, json_encode($manifest, JSON_THROW_ON_ERROR), $allowPartial, $reason]);
            DB::statement('SET LOCAL ROLE gis_worker');

            return json_decode($result->result, true, 512, JSON_THROW_ON_ERROR);
        });
    }
}
