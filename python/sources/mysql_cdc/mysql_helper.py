import pymysql
import os
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)
from setup_logger import logger

def connect_mysql():
    """Connect to MySQL database"""
    MYSQL_HOST = os.environ["MYSQL_HOST"]
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ["MYSQL_USER"]
    MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]  
    MYSQL_DATABASE = os.environ["MYSQL_DATABASE"]

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4'
    )
    return conn

def run_query(conn, query: str):
    """Execute a query on MySQL"""
    with conn.cursor() as cursor:
        cursor.execute(query)
        conn.commit()

def enable_binlog_if_needed():
    """Check and enable binary logging if not already enabled"""
    conn = connect_mysql()
    try:
        with conn.cursor() as cursor:
            # Check if binary logging is enabled
            cursor.execute("SHOW VARIABLES LIKE 'log_bin'")
            result = cursor.fetchone()
            
            if result and result[1] == 'ON':
                logger.info("Binary logging is already enabled")
            else:
                logger.warning("Binary logging is not enabled. Please enable it in MySQL configuration.")
                logger.warning("Add the following to your MySQL config:")
                logger.warning("log-bin=mysql-bin")
                logger.warning("binlog-format=ROW")
                raise Exception("Binary logging must be enabled for CDC")
                
            # Check binlog format
            cursor.execute("SHOW VARIABLES LIKE 'binlog_format'")
            result = cursor.fetchone()
            
            if result and result[1] != 'ROW':
                logger.warning(f"Binlog format is {result[1]}, should be ROW for CDC")
                logger.warning("Please set binlog_format=ROW in MySQL configuration")
                
    finally:
        conn.close()

def setup_mysql_cdc(table_name: str):
    """Setup MySQL for CDC - mainly validation"""
    conn = connect_mysql()
    try:
        with conn.cursor() as cursor:
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name.split('.')[-1]}'")
            result = cursor.fetchone()
            
            if not result:
                raise Exception(f"Table {table_name} not found")
                
            logger.info(f"Table {table_name} found and ready for CDC")
            
    finally:
        conn.close()

def create_binlog_stream(server_id=1):
    """Create and return a MySQL binlog stream reader"""
    MYSQL_HOST = os.environ["MYSQL_HOST"]
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ["MYSQL_USER"]
    MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
    
    mysql_settings = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "passwd": MYSQL_PASSWORD,
    }
    
    stream = BinLogStreamReader(
        connection_settings=mysql_settings,
        server_id=server_id,
        only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
        resume_stream=True,
        blocking=False
    )
    
    return stream

def get_changes(stream, schema_name: str, table_name: str):
    """Get changes from MySQL binlog stream"""
    changes = []
    
    # Read available events (non-blocking)
    for binlogevent in stream:
        # Filter by schema and table
        if binlogevent.schema == schema_name and binlogevent.table == table_name:
            
            if isinstance(binlogevent, WriteRowsEvent):
                # INSERT operation
                for row in binlogevent.rows:
                    change = {
                        "kind": "insert",
                        "schema": binlogevent.schema,
                        "table": binlogevent.table,
                        "columnnames": list(row["values"].keys()),
                        "columnvalues": list(row["values"].values()),
                        "oldkeys": {}
                    }
                    changes.append(change)
                    
            elif isinstance(binlogevent, UpdateRowsEvent):
                # UPDATE operation
                for row in binlogevent.rows:
                    change = {
                        "kind": "update", 
                        "schema": binlogevent.schema,
                        "table": binlogevent.table,
                        "columnnames": list(row["after_values"].keys()),
                        "columnvalues": list(row["after_values"].values()),
                        "oldkeys": {
                            "keynames": list(row["before_values"].keys()),
                            "keyvalues": list(row["before_values"].values())
                        }
                    }
                    changes.append(change)
                    
            elif isinstance(binlogevent, DeleteRowsEvent):
                # DELETE operation
                for row in binlogevent.rows:
                    change = {
                        "kind": "delete",
                        "schema": binlogevent.schema, 
                        "table": binlogevent.table,
                        "columnnames": [],
                        "columnvalues": [],
                        "oldkeys": {
                            "keynames": list(row["values"].keys()),
                            "keyvalues": list(row["values"].values())
                        }
                    }
                    changes.append(change)
    
    return changes 