import os
import sys
import time

import pymysql

conn = pymysql.connect(
    host=os.environ["MYSQL_HOST"],
    user="root",
    password=os.environ["MYSQL_ROOT_PASSWORD"],
    database="test_db",
    autocommit=True,
)
cursor = conn.cursor()

# cdc connects: setup(), start position, binlog stream. DML after the 3rd is captured.
deadline = time.monotonic() + 60
while True:
    cursor.execute(
        "SELECT COALESCE(SUM(TOTAL_CONNECTIONS), 0) "
        "FROM performance_schema.accounts WHERE USER = 'cdc'"
    )
    if cursor.fetchone()[0] >= 3:
        break
    if time.monotonic() > deadline:
        sys.exit("source never opened the binlog stream")
    time.sleep(0.5)

cursor.execute(
    "INSERT INTO test_table (id, name, value) VALUES (1, 'alice', 100), (2, 'bob', 200)"
)
cursor.execute("UPDATE test_table SET value = 150 WHERE id = 1")
cursor.execute("DELETE FROM test_table WHERE id = 2")
conn.close()

print("Completed 3 statements (4 row changes) on test_db.test_table")
