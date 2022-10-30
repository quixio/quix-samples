import psycopg2
import os

# Timescale Constants
TS_HOST = os.environ["TS_HOST"]
TS_PORT = os.environ["TS_PORT"]
TS_USER = os.environ["TS_USER"]
TS_PASSWORD = os.environ["TS_PASSWORD"]
TS_DATABASE = os.environ["TS_DATABASE"]


class Null:
    def __init__(self):
        self.name = 'NULL'

    def __str__(self):
        return self.name


def connect_timescale():
    conn = psycopg2.connect(
        database=TS_DATABASE, user=TS_USER, password=TS_PASSWORD, host=TS_HOST, port=TS_PORT
    )
    return conn


def run_query(conn, query: str):
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()


def create_paramdata_table(conn, table_name: str):
    query = f'''
    CREATE TABLE IF NOT EXISTS public.{table_name} (
    uid SERIAL,
    timestamp TIMESTAMPTZ NOT NULL
    );
    SELECT create_hypertable('public.{table_name}', 'timestamp');
    '''
    run_query(conn, query)


def create_metadata_table(conn, table_name: str):
    query = f'''
    CREATE TABLE IF NOT EXISTS public.{table_name} (
    uid SERIAL
    );
    '''
    run_query(conn, query)


def create_eventdata_table(conn, table_name: str):
    query = f'''
    CREATE TABLE IF NOT EXISTS public.{table_name} (
    uid SERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    value VARCHAR(100)
    );
    SELECT create_hypertable('public.{table_name}', 'timestamp');
    '''
    run_query(conn, query)


def create_parents_table(conn, table_name: str):
    query = f'''
    CREATE TABLE IF NOT EXISTS public.{table_name} (
    uid SERIAL,
    stream_id VARCHAR(100),
    parent_id VARCHAR(100)
    );
    '''
    run_query(conn, query)


def create_properties_table(conn, table_name: str):
    query = f'''
    CREATE TABLE IF NOT EXISTS public.{table_name} (
    uid SERIAL,
    name VARCHAR(100),
    location VARCHAR(100),
    topic VARCHAR(100),
    status VARCHAR(100),
    data_start NUMERIC,
    data_end NUMERIC
    );
    '''
    run_query(conn, query)


def create_column(conn, table_name: str, column_name: str, col_type: str):
    if col_type == 'STRING':
        col_type = 'VARCHAR(100)'
    query = f'''ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {col_type};'''
    run_query(conn, query)


def insert_row(conn, table_name: str, cols: list, vals: list):
    (col_str, row_str) = build_insert_str(cols, vals)
    _insert_row_str(conn, table_name, col_str, row_str)


def _insert_row_str(conn, table_name: str, cols: str, vals: str):
    query = f'''INSERT INTO public.{table_name}({cols}) VALUES {vals}'''
    run_query(conn, query)


def delete_row(conn, table_name: str, condition: str):
    query = f'''DELETE FROM public.{table_name} WHERE {condition}'''
    run_query(conn, query)


def build_insert_str(cols: list, rows_list: list):
    col_str = ",".join([str(s) for s in cols])
    row_strs = []
    for row in rows_list:
        row_str = '(' + ",".join(["'{0}'".format(s)
                                  if type(s) is str else str(s) for s in row]) + ')'
        row_strs.append(row_str)
    batch_row_str = ",".join(row_strs)
    return (col_str, batch_row_str)


