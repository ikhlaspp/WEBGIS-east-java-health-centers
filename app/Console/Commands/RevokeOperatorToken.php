<?php

namespace App\Console\Commands;

use App\Services\OperatorTokenService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Throwable;

#[Signature('gis:revoke-token {token-id}')]
#[Description('Revoke an operator capability using a privileged provisioning connection')]
class RevokeOperatorToken extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(OperatorTokenService $tokens): int
    {
        try {
            $changed = $tokens->revoke((string) $this->argument('token-id'));
            $this->info($changed ? 'Capability revoked.' : 'No active capability matched.');

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Capability revocation failed. Check token identity and provisioning privileges.');

            return self::FAILURE;
        }
    }
}
