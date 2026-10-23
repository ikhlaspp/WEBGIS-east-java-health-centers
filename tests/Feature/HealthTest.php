<?php

namespace Tests\Feature;

use Tests\TestCase;

class HealthTest extends TestCase
{
    public function test_the_home_page_is_available(): void
    {
        $this->get('/')->assertOk();
    }

    public function test_the_framework_health_endpoint_is_available(): void
    {
        $this->get('/up')->assertOk();
    }
}
