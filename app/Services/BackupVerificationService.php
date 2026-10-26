<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use RuntimeException;

class BackupVerificationService
{
    public function verify(#[\SensitiveParameter] string $token, string $checkpoint): array
    {
        if (! Str::isUuid($checkpoint)) {
            throw new InvalidArgumentException('Explicit backup checkpoint UUID required.');
        }

        return DB::transaction(function () use ($token, $checkpoint): array {
            DB::statement('SET LOCAL ROLE gis_worker');
            DB::selectOne("SELECT actor_id FROM gis.operator_identity(?,'publish')", [$token]);
            $root = storage_path('app/private/backups');
            $directory = $root.'/'.$checkpoint;
            $manifestPath = $directory.'/manifest.json';
            if (is_link($root) || is_link($directory) || is_link($manifestPath) || ! is_file($manifestPath) || filesize($manifestPath) > 65536) {
                throw new RuntimeException('Private backup manifest unavailable.');
            }
            $raw = file_get_contents($manifestPath);
            $manifest = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
            if (($manifest['schema_version'] ?? null) !== 'backup-checkpoint-v1' || ($manifest['checkpoint_id'] ?? null) !== $checkpoint
                || ! is_array($manifest['files'] ?? null) || count($manifest['files']) !== 2) {
                throw new RuntimeException('Invalid backup manifest.');
            }
            $expected = ['database_snapshot' => 'database.snapshot', 'artifact_bundle' => 'artifacts.bundle'];
            $seen = [];
            foreach ($manifest['files'] as $file) {
                $kind = $file['kind'] ?? '';
                if (! isset($expected[$kind]) || isset($seen[$kind]) || ($file['path'] ?? null) !== $expected[$kind]) {
                    throw new RuntimeException('Invalid backup inventory.');
                }
                $path = $directory.'/'.$expected[$kind];
                if (is_link($path) || ! is_file($path) || ($file['bytes'] ?? 0) < 1 || filesize($path) !== $file['bytes']
                    || ! hash_equals(hash_file('sha256', $path), $file['sha256'] ?? '')) {
                    throw new RuntimeException('Backup bytes or digest mismatch.');
                }
                $seen[$kind] = true;
            }
            DB::statement('SET LOCAL ROLE gis_artifact_verifier');
            $result = DB::selectOne('SELECT gis.register_backup_checkpoint(?,?::jsonb,?) AS result', [$token, json_encode($manifest, JSON_THROW_ON_ERROR), hash('sha256', $raw)]);
            DB::statement('SET LOCAL ROLE gis_worker');

            return json_decode($result->result, true, 512, JSON_THROW_ON_ERROR);
        });
    }
}
