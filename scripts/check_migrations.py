#!/usr/bin/env python3
"""
Quick verification script to check that all migration files have proper idempotent patterns.
This can be run to validate migration files after any future changes.
"""

import os
import re
from pathlib import Path

def check_migration_file(filepath):
    """Check if a migration file has proper idempotent patterns"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for enum creation with checkfirst=True
    if 'postgresql.ENUM(' in content and '.create(' in content:
        # Look for the specific pattern: .create(op.get_bind(), checkfirst=True)
        if 'checkfirst=True' not in content:
            issues.append("❌ Enum creation without checkfirst=True found")
        elif '.create(op.get_bind(), checkfirst=True)' not in content:
            issues.append("❌ Enum creation not using proper checkfirst pattern")
    
    # Check for table existence checks
    if 'op.create_table(' in content:
        if 'inspector = sa.inspect(bind)' not in content:
            issues.append("❌ Table creation without existence check found")
        elif 'existing_tables = inspector.get_table_names()' not in content:
            issues.append("❌ Table creation without table list check found")
        elif 'not in existing_tables:' not in content:
            issues.append("❌ Table creation without conditional check found")
    
    # Check for proper downgrade handling
    if 'def downgrade()' in content:
        if 'op.drop_table(' in content and 'try:' not in content:
            issues.append("⚠️  Downgrade may not handle missing indexes gracefully")
    
    return issues

def main():
    """Check all migration files"""
    print("🔍 Checking Migration Files for Idempotent Patterns")
    print("=" * 60)
    
    # Find all migration files
    migration_files = []
    services_dir = Path.cwd() / 'services'  # Use current working directory
    
    if services_dir.exists():
        for service_dir in services_dir.iterdir():
            if service_dir.is_dir():
                versions_dir = service_dir / 'alembic' / 'versions'
                if versions_dir.exists():
                    for py_file in versions_dir.glob('*.py'):
                        if not py_file.name.startswith('__'):
                            migration_files.append(py_file)
    
    if not migration_files:
        print("❌ No migration files found!")
        return False
    
    all_good = True
    
    for filepath in sorted(migration_files):
        print(f"\\nChecking: {filepath.relative_to(Path.cwd())}")
        issues = check_migration_file(filepath)
        
        if issues:
            all_good = False
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ All checks passed")
    
    print("\\n" + "=" * 60)
    if all_good:
        print("✅ ALL MIGRATION FILES LOOK GOOD!")
        print("   All files have proper idempotent patterns.")
    else:
        print("❌ SOME MIGRATION FILES HAVE ISSUES!")
        print("   Please review and fix the issues above.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)