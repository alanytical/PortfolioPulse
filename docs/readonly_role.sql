-- Run AS Neon owner AFTER the first successful dbt run.
-- Choose a UNIQUE, strong password. NEVER commit real passwords or post them in chat.
CREATE ROLE portfoliopulse_reviewer LOGIN PASSWORD 'CHANGE_TO_STRONG_UNIQUE_PASSWORD';
GRANT CONNECT ON DATABASE neondb TO portfoliopulse_reviewer; -- replace neondb if different
GRANT USAGE ON SCHEMA raw, analytics, public TO portfoliopulse_reviewer;
GRANT SELECT ON ALL TABLES IN SCHEMA raw, analytics, public TO portfoliopulse_reviewer;
-- Add USAGE on other dbt-generated schemas if you chose different output names.
-- Re-apply after creating/replacing models, or configure default privileges for dbt owner:
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO portfoliopulse_reviewer;
-- Verify by connecting as reviewer: SELECT works; CREATE/INSERT/UPDATE should fail.
