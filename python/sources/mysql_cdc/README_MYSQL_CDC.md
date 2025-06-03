# MySQL CDC Setup

This application implements MySQL CDC using MySQL binary log replication.

## Prerequisites

1. **MySQL Configuration**: Your MySQL server must have binary logging enabled with ROW format:
   ```ini
   # Add to MySQL configuration file (my.cnf or my.ini)
   log-bin=mysql-bin
   binlog-format=ROW
   server-id=1
   ```

2. **MySQL User Permissions**: The MySQL user needs REPLICATION SLAVE and REPLICATION CLIENT privileges:
   ```sql
   GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'your_user'@'%';
   GRANT SELECT ON your_database.your_table TO 'your_user'@'%';
   FLUSH PRIVILEGES;
   ```

## Environment Variables

Set the following environment variables:

### MySQL Connection
- `MYSQL_HOST` - MySQL server hostname (e.g., localhost)
- `MYSQL_PORT` - MySQL server port (default: 3306)
- `MYSQL_USER` - MySQL username
- `MYSQL_PASSWORD` - MySQL password
- `MYSQL_DATABASE` - MySQL database name
- `MYSQL_SCHEMA` - MySQL database name (same as MYSQL_DATABASE)
- `MYSQL_TABLE` - Table name to monitor for changes

### Kafka Output (unchanged)
- `output` - Kafka topic name for publishing changes

## Example .env file

```env
# MySQL Connection
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=replication_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MYSQL_SCHEMA=your_database
MYSQL_TABLE=your_table

# Kafka Output
output=cdc-changes-topic
```

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

1. Ensure MySQL is configured with binary logging
2. Set environment variables
3. Run the application:
   ```bash
   python main.py
   ```

The application will:
1. Connect to MySQL and validate binary logging is enabled
2. Create a binary log stream reader
3. Monitor the specified table for changes
4. Buffer changes and publish them to Kafka every 500ms 