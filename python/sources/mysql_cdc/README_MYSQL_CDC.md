# MySQL CDC Setup

This application implements MySQL CDC using MySQL binary log replication with **persistent binlog position tracking** for exactly-once processing and automatic recovery.

## Key Features

- **Persistent Binlog Position**: Automatically saves and resumes from the last processed binlog position
- **Exactly-Once Processing**: No data loss during application restarts or failures  
- **Initial Snapshot**: Optionally capture existing data before starting CDC
- **Automatic Recovery**: Seamlessly resume processing after interruptions
- **Change Buffering**: Batches changes for efficient Kafka publishing
- **State Management**: Integrated state persistence for production reliability

## Prerequisites

1. **MySQL Configuration**: Your MySQL server must have binary logging enabled with ROW format:
   ```ini
   # Add to MySQL configuration file (my.cnf or my.ini)
   [mysqld]
   server-id = 1
   log_bin = /var/log/mysql/mysql-bin.log
   binlog_expire_logs_seconds = 864000
   max_binlog_size = 100M
   binlog-format = ROW
   binlog_row_metadata = FULL
   binlog_row_image = FULL
   ```

2. **MySQL User Permissions**: The MySQL user needs REPLICATION SLAVE and REPLICATION CLIENT privileges:
   ```sql
   -- Create replication user
   CREATE USER 'cdc_user'@'%' IDENTIFIED BY 'secure_password';
   
   -- Grant replication privileges for CDC
   GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc_user'@'%';
   
   -- Grant select for initial snapshot (if using snapshot feature)
   GRANT SELECT ON your_database.your_table TO 'cdc_user'@'%';
   
   FLUSH PRIVILEGES;
   ```

## Environment Variables

Set the following environment variables:

### Required MySQL Connection
- `MYSQL_HOST` - MySQL server hostname (e.g., localhost)
- `MYSQL_PORT` - MySQL server port (default: 3306)
- `MYSQL_USER` - MySQL username
- `MYSQL_PASSWORD` - MySQL password
- `MYSQL_DATABASE` - MySQL database name
- `MYSQL_SCHEMA` - MySQL database name (same as MYSQL_DATABASE)
- `MYSQL_TABLE` - Table name to monitor for changes

### Optional Configuration
- `MYSQL_SNAPSHOT_HOST` - MySQL host for initial snapshot (defaults to MYSQL_HOST). Use this to snapshot from a read replica
- `INITIAL_SNAPSHOT` - Set to "true" to perform initial snapshot (default: false)
- `SNAPSHOT_BATCH_SIZE` - Rows per snapshot batch (default: 1000)
- `FORCE_SNAPSHOT` - Set to "true" to force re-snapshot (default: false)

### State Management
- `Quix__State__Dir` - Directory for storing state files (default: "state")

### Kafka Output
- `output` - Kafka topic name for publishing changes

## Example .env file

```env
# MySQL Connection
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=cdc_user
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=your_database
MYSQL_SCHEMA=your_database
MYSQL_TABLE=your_table

# Optional: Use read replica for initial snapshot
MYSQL_SNAPSHOT_HOST=replica.mysql.example.com

# Initial Snapshot Configuration
INITIAL_SNAPSHOT=true
SNAPSHOT_BATCH_SIZE=1000
FORCE_SNAPSHOT=false

# State Management
Quix__State__Dir=./state

# Kafka Output
output=cdc-changes-topic
```

## Binlog Position Persistence

The application automatically tracks MySQL binlog positions and persists them to disk:

### How it works:
1. **Position Tracking**: Records current binlog file and position during processing
2. **Automatic Saving**: Saves position after successful Kafka delivery
3. **Recovery**: Automatically resumes from last saved position on restart
4. **Exactly-Once**: Ensures no data loss or duplication

### Position Storage:
- Location: `{STATE_DIR}/binlog_position_{schema}_{table}.json`
- Format:
  ```json
  {
    "log_file": "mysql-bin.000123",
    "log_pos": 45678,
    "timestamp": 1704067200.0,
    "readable_time": "2024-01-01 12:00:00 UTC"
  }
  ```

### Benefits:
- ✅ **No data loss** during application restarts
- ✅ **Exactly-once processing** of database changes
- ✅ **Automatic recovery** from last processed position
- ✅ **Production-ready** state management

## Initial Snapshot

Capture existing table data before starting real-time CDC:

### Configuration:
```env
INITIAL_SNAPSHOT=true
SNAPSHOT_BATCH_SIZE=1000
MYSQL_SNAPSHOT_HOST=replica.mysql.example.com  # Optional
```

### Features:
- **Batched Processing**: Configurable batch sizes to handle large tables
- **Memory Efficient**: Processes data in chunks to avoid memory issues
- **Read Replica Support**: Use `MYSQL_SNAPSHOT_HOST` to snapshot from replica
- **Completion Tracking**: Marks snapshot completion to avoid re-processing
- **Force Re-snapshot**: Use `FORCE_SNAPSHOT=true` to re-run if needed

### Snapshot Process:
1. Connects to snapshot host (or main host if not specified)
2. Processes table data in batches
3. Sends records with `"kind": "snapshot_insert"`
4. Marks completion in state file
5. Proceeds to real-time CDC

## Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

The key MySQL-specific dependencies are:
- `pymysql` - MySQL database connector
- `mysql-replication` - MySQL binary log replication library

## Change Data Format

The MySQL CDC produces change events in the following format:

### Snapshot Insert Event
```json
{
  "kind": "snapshot_insert",
  "schema": "database_name",
  "table": "table_name", 
  "columnnames": ["col1", "col2"],
  "columnvalues": ["value1", "value2"],
  "oldkeys": {}
}
```

### INSERT Event
```json
{
  "kind": "insert",
  "schema": "database_name",
  "table": "table_name", 
  "columnnames": ["col1", "col2"],
  "columnvalues": ["value1", "value2"],
  "oldkeys": {}
}
```

### UPDATE Event
```json
{
  "kind": "update",
  "schema": "database_name", 
  "table": "table_name",
  "columnnames": ["col1", "col2"],
  "columnvalues": ["new_value1", "new_value2"],
  "oldkeys": {
    "keynames": ["col1", "col2"],
    "keyvalues": ["old_value1", "old_value2"]
  }
}
```

### DELETE Event
```json
{
  "kind": "delete",
  "schema": "database_name",
  "table": "table_name", 
  "columnnames": [],
  "columnvalues": [],
  "oldkeys": {
    "keynames": ["col1", "col2"],
    "keyvalues": ["deleted_value1", "deleted_value2"]
  }
}
```

## Running the Application

1. **Configure MySQL** with binary logging enabled
2. **Set environment variables** (see example above)
3. **Run the application**:
   ```bash
   python main.py
   ```

### Application Flow:
1. **Load State**: Attempts to load saved binlog position
2. **Initial Snapshot** (if enabled and not completed):
   - Connects to snapshot host
   - Processes existing data in batches
   - Sends snapshot events to Kafka
   - Marks completion
3. **Real-time CDC**:
   - Connects to MySQL binlog stream
   - Resumes from saved position (or current if first run)
   - Monitors specified table for changes
   - Buffers changes and publishes to Kafka every 500ms
   - Saves binlog position after successful delivery
4. **Recovery**: On restart, automatically resumes from last saved position

### Monitoring:
- Check application logs for binlog position updates
- Monitor state directory for position files
- Verify Kafka topic for change events
- Use MySQL's `SHOW MASTER STATUS` to compare positions

## Troubleshooting

### Common Issues:

1. **Binary logging not enabled**:
   - Error: "Binary logging must be enabled for CDC"
   - Solution: Enable binlog in MySQL configuration and restart

2. **Insufficient privileges**:
   - Error: Access denied
   - Solution: Grant REPLICATION SLAVE, REPLICATION CLIENT privileges

3. **Position file corruption**:
   - Delete position file to restart from current position
   - Location: `{STATE_DIR}/binlog_position_{schema}_{table}.json`

4. **Snapshot issues**:
   - Check `MYSQL_SNAPSHOT_HOST` connectivity
   - Verify SELECT privileges on target table
   - Review batch size for memory constraints

### Best Practices:
- Use read replicas for initial snapshots on large tables
- Monitor disk space for state directory
- Set appropriate `SNAPSHOT_BATCH_SIZE` based on available memory
- Regularly backup state files for disaster recovery 