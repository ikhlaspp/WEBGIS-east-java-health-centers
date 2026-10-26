<?php

namespace Tests\Feature;

use App\Http\Middleware\PublicApiContext;
use Illuminate\Foundation\Http\Middleware\PreventRequestForgery;
use Tests\TestCase;

class AdminLoginValidationTest extends TestCase
{
    public function test_login_form_has_csrf_and_never_offers_public_registration(): void
    {
        $this->get('/admin/login')->assertOk()->assertSee('name="_token"', false)->assertSee('autocomplete="current-password"', false)->assertDontSee('/register');
    }

    public function test_role_injection_and_invalid_credentials_are_rejected_before_database_access(): void
    {
        $this->withoutMiddleware(PublicApiContext::class);
        foreach ([[], ['email' => 'bad', 'password' => 'test'], ['email' => 'fixture@example.test', 'password' => 'test', 'role' => 'admin'], ['email' => 'fixture@example.test', 'password' => str_repeat('é', 40)]] as $input) {
            $this->postJson('/admin/login', $input)->assertUnprocessable();
        }
    }

    public function test_real_csrf_middleware_rejects_login_and_logout_without_tokens(): void
    {
        $this->app->bind(PreventRequestForgery::class, fn ($app) => new class($app, $app['encrypter']) extends PreventRequestForgery
        {
            protected function runningUnitTests(): bool
            {
                return false;
            }
        });
        $this->postJson('/admin/login', ['email' => 'fixture@example.test', 'password' => 'test'])->assertStatus(419);
        $this->postJson('/admin/logout')->assertStatus(419);
    }

    public function test_noninteractive_provisioning_refuses_to_create_an_account(): void
    {
        $this->artisan('gis:provision-admin', ['email' => 'fixture@example.test', '--name' => 'Fixture', '--no-interaction' => true])->assertFailed();
    }
}
