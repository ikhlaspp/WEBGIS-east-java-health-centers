<?php

use App\Exceptions\ApiException;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        //
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->render(function (Throwable $exception, Request $request) {
            if (! $request->is('api/v1/*')) {
                return null;
            }
            $headers = [];
            $fields = null;
            if ($exception instanceof ApiException) {
                $status = $exception->getStatusCode();
                $code = $exception->errorCode;
                $message = $exception->getMessage();
            } elseif ($exception instanceof ValidationException) {
                $status = 422;
                $code = 'VALIDATION_FAILED';
                $message = 'Query parameters are invalid.';
                $fields = $exception->errors();
            } elseif ($exception instanceof QueryException) {
                $status = 503;
                $code = 'DEPENDENCY_UNAVAILABLE';
                $message = 'The data service is temporarily unavailable.';
            } elseif ($exception instanceof HttpExceptionInterface) {
                $status = $exception->getStatusCode();
                $headers = $exception->getHeaders();
                $code = match ($status) {
                    404 => 'NOT_FOUND', 405 => 'METHOD_NOT_ALLOWED', 429 => 'RATE_LIMITED', default => 'REQUEST_FAILED'
                };
                $message = match ($status) {
                    404 => 'Resource not found.', 405 => 'Method not allowed.', 429 => 'Too many requests.', default => 'Request failed.'
                };
            } else {
                $status = 500;
                $code = 'INTERNAL_ERROR';
                $message = 'The request could not be completed.';
            }
            $requestId = $request->attributes->get('request_id') ?? (string) Str::uuid();
            $error = ['code' => $code, 'message' => $message, 'request_id' => $requestId];
            if ($fields !== null) {
                $error['fields'] = $fields;
            }

            return response()->json(['error' => $error], $status, [...$headers, 'Cache-Control' => 'no-cache, must-revalidate', 'X-Request-ID' => $requestId]);
        });
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );
    })->create();
