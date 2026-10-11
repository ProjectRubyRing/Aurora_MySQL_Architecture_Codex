-- Read-only diagnostics. Run separately on writer/readers and through the Proxy.
-- Store the output as restricted operational evidence, not in ordinary application logs.
SELECT AURORA_VERSION(), VERSION(), @@hostname, @@read_only;
SELECT @@GLOBAL.max_connections, @@GLOBAL.innodb_buffer_pool_size,
       @@GLOBAL.innodb_purge_threads, @@GLOBAL.table_definition_cache,
       @@GLOBAL.table_open_cache, @@GLOBAL.performance_schema;
SELECT @@SESSION.sql_mode, @@SESSION.time_zone, @@SESSION.transaction_isolation,
       @@SESSION.wait_timeout, @@SESSION.innodb_lock_wait_timeout,
       @@SESSION.lock_wait_timeout, @@SESSION.max_execution_time,
       @@GLOBAL.require_secure_transport, @@GLOBAL.authentication_policy;
SHOW GLOBAL VARIABLES;
SHOW SESSION VARIABLES;
-- Administrative connection only; this reveals account metadata.
SELECT user, host, plugin FROM mysql.user ORDER BY user, host;
-- Proxy terminates TLS: DB-side SSL variables alone do not prove client-to-Proxy TLS.
