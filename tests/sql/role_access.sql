-- Diagnostic inventory only; behavioral allow/deny coverage lives in DatabaseAccessTest.
-- Execute as the isolated test migrator, never with production credentials in CI.
SELECT rolname, rolcanlogin, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb
FROM pg_roles WHERE rolname IN ('gis_runtime','gis_worker','gis_publisher','gis_lifecycle_owner');
SELECT n.nspname, c.relname, c.relrowsecurity, c.relforcerowsecurity
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname IN ('gis','staging') AND c.relkind='r' ORDER BY 1,2;
SELECT schemaname, tablename, policyname, roles, cmd FROM pg_policies
WHERE schemaname IN ('app','gis','staging') ORDER BY 1,2,3;
