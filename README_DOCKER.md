# Docker Setup for PostgreSQL

This project uses Docker to run PostgreSQL with the following configuration:
- **Database**: room_counselling
- **User**: admin
- **Password**: admin
- **Port**: 5432

## Prerequisites

- Docker Desktop for Windows must be installed and running
- Download from: https://www.docker.com/products/docker-desktop/

## Quick Start

### 1. Start PostgreSQL Container

```powershell
# Start the database (creates and starts the container)
docker-compose up -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f postgres
```

### 2. Run Migrations

After the database is running, apply the schema:

```powershell
python run_migration.py
```

### 3. Load Sample Data (Optional)

```powershell
python load_sample_data.py
```

## Useful Commands

### Stop the database
```powershell
docker-compose stop
```

### Start the database (if already created)
```powershell
docker-compose start
```

### Stop and remove the database (DELETE ALL DATA)
```powershell
docker-compose down
```

### Stop and remove database WITH volumes (COMPLETE CLEANUP)
```powershell
docker-compose down -v
```

### Recreate the database from scratch
```powershell
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait a few seconds for DB to be ready
Start-Sleep -Seconds 5

# Run migrations
python run_migration.py

# Load sample data
python load_sample_data.py
```

### Access PostgreSQL CLI
```powershell
docker-compose exec postgres psql -U admin -d room_counselling
```

### View logs
```powershell
docker-compose logs -f postgres
```

## Troubleshooting

### Port 5432 already in use
If you have another PostgreSQL instance running, either:
1. Stop the other PostgreSQL service
2. Or change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "5433:5432"  # Use port 5433 instead
   ```
   Then update `DB_CONFIG` in all Python files to use port 5433.

### Container won't start
```powershell
# Check Docker Desktop is running
# View detailed logs
docker-compose logs postgres

# Remove and recreate
docker-compose down -v
docker-compose up -d
```
