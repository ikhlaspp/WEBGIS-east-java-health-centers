<?php

namespace App\Http\Requests;

use App\Exceptions\ApiException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class ReferenceApiRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    protected function prepareForValidation(): void
    {
        $allowed = $this->routeIs('api.v1.releases') ? ['page', 'per_page'] : ['release_id', 'analysis_run_id'];
        if ($this->routeIs('api.v1.regions')) {
            $allowed = [...$allowed, 'level', 'parent_code'];
        }
        if (array_diff(array_keys($this->query()), $allowed)) {
            throw new ApiException(400, 'UNKNOWN_PARAMETER', 'Unsupported query parameter.');
        }
    }

    public function rules(): array
    {
        if ($this->routeIs('api.v1.releases')) {
            return ['page' => ['sometimes', 'integer', 'min:1'], 'per_page' => ['sometimes', 'integer', 'min:1', 'max:100']];
        }
        $rules = ['release_id' => ['sometimes', 'required', 'uuid'], 'analysis_run_id' => ['sometimes', 'required', 'uuid']];
        if ($this->routeIs('api.v1.regions')) {
            $rules['level'] = ['sometimes', 'required', Rule::in(['regency', 'district'])];
            $rules['parent_code'] = ['required_if:level,district', 'prohibited_unless:level,district', 'string', 'regex:/^[0-9]{4}$/D'];
        }

        return $rules;
    }
}
