<?php

namespace Tests\Feature;

use App\Services\BackupVerificationService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use PHPUnit\Framework\Attributes\DataProvider;
use RuntimeException;
use Tests\GisDatabaseTestCase;

class BackupVerificationTest extends GisDatabaseTestCase
{
    private ?string $checkpoint = null;

    private function fixture(): array
    {
        DB::update('UPDATE app.users SET is_admin=true');
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"publish\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);
        $this->checkpoint = (string) Str::uuid();
        $directory = storage_path('app/private/backups/'.$this->checkpoint);
        mkdir($directory, 0700, true);
        $manifest = ['schema_version' => 'backup-checkpoint-v1', 'checkpoint_id' => $this->checkpoint, 'database_name' => 'gis_schema_testing', 'instance_id' => DB::table('app.backup_environment')->value('instance_id'), 'completed_at' => gmdate('c', time() - 60), 'files' => []];
        foreach (['database_snapshot' => 'database.snapshot', 'artifact_bundle' => 'artifacts.bundle'] as $kind => $file) {
            file_put_contents($directory.'/'.$file, 'Synthetic byte-verification fixture; not a real backup: '.$kind);
            $manifest['files'][] = ['kind' => $kind, 'path' => $file, 'bytes' => filesize($directory.'/'.$file), 'sha256' => hash_file('sha256', $directory.'/'.$file)];
        }
        $this->writeManifest($manifest);

        return $manifest;
    }

    private function writeManifest(array $manifest): void
    {
        file_put_contents(storage_path('app/private/backups/'.$this->checkpoint.'/manifest.json'), json_encode($manifest, JSON_THROW_ON_ERROR));
    }

    protected function tearDown(): void
    {
        if ($this->checkpoint !== null) {
            $directory = storage_path('app/private/backups/'.$this->checkpoint);
            foreach (['manifest.json', 'database.snapshot', 'artifacts.bundle'] as $file) {
                if (is_file($directory.'/'.$file)) {
                    unlink($directory.'/'.$file);
                }
            }
            rmdir($directory);
        }
        parent::tearDown();
    }

    public function test_verified_bytes_register_once_with_actor_and_immutable_evidence(): void
    {
        $this->fixture();
        $service = app(BackupVerificationService::class);
        $context = $service->context(str_repeat('A', 43));
        $this->assertSame('gis_schema_testing', $context['database_name']);
        $this->assertTrue(Str::isUuid($context['instance_id']));
        $this->assertFalse($service->verify(str_repeat('A', 43), $this->checkpoint)['replayed']);
        $this->assertTrue($service->verify(str_repeat('A', 43), $this->checkpoint)['replayed']);
        DB::statement('RESET ROLE');
        $row = DB::table('app.backup_checkpoints')->where('id', $this->checkpoint)->sole();
        $this->assertSame('gis_schema_testing', $row->database_name);
        $this->assertSame($this->id(1), $row->verified_by);
        $this->assertSame(1, DB::table('app.audit_logs')->where('action', 'backup.verified')->count());
        try {
            DB::transaction(fn () => DB::update('UPDATE app.backup_checkpoints SET completed_at=clock_timestamp() WHERE id=?', [$this->checkpoint]));
            $this->fail('Backup evidence was rewritten.');
        } catch (QueryException $exception) {
            $this->assertSame('23514', (string) $exception->getCode());
        }
    }

    public static function failures(): array
    {
        return array_map(fn ($case) => [$case], ['tampered', 'missing', 'stale', 'future', 'wrong_database', 'wrong_instance', 'wrong_ability']);
    }

    #[DataProvider('failures')]
    public function test_invalid_backup_evidence_is_not_registered(string $case): void
    {
        $manifest = $this->fixture();
        if ($case === 'tampered') {
            file_put_contents(storage_path('app/private/backups/'.$this->checkpoint.'/database.snapshot'), 'tampered');
        } elseif ($case === 'missing') {
            unlink(storage_path('app/private/backups/'.$this->checkpoint.'/artifacts.bundle'));
        } elseif ($case === 'wrong_ability') {
            DB::update("UPDATE app.operator_tokens SET abilities='[\"review\"]'");
        } elseif ($case === 'wrong_database') {
            $manifest['database_name'] = 'different_database';
        } elseif ($case === 'wrong_instance') {
            $manifest['instance_id'] = (string) Str::uuid();
        } else {
            $manifest['completed_at'] = gmdate('c', time() + ($case === 'future' ? 3600 : -90000));
        }
        $this->writeManifest($manifest);
        try {
            app(BackupVerificationService::class)->verify(str_repeat('A', 43), $this->checkpoint);
            $this->fail('Invalid backup registered.');
        } catch (QueryException|RuntimeException) {
            $this->addToAssertionCount(1);
        }
        DB::statement('RESET ROLE');
        $this->assertFalse(DB::table('app.backup_checkpoints')->where('id', $this->checkpoint)->exists());
        $this->assertSame(0, DB::table('app.audit_logs')->where('action', 'backup.verified')->count());
    }

    public function test_application_roles_cannot_forge_backup_attestation(): void
    {
        $manifest = $this->fixture();
        foreach (['gis_runtime', 'gis_worker', 'gis_publisher'] as $role) {
            try {
                DB::transaction(function () use ($role, $manifest): void {
                    DB::statement('SET LOCAL ROLE '.$role);
                    DB::selectOne('SELECT gis.register_backup_checkpoint(?,?::jsonb,?)', [str_repeat('A', 43), json_encode($manifest), str_repeat('a', 64)]);
                });
                $this->fail('Untrusted role attested backup files.');
            } catch (QueryException $exception) {
                $this->assertSame('42501', (string) $exception->getCode());
            }
        }
    }
}
