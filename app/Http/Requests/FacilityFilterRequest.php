<?php

namespace App\Http\Requests;

use App\Exceptions\ApiException;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class FacilityFilterRequest extends FormRequest
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
        $rules = ['release_id' => ['sometimes', 'required', 'uuid'], 'analysis_run_id' => ['sometimes', 'required', 'uuid']];
        if ($this->routeIs('api.v1.facilities.show')) {
            return $rules;
        }

        return [...$rules,
            'q' => ['nullable', 'string', 'max:100'],
            'regency_code' => ['sometimes', 'required', 'string', 'regex:/^[0-9]{4}$/D'],
            'district_code' => ['sometimes', 'required', 'string', 'regex:/^[0-9]{7}$/D'],
            'service_type' => ['sometimes', 'required', Rule::in(['Rawat Inap', 'Non Rawat Inap'])],
            'area_type' => ['sometimes', 'required', Rule::in(['Perdesaan', 'Perkotaan', 'Terpencil', 'Sangat Terpencil'])],
            'coordinate_status' => ['sometimes', 'required', Rule::in(['missing', 'unverified', 'verified', 'rejected'])],
            'sort' => ['sometimes', 'required', Rule::in(['name', '-name', 'code', '-code'])],
            'page' => ['sometimes', 'integer', 'min:1', 'max:2147483647'],
            'per_page' => ['sometimes', 'integer', 'min:1', 'max:100'],
        ];
    }

    protected function prepareForValidation(): void
    {
        $allowed = ['release_id', 'analysis_run_id'];
        if (! $this->routeIs('api.v1.facilities.show')) {
            $allowed = [...$allowed, 'q', 'regency_code', 'district_code', 'service_type', 'area_type', 'coordinate_status', 'sort', 'page', 'per_page'];
        }
        if (array_diff(array_keys($this->query()), $allowed)) {
            throw new ApiException(400, 'UNKNOWN_PARAMETER', 'Unsupported query parameter.');
        }
    }
}
