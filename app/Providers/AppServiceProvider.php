<?php

namespace App\Providers;

use App\Auth\RuntimeUserProvider;
use App\Models\User;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Gate;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        Auth::provider('gis-runtime', fn ($app, array $config) => new RuntimeUserProvider($app['hash'], $config['model']));
        Gate::define('operate-internal', fn (User $user): bool => $user->is_active && $user->is_admin);
        RateLimiter::for('public-api', function (Request $request) {
            return Limit::perMinute(max(1, (int) config('gis.public_api_rate_limit', 60)))->by($request->ip());
        });
    }
}
