# PostgreSQL External Access Configuration

This document explains how PostgreSQL is configured to allow external database management tools (like DataGrip, pgAdmin, etc.) to connect to the database.

## Configuration Changes

### 1. Port Exposure
The PostgreSQL service now exposes port 5432 to the host machine:
```yaml
ports:
  - "5432:5432"  # Expose PostgreSQL port for external database management tools
```

### 2. PostgreSQL Configuration
Custom configuration files are mounted to enable external connections:

#### postgresql.conf
- `listen_addresses = '*'` - Accept connections from any IP address
- Standard PostgreSQL settings for development environment

#### pg_hba.conf  
- Allows connections from Docker networks (172.16.0.0/12, 10.0.0.0/8, 192.168.0.0/16)
- Allows connections from localhost (127.0.0.1/32)
- **Development only**: Allows all connections (0.0.0.0/0) with password authentication

## Connection Details

### For Database Management Tools (DataGrip, pgAdmin, etc.)
- **Host**: `localhost` (or your server's external IP)
- **Port**: `5432`
- **Database**: `yakhteh`
- **Username**: `postgres`
- **Password**: `postgres` (default, change in production)

### Connection String
```
postgresql://postgres:postgres@localhost:5432/yakhteh
```

## Security Considerations

### Development Environment
- Current configuration is suitable for development
- All IPs are allowed for convenience

### Production Environment
**IMPORTANT**: For production deployments, you should:

1. **Restrict IP Access**: Replace the broad access rule in `pg_hba.conf`:
   ```
   # Instead of allowing all IPs:
   # host    all             all             0.0.0.0/0               md5
   
   # Use specific IP addresses:
   host    all             all             YOUR_IP_ADDRESS/32      md5
   host    all             all             OFFICE_IP_ADDRESS/32    md5
   ```

2. **Use SSL**: Enable SSL in PostgreSQL configuration:
   ```
   ssl = on
   ssl_cert_file = '/path/to/server.crt'
   ssl_key_file = '/path/to/server.key'
   ```

3. **Strong Passwords**: Change default passwords in `.env`:
   ```bash
   POSTGRES_PASSWORD=your-strong-password
   ```

4. **Firewall**: Use server firewall to limit port 5432 access:
   ```bash
   # Example with ufw
   sudo ufw allow from YOUR_IP to any port 5432
   ```

## Testing the Configuration

### Using psql (command line)
```bash
psql -h localhost -U postgres -d yakhteh
```

### Using DataGrip
1. Create new Data Source
2. Choose PostgreSQL
3. Enter connection details above
4. Test connection

### Verify External Access
```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d yakhteh -c "SELECT version();"
```

## Troubleshooting

### Connection Refused
- Ensure PostgreSQL container is running: `docker ps`
- Check port is exposed: `docker port yakhteh_postgres`
- Verify container logs: `docker logs yakhteh_postgres`

### Authentication Failed
- Check username/password in `.env` file
- Verify pg_hba.conf allows your connection type

### Internal Services Still Work
- Internal services use `postgres_db:5432` (Docker network)
- External tools use `localhost:5432` (host network)
- Both access methods work simultaneously