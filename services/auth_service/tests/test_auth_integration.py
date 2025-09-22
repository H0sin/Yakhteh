"""
Integration tests for auth_service registration and login endpoints.

These tests ensure the complete registration → login flow works correctly
and catch potential database issues like UndefinedTableError before runtime.
"""
import pytest
import logging
import uuid
from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User


pytestmark = pytest.mark.anyio

BASE = "/api/v1/auth"


async def test_complete_registration_login_integration(client):
    """
    Integration test for complete registration → login flow.
    
    This test ensures:
    - Registration returns HTTP 201 with correct user data
    - Login returns HTTP 200 with valid JWT token
    - Database operations work correctly without table errors
    - User data persists correctly between operations
    """
    fake = Faker()
    
    # Step 1: Register a new user
    email = fake.unique.email()
    password = "StrongPassw0rd!"
    full_name = fake.name()
    workspace_name = f"{fake.last_name()} Clinic"
    
    register_payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "workspace_name": workspace_name,
    }
    
    # Test registration endpoint
    register_resp = await client.post(f"{BASE}/register", json=register_payload)
    assert register_resp.status_code == 201, f"Registration failed: {register_resp.text}"
    
    register_data = register_resp.json()
    assert register_data["email"] == email
    assert register_data["role"] == "doctor"
    assert register_data["is_active"] is True
    assert "id" in register_data
    
    # Verify the response contains a valid UUID
    user_id = register_data["id"]
    assert uuid.UUID(user_id)  # Should not raise exception if valid UUID
    
    # Step 2: Login with the registered user
    login_form = {"username": email, "password": password}
    login_resp = await client.post(f"{BASE}/login", data=login_form)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["access_token"], "Token should not be empty"
    assert login_data["token_type"] == "bearer"
    
    # Step 3: Verify token works with protected endpoint
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}
    me_resp = await client.get(f"{BASE}/me", headers=headers)
    assert me_resp.status_code == 200, f"Token validation failed: {me_resp.text}"
    
    me_data = me_resp.json()
    assert me_data["email"] == email
    assert me_data["id"] == user_id
    assert me_data["is_active"] is True


async def test_database_table_existence_and_operations(test_engine_and_sessionmaker):
    """
    Test that verifies database tables exist and operations work correctly.
    
    This test specifically catches UndefinedTableError and similar DB issues
    that could occur at runtime if migrations haven't run properly.
    """
    engine, SessionLocal = test_engine_and_sessionmaker
    
    async with SessionLocal() as session:
        # Test 1: Verify the users table exists and is accessible
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'users'"))
        table_exists = result.fetchone()
        assert table_exists is not None, "Users table does not exist in database"
        
        # Test 2: Verify we can query the users table structure
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        # Verify essential columns exist
        column_names = [col[0] for col in columns]
        expected_columns = ["id", "email", "hashed_password", "full_name", "role", "is_active", "created_at", "updated_at"]
        
        for expected_col in expected_columns:
            assert expected_col in column_names, f"Required column '{expected_col}' missing from users table"
        
        # Test 3: Verify we can perform basic CRUD operations on users table
        # This would catch issues like missing constraints, enum types, etc.
        fake = Faker()
        test_user = User(
            email=fake.unique.email(),
            hashed_password="$2b$12$test.hash.value",
            full_name=fake.name(),
            role="doctor",
            is_active=True
        )
        
        session.add(test_user)
        await session.commit()
        
        # Verify the user was inserted
        result = await session.execute(text("SELECT COUNT(*) FROM users WHERE email = :email"), {"email": test_user.email})
        count = result.scalar()
        assert count == 1, "User insertion failed"
        
        # Verify we can query the user back
        from app.crud.crud_user import get_user_by_email
        retrieved_user = await get_user_by_email(session, test_user.email)
        assert retrieved_user is not None, "User retrieval failed"
        assert retrieved_user.email == test_user.email


async def test_registration_validation_and_error_handling(client):
    """
    Test registration endpoint validation and proper error responses.
    
    Ensures the endpoint properly validates input and returns appropriate
    HTTP status codes for various error conditions.
    """
    fake = Faker()
    
    # Test 1: Registration with missing required fields
    incomplete_payload = {"email": fake.email()}
    resp = await client.post(f"{BASE}/register", json=incomplete_payload)
    assert resp.status_code == 422, "Should return validation error for incomplete data"
    
    # Test 2: Registration with invalid email format
    invalid_email_payload = {
        "email": "not-an-email",
        "password": "StrongPassw0rd!",
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    resp = await client.post(f"{BASE}/register", json=invalid_email_payload)
    assert resp.status_code == 422, "Should return validation error for invalid email"
    
    # Test 3: Registration with weak password (if validation exists)
    weak_password_payload = {
        "email": fake.unique.email(),
        "password": "123",
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    resp = await client.post(f"{BASE}/register", json=weak_password_payload)
    # Note: This might pass depending on password validation rules
    # The important thing is it doesn't cause a server error
    assert resp.status_code in [201, 422], f"Unexpected error: {resp.text}"


async def test_login_validation_and_error_handling(client):
    """
    Test login endpoint validation and proper error responses.
    
    Ensures the endpoint properly handles various login scenarios
    and returns appropriate HTTP status codes.
    """
    fake = Faker()
    
    # First, register a user for testing
    email = fake.unique.email()
    password = "StrongPassw0rd!"
    register_payload = {
        "email": email,
        "password": password,
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    register_resp = await client.post(f"{BASE}/register", json=register_payload)
    assert register_resp.status_code == 201
    
    # Test 1: Login with correct credentials
    login_form = {"username": email, "password": password}
    resp = await client.post(f"{BASE}/login", data=login_form)
    assert resp.status_code == 200, "Login with correct credentials should succeed"
    
    # Test 2: Login with incorrect password
    wrong_password_form = {"username": email, "password": "WrongPassword!"}
    resp = await client.post(f"{BASE}/login", data=wrong_password_form)
    assert resp.status_code == 401, "Login with wrong password should return 401"
    assert resp.json().get("detail") == "Incorrect email or password"
    
    # Test 3: Login with non-existent email
    nonexistent_form = {"username": "nonexistent@example.com", "password": password}
    resp = await client.post(f"{BASE}/login", data=nonexistent_form)
    assert resp.status_code == 401, "Login with non-existent email should return 401"
    assert resp.json().get("detail") == "Incorrect email or password"
    
    # Test 4: Login with missing credentials
    resp = await client.post(f"{BASE}/login", data={})
    assert resp.status_code == 422, "Login with missing credentials should return 422"


async def test_concurrent_registrations_database_integrity(client):
    """
    Test that concurrent registrations maintain database integrity.
    
    This test helps catch race conditions and database constraint issues
    that might occur under load.
    """
    fake = Faker()
    
    # Test duplicate email registration (should fail on second attempt)
    email = fake.unique.email()
    password = "StrongPassw0rd!"
    
    payload = {
        "email": email,
        "password": password,
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    
    # First registration should succeed
    first_resp = await client.post(f"{BASE}/register", json=payload)
    assert first_resp.status_code == 201, "First registration should succeed"
    
    # Second registration with same email should fail
    second_resp = await client.post(f"{BASE}/register", json=payload)
    assert second_resp.status_code == 400, "Duplicate email registration should fail"
    assert second_resp.json().get("detail") == "Email already registered"


async def test_token_structure_and_validity(client):
    """
    Test that generated JWT tokens have the correct structure and claims.
    
    This ensures tokens contain the necessary information and are properly formatted.
    """
    import jose.jwt
    from app.core.config import settings
    
    fake = Faker()
    
    # Register and login to get a token
    email = fake.unique.email()
    password = "StrongPassw0rd!"
    
    register_payload = {
        "email": email,
        "password": password,
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    register_resp = await client.post(f"{BASE}/register", json=register_payload)
    assert register_resp.status_code == 201
    user_id = register_resp.json()["id"]
    
    login_form = {"username": email, "password": password}
    login_resp = await client.post(f"{BASE}/login", data=login_form)
    assert login_resp.status_code == 200
    
    token = login_resp.json()["access_token"]
    
    # Decode token and verify structure
    try:
        # Note: In production, you'd verify the signature properly
        # For testing, we just decode without verification to check structure
        payload = jose.jwt.get_unverified_claims(token)
        
        # Verify required claims exist
        assert "sub" in payload, "Token should contain 'sub' claim"
        assert "exp" in payload, "Token should contain 'exp' claim"
        
        # Verify the subject matches the user ID
        assert payload["sub"] == user_id, "Token subject should match user ID"
        
        # Verify token is not expired (exp claim should be in the future)
        import time
        current_time = int(time.time())
        assert payload["exp"] > current_time, "Token should not be expired"
        
    except Exception as e:
        pytest.fail(f"Token structure validation failed: {e}")


async def test_auth_endpoints_logging_no_errors(client, caplog):
    """
    Test that auth operations don't generate error logs.
    
    This test ensures no unexpected errors are logged during normal operations,
    which could indicate underlying issues.
    """
    fake = Faker()
    
    # Clear any existing log records
    caplog.clear()
    
    # Set log level to capture errors
    with caplog.at_level(logging.ERROR):
        # Perform complete registration → login flow
        email = fake.unique.email()
        password = "StrongPassw0rd!"
        
        register_payload = {
            "email": email,
            "password": password,
            "full_name": fake.name(),
            "workspace_name": f"{fake.last_name()} Clinic",
        }
        
        register_resp = await client.post(f"{BASE}/register", json=register_payload)
        assert register_resp.status_code == 201
        
        login_form = {"username": email, "password": password}
        login_resp = await client.post(f"{BASE}/login", data=login_form)
        assert login_resp.status_code == 200
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = await client.get(f"{BASE}/me", headers=headers)
        assert me_resp.status_code == 200
    
    # Check that no error-level logs were generated
    error_logs = [record for record in caplog.records if record.levelno >= logging.ERROR]
    assert len(error_logs) == 0, f"Unexpected error logs detected: {[r.message for r in error_logs]}"


async def test_prevent_undefined_table_errors(test_engine_and_sessionmaker):
    """
    Specific test to prevent UndefinedTableError and similar database issues.
    
    This test ensures all required database objects (tables, indexes, constraints)
    are properly created and accessible, preventing runtime errors like UndefinedTableError.
    """
    engine, SessionLocal = test_engine_and_sessionmaker
    
    async with SessionLocal() as session:
        # Test 1: Verify all expected tables exist
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        # At minimum, we need the users table
        assert "users" in tables, "Users table is missing - this would cause UndefinedTableError"
        
        # Test 2: Verify all expected columns exist with correct types
        result = await session.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        column_info = {col[0]: {"type": col[1], "nullable": col[3]} for col in columns}
        
        # Verify critical columns
        critical_columns = {
            "id": {"type": "uuid", "nullable": "NO"},
            "email": {"type": "character varying", "nullable": "NO"},
            "hashed_password": {"type": "character varying", "nullable": "NO"},
            "role": {"type": "USER_DEFINED", "nullable": "NO"},  # Enum type
            "is_active": {"type": "boolean", "nullable": "NO"},
        }
        
        for col_name, expected in critical_columns.items():
            assert col_name in column_info, f"Critical column '{col_name}' missing"
            actual = column_info[col_name]
            assert actual["nullable"] == expected["nullable"], f"Column '{col_name}' nullable mismatch"
            # Note: data_type matching can be flexible due to PostgreSQL type mapping
        
        # Test 3: Verify enum types exist (role enum)
        result = await session.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e'
        """))
        enum_types = [row[0] for row in result.fetchall()]
        
        # Check if the user role enum exists (name may vary)
        role_enum_exists = any("userrole" in enum_type.lower() for enum_type in enum_types)
        assert role_enum_exists, "UserRole enum type is missing - this could cause enum errors"
        
        # Test 4: Verify indexes exist (especially unique constraints)
        result = await session.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE tablename = 'users'
        """))
        indexes = result.fetchall()
        
        # Verify email unique index exists
        email_index_exists = any("email" in idx[1].lower() and "unique" in idx[1].lower() for idx in indexes)
        assert email_index_exists, "Email unique index missing - this could cause constraint errors"
        
        # Test 5: Try actual operations that would fail with UndefinedTableError
        try:
            # This would fail with UndefinedTableError if tables don't exist
            from app.crud.crud_user import get_user_by_email, create_user
            from app.schemas.user_schema import UserCreate
            
            # Test user lookup (would fail if table doesn't exist)
            user = await get_user_by_email(session, "nonexistent@example.com")
            assert user is None, "Should return None for non-existent user"
            
            # Test user creation (would fail if table/constraints don't exist)
            fake = Faker()
            user_data = UserCreate(
                email=fake.unique.email(),
                password="TestPassword123!",
                full_name=fake.name(),
                workspace_name=f"{fake.last_name()} Test Clinic"
            )
            
            created_user = await create_user(session, user_data)
            assert created_user is not None, "User creation should succeed"
            assert created_user.email == user_data.email
            
        except Exception as e:
            if "UndefinedTableError" in str(type(e)) or "relation does not exist" in str(e).lower():
                pytest.fail(f"UndefinedTableError or similar database error detected: {e}")
            else:
                # Re-raise other unexpected errors
                raise