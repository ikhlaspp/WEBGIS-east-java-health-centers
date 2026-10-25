<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DB::statement('GRANT SELECT(source_id,coordinate_source_id) ON gis.facility_snapshots TO gis_runtime');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::statement('REVOKE SELECT(source_id,coordinate_source_id) ON gis.facility_snapshots FROM gis_runtime');
    }
};
