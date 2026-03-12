# MongoDB Backup Manager

A web-based tool for managing MongoDB backups across multiple servers. Provides a Flask API backend, a SvelteKit frontend, and automated scheduling via APScheduler. Backup archives are stored in blob storage (Quix Cloud or MinIO locally).

## Features

- **Multi-server management** — Add any number of MongoDB servers with encrypted credential storage
- **Auto-discovery** — Automatically detects databases on connected servers
- **Manual & scheduled backups** — Trigger one-off backups or configure cron-based schedules
- **Fan-out** — Back up a single database, all databases on a server, or everything at once
- **Restore** — Restore any completed backup to its original server or a different target
- **Pluggable metadata storage** — Store the manager's own state in MongoDB or a local JSON file (synced to blob storage)
- **Dashboard** — Overview of backup status, storage usage, and schedule activity

## Architecture

```
backup-manager/
  api/                  Flask backend (gunicorn, port 80)
    app.py              App factory, metadata backend init
    config.py           Environment variables
    models.py           Dataclasses (ManagedServer, ManagedDatabase, Backup, Schedule, RestoreOperation)
    scheduler.py        APScheduler initialization
    routes/
      servers.py        Server CRUD + connection test
      databases.py      Database CRUD + auto-discovery sync
      backups.py        Backup list / trigger / annotate / delete
      schedules.py      Schedule CRUD + toggle
      restore.py        Restore list / trigger
      system.py         Health check + stats
      settings.py       App configuration
    services/
      backup_service.py     mongodump execution + blob upload
      restore_service.py    mongorestore execution + blob download
      scheduler_service.py  APScheduler job management
      crypto_service.py     Fernet encryption for stored passwords
      blob_service.py       Blob storage abstraction (Quix filesystem)
      json_backend.py       JSON file metadata backend (pymongo-compatible)
  frontend/             SvelteKit (built into /app/static at Docker build time)
    src/lib/            api.ts, types.ts, stores.ts
    src/routes/         Pages: dashboard, backups, schedules, restore, settings, help
  tests/
    test_json_backend.py  76 tests for the JSON metadata backend
```

## Quick Start (Run locally with Docker Compose)

```bash
# Clone and start all services
docker compose up -d

# Backup Manager UI is at http://localhost:8090
# MinIO console is at http://localhost:9001 (minioadmin/minioadmin)
```

This starts:
- **backup-manager** on port 8090 — the main application
- **mongodb** on port 27017 — a target MongoDB server (for backups)
- **minio** on ports 9000/9001 — local blob storage
- **test-client** on port 8091 — inserts sample data into the target MongoDB

The metadata MongoDB (`metadata-mongodb`) is only started when `METADATA_BACKEND=mongo`.

## Configuration

All configuration is via environment variables. See [.env](.env) for local defaults.

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `METADATA_BACKEND` | `json` | Metadata storage backend: `mongo` or `json` |
| `SECRET_KEY` | *(required)* | Encryption key for stored server passwords (Fernet) |
| `BLOB_BASE_PATH` | `backups/mongodb` | Base path in blob storage for backup archives |
| `BACKUP_RETENTION_DAYS` | `30` | Default retention period for backups |

### MongoDB Metadata Backend (only when `METADATA_BACKEND=mongo`)

| Variable | Default | Description |
|----------|---------|-------------|
| `METADATA_MONGO_HOST` | `metadata-mongodb` | Metadata MongoDB hostname |
| `METADATA_MONGO_PORT` | `80` | Metadata MongoDB port |
| `METADATA_MONGO_USERNAME` | `admin` | Metadata MongoDB username |
| `METADATA_MONGO_PASSWORD` | *(empty)* | Metadata MongoDB password |
| `METADATA_MONGO_DATABASE` | `backup_manager` | Metadata database name |

### JSON Metadata Backend (only when `METADATA_BACKEND=json`)

| Variable | Default | Description |
|----------|---------|-------------|
| `METADATA_JSON_DIR` | `/tmp/metadata-json` | Local directory for the metadata JSON file |

The JSON backend persists all state to a single `metadata.json` file. On every write, it saves locally immediately and uploads to blob storage on a 2-second debounce. On startup, if the local file is missing, it downloads from blob storage automatically.

## Metadata Backends

### MongoDB (`METADATA_BACKEND=mongo`)

The original backend. Requires a dedicated MongoDB instance for the manager's own state (servers, databases, backups, schedules, restore operations). Good for production deployments where you already have MongoDB infrastructure.

### JSON File (`METADATA_BACKEND=json`)

A lightweight alternative that stores all metadata in a single JSON file. No additional database required. The file is synced to blob storage for durability, so data survives container restarts. Suitable for simpler deployments or when you want to minimize infrastructure.

## API Reference

All endpoints are under `/api`.

### Servers

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/servers` | List all managed servers |
| `GET` | `/api/servers/:id` | Get a single server |
| `POST` | `/api/servers` | Add a new server |
| `PUT` | `/api/servers/:id` | Update server connection details |
| `DELETE` | `/api/servers/:id` | Delete a server (cascades to its databases) |
| `POST` | `/api/servers/:id/test` | Test server connectivity |
| `GET` | `/api/servers/:id/databases` | List databases on a server |
| `POST` | `/api/servers/probe-databases` | Probe databases with ad-hoc credentials |

**Create/update server body:**
```json
{
  "name": "Production",
  "host": "mongodb.example.com",
  "port": 27017,
  "username": "admin",
  "password": "secret",
  "auth_source": "admin"
}
```

### Databases

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/databases?server_id=` | List managed databases (optional server filter) |
| `POST` | `/api/databases/sync` | Auto-discover databases from servers |
| `PATCH` | `/api/databases/:id` | Toggle database enabled/disabled |
| `DELETE` | `/api/databases/:id` | Remove a managed database |

### Backups

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/backups?status=&server_id=&database=&limit=&offset=` | List backups (with filters) |
| `GET` | `/api/backups/:id` | Get a single backup |
| `POST` | `/api/backups` | Trigger backup(s) |
| `PATCH` | `/api/backups/:id` | Update backup name/notes |
| `DELETE` | `/api/backups/:id` | Delete backup (removes blob too) |

**Trigger backup body (all fields optional):**
```json
{
  "server_id": "uuid",
  "database": "mydb",
  "name": "Pre-release backup",
  "notes": "Before v2.0 deploy"
}
```

Fan-out behavior:
- No body or `{}` — backs up all enabled databases across all servers
- `server_id` only — backs up all enabled databases on that server
- `server_id` + `database` — backs up a single database

### Schedules

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/schedules` | List all schedules |
| `GET` | `/api/schedules/:id` | Get a single schedule |
| `POST` | `/api/schedules` | Create a schedule |
| `PUT` | `/api/schedules/:id` | Update a schedule |
| `DELETE` | `/api/schedules/:id` | Delete a schedule |
| `POST` | `/api/schedules/:id/toggle` | Toggle enabled/disabled |

**Create schedule body:**
```json
{
  "name": "Nightly full backup",
  "cron_expression": "0 2 * * *",
  "server_id": "uuid",
  "database": "mydb",
  "retention_days": 30,
  "enabled": true
}
```

Schedules follow the same fan-out logic as manual backups. Omit `server_id` and `database` to back up everything.

### Restore

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/restore` | List restore operations |
| `GET` | `/api/restore/:id` | Get a single restore |
| `POST` | `/api/restore` | Trigger a restore |

**Trigger restore body:**
```json
{
  "backup_id": "uuid",
  "target_server_id": "uuid",
  "target_database": "restored_db"
}
```

If `target_server_id` is omitted, the backup's original server is used.

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check (metadata store + scheduler status) |
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/settings` | App configuration |

## Frontend Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard with stat cards and recent backups |
| `/backups` | Backup list with filters, trigger, annotate, delete, restore |
| `/schedules` | Schedule management with cron builder and toggle switches |
| `/restore` | Restore history and trigger new restores |
| `/settings` | Server and database management (add/edit/delete/test/sync) |
| `/help` | Built-in help documentation |

## How Backups Work

1. A backup is created with status `pending` and a background thread is started
2. The status changes to `running` and `mongodump` is executed against the target server
3. The dump is compressed into a `.tar.gz` archive
4. The archive is uploaded to blob storage at `YYYY/MM/DD/mongodb_backup_TIMESTAMP.tar.gz`
5. The backup record is updated with `completed` status, `blob_path`, and `file_size_bytes`
6. If any step fails, the status is set to `failed` with an error message

Restores follow the reverse process: download from blob, extract, run `mongorestore`.

## Security

- Server passwords are encrypted at rest using Fernet symmetric encryption (derived from `SECRET_KEY` via SHA-256)
- Passwords are never returned in API responses
- The `SECRET_KEY` should be a strong random value in production

## Running Tests

```bash
# Build the image first
docker compose build backup-manager

# Run the JSON backend tests (76 tests)
docker run --rm -w /app \
  -v ./backup-manager/tests:/app/tests \
  mongodb-backup-backup-manager \
  python -m pytest tests/test_json_backend.py -v
```

## Deployment on Quix Cloud

The application is configured via [quix.yaml](quix.yaml) for Quix Cloud deployment. Set `METADATA_BACKEND=json` to avoid needing a separate metadata MongoDB instance. The JSON metadata file is automatically synced to Quix blob storage.

Key Quix variables to configure:
- `METADATA_BACKEND` — `json` (recommended) or `mongo`
- `SECRET_KEY` — set as a Secret in Quix Cloud
- Blob storage is automatically bound
