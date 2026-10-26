<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Session\DatabaseSessionHandler;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\RateLimiter;
use Tests\GisDatabaseTestCase;

class AdminAuthenticationTest extends GisDatabaseTestCase
{
    private function credentials(): array
    {
        DB::update('UPDATE app.users SET is_admin=true,password_hash=? WHERE id=?', [Hash::make('synthetic-password'), $this->id(1)]);
        RateLimiter::clear('admin-login:'.hash('sha256', 'fixture@example.test|127.0.0.1'));

        return ['email' => 'fixture@example.test', 'password' => 'synthetic-password'];
    }

    public function test_admin_login_rotates_session_and_logout_invalidates_it(): void
    {
        $credentials = $this->credentials();
        $this->get('/admin/login')->assertOk();
        $before = session()->getId();
        $this->post('/admin/login', $credentials)->assertRedirect('/admin');
        $this->assertNotSame($before, session()->getId());
        $this->assertAuthenticatedAs(Auth::user());
        $this->assertSame('gis_runtime', DB::selectOne('SELECT current_user AS role')->role);
        $this->get('/admin')->assertOk()->assertSee('Fixture')->assertDontSee('password_hash');
        $token = session()->token();
        $this->post('/admin/logout')->assertRedirect('/admin/login');
        $this->assertGuest();
        $this->assertNotSame($token, session()->token());
        $this->getJson('/admin')->assertUnauthorized();
    }

    public function test_guest_is_redirected_and_has_no_public_registration_or_profile_write(): void
    {
        $this->get('/admin')->assertRedirect('/admin/login');
        $this->getJson('/admin')->assertUnauthorized();
        $this->postJson('/register', [])->assertNotFound();
        $this->patchJson('/admin/profile', ['is_admin' => true])->assertNotFound();
        $this->getJson('/api/v1/regions?release_id='.$this->id(6))->assertNotFound();
    }

    public function test_failed_login_is_generic_and_limited_after_five_attempts(): void
    {
        $credentials = $this->credentials();
        $credentials['password'] = 'wrong-password';
        for ($attempt = 0; $attempt < 5; $attempt++) {
            $this->postJson('/admin/login', $credentials)->assertUnprocessable()->assertJsonPath('errors.email.0', 'The supplied credentials could not be authenticated.');
        }
        $this->postJson('/admin/login', $credentials)->assertStatus(429)->assertHeader('Retry-After');
        $this->assertGuest();
    }

    public function test_non_admin_and_disabled_accounts_cannot_login_or_elevate_roles(): void
    {
        $credentials = $this->credentials();
        DB::update('UPDATE app.users SET is_admin=false');
        $this->postJson('/admin/login', $credentials)->assertUnprocessable();
        $this->postJson('/admin/login', [...$credentials, 'is_admin' => true])->assertUnprocessable();
        $this->assertGuest();
        DB::statement('RESET ROLE');
        DB::update('UPDATE app.users SET is_admin=true,is_active=false');
        $this->postJson('/admin/login', $credentials)->assertUnprocessable();
        $model = new User;
        $model->forceFill(['is_admin' => false, 'is_active' => false]);
        $model->fill(['is_admin' => true, 'is_active' => true]);
        $this->assertFalse($model->is_admin);
        $this->assertFalse($model->is_active);
    }

    public function test_idle_and_absolute_expiry_invalidate_sessions(): void
    {
        $credentials = $this->credentials();
        foreach ([['admin_last_activity' => now()->timestamp - 1800], ['admin_started_at' => now()->timestamp - 28800]] as $expiry) {
            $this->post('/admin/login', $credentials)->assertRedirect('/admin');
            $this->withSession($expiry)->getJson('/admin')->assertUnauthorized();
            $this->assertGuest();
        }
    }

    public function test_revoked_admin_role_is_rechecked_on_the_next_request(): void
    {
        $this->post('/admin/login', $this->credentials())->assertRedirect('/admin');
        DB::statement('RESET ROLE');
        DB::update('UPDATE app.users SET is_active=false');
        Auth::forgetGuards();
        $this->getJson('/admin')->assertForbidden();
    }

    public function test_database_session_handler_can_write_under_runtime_permissions(): void
    {
        DB::statement('SET LOCAL ROLE gis_runtime');
        $handler = new DatabaseSessionHandler(DB::connection(), 'app.sessions', 30, app());
        $handler->write('synthetic-session', 'synthetic-payload');
        $this->assertSame('synthetic-payload', $handler->read('synthetic-session'));
        $this->assertNotNull(DB::table('app.sessions')->where('id', 'synthetic-session')->value('absolute_expires_at'));
        $handler->destroy('synthetic-session');
        $this->assertSame('', $handler->read('synthetic-session'));
    }

    public function test_private_provisioning_hashes_password_and_refuses_existing_accounts(): void
    {
        $this->artisan('gis:provision-admin', ['email' => 'new-admin@example.test', '--name' => 'Synthetic Admin'])
            ->expectsQuestion('New password', 'synthetic-private-password')
            ->expectsQuestion('Confirm password', 'synthetic-private-password')
            ->assertSuccessful();
        $account = DB::table('app.users')->where('email', 'new-admin@example.test')->first();
        $this->assertTrue($account->is_admin);
        $this->assertTrue(Hash::check('synthetic-private-password', $account->password_hash));
        $this->assertSame(0, DB::table('app.operator_tokens')->count());
        $this->artisan('gis:provision-admin', ['email' => 'new-admin@example.test', '--name' => 'Replacement'])->assertFailed();
        $this->assertSame('Synthetic Admin', DB::table('app.users')->where('id', $account->id)->value('name'));
    }
}
