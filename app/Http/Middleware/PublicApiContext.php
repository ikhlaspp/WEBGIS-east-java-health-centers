<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class PublicApiContext
{
    public function handle(Request $request, Closure $next): Response
    {
        $request->attributes->set('request_id', (string) Str::uuid());

        return DB::transaction(function () use ($request, $next): Response {
            DB::statement('SET LOCAL ROLE gis_runtime');
            $response = $next($request);
            $response->headers->set('Cache-Control', 'no-cache, must-revalidate');
            $response->headers->set('X-Request-ID', $request->attributes->get('request_id'));

            return $response;
        });
    }
}
