"""
SQL Server CDC Helper Functions

Provides utilities for working with SQL Server Change Data Capture.
"""
import pyodbc
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def connect_sql_server(server: str, database: str, username: str, password: str, driver: str) -> pyodbc.Connection:
    """
    Connect to SQL Server database.

    Args:
        server: SQL Server hostname or IP
        database: Database name
        username: Username for authentication
        password: Password for authentication
        driver: ODBC driver name

    Returns:
        pyodbc.Connection object
    """
    connection_string = (
        f"Driver={driver};"
        f"Server={server};"
        f"Database={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )

    logger.info(f"Connecting to SQL Server: {server}/{database}")
    return pyodbc.connect(connection_string)


def is_cdc_enabled(conn: pyodbc.Connection, schema: str, table: str) -> bool:
    """
    Check if CDC is enabled on a specific table.

    Args:
        conn: SQL Server connection
        schema: Schema name
        table: Table name

    Returns:
        True if CDC is enabled, False otherwise
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_tracked_by_cdc
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = ? AND t.name = ?
    """, (schema, table))

    row = cursor.fetchone()
    cursor.close()

    if row is None:
        raise ValueError(f"Table {schema}.{table} not found")

    return row[0] == 1


def get_cdc_table_name(schema: str, table: str) -> str:
    """
    Get the CDC change table name for a source table.

    Args:
        schema: Source schema name
        table: Source table name

    Returns:
        CDC change table name (e.g., 'cdc.dbo_MyTable_CT')
    """
    return f"cdc.{schema}_{table}_CT"


def get_min_lsn(conn: pyodbc.Connection, schema: str, table: str) -> bytes:
    """
    Get the minimum LSN available for a CDC-enabled table.

    Args:
        conn: SQL Server connection
        schema: Schema name
        table: Table name

    Returns:
        Minimum LSN as bytes
    """
    cursor = conn.cursor()

    # Get the capture instance name
    cursor.execute("""
        SELECT capture_instance
        FROM cdc.change_tables ct
        JOIN sys.tables t ON ct.source_object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = ? AND t.name = ?
    """, (schema, table))

    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"CDC not enabled on {schema}.{table}")

    capture_instance = row[0]

    # Get minimum LSN
    cursor.execute(f"SELECT sys.fn_cdc_get_min_lsn(?)", (capture_instance,))
    min_lsn = cursor.fetchone()[0]
    cursor.close()

    return min_lsn


def get_changes(
    conn: pyodbc.Connection,
    schema: str,
    table: str,
    from_lsn: bytes,
    to_lsn: Optional[bytes] = None,
    row_filter: str = 'all'
) -> List[Dict[str, Any]]:
    """
    Get CDC changes for a table.

    Args:
        conn: SQL Server connection
        schema: Schema name
        table: Table name
        from_lsn: Starting LSN
        to_lsn: Ending LSN (None for current)
        row_filter: 'all', 'all update old', or operation filter

    Returns:
        List of change records as dictionaries
    """
    cursor = conn.cursor()

    # Get capture instance
    cursor.execute("""
        SELECT capture_instance
        FROM cdc.change_tables ct
        JOIN sys.tables t ON ct.source_object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = ? AND t.name = ?
    """, (schema, table))

    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"CDC not enabled on {schema}.{table}")

    capture_instance = row[0]

    # Get current LSN if to_lsn not specified
    if to_lsn is None:
        cursor.execute("SELECT sys.fn_cdc_get_max_lsn()")
        to_lsn = cursor.fetchone()[0]

    # Get changes using CDC function
    # fn_cdc_get_all_changes takes 3 parameters (from_lsn, to_lsn, row_filter_option)
    query = f"""
        SELECT *
        FROM cdc.fn_cdc_get_all_changes_{capture_instance}(?, ?, ?)
        ORDER BY __$start_lsn
    """

    cursor.execute(query, (from_lsn, to_lsn, row_filter))

    # Convert rows to dictionaries
    columns = [column[0] for column in cursor.description]
    changes = []

    for row in cursor.fetchall():
        change = dict(zip(columns, row))
        changes.append(change)

    cursor.close()
    return changes


def format_change_event(change: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a CDC change record into a standardized event.

    Args:
        change: Raw CDC change record

    Returns:
        Formatted change event with operation type and data
    """
    operation_map = {
        1: 'delete',
        2: 'insert',
        3: 'update_before',
        4: 'update_after'
    }

    operation_code = change.pop('__$operation')
    start_lsn = change.pop('__$start_lsn')
    seqval = change.pop('__$seqval')
    update_mask = change.pop('__$update_mask', None)

    # Convert LSN to hex string for serialization
    lsn_hex = start_lsn.hex() if isinstance(start_lsn, bytes) else str(start_lsn)

    event = {
        'operation': operation_map.get(operation_code, f'unknown_{operation_code}'),
        'lsn': lsn_hex,
        'seqval': seqval.hex() if isinstance(seqval, bytes) else str(seqval),
        'data': change
    }

    if update_mask is not None:
        event['update_mask'] = update_mask.hex() if isinstance(update_mask, bytes) else str(update_mask)

    return event


def lsn_to_hex(lsn: bytes) -> str:
    """
    Convert LSN bytes to hex string for storage/serialization.

    Args:
        lsn: LSN as bytes

    Returns:
        LSN as hex string
    """
    return lsn.hex() if lsn else None


def hex_to_lsn(hex_str: str) -> bytes:
    """
    Convert hex string back to LSN bytes.

    Args:
        hex_str: LSN as hex string

    Returns:
        LSN as bytes
    """
    return bytes.fromhex(hex_str) if hex_str else None
