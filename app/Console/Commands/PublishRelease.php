<?php

namespace App\Console\Commands;

use App\Services\OperatorTokenService;
use App\Services\ReleaseLifecycleService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use InvalidArgumentException;
use Throwable;

#[Signature('gis:publish {release} {--expected-version=} {--operation-id=} {--reason=} {--token-file=}')]
#[Description('Atomically publish an accepted release using a versioned active pointer')]
class PublishRelease extends Command
{
    public function handle(ReleaseLifecycleService $lifecycle, OperatorTokenService $tokens): int
    {
        try {
            $version = filter_var($this->option('expected-version'), FILTER_VALIDATE_INT);
            if ($version === false || $this->option('expected-version') === null) {
                throw new InvalidArgumentException('Expected pointer version required.');
            }
            $result = $lifecycle->publish($tokens->read((string) $this->option('token-file')), (string) $this->argument('release'), $version, (string) $this->option('operation-id'), (string) $this->option('reason'));
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Publication failed. Check capability, accepted release, artifact integrity, operation identity and expected active version.');

            return self::FAILURE;
        }
    }
}
