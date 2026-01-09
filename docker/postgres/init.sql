-- Initialize database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create application user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'agile') THEN
        CREATE USER agile WITH PASSWORD 'agile';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE agile_pm TO agile;
