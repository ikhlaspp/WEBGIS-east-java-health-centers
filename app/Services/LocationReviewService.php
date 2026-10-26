<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class LocationReviewService
{
    /**
     * Create a new class instance.
     */
    public function decide(#[\SensitiveParameter] string $token, array $request): array
    {
        $validated = Validator::make($request, [
            'release_id' => ['required', 'uuid'], 'facility_code' => ['required', 'string', 'regex:/^[0-9]{11}$/D'],
            'review_id' => ['required', 'uuid'], 'decision' => ['required', Rule::in(['accepted', 'rejected'])],
            'reason' => ['required', 'string', 'min:10', 'max:2000'], 'expected_revision' => ['required', 'integer', 'min:0'],
            'operation_id' => ['required', 'uuid'], 'confirmed_facility_point' => ['required', 'boolean'],
        ])->validate();

        return DB::transaction(function () use ($token, $validated): array {
            DB::statement('SET LOCAL ROLE gis_worker');
            $result = DB::selectOne('SELECT gis.review_location(?,?,?,?,?,?,?,?,?) AS result', [$token, $validated['release_id'], $validated['facility_code'], $validated['review_id'], $validated['decision'], $validated['reason'], $validated['expected_revision'], $validated['operation_id'], $validated['confirmed_facility_point']]);

            return json_decode($result->result, true, 512, JSON_THROW_ON_ERROR);
        });
    }
}
