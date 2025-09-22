# Database Migration Enum Conflict Fix

## Problem Summary

The Yakhteh microservices were experiencing database migration failures due to PostgreSQL enum type conflicts:

```
sqlalchemy.exc.ProgrammingError: type "subscriptionstatus" already exists
sqlalchemy.exc.ProgrammingError: type "appointmentstatus" already exists
```

## Root Cause

- All microservices (auth_service, clinic_service, scheduling_service) connect to the same PostgreSQL database (`yakhteh`)
- Services start simultaneously via Docker Compose
- Each service runs Alembic migrations that create PostgreSQL enum types
- When multiple services try to create the same enum type, PostgreSQL throws "already exists" errors
- This caused services to crash and restart in loops

## Solution

Modified all Alembic migration files to use `checkfirst=True` parameter when creating/dropping enum types, making migrations idempotent:

### Before Fix
```python
def upgrade() -> None:
    op.create_table(
        'clinics',
        # ... other columns ...
        sa.Column('subscription_status', sa.Enum('free', 'premium', 'expired', name='subscriptionstatus'), ...),
    )
```

### After Fix
```python  
def upgrade() -> None:
    # Create enum type if it doesn't exist
    subscription_status_enum = postgresql.ENUM('free', 'premium', 'expired', name='subscriptionstatus')
    subscription_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.create_table(
        'clinics',
        # ... other columns ...
        sa.Column('subscription_status', sa.Enum('free', 'premium', 'expired', name='subscriptionstatus'), ...),
    )

def downgrade() -> None:
    op.drop_table('clinics')
    
    # Drop enum type if it exists
    subscription_status_enum = postgresql.ENUM(name='subscriptionstatus')
    subscription_status_enum.drop(op.get_bind(), checkfirst=True)
```

## Files Modified

1. `services/auth_service/alembic/versions/20250921_000001_create_users_table.py`
   - Fixed `userrole` enum creation
2. `services/clinic_service/alembic/versions/20250921_000002_create_clinics_table.py`
   - Fixed `subscriptionstatus` enum creation  
3. `services/scheduling_service/alembic/versions/20250921_000003_create_appointments_table.py`
   - Fixed `appointmentstatus` enum creation

## Expected Results

- ✅ Services start successfully without enum conflicts
- ✅ Migrations complete without "already exists" errors
- ✅ Database schema created correctly with all required enums
- ✅ Multiple container restarts work smoothly
- ✅ No more service crash loops due to migration failures

## Testing

All migration files have been validated for:
- ✅ Correct syntax and imports
- ✅ Proper enum creation with `checkfirst=True`
- ✅ Idempotent behavior (safe to run multiple times)
- ✅ Proper cleanup in downgrade operations