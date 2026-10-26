<?php

namespace App\Auth;

use Illuminate\Auth\EloquentUserProvider;
use Illuminate\Database\Eloquent\Builder;

class RuntimeUserProvider extends EloquentUserProvider
{
    /**
     * Create a new class instance.
     */
    protected function newModelQuery($model = null): Builder
    {
        return parent::newModelQuery($model)->select(['id', 'name', 'email', 'password_hash', 'is_admin', 'is_active']);
    }
}
