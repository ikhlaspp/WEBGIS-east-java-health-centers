<?php

namespace App\Services;

use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;
use RuntimeException;
use Throwable;

class ReleaseOutboxService
{
    public function __construct(private ReleaseCache $cache) {}

    public function dispatch(#[\SensitiveParameter] string $token, int $limit = 50): array
    {
        if ($limit < 1 || $limit > 500 || DB::transactionLevel() !== 0) {
            throw new InvalidArgumentException('Outbox delivery requires a standalone transaction and a limit of 1 to 500.');
        }
        $result = ['delivered' => 0, 'failed' => 0];
        for ($index = 0; $index < $limit; $index++) {
            $event = DB::transaction(function () use ($token): ?array {
                DB::statement('SET LOCAL ROLE gis_publisher');
                $row = DB::selectOne('SELECT gis.claim_release_event(?) AS event', [$token]);

                return $row->event === null ? null : json_decode($row->event, true, 512, JSON_THROW_ON_ERROR);
            });
            if ($event === null) {
                break;
            }
            $success = false;
            try {
                $payload = $event['payload'];
                $success = Cache::forever($this->cache->generationKey($payload['release_id'], $payload['analysis_run_id']), $event['id']);
                if (! $success) {
                    throw new RuntimeException('Release cache invalidation failed.');
                }
            } catch (Throwable) {
                $success = false;
            }
            DB::transaction(function () use ($token, $event, $success): void {
                DB::statement('SET LOCAL ROLE gis_publisher');
                DB::selectOne('SELECT gis.finish_release_event(?,?::uuid,?::integer,?::boolean)', [$token, $event['id'], $event['attempt'], $success]);
            });
            $result[$success ? 'delivered' : 'failed']++;
        }

        return $result;
    }
}
