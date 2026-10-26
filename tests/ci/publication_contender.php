<?php

if (getenv('RUN_POSTGIS_TESTS') !== '1' || ! in_array(getenv('RACE_HOST'), ['127.0.0.1', 'localhost', '::1'], true)) {
    exit(2);
}
$input = json_decode(stream_get_contents(STDIN), true, 512, JSON_THROW_ON_ERROR);
$pdo = new PDO('pgsql:host='.getenv('RACE_HOST').';port='.getenv('RACE_PORT').';dbname=gis_schema_testing', getenv('RACE_USER'), getenv('RACE_PASSWORD'), [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
echo 'PID:'.$pdo->query('SELECT pg_backend_pid()')->fetchColumn().PHP_EOL;
flush();
$pdo->beginTransaction();
try {
    $pdo->exec('SET LOCAL ROLE gis_artifact_verifier');
    $pdo->exec("SET LOCAL statement_timeout='15s'");
    $statement = $pdo->prepare('SELECT gis.publish_release(?,?::uuid,0,?::uuid,?,?::jsonb)');
    $statement->execute([str_repeat('A', 43), $input['release'], $input['operation'], 'Second competing publication', json_encode($input['manifest'], JSON_THROW_ON_ERROR)]);
    $pdo->commit();
    echo 'UNEXPECTED_SUCCESS'.PHP_EOL;
    exit(1);
} catch (PDOException $exception) {
    $pdo->rollBack();
    echo 'SQLSTATE:'.$exception->getCode().PHP_EOL;
    exit($exception->getCode() === 'P4090' ? 0 : 1);
}
