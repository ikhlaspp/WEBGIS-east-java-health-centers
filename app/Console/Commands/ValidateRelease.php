<?php

namespace App\Console\Commands;

use App\Services\OperatorTokenService;
use App\Services\ReleaseValidationService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use InvalidArgumentException;
use Throwable;

#[Signature('gis:validate {release} {--run-id=} {--expected-revision=} {--reason=} {--allow-partial} {--token-file=}')]
#[Description('Verify private artifacts and draft quality before freezing a release candidate')]
class ValidateRelease extends Command
{
    public function handle(ReleaseValidationService $validation, OperatorTokenService $tokens): int
    {
        try {
            $revision = filter_var($this->option('expected-revision'), FILTER_VALIDATE_INT);
            if ($revision === false || $this->option('expected-revision') === null) {
                throw new InvalidArgumentException('Expected revision required.');
            }
            $result = $validation->validate($tokens->read((string) $this->option('token-file')), (string) $this->argument('release'), (string) $this->option('run-id'), $revision, (string) $this->option('reason'), (bool) $this->option('allow-partial'));
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Validation failed. Check capability, verifier-role access, current draft/run, source quality and private artifact integrity.');

            return self::FAILURE;
        }
    }
}
