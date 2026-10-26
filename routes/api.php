<?php

use App\Http\Controllers\Api\FacilityController;
use App\Http\Controllers\Api\MapController;
use App\Http\Controllers\Api\RegionController;
use App\Http\Controllers\Api\ReleaseController;
use App\Http\Controllers\Api\SourceController;
use App\Http\Controllers\Api\StatisticsController;
use App\Http\Middleware\PublicApiContext;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->name('api.v1.')->middleware(['throttle:public-api', PublicApiContext::class])->group(function (): void {
    Route::get('releases', ReleaseController::class)->name('releases');
    Route::get('regions', RegionController::class)->name('regions');
    Route::get('sources', SourceController::class)->name('sources');
    Route::get('map/points', MapController::class)->name('map.points');
    Route::get('map/regions', MapController::class)->name('map.regions');
    Route::get('analysis/buffers', MapController::class)->name('analysis.buffers');
    Route::get('statistics', StatisticsController::class)->name('statistics');
    Route::get('facilities', [FacilityController::class, 'index'])->name('facilities.index');
    Route::get('facilities/{code}', [FacilityController::class, 'show'])->where('code', '[0-9]{11}')->name('facilities.show');
});
