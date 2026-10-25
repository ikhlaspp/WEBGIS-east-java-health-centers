<?php

use App\Http\Controllers\Api\RegionController;
use App\Http\Controllers\Api\ReleaseController;
use App\Http\Controllers\Api\SourceController;
use App\Http\Middleware\PublicApiContext;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->name('api.v1.')->middleware(['throttle:public-api', PublicApiContext::class])->group(function (): void {
    Route::get('releases', ReleaseController::class)->name('releases');
    Route::get('regions', RegionController::class)->name('regions');
    Route::get('sources', SourceController::class)->name('sources');
});
