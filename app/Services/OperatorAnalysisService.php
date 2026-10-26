<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use RuntimeException;
use Symfony\Component\Process\Process;

class OperatorAnalysisService
{
    /**
     * Create a new class instance.
     */
    public function __construct(private AnalysisRunService $analysis) {}

    public function run(#[\SensitiveParameter] string $token, string $releaseId, string $runId, int $threshold, string $codeRevision): array
    {
        if (! Str::isUuid($releaseId) || ! Str::isUuid($runId) || $threshold < 1 || ! preg_match('/^[0-9a-f]{40}$/D', $codeRevision)) {
            throw new InvalidArgumentException('Explicit release/run UUIDs, positive threshold and code commit required.');
        }
        $prepared = DB::transaction(function () use ($token, $releaseId, $runId, $threshold, $codeRevision): array {
            DB::statement('SET LOCAL ROLE gis_worker');
            DB::selectOne("SELECT actor_id FROM gis.operator_identity(?,'analyze')", [$token]);

            return $this->analysis->prepare($releaseId, $runId, $threshold, $codeRevision);
        });
        $relative = 'analysis/'.$runId;
        $root = storage_path('app/private');
        if (! is_dir($root) && ! mkdir($root, 0700, true)) {
            throw new RuntimeException('Private storage unavailable.');
        }
        $input = $root.'/analysis-input-'.$runId.'.json';
        $encoded = json_encode($prepared, JSON_THROW_ON_ERROR);
        if (is_link($input) || is_link($root.'/analysis') || is_link($root.'/'.$relative)) {
            throw new RuntimeException('Analysis paths cannot be symbolic links.');
        }
        $ownedInput = false;
        if (is_file($input)) {
            if (! hash_equals(hash('sha256', $encoded), hash_file('sha256', $input))) {
                throw new RuntimeException('Run input file conflicts with current snapshot.');
            }
        } else {
            $handle = fopen($input, 'x');
            if ($handle === false) {
                throw new RuntimeException('Cannot create exclusive analysis input.');
            }
            try {
                if (fwrite($handle, $encoded) !== strlen($encoded)) {
                    throw new RuntimeException('Cannot write complete analysis input.');
                }
            } finally {
                fclose($handle);
            }
            $ownedInput = true;
        }
        try {
            if (! is_file($root.'/'.$relative.'/manifest.json')) {
                $python = config('gis.python_binary') ?: (PHP_OS_FAMILY === 'Windows' ? base_path('.venv/Scripts/python.exe') : 'python');
                $process = new Process([$python, base_path('scripts/analysis/export_layers.py'), '--input', $input, '--sha256', hash('sha256', $encoded), '--output-dir', $root.'/'.$relative], base_path());
                $process->setTimeout(600);
                $process->run();
                if (! $process->isSuccessful()) {
                    throw new RuntimeException('Python export failed; no successful analysis was persisted.');
                }
            }

            return DB::transaction(function () use ($token, $prepared, $relative): array {
                DB::statement('SET LOCAL ROLE gis_worker');
                $actor = DB::selectOne("SELECT actor_id FROM gis.operator_identity(?,'analyze')", [$token]);

                return $this->analysis->persist($prepared, $actor->actor_id, $relative, $token);
            });
        } finally {
            if ($ownedInput && is_file($input)) {
                unlink($input);
            }
        }
    }
}
