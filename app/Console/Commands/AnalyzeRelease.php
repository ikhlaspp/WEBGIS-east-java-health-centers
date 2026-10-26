<?php

namespace App\Console\Commands;

use App\Services\OperatorAnalysisService;
use App\Services\OperatorTokenService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Throwable;

#[Signature('gis:analyze {release} {--run-id=} {--threshold=30000} {--code-revision=} {--token-file=}')]
#[Description('Run private Python analysis and persist independently recomputed database results using an operator capability')]
class AnalyzeRelease extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(OperatorAnalysisService $analysis, OperatorTokenService $tokens): int
    {
        try {
            $threshold = filter_var($this->option('threshold'), FILTER_VALIDATE_INT);
            if ($threshold === false) {
                throw new \InvalidArgumentException('Invalid threshold.');
            }
            $result = $analysis->run($tokens->read((string) $this->option('token-file')), (string) $this->argument('release'), (string) $this->option('run-id'), $threshold, (string) $this->option('code-revision'));
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Analysis failed. Check private capability, draft inputs, run identity, Python environment and artifact integrity. No publication was performed.');

            return self::FAILURE;
        }
    }
}
