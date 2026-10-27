<?php

use App\Http\Controllers\Auth\AdminSessionController;
use App\Http\Middleware\PublicApiContext;
use App\Http\Middleware\RequireAdminSession;
use Illuminate\Support\Facades\Route;

Route::view('/', 'home')->name('home');
Route::view('/peta', 'map')->name('map');
Route::get('/puskesmas/{code}', fn (string $code) => view('facility', ['code' => $code]))->where('code', '[0-9]{11}')->name('facility');

Route::view('/admin/login', 'auth.login')->name('login');
Route::middleware(PublicApiContext::class)->group(function (): void {
    Route::post('/admin/login', [AdminSessionController::class, 'store'])->name('admin.login');
    Route::post('/admin/logout', [AdminSessionController::class, 'destroy'])->name('admin.logout');
    Route::view('/admin', 'auth.admin')->middleware(RequireAdminSession::class)->name('admin.home');
});
