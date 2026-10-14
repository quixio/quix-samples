# MongoDB Backup Manager

A web-based tool for managing MongoDB backups across multiple servers. Provides a Flask API backend, a SvelteKit frontend, and automated scheduling via APScheduler. Backup archives are stored in blob storage (Quix Cloud or MinIO locally).

This sample deploys the prebuilt image `ghcr.io/quixio/mongodb-backup-manager:1.0.6`. To move to a newer release, change the tag in [dockerfile](dockerfile) and redeploy.

## Features

- **Multi-server management** — Add any number of MongoDB servers with encrypted credential storage
- **Auto-discovery** — Automatically detects databases on connected servers
- **Manual & scheduled backups** — Trigger one-off backups or configure cron-based schedules
- **Fan-out** — Back up a single database, all databases on a server, or everything at once
- **Restore** — Restore any completed backup to its original server or a different target
- **Retention** — Expired backups are removed automatically, with safeguards that keep a minimum number of recent recovery points per database and exempt anything you pin
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
      schedules.py      Schedule CRUD + toggle + retention impact
      restore.py        Restore list / trigger
      retention.py      Retention status / preview / sweep / hold
      workspaces.py     Cross-environment backup browsing
      system.py         Health check + stats
      settings.py       App configuration
    services/
      backup_service.py     mongodump execution + blob upload
      restore_service.py    mongorestore execution + blob download
      scheduler_service.py  APScheduler job management
      retention_service.py  Retention classification and enforcement
      crypto_service.py     Fernet encryption for stored passwords
      blob_service.py       Blob storage abstraction (Quix filesystem)
      json_backend.py       JSON file metadata backend (pymongo-compatible)
  frontend/             SvelteKit (built into /app/static at Docker build time)
    src/lib/            api.ts, types.ts, stores.ts
    src/routes/         Pages: dashboard, backups, schedules, restore, settings, help
  tests/                Test suite for the API, services and metadata backend
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

All configuration is via environment variables, set on the deployment. Every variable below has a working default except `SECRET_KEY`.

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `METADATA_BACKEND` | `json` | Metadata storage backend: `mongo` or `json` |
| `SECRET_KEY` | *(required)* | Encryption key for stored server passwords (Fernet) |
| `BLOB_BASE_PATH` | `backups/mongodb` | Base path in blob storage for backup archives |

### Retention Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKUP_RETENTION_DAYS` | `30` | Retention period applied to a backup when no schedule sets one |
| `RETENTION_MIN_KEEP` | `3` | Most recent successful backups always kept per server + database, regardless of age |
| `RETENTION_AUTO_SWEEP` | `true` | Whether expired backups are removed automatically |
| `RETENTION_SWEEP_CRON` | `20 * * * *` | How often retention is enforced. Hourly by default — retention is expressed in days, so a daily sweep would leave a backup up to another 24h past its window |

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

## Retention

Expired backups are deleted automatically, from blob storage and from the metadata store. A sweep runs on the schedule set by `RETENTION_SWEEP_CRON`.

### How a backup's policy is resolved

Retention is resolved snapshot-first: a backup carries the `retention_days` that was in force when it was created, so changing a schedule afterwards does not retroactively change backups it has already taken.

| Order | Source | Automatically deletable |
|-------|--------|-------------------------|
| 1 | The backup's own `retention_days`, stamped at creation | Yes |
| 2 | The `retention_days` of the schedule that created it | No — surfaced for review |
| 3 | `BACKUP_RETENTION_DAYS` | No — surfaced for review |

Only a backup carrying its own snapshot is eligible for the automatic sweep. Anything whose policy has to be inferred — chiefly backups taken before an upgrade to a version with retention — is reported in the UI and waits for an explicit confirmation, so pre-existing backups are never removed without a click.

### What is never deleted

- The most recent successful backups for each server + database pair, however old, up to `RETENTION_MIN_KEEP`
- Any backup with a retention hold (`POST /api/backups/:id/hold`)
- Any backup still `running` or `pending`
- Anything whose creation timestamp cannot be read

Expiry is measured in real elapsed time rather than whole days, so a 1-day policy expires a backup at 24 hours, not at the end of the following day.

### Changing a schedule's retention

`POST /api/schedules/:id/retention-impact` reports what a proposed value would do to backups the schedule has already created — which would newly expire, how much storage that frees, and which would come back inside the window if you are raising it. It is read-only.

Applying the new value to those existing backups is opt-in: pass `apply_to_existing: true` on the schedule update. This stamps them with the new policy, which also makes them eligible for the automatic sweep. Without it, the change governs future backups only.

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
| `POST` | `/api/backups/:id/hold` | Pin or unpin a backup so retention never removes it |

**Trigger backup body (all fields optional):**
```json
{
  "server_id": "uuid",
  "database": "mydb",
  "name": "Pre-release backup",
  "notes": "Before v2.0 deploy",
  "retention_days": 90
}
```

`retention_days` is stamped onto the backup at creation. Omit it and `BACKUP_RETENTION_DAYS` is used.

**Hold body:** `{"hold": true}` to pin, `{"hold": false}` to unpin. Defaults to pinning when the body is omitted.

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
| `POST` | `/api/schedules/:id/retention-impact` | Preview what a proposed retention value would do to existing backups |

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

Schedules follow the same fan-out logic as manual backups. Omit `server_id` and `database` to back up everything. Backups a schedule creates inherit its `retention_days` and its name.

**Update body** takes the same fields, plus `apply_to_existing: true` to stamp a changed `retention_days` onto backups the schedule has already created. The response reports how many were updated as `applied_to_existing`.

### Retention

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/retention/status` | Summary counts and storage totals for expired backups |
| `GET` | `/api/retention/preview?include_legacy=` | Everything a sweep would remove, plus what is protected and why |
| `POST` | `/api/retention/run` | Run a sweep |

**Sweep body (all fields optional):**
```json
{
  "dry_run": false,
  "include_legacy": false,
  "backup_ids": ["uuid"]
}
```

- `dry_run` defaults to `true`. Deletion requires an explicit `false`, so a malformed or empty request can never destroy anything.
- `include_legacy` extends the sweep to backups whose retention was inferred rather than snapshotted. The automatic sweep never sets this.
- `backup_ids` narrows the run to a specific set. The list is intersected with the expired set, so it can never reach a backup that is still in policy; anything excluded comes back in `rejected_ids`.

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
| `/` | Dashboard with stat cards, recent backups, and the stale-backup banner |
| `/backups` | Backup list with filters, trigger, annotate, delete, restore, pin, and per-row retention review |
| `/schedules` | Schedule management with cron builder, toggle switches, and the retention impact dialog |
| `/restore` | Restore history and trigger new restores |
| `/settings` | Server and database management (add/edit/delete/test/sync) |
| `/help` | Built-in help documentation |

## How Backups Work

1. A backup is created with status `pending`, stamped with its retention period, and a background thread is started
2. The status changes to `running` and `mongodump` is executed against the target server
3. The dump is compressed into a `.tar.gz` archive
4. The archive is uploaded to blob storage at `YYYY/MM/DD/mongodb_backup_TIMESTAMP.tar.gz`
5. The backup record is updated with `completed` status, `blob_path`, and `file_size_bytes`
6. If any step fails, the status is set to `failed` with an error message

Restores follow the reverse process: download from blob, extract, run `mongorestore`.

Once a backup passes the retention period stamped in step 1, the next sweep removes both the archive and its metadata record — unless one of the safeguards in [Retention](#retention) applies.

## Security

- Server passwords are encrypted at rest using Fernet symmetric encryption (derived from `SECRET_KEY` via SHA-256)
- Passwords are never returned in API responses
- The `SECRET_KEY` should be a strong random value in production

## Running Tests

The test suite ships with the source repository rather than the published image. From a checkout:

```bash
cd backup-manager
python -m pytest
```

## Deployment on Quix Cloud

The deployment is configured via [app.yaml](app.yaml). Set `METADATA_BACKEND=json` to avoid needing a separate metadata MongoDB instance. The JSON metadata file is automatically synced to Quix blob storage.

Key Quix variables to configure:
- `METADATA_BACKEND` — `json` (recommended) or `mongo`
- `SECRET_KEY` — set as a Secret in Quix Cloud
- `BACKUP_RETENTION_DAYS` — how long backups are kept when no schedule sets its own period
- `RETENTION_MIN_KEEP` — recent backups always kept per database, whatever their age
- Blob storage is automatically bound

Retention needs nothing switched on. It runs from first start with the defaults above, and backups that predate the upgrade are listed for review rather than deleted.
