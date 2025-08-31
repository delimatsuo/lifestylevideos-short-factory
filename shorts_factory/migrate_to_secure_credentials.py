#!/usr/bin/env python3
"""
Credential Migration Script for Shorts Factory
Migrates API keys from plain text .env files to encrypted keychain storage

This script addresses CV-001: API Key Exposure vulnerability by:
1. Reading existing credentials from .env files
2. Storing them securely in macOS Keychain
3. Creating a secure backup of .env with sensitive data removed
4. Verifying the migration was successful

Usage:
    python migrate_to_secure_credentials.py [--env-file PATH] [--backup]

Author: Security Remediation Team
Date: August 31, 2025  
Security Level: CRITICAL
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import shutil
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from security.secure_credential_manager import SecureCredentialManager


def print_banner():
    """Print security migration banner"""
    print("=" * 70)
    print("🔐 SHORTS FACTORY - SECURE CREDENTIAL MIGRATION")
    print("=" * 70)
    print("⚠️  SECURITY REMEDIATION: CV-001 API Key Exposure")
    print("🎯 Migrating API keys from plain text to encrypted storage")
    print("=" * 70)
    print()


def validate_keyring_available() -> bool:
    """Verify that keyring (keychain) is available"""
    try:
        import keyring
        
        # Test keyring functionality
        test_service = "ShortsFactory_Test"
        test_key = "test_migration_key"
        test_value = "test_value_123"
        
        keyring.set_password(test_service, test_key, test_value)
        retrieved = keyring.get_password(test_service, test_key)
        keyring.delete_password(test_service, test_key)
        
        if retrieved == test_value:
            print("✅ Keychain access verified")
            return True
        else:
            print("❌ Keychain test failed - retrieved value doesn't match")
            return False
            
    except ImportError:
        print("❌ keyring module not available. Install with: pip install keyring")
        return False
    except Exception as e:
        print(f"❌ Keychain access failed: {e}")
        return False


def analyze_env_file(env_file_path: Path) -> dict:
    """Analyze .env file and categorize variables"""
    if not env_file_path.exists():
        print(f"❌ Environment file not found: {env_file_path}")
        return {}
    
    print(f"🔍 Analyzing environment file: {env_file_path}")
    
    variables = {}
    sensitive_vars = []
    non_sensitive_vars = []
    placeholder_vars = []
    
    # Define what we consider sensitive
    sensitive_patterns = [
        'API_KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'PRIVATE_KEY'
    ]
    
    try:
        with open(env_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    variables[key] = value
                    
                    # Categorize the variable
                    is_sensitive = any(pattern in key.upper() for pattern in sensitive_patterns)
                    is_placeholder = value.startswith('your_') or len(value) < 8
                    
                    if is_sensitive:
                        if is_placeholder:
                            placeholder_vars.append(key)
                        else:
                            sensitive_vars.append(key)
                    else:
                        non_sensitive_vars.append(key)
    
    except Exception as e:
        print(f"❌ Error reading environment file: {e}")
        return {}
    
    # Print analysis results
    print(f"📊 Analysis Results:")
    print(f"   📈 Total variables: {len(variables)}")
    print(f"   🔴 Sensitive credentials: {len(sensitive_vars)}")
    print(f"   🟡 Placeholder values: {len(placeholder_vars)}")
    print(f"   🟢 Non-sensitive configs: {len(non_sensitive_vars)}")
    print()
    
    if sensitive_vars:
        print("🔴 Sensitive credentials found:")
        for var in sensitive_vars:
            print(f"   • {var}")
        print()
    
    if placeholder_vars:
        print("⚠️  Placeholder values (will be skipped):")
        for var in placeholder_vars:
            print(f"   • {var}: {variables[var]}")
        print()
    
    return {
        'all_variables': variables,
        'sensitive': sensitive_vars,
        'non_sensitive': non_sensitive_vars,
        'placeholders': placeholder_vars
    }


def create_secure_backup(env_file_path: Path) -> Path:
    """Create a backup of the original .env file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = env_file_path.parent / f".env.backup.{timestamp}"
    
    try:
        shutil.copy2(env_file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        raise


def migrate_credentials(credential_manager: SecureCredentialManager, 
                       env_analysis: dict) -> dict:
    """Migrate sensitive credentials to secure storage"""
    print("🔄 Migrating sensitive credentials to encrypted storage...")
    
    results = {}
    variables = env_analysis['all_variables']
    sensitive_vars = env_analysis['sensitive']
    
    for var_name in sensitive_vars:
        value = variables[var_name]
        
        print(f"   🔐 Migrating {var_name}...", end=" ")
        
        success = credential_manager.store_credential(
            var_name, 
            value, 
            f"Migrated from .env on {datetime.now()}"
        )
        
        if success:
            print("✅")
            results[var_name] = True
        else:
            print("❌")
            results[var_name] = False
    
    return results


def create_sanitized_env(env_file_path: Path, env_analysis: dict, 
                        migration_results: dict) -> Path:
    """Create a new .env file with sensitive credentials removed"""
    sanitized_path = env_file_path.parent / ".env.secure"
    
    print(f"📝 Creating sanitized environment file: {sanitized_path}")
    
    try:
        with open(env_file_path, 'r') as original:
            with open(sanitized_path, 'w') as sanitized:
                # Write header
                sanitized.write("# Shorts Factory Environment Configuration\n")
                sanitized.write("# SECURITY: Sensitive credentials moved to encrypted storage\n")
                sanitized.write(f"# Generated: {datetime.now()}\n")
                sanitized.write("\n")
                
                # Process each line
                for line in original:
                    line = line.rstrip()
                    
                    # Keep comments and empty lines
                    if not line or line.startswith('#'):
                        sanitized.write(line + "\n")
                        continue
                    
                    # Process key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        
                        # Check if this credential was migrated
                        if key in migration_results and migration_results[key]:
                            sanitized.write(f"# {key}=MOVED_TO_SECURE_STORAGE\n")
                        else:
                            # Keep non-sensitive or failed migrations
                            sanitized.write(line + "\n")
                    else:
                        sanitized.write(line + "\n")
        
        print("✅ Sanitized environment file created")
        return sanitized_path
        
    except Exception as e:
        print(f"❌ Failed to create sanitized file: {e}")
        raise


def verify_migration(credential_manager: SecureCredentialManager, 
                    migration_results: dict) -> bool:
    """Verify that migrated credentials can be retrieved"""
    print("🔍 Verifying migration...")
    
    all_success = True
    
    for var_name, was_migrated in migration_results.items():
        if was_migrated:
            print(f"   🔓 Testing {var_name}...", end=" ")
            
            retrieved = credential_manager.get_credential(var_name)
            if retrieved:
                print("✅")
            else:
                print("❌")
                all_success = False
    
    return all_success


def print_migration_summary(migration_results: dict, backup_path: Path, 
                           sanitized_path: Path):
    """Print migration summary"""
    print("\n" + "=" * 70)
    print("📋 MIGRATION SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for success in migration_results.values() if success)
    total = len(migration_results)
    
    print(f"✅ Successfully migrated: {successful}/{total} credentials")
    print(f"📁 Original backup: {backup_path}")
    print(f"📁 Sanitized config: {sanitized_path}")
    
    if successful == total:
        print("\n🎉 MIGRATION COMPLETE!")
        print("🔐 All sensitive credentials are now encrypted")
        print("⚡ Next steps:")
        print("   1. Replace .env with .env.secure:")
        print(f"      mv '{sanitized_path}' '{sanitized_path.parent / '.env'}'")
        print("   2. Update imports to use secure_config:")
        print("      from security.secure_config import config")
        print("   3. Test your application")
        print("   4. Delete backup after verification")
    else:
        failed = [name for name, success in migration_results.items() if not success]
        print(f"\n⚠️ Some migrations failed:")
        for name in failed:
            print(f"   ❌ {name}")
        print("\nPlease check the logs and retry failed credentials.")


def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(
        description="Migrate Shorts Factory credentials to secure storage"
    )
    parser.add_argument(
        '--env-file', 
        type=Path,
        default=Path('.env'),
        help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help="Create backup before migration (default: True)"
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help="Only verify keyring access, don't migrate"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Verify keyring is available
    if not validate_keyring_available():
        print("\n❌ Migration cannot continue without keyring access")
        print("Please install keyring: pip install keyring")
        sys.exit(1)
    
    if args.verify_only:
        print("✅ Keyring verification complete. Ready for migration.")
        sys.exit(0)
    
    # Initialize credential manager
    try:
        credential_manager = SecureCredentialManager()
        print("✅ Secure credential manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize credential manager: {e}")
        sys.exit(1)
    
    # Analyze environment file
    env_analysis = analyze_env_file(args.env_file)
    if not env_analysis:
        print("❌ No environment file to migrate")
        sys.exit(1)
    
    if not env_analysis['sensitive']:
        print("ℹ️  No sensitive credentials found to migrate")
        sys.exit(0)
    
    # Confirm migration
    print("⚠️  This will migrate sensitive credentials to encrypted storage.")
    response = input("Continue? [y/N]: ")
    if response.lower() != 'y':
        print("Migration cancelled")
        sys.exit(0)
    
    try:
        # Create backup
        backup_path = create_secure_backup(args.env_file)
        
        # Migrate credentials
        migration_results = migrate_credentials(credential_manager, env_analysis)
        
        # Verify migration
        verification_success = verify_migration(credential_manager, migration_results)
        
        # Create sanitized environment file
        sanitized_path = create_sanitized_env(args.env_file, env_analysis, migration_results)
        
        # Print summary
        print_migration_summary(migration_results, backup_path, sanitized_path)
        
        if verification_success:
            print("\n🔐 SECURITY VULNERABILITY CV-001 RESOLVED!")
            sys.exit(0)
        else:
            print("\n⚠️  Migration completed with some issues")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Check the logs and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
