<?php

namespace App\Console\Commands;

use App\Services\BackupVerificationService;
use App\Services\OperatorTokenService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Throwable;

#[Signature('gis:verify-backup {checkpoint} {--token-file=}')]
#[Description('Verify private backup bytes and register a database-bound publication prerequisite')]
class VerifyBackup extends Command
{
    public function handle(BackupVerificationService $backups, OperatorTokenService $tokens): int
    {
        try {
            $result = $backups->verify($tokens->read((string) $this->option('token-file')), (string) $this->argument('checkpoint'));
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Backup verification failed. Check capability, private checkpoint files, database identity, completion time and hashes.');

            return self::FAILURE;
        }
    }
}
