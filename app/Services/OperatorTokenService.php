<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use InvalidArgumentException;
use RuntimeException;
use Symfony\Component\Process\Process;
use Throwable;

class OperatorTokenService
{
    public const ABILITIES = ['import', 'review', 'analyze', 'validate', 'publish', 'rollback', 'withdraw'];

    public function read(string $path): string
    {
        if (! is_file($path) || is_link($path) || filesize($path) > 4096) {
            throw new InvalidArgumentException('A private token file is required.');
        }
        if (PHP_OS_FAMILY !== 'Windows' && (fileperms($path) & 0077) !== 0) {
            throw new InvalidArgumentException('Token file must be readable only by its owner.');
        }
        $token = trim(file_get_contents($path));
        if (! preg_match('/^[A-Za-z0-9_-]{43}$/D', $token)) {
            throw new InvalidArgumentException('Invalid operator token format.');
        }

        return $token;
    }

    public function issue(string $email, array $abilities, int $minutes): array
    {
        if ($minutes < 1 || $minutes > 480 || $abilities === [] || array_diff($abilities, self::ABILITIES)) {
            throw new InvalidArgumentException('Explicit valid abilities and a lifetime of 1 to 480 minutes are required.');
        }
        $user = DB::table('app.users')->where('email', strtolower(trim($email)))->where('is_active', true)->where('is_admin', true)->first(['id']);
        if ($user === null) {
            throw new InvalidArgumentException('An active internal admin is required.');
        }
        $id = (string) Str::uuid();
        $token = rtrim(strtr(base64_encode(random_bytes(32)), '+/', '-_'), '=');
        $directory = storage_path('app/private/operator-tokens');
        if (! is_dir($directory) && ! mkdir($directory, 0700, true)) {
            throw new RuntimeException('Cannot create private token directory.');
        }
        $path = $directory.'/'.$id.'.token';
        $handle = fopen($path, 'x');
        if ($handle === false) {
            throw new RuntimeException('Cannot create exclusive token file.');
        }
        fclose($handle);
        try {
            if (PHP_OS_FAMILY === 'Windows') {
                $account = getenv('USERDOMAIN').'\\'.getenv('USERNAME');
                $permissions = new Process(['icacls', $path, '/inheritance:r', '/grant:r', $account.':F']);
                $permissions->mustRun();
            } elseif (! chmod($path, 0600)) {
                throw new RuntimeException('Cannot restrict token file permissions.');
            }
            if (file_put_contents($path, $token, LOCK_EX) !== strlen($token)) {
                throw new RuntimeException('Cannot write private token file.');
            }
            $created = now();
            $expires = $created->copy()->addMinutes($minutes);
            DB::table('app.operator_tokens')->insert(['id' => $id, 'user_id' => $user->id, 'token_hash' => hash('sha256', $token), 'abilities' => json_encode(array_values(array_unique($abilities)), JSON_THROW_ON_ERROR), 'created_at' => $created, 'expires_at' => $expires]);

            return ['token_id' => $id, 'token_file' => $path, 'expires_at' => $expires->toIso8601String(), 'abilities' => array_values(array_unique($abilities))];
        } catch (Throwable $exception) {
            unlink($path);
            throw $exception;
        }
    }

    public function revoke(string $id): bool
    {
        if (! Str::isUuid($id)) {
            throw new InvalidArgumentException('A token UUID is required.');
        }

        return DB::table('app.operator_tokens')->where('id', $id)->whereNull('revoked_at')->update(['revoked_at' => now()]) === 1;
    }
}
