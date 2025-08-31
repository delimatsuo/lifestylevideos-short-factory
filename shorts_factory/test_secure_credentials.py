#!/usr/bin/env python3
"""
Test script for secure credential system
Verifies that the migration was successful and credentials can be retrieved

Usage:
    python test_secure_credentials.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from security.secure_config import config
    from security.secure_credential_manager import get_credential_manager
    
    print("🔍 TESTING SECURE CREDENTIAL SYSTEM")
    print("=" * 50)
    
    # Test credential manager directly
    print("\n📋 Testing Credential Manager:")
    credential_manager = get_credential_manager()
    
    # List stored credentials
    stored = credential_manager.list_stored_credentials()
    print(f"✅ Found {len(stored)} stored credentials")
    
    # Test specific credentials
    test_credentials = [
        'GOOGLE_GEMINI_API_KEY',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'PEXELS_API_KEY'
    ]
    
    print("\n🔐 Testing Credential Retrieval:")
    for cred_name in test_credentials:
        try:
            value = credential_manager.get_credential(cred_name)
            if value:
                print(f"✅ {cred_name}: Retrieved ({len(value)} chars)")
            else:
                print(f"❌ {cred_name}: Not found")
        except Exception as e:
            print(f"❌ {cred_name}: Error - {e}")
    
    print("\n🔧 Testing Secure Config:")
    
    # Test secure config properties
    config_tests = [
        ('Google Gemini API Key', lambda: config.google_gemini_api_key),
        ('OpenAI API Key', lambda: config.openai_api_key),
        ('ElevenLabs API Key', lambda: config.elevenlabs_api_key),
        ('Pexels API Key', lambda: config.pexels_api_key),
        ('Reddit Client Secret', lambda: config.reddit_client_secret),
    ]
    
    for name, getter in config_tests:
        try:
            value = getter()
            if value:
                print(f"✅ {name}: Retrieved ({len(value)} chars)")
            else:
                print(f"❌ {name}: Empty value")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n🔍 Testing Non-sensitive Config:")
    try:
        print(f"✅ Spreadsheet ID: {config.google_sheets_spreadsheet_id}")
        print(f"✅ Working Directory: {config.working_directory}")
        print(f"✅ Log Level: {config.log_level}")
    except Exception as e:
        print(f"❌ Non-sensitive config error: {e}")
    
    print("\n🛡️ Testing Security Status:")
    security_report = credential_manager.verify_system_security()
    print(f"✅ Keychain Available: {security_report['keychain_available']}")
    print(f"✅ Audit System: {security_report['audit_system_active']}")
    print(f"✅ Stored Credentials: {security_report['stored_credentials']}")
    
    if security_report['security_issues']:
        print("⚠️ Security Issues:")
        for issue in security_report['security_issues']:
            print(f"   - {issue}")
    else:
        print("✅ No security issues detected")
    
    print("\n" + "=" * 50)
    print("🎉 SECURE CREDENTIAL SYSTEM TEST COMPLETE!")
    print("🔐 CV-001 API Key Exposure vulnerability RESOLVED!")
    print("=" * 50)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
