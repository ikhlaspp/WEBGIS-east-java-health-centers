# Admin session verification

26 October 2026. Local validation: four cases / 11 assertions passed. Real CSRF middleware was enabled explicitly in its test, rather than relying on Laravel's test-mode bypass. Tests verify the login form token, invalid/role-injection input, password byte limits, CSRF rejection on login and logout, and refusal of unattended account provisioning. Pint passed.

Eight database integration cases are pending isolated CI: login/session rotation/logout; guest/registration/profile/draft access; five failures then rate limit; non-admin/inactive accounts and mass assignment; idle and absolute expiration; next-request account deactivation; database session writes under gis_runtime; hidden-prompt provisioning with hashed password and duplicate-account refusal. All credentials/accounts are synthetic and transactionally rolled back.

No real admin account, actual data publication, or deployment acceptance is claimed. Full CI is required before closing the item.
