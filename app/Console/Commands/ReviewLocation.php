<?php

namespace App\Console\Commands;

use App\Services\LocationReviewService;
use App\Services\OperatorTokenService;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Throwable;

#[Signature('gis:review-location {release} {facility} {review} {decision} {--reason=} {--expected-revision=} {--operation-id=} {--token-file=} {--confirm-facility-point}')]
#[Description('Record an evidence-backed location decision on a draft using an operator capability')]
class ReviewLocation extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(LocationReviewService $reviews, OperatorTokenService $tokens): int
    {
        try {
            $result = $reviews->decide($tokens->read((string) $this->option('token-file')), ['release_id' => $this->argument('release'), 'facility_code' => $this->argument('facility'), 'review_id' => $this->argument('review'), 'decision' => $this->argument('decision'), 'reason' => $this->option('reason'), 'expected_revision' => $this->option('expected-revision'), 'operation_id' => $this->option('operation-id'), 'confirmed_facility_point' => (bool) $this->option('confirm-facility-point')]);
            $this->line(json_encode($result, JSON_THROW_ON_ERROR));

            return self::SUCCESS;
        } catch (Throwable) {
            $this->error('Review rejected. Check capability, evidence, draft state, revision and operation identity. No review was committed by this request.');

            return self::FAILURE;
        }
    }
}
