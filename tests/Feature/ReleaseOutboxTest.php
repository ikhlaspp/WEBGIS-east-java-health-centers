<?php

namespace Tests\Feature;

use App\Services\ReleaseCache;
use App\Services\ReleaseOutboxService;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;
use Tests\GisDatabaseTestCase;

class ReleaseOutboxTest extends GisDatabaseTestCase
{
    private function event(): void
    {
        DB::update('UPDATE app.users SET is_admin=true');
        DB::insert("INSERT INTO app.operator_tokens(id,user_id,token_hash,abilities,expires_at) VALUES(?,?,?,'[\"publish\"]',now()+interval '1 hour')", [$this->id(70), $this->id(1), hash('sha256', str_repeat('A', 43))]);
        DB::insert("INSERT INTO app.audit_logs(id,actor_id,token_id,action,entity_type,entity_key,before_json,after_json,request_id) VALUES(?,?,?,'release.published','fixture',?,'{}','{}','fixture')", [$this->id(71), $this->id(1), $this->id(70), $this->id(6)]);
        DB::insert("INSERT INTO app.outbox_events(id,audit_id,event_type,payload,available_at) VALUES(?,?,'release.published',?::jsonb,clock_timestamp())", [$this->id(72), $this->id(71), json_encode(['release_id' => $this->id(6), 'analysis_run_id' => $this->id(73)])]);
    }

    private function claim(): ?array
    {
        DB::statement('SET LOCAL ROLE gis_publisher');
        $row = DB::selectOne('SELECT gis.claim_release_event(?) AS event', [str_repeat('A', 43)]);

        return $row->event === null ? null : json_decode($row->event, true);
    }

    public function test_lease_excludes_claimed_events_and_rejects_stale_acknowledgement(): void
    {
        $this->event();
        $first = $this->claim();
        $this->assertSame(1, $first['attempt']);
        $this->assertNull($this->claim());
        DB::statement('RESET ROLE');
        DB::update("UPDATE app.outbox_events SET available_at=clock_timestamp()-interval '1 second'");
        $second = $this->claim();
        $this->assertSame(2, $second['attempt']);
        try {
            DB::transaction(fn () => DB::selectOne('SELECT gis.finish_release_event(?,?::uuid,1,true)', [str_repeat('A', 43), $this->id(72)]));
            $this->fail('Stale attempt acknowledged.');
        } catch (QueryException $exception) {
            $this->assertSame('P4090', (string) $exception->getCode());
        }
        DB::selectOne('SELECT gis.finish_release_event(?,?::uuid,2,true)', [str_repeat('A', 43), $this->id(72)]);
        $this->assertNull($this->claim());
    }

    public function test_wrong_ability_and_unprivileged_roles_cannot_deliver_events(): void
    {
        $this->event();
        DB::update("UPDATE app.operator_tokens SET abilities='[\"review\"]'");
        foreach (['gis_publisher' => '28000', 'gis_runtime' => '42501', 'gis_worker' => '42501'] as $role => $state) {
            try {
                DB::transaction(function () use ($role): void {
                    DB::statement('SET LOCAL ROLE '.$role);
                    DB::selectOne('SELECT gis.claim_release_event(?)', [str_repeat('A', 43)]);
                });
                $this->fail('Unauthorized delivery accepted.');
            } catch (QueryException $exception) {
                $this->assertSame($state, (string) $exception->getCode());
            }
        }
    }

    public function test_dispatch_refuses_an_outer_transaction_before_cache_writes(): void
    {
        $this->event();
        $this->expectException(InvalidArgumentException::class);
        app(ReleaseOutboxService::class)->dispatch(str_repeat('A', 43));
    }

    public function test_committed_delivery_invalidates_payload_cache_and_retries_failure(): void
    {
        $this->event();
        $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
        DB::commit();
        $store = Cache::getFacadeRoot();
        try {
            $context = ['release' => (object) ['id' => $this->id(6)], 'run' => (object) ['id' => $this->id(73)], 'boundary' => (object) ['id' => $this->id(3)]];
            $cache = app(ReleaseCache::class);
            $this->assertSame(['old'], $cache->remember($context, 'points', [], fn () => ['old']));
            Cache::shouldReceive('forever')->once()->andReturn(false);
            $this->assertSame(['delivered' => 0, 'failed' => 1], app(ReleaseOutboxService::class)->dispatch(str_repeat('A', 43)));
            Cache::swap($store);
            $this->assertNull(DB::table('app.outbox_events')->value('delivered_at'));
            $this->assertSame('cache_delivery_failed', DB::table('app.outbox_events')->value('last_error'));
            DB::update("UPDATE app.outbox_events SET available_at=clock_timestamp()-interval '1 second'");
            $this->assertSame(['delivered' => 1, 'failed' => 0], app(ReleaseOutboxService::class)->dispatch(str_repeat('A', 43)));
            $this->assertSame(['new'], $cache->remember($context, 'points', [], fn () => ['new']));
            $this->assertSame(['delivered' => 0, 'failed' => 0], app(ReleaseOutboxService::class)->dispatch(str_repeat('A', 43)));
            $this->assertSame(2, DB::table('app.outbox_events')->value('attempts'));
            $this->assertSame(1, DB::table('app.audit_logs')->count());
        } finally {
            Cache::swap($store);
            DB::statement('RESET ROLE');
            $this->assertSame('gis_schema_testing', DB::selectOne('SELECT current_database() AS name')->name);
            $tables = DB::select("SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('app','gis','staging')");
            $names = array_map(fn ($row) => '"'.str_replace('"', '""', $row->schemaname).'"."'.str_replace('"', '""', $row->tablename).'"', $tables);
            DB::statement('TRUNCATE TABLE '.implode(',', $names).' RESTART IDENTITY');
            DB::insert('INSERT INTO app.active_release(singleton) VALUES(1)');
        }
    }
}
