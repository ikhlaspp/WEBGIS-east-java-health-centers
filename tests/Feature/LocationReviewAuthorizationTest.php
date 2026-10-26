<?php

namespace Tests\Feature;

use App\Services\LocationReviewService;
use App\Services\OperatorTokenService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Tests\GisDatabaseTestCase;

class LocationReviewAuthorizationTest extends GisDatabaseTestCase
{
    private function fixture(): array
    {
        DB::update('UPDATE app.users SET is_admin=true');
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"review\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);
        DB::insert("INSERT INTO gis.geocode_reviews(id,release_id,facility_code,source_id,candidate_location,provider,query,precision_level,result_status,evidence_url,evidence_note,decision_reason) VALUES(?,?,'35010100001',?,extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),'fixture','synthetic','facility','pending','https://example.test/evidence','synthetic evidence','')", [$this->id(7), $this->id(6), $this->id(2)]);

        return ['release_id' => $this->id(6), 'facility_code' => '35010100001', 'review_id' => $this->id(7), 'decision' => 'accepted', 'reason' => 'Synthetic facility evidence checked', 'expected_revision' => (int) DB::table('gis.dataset_releases')->where('id', $this->id(6))->value('input_revision'), 'operation_id' => $this->id(80), 'confirmed_facility_point' => true];
    }

    private function rejected(callable $operation, string $state): void
    {
        try {
            DB::transaction($operation);
            $this->fail('Invalid operation succeeded.');
        } catch (QueryException $exception) {
            $this->assertSame($state, (string) $exception->getCode());
        }
    }

    public function test_worker_review_is_evidenced_audited_and_idempotent(): void
    {
        $request = $this->fixture();
        $service = app(LocationReviewService::class);
        $result = $service->decide(str_repeat('A', 43), $request);
        $this->assertFalse($result['replayed']);
        $this->assertTrue($service->decide(str_repeat('A', 43), $request)['replayed']);
        DB::statement('RESET ROLE');
        $snapshot = DB::table('gis.facility_snapshots')->first();
        $this->assertSame('verified', $snapshot->coordinate_status);
        $this->assertSame($this->id(7), $snapshot->selected_review_id);
        $review = DB::table('gis.geocode_reviews')->first();
        $this->assertSame($this->id(1), $review->reviewed_by);
        $this->assertSame($request['reason'], $review->decision_reason);
        $this->assertGreaterThan($request['expected_revision'], $result['input_revision']);
        $this->assertNull(DB::table('gis.dataset_releases')->value('quality_report_id'));
        $audit = DB::table('app.audit_logs')->sole();
        $this->assertSame($this->id(70), $audit->token_id);
        $this->assertStringNotContainsString(str_repeat('A', 43), json_encode($audit));
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), [...$request, 'reason' => 'Different decision reason']), '23505');
    }

    public function test_fake_expired_revoked_wrong_ability_and_inactive_tokens_are_denied(): void
    {
        $request = $this->fixture();
        $service = app(LocationReviewService::class);
        $this->rejected(fn () => $service->decide(str_repeat('B', 43), $request), '28000');
        foreach (["abilities='[\"publish\"]'", 'revoked_at=now()', "created_at=now()-interval '2 hours',expires_at=now()-interval '1 hour'"] as $change) {
            DB::beginTransaction();
            DB::update('UPDATE app.operator_tokens SET '.$change);
            $this->rejected(fn () => $service->decide(str_repeat('A', 43), $request), '28000');
            DB::rollBack();
        }
        DB::update('UPDATE app.users SET is_active=false');
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), $request), '28000');
    }

    public function test_stale_revision_and_wrong_facility_identity_leave_evidence_unchanged(): void
    {
        $request = $this->fixture();
        $service = app(LocationReviewService::class);
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), [...$request, 'expected_revision' => 0]), '40001');
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), [...$request, 'facility_code' => '35010100002']), '23514');
        $this->assertSame('pending', DB::table('gis.geocode_reviews')->value('result_status'));
        $this->assertSame(0, DB::table('app.audit_logs')->count());
    }

    public function test_acceptance_requires_confirmation_evidence_and_assigned_boundary(): void
    {
        $request = $this->fixture();
        $service = app(LocationReviewService::class);
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), [...$request, 'confirmed_facility_point' => false]), '23514');
        DB::update('UPDATE gis.geocode_reviews SET candidate_location=extensions.ST_SetSRID(extensions.ST_MakePoint(114,-7.5),4326)');
        $request['expected_revision'] = (int) DB::table('gis.dataset_releases')->value('input_revision');
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), $request), '23514');
        DB::update("UPDATE gis.geocode_reviews SET candidate_location=extensions.ST_SetSRID(extensions.ST_MakePoint(112.5,-7.5),4326),evidence_url=NULL,evidence_note=''");
        $request['expected_revision'] = (int) DB::table('gis.dataset_releases')->value('input_revision');
        $this->rejected(fn () => $service->decide(str_repeat('A', 43), $request), '23514');
    }

    public function test_rejection_is_audited_without_creating_verified_coordinates(): void
    {
        $request = $this->fixture();
        app(LocationReviewService::class)->decide(str_repeat('A', 43), [...$request, 'decision' => 'rejected', 'confirmed_facility_point' => false]);
        DB::statement('RESET ROLE');
        $this->assertSame('rejected', DB::table('gis.geocode_reviews')->value('result_status'));
        $this->assertSame('missing', DB::table('gis.facility_snapshots')->value('coordinate_status'));
        $this->assertSame(1, DB::table('app.audit_logs')->count());
        $this->rejected(fn () => DB::update("UPDATE gis.geocode_reviews SET result_status='pending'"), '23514');
    }

    public function test_runtime_and_publisher_cannot_review_and_worker_cannot_write_decisions_directly(): void
    {
        $this->fixture();
        foreach (['gis_runtime', 'gis_publisher'] as $role) {
            $this->rejected(function () use ($role): void {
                DB::statement('SET LOCAL ROLE '.$role);
                DB::selectOne("SELECT gis.review_location(?,?,'35010100001',?,'accepted','synthetic evidence',2,?,true)", [str_repeat('A', 43), $this->id(6), $this->id(7), $this->id(80)]);
            }, '42501');
        }
        $this->rejected(function (): void {
            DB::statement('SET LOCAL ROLE gis_worker');
            DB::update("UPDATE gis.geocode_reviews SET result_status='accepted'");
        }, '42501');
    }

    public function test_validated_release_cannot_receive_reviews(): void
    {
        $request = $this->fixture();
        DB::update("UPDATE gis.dataset_releases SET status='validated'");
        $this->rejected(fn () => app(LocationReviewService::class)->decide(str_repeat('A', 43), $request), '23514');
    }

    public function test_provisioned_token_is_private_hashed_and_revocable(): void
    {
        DB::update('UPDATE app.users SET is_admin=true');
        $service = app(OperatorTokenService::class);
        $issued = $service->issue('fixture@example.test', ['review'], 30);
        try {
            $token = $service->read($issued['token_file']);
            $row = DB::table('app.operator_tokens')->where('id', $issued['token_id'])->first();
            $this->assertSame(hash('sha256', $token), $row->token_hash);
            $this->assertStringNotContainsString($token, json_encode($issued));
            $this->assertTrue($service->revoke($issued['token_id']));
            $this->assertFalse($service->revoke($issued['token_id']));
        } finally {
            unlink($issued['token_file']);
        }
    }
}
