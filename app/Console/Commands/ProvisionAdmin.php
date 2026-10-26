<?php

namespace App\Console\Commands;

use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;

#[Signature('gis:provision-admin {email} {--name=}')]
#[Description('Provision a new internal admin using a privileged database connection and a hidden password prompt')]
class ProvisionAdmin extends Command
{
    /**
     * Execute the console command.
     */
    public function handle(): int
    {
        $email = strtolower(trim($this->argument('email')));
        $name = trim($this->option('name') ?? '');
        if (Validator::make(['email' => $email, 'name' => $name], ['email' => 'required|email|max:254', 'name' => 'required|string|max:200'])->fails()) {
            $this->error('A valid email and --name are required.');

            return self::FAILURE;
        }
        if (! $this->input->isInteractive()) {
            $this->error('Provisioning requires an interactive hidden password prompt.');

            return self::FAILURE;
        }
        if (DB::table('app.users')->where('email', $email)->exists()) {
            $this->error('Account already exists; provisioning never changes existing roles or passwords.');

            return self::FAILURE;
        }
        $password = $this->secret('New password');
        $confirmation = $this->secret('Confirm password');
        if (! is_string($password) || mb_strlen($password) < 12 || strlen($password) > 72 || $password !== $confirmation) {
            $this->error('Passwords must match and contain at least 12 characters, up to 72 bytes.');

            return self::FAILURE;
        }
        DB::table('app.users')->insert(['id' => (string) Str::uuid(), 'name' => $name, 'email' => $email, 'password_hash' => Hash::make($password), 'is_admin' => true, 'is_active' => true]);
        $this->info('Internal admin created. No operator token was issued.');

        return self::SUCCESS;
    }
}
