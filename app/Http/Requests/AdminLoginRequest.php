<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\ValidationException;

class AdminLoginRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return ['email' => ['required', 'string', 'email', 'max:254'], 'password' => ['required', 'string', 'max:72'], 'is_admin' => ['prohibited'], 'is_active' => ['prohibited'], 'role' => ['prohibited'], 'remember' => ['prohibited']];
    }

    protected function prepareForValidation(): void
    {
        if (is_string($this->input('password')) && strlen($this->input('password')) > 72) {
            throw ValidationException::withMessages(['email' => 'Invalid credentials.']);
        }
        if (is_string($this->input('email'))) {
            $this->merge(['email' => strtolower(trim($this->input('email')))]);
        }
        if (array_diff(array_keys($this->all()), ['email', 'password', '_token'])) {
            throw ValidationException::withMessages(['email' => 'Unsupported login fields.']);
        }
    }
}
