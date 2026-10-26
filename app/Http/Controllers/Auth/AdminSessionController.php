<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Http\Requests\AdminLoginRequest;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\HttpException;

class AdminSessionController extends Controller
{
    public function store(AdminLoginRequest $request): RedirectResponse
    {
        $key = 'admin-login:'.hash('sha256', $request->validated('email').'|'.$request->ip());
        if (RateLimiter::tooManyAttempts($key, 5)) {
            throw new HttpException(429, 'Too many login attempts.', null, ['Retry-After' => (string) RateLimiter::availableIn($key)]);
        }
        if (! Auth::attempt([...$request->safe()->only(['email', 'password']), 'is_active' => true, 'is_admin' => true], false)) {
            RateLimiter::hit($key, 60);
            throw ValidationException::withMessages(['email' => 'The supplied credentials could not be authenticated.']);
        }
        RateLimiter::clear($key);
        $request->session()->regenerate();
        $request->session()->put(['admin_started_at' => now()->timestamp, 'admin_last_activity' => now()->timestamp]);

        return redirect()->route('admin.home');
    }

    public function destroy(Request $request): RedirectResponse
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('login');
    }
}
