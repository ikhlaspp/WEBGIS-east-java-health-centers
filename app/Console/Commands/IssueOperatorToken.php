<?php

namespace App\Console\Commands;

use App\Services\OperatorTokenService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Throwable;

#[Signature('gis:issue-token {email} {--abilities=} {--minutes=60}')]
#[Description('Privileged provisioning of an expiring operator capability into an owner-only private file')]
class IssueOperatorToken extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(OperatorTokenService $tokens): int
    {
        try {
            $minutes = filter_var($this->option('minutes'), FILTER_VALIDATE_INT);
            if ($minutes === false) {
                throw new \InvalidArgumentException('Invalid lifetime.');
            }
            $result = $tokens->issue((string) $this->argument('email'), explode(',', (string) $this->option('abilities')), $minutes);
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Capability issuance failed. Check admin identity, abilities, expiry, provisioning privileges and private file permissions.');

            return self::FAILURE;
        }
    }
}
