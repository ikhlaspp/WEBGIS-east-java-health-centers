<?php

namespace App\Console\Commands;

use App\Services\OperatorTokenService;
use App\Services\ReleaseOutboxService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use InvalidArgumentException;
use Throwable;

#[Signature('gis:dispatch-release-events {--limit=50} {--token-file=}')]
#[Description('Retry committed release events and invalidate versioned map cache entries')]
class DispatchReleaseEvents extends Command
{
    public function handle(ReleaseOutboxService $outbox, OperatorTokenService $tokens): int
    {
        try {
            $limit = filter_var($this->option('limit'), FILTER_VALIDATE_INT);
            if ($limit === false) {
                throw new InvalidArgumentException('Invalid batch limit.');
            }
            $result = $outbox->dispatch($tokens->read((string) $this->option('token-file')), $limit);
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return $result['failed'] === 0 ? self::SUCCESS : self::FAILURE;
        } catch (Throwable) {
            $this->error('Event delivery failed. Check publish capability, database access and cache availability. Pending events remain retryable.');

            return self::FAILURE;
        }
    }
}
