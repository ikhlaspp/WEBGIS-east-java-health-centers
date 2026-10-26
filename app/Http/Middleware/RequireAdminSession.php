<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Gate;
use Symfony\Component\HttpFoundation\Response;

class RequireAdminSession
{
    /**
     * Handle an incoming request.
     *
     * @param  Closure(Request): (Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (! Auth::check()) {
            return $request->expectsJson() ? response()->json(['message' => 'Unauthenticated.'], 401) : redirect()->route('login');
        }
        $started = $request->session()->get('admin_started_at');
        $last = $request->session()->get('admin_last_activity');
        if (! is_int($started) || ! is_int($last) || now()->timestamp - $started >= 28800 || now()->timestamp - $last >= 1800) {
            Auth::logout();
            $request->session()->invalidate();
            $request->session()->regenerateToken();

            return $request->expectsJson() ? response()->json(['message' => 'Session expired.'], 401) : redirect()->route('login');
        }
        Gate::authorize('operate-internal');
        $request->session()->put('admin_last_activity', now()->timestamp);

        return $next($request);
    }
}
