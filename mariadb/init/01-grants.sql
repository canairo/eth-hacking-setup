CREATE DATABASE IF NOT EXISTS appdb;
USE appdb;

CREATE TABLE IF NOT EXISTS SECRETS (
    filename VARCHAR(64),
    secret VARCHAR(64)
);

-- Strip all global privileges (guarantees NO FILE, SUPER, PROCESS, RELOAD)
REVOKE ALL PRIVILEGES ON *.* FROM 'example-user'@'%';

-- Allow the application and exploit chain full database-level operations inside appdb
GRANT ALL PRIVILEGES ON appdb.* TO 'example-user'@'%';

FLUSH PRIVILEGES;
