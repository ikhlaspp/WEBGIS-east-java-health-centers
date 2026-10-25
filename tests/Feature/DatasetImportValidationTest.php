<?php

namespace Tests\Feature;

use App\Services\DatasetImportService;
use InvalidArgumentException;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class DatasetImportValidationTest extends TestCase
{
    #[DataProvider('invalidInputs')]
    public function test_rejects_invalid_input_before_database_access(string $change): void
    {
        $document = ['format' => 'gis-import-v1', 'source_id' => '00000000-0000-4000-8000-000000000002', 'target_release_id' => '00000000-0000-4000-8000-000000000006', 'pipeline_version' => 'fixture', 'parameters' => (object) [], 'rows' => [['row_no' => 1, 'source_locator' => 'fixture:1', 'dataset' => 'dataset_releases', 'raw_fields' => (object) [], 'normalized_fields' => ['id' => '00000000-0000-4000-8000-000000000006'], 'disposition' => 'accepted', 'errors' => []]]];
        if ($change === 'protected') {
            $document['rows'][0]['normalized_fields']['status'] = 'published';
        } elseif ($change === 'duplicate_row') {
            $document['rows'][] = $document['rows'][0];
        } elseif ($change === 'empty') {
            $document['rows'] = [];
        }
        $bytes = json_encode($document, JSON_THROW_ON_ERROR);
        if ($change === 'duplicate_key') {
            $bytes = str_replace('"format":', '"format":"other","format":', $bytes);
        }
        $path = sys_get_temp_dir().'/gis-validation-'.bin2hex(random_bytes(8)).'.json';
        file_put_contents($path, $bytes);
        try {
            $this->expectException(InvalidArgumentException::class);
            (new DatasetImportService)->read($path, $change === 'hash' ? str_repeat('0', 64) : hash('sha256', $bytes));
        } finally {
            unlink($path);
        }
    }

    public static function invalidInputs(): array
    {
        return array_map(fn ($value) => [$value], ['protected', 'duplicate_row', 'empty', 'duplicate_key', 'hash']);
    }

    public function test_command_requires_private_capability_file(): void
    {
        $this->artisan('gis:import', ['file' => 'missing.json'])->assertFailed();
    }
}
