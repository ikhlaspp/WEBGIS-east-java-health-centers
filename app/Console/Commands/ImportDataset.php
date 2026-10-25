<?php

namespace App\Console\Commands;

use App\Services\DatasetImportService;
use Illuminate\Console\Command;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\Storage;
use Throwable;

class ImportDataset extends Command
{
    protected $signature = 'gis:import {file : Canonical gis-import-v1 JSON} {--sha256= : Expected file digest} {--token-file= : Private file containing an import capability}';

    protected $description = 'Import canonical source rows into a draft with immutable staging and repeat-run protection';

    public function handle(DatasetImportService $service): int
    {
        try {
            $tokenPath = $this->option('token-file');
            if (! is_string($tokenPath) || ! is_file($tokenPath) || filesize($tokenPath) > 4096) {
                $this->error('Provide --token-file pointing to a private import capability file.');

                return self::FAILURE;
            }
            $token = trim(file_get_contents($tokenPath));
            $result = $service->import((string) $this->argument('file'), (string) $this->option('sha256'), $token);
        } catch (Throwable $exception) {
            $result = ['status' => 'failed', 'code' => $exception instanceof QueryException ? (string) $exception->getCode() : 'invalid_import', 'message' => 'Import failed; no publication was performed. Check the canonical file, capability, and database prerequisites.'];
        }
        $report = 'imports/reports/'.bin2hex(random_bytes(16)).'.json';
        if (! Storage::disk('local')->put($report, json_encode($result, JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT))) {
            $this->error('Unable to save the private report. Check batch history before retrying.');

            return self::FAILURE;
        }
        $this->line('Import '.$result['status'].'; private report: '.$report);

        return $result['status'] === 'succeeded' ? self::SUCCESS : self::FAILURE;
    }
}
