import pymysql
import os
import json
import time
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)
from setup_logger import logger

def serialize_value(value):
    """Convert a value to JSON-serializable format"""
    if value is None:
        return None
    elif isinstance(value, (bytes, bytearray)):
        # Convert binary data to base64 string
        import base64
        return base64.b64encode(value).decode('utf-8')
    elif hasattr(value, 'isoformat'):
        # Handle datetime, date, time objects
        return value.isoformat()
    elif isinstance(value, (int, float, str, bool)):
        # Already JSON serializable
        return value
    else:
        # Convert other types to string
        return str(value)

def connect_mysql(host=None):
    """Connect to MySQL database"""
    MYSQL_HOST = host or os.environ["MYSQL_HOST"]
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

# Binlog position management
def get_binlog_position_file():
    """Get the path to the binlog position file"""
    state_dir = os.getenv("Quix__State__Dir", "state")
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)
    schema = os.environ["MYSQL_SCHEMA"]
    table = os.environ["MYSQL_TABLE"]
    return os.path.join(state_dir, f"binlog_position_{schema}_{table}.json")

def save_binlog_position(log_file, log_pos):
    """Save the current binlog position to disk"""
    position_file = get_binlog_position_file()
    position_data = {
        "log_file": log_file,
        "log_pos": log_pos,
        "timestamp": time.time(),
        "readable_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    try:
        with open(position_file, 'w') as f:
            json.dump(position_data, f, indent=2)
        logger.debug(f"Saved binlog position: {log_file}:{log_pos}")
    except Exception as e:
        logger.error(f"Failed to save binlog position: {e}")

def load_binlog_position():
    """Load the last saved binlog position from disk"""
    position_file = get_binlog_position_file()
    if os.path.exists(position_file):
        try:
            with open(position_file, 'r') as f:
                position_data = json.load(f)
            logger.info(f"Loaded binlog position: {position_data['log_file']}:{position_data['log_pos']} from {position_data.get('readable_time', 'unknown time')}")
            return position_data['log_file'], position_data['log_pos']
        except Exception as e:
            logger.error(f"Failed to load binlog position: {e}")
    return None, None

def create_binlog_stream(server_id=1):
    """Create and return a MySQL binlog stream reader with position resumption"""
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
    
    # Load saved binlog position
    log_file, log_pos = load_binlog_position()
    
    stream_kwargs = {
        "connection_settings": mysql_settings,
        "server_id": server_id,
        "only_events": [DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
        "resume_stream": True,
        "blocking": False
    }
    
    # If we have a saved position, use it
    if log_file and log_pos:
        stream_kwargs["log_file"] = log_file
        stream_kwargs["log_pos"] = log_pos
        logger.info(f"Resuming binlog stream from saved position: {log_file}:{log_pos}")
    else:
        logger.info("No saved binlog position found, starting from current position")
    
    stream = BinLogStreamReader(**stream_kwargs)
    return stream

def get_changes(stream, schema_name: str, table_name: str):
    """Get changes from MySQL binlog stream and save position after processing"""
    changes = []
    last_position = None
    
    # Read available events (non-blocking)
    for binlogevent in stream:
        # Update position tracking
        if hasattr(stream, 'log_file') and hasattr(stream, 'log_pos'):
            last_position = (stream.log_file, stream.log_pos)
        
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
                        "columnvalues": [serialize_value(v) for v in row["values"].values()],
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
                        "columnvalues": [serialize_value(v) for v in row["after_values"].values()],
                        "oldkeys": {
                            "keynames": list(row["before_values"].keys()),
                            "keyvalues": [serialize_value(v) for v in row["before_values"].values()]
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
                            "keyvalues": [serialize_value(v) for v in row["values"].values()]
                        }
                    }
                    changes.append(change)
    
    # Save position if we processed any events
    if last_position and changes:
        save_binlog_position(last_position[0], last_position[1])
    
    return changes

def perform_initial_snapshot(schema_name: str, table_name: str, batch_size: int = 1000):
    """Perform initial snapshot of the table and return all existing rows as insert events"""
    conn = connect_mysql(os.environ["MYSQL_SNAPSHOT_HOST"])
    changes = []
    
    try:
        with conn.cursor() as cursor:
            # Get total row count for logging
            cursor.execute(f"SELECT COUNT(*) FROM `{schema_name}`.`{table_name}`")
            total_rows = cursor.fetchone()[0]
            logger.info(f"Starting initial snapshot of {schema_name}.{table_name} - {total_rows} rows")
            
            # Use LIMIT with OFFSET for batching to avoid memory issues with large tables
            offset = 0
            processed_rows = 0
            
            while True:
                # Fetch batch of rows
                cursor.execute(f"SELECT * FROM `{schema_name}`.`{table_name}` LIMIT {batch_size} OFFSET {offset}")
                rows = cursor.fetchall()
                
                if not rows:
                    break
                
                # Get column names
                column_names = [desc[0] for desc in cursor.description]
                
                # Convert each row to a change event
                for row in rows:
                    # Convert row tuple to dictionary
                    row_dict = dict(zip(column_names, row))
                    
                    # Convert values to JSON-serializable format
                    serialized_values = [serialize_value(value) for value in row_dict.values()]
                    
                    change = {
                        "kind": "snapshot_insert",  # Different kind to distinguish from real inserts
                        "schema": schema_name,
                        "table": table_name,
                        "columnnames": column_names,
                        "columnvalues": serialized_values,
                        "oldkeys": {}
                    }
                    changes.append(change)
                
                processed_rows += len(rows)
                offset += batch_size
                
                if processed_rows % 50000 == 0:  # Log progress every 50k rows
                    logger.info(f"Snapshot progress: {processed_rows}/{total_rows} rows processed")
            
            logger.info(f"Initial snapshot completed: {processed_rows} rows captured")
            
    except Exception as e:
        logger.error(f"Error during initial snapshot: {e}")
        raise
    finally:
        conn.close()
    
    return changes 