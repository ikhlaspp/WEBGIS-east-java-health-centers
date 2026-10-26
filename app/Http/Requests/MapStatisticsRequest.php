<?php

namespace App\Http\Requests;

use App\Exceptions\ApiException;
use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class MapStatisticsRequest extends FormRequest
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
        if ($this->routeIs('api.v1.map.regions')) {
            return [...$rules,
                'level' => ['sometimes', 'required', Rule::in(['regency', 'district'])],
                'parent_code' => ['required_if:level,district', 'prohibited_unless:level,district', 'string', 'regex:/^[0-9]{4}$/D'],
                'metric' => ['sometimes', 'required', Rule::in(['count', 'density', 'population_per_facility', 'indicative_deficit'])],
                'geometry_detail' => ['sometimes', 'required', Rule::in(['full', 'display'])],
            ];
        }
        $rules += ['regency_code' => ['sometimes', 'required', 'string', 'regex:/^[0-9]{4}$/D'], 'district_code' => ['sometimes', 'required', 'string', 'regex:/^[0-9]{7}$/D']];
        if ($this->routeIs('api.v1.map.points')) {
            $facility = (new FacilityFilterRequest)->rules();
            foreach (['q', 'service_type', 'area_type', 'coordinate_status'] as $key) {
                $rules[$key] = $facility[$key];
            }
            $rules['bbox'] = ['sometimes', 'required', 'string', function (string $attribute, mixed $value, \Closure $fail): void {
                $parts = is_string($value) ? explode(',', $value) : [];
                if (count($parts) !== 4 || count(array_filter($parts, fn ($v) => is_numeric($v) && is_finite((float) $v))) !== 4) {
                    $fail('Bbox must contain four finite coordinates.');

                    return;
                }
                [$west, $south, $east, $north] = array_map('floatval', $parts);
                if ($west < -180 || $east > 180 || $south < -90 || $north > 90 || $west >= $east || $south >= $north) {
                    $fail('Bbox must have ordered geographic bounds.');
                }
            }];
        } elseif ($this->routeIs('api.v1.analysis.buffers')) {
            $rules['radius_m'] = ['required', 'integer', Rule::in([1000, 3000, 5000])];
            $rules['geometry_detail'] = ['sometimes', 'required', Rule::in(['full', 'display'])];
        }

        return $rules;
    }

    protected function prepareForValidation(): void
    {
        if (array_diff(array_keys($this->query()), array_keys($this->rules()))) {
            throw new ApiException(400, 'UNKNOWN_PARAMETER', 'Unsupported query parameter.');
        }
    }
}
