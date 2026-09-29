#!/usr/bin/env python3

import mariadb
import os
import base64

def initialize_database(filename, secret):
    conn = mariadb.connect(
        host = os.environ.get("MARIADB_HOST", "mariadb"),
        user = os.environ.get("MARIADB_USER", "example-user"),
        password = os.environ.get("MARIADB_PASSWORD", "my_cool_secret"),
	database = os.environ.get("MARIADB_DATABASE", "appdb")
    )

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS SECRETS (
            filename VARCHAR(64),
            secret VARCHAR(64)
        )
    """)

    for i in range(1, 100):

        cur.execute(
            "INSERT INTO SECRETS (filename, secret) VALUES (?, ?)",
            (filename, base64.b64encode(os.urandom(8)).decode())
        )

    conn.commit()

    cur.close()
    conn.close()
