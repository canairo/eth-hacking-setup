#!/usr/bin/env python3

import mariadb
import os

def initialize_database(filename, secret):
    conn = mariadb.connect(
        host = os.environ.get("MARIADB_HOST", "mariadb")
	user = os.environ.get("MARIADB_USER", "example-user")
	password = os.environ.get("MARIADB_PASSWORD", "my_cool_secret")
    )

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS SECRETS (
            filename VARCHAR(64),
            secret VARCHAR(64)
        )
    """)

    cur.execute(
        "INSERT INTO SECRETS (filename, secret) VALUES (?, ?)",
        (filename, secret)
    )

    conn.commit()

    cur.close()
    conn.close()
