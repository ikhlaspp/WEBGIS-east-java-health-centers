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
        DB::statement("ALTER TABLE app.sessions ALTER COLUMN absolute_expires_at SET DEFAULT (now() + interval '8 hours')");
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::statement('ALTER TABLE app.sessions ALTER COLUMN absolute_expires_at DROP DEFAULT');
    }
};
