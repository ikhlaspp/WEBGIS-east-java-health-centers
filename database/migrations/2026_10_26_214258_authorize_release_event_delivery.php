<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
GRANT CREATE ON SCHEMA gis TO gis_lifecycle_owner;
GRANT SELECT,UPDATE(attempts,available_at,delivered_at,last_error) ON app.outbox_events TO gis_lifecycle_owner;
CREATE FUNCTION gis.claim_release_event(raw_token text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
DECLARE event record;
BEGIN
 PERFORM gis.operator_identity(raw_token,'publish');
 SELECT * INTO event FROM app.outbox_events WHERE delivered_at IS NULL AND available_at<=clock_timestamp()
 AND event_type IN ('release.published','release.rolled_back') ORDER BY available_at,id FOR UPDATE SKIP LOCKED LIMIT 1;
 IF NOT FOUND THEN RETURN NULL; END IF;
 UPDATE app.outbox_events SET attempts=attempts+1,available_at=clock_timestamp()+interval '60 seconds',last_error=NULL WHERE id=event.id;
 RETURN jsonb_build_object('id',event.id,'payload',event.payload,'attempt',event.attempts+1);
END $fn$;
CREATE FUNCTION gis.finish_release_event(raw_token text,event_id uuid,attempt integer,success boolean) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $fn$
BEGIN
 PERFORM gis.operator_identity(raw_token,'publish');
 IF success IS NULL THEN RAISE EXCEPTION 'Explicit event outcome required' USING ERRCODE='22023'; END IF;
 UPDATE app.outbox_events SET delivered_at=CASE WHEN success THEN clock_timestamp() ELSE NULL END,
 available_at=CASE WHEN success THEN available_at ELSE clock_timestamp()+interval '30 seconds' END,
 last_error=CASE WHEN success THEN NULL ELSE 'cache_delivery_failed' END
 WHERE id=event_id AND attempts=attempt AND delivered_at IS NULL AND last_error IS NULL AND available_at>clock_timestamp()
 AND event_type IN ('release.published','release.rolled_back');
 IF NOT FOUND THEN RAISE EXCEPTION 'Stale event delivery lease' USING ERRCODE='P4090'; END IF;
 RETURN success;
END $fn$;
ALTER FUNCTION gis.claim_release_event(text) OWNER TO gis_lifecycle_owner;
ALTER FUNCTION gis.finish_release_event(text,uuid,integer,boolean) OWNER TO gis_lifecycle_owner;
REVOKE CREATE ON SCHEMA gis FROM gis_lifecycle_owner;
REVOKE ALL ON FUNCTION gis.claim_release_event(text),gis.finish_release_event(text,uuid,integer,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION gis.claim_release_event(text),gis.finish_release_event(text,uuid,integer,boolean) TO gis_publisher;
SQL);
    }

    public function down(): void
    {
        throw new RuntimeException('Outbox rollback requires a reviewed deployment plan.');
    }
};
