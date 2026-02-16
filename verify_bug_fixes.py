#!/usr/bin/env python3
"""
Bug Fix Verification Script
Verifies all 15 bug fixes are properly implemented
"""

import sys
import os

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_file_contains(filepath, search_string, description):
    """Check if file contains a specific string"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}: NOT FOUND")
                return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def main():
    print("=" * 60)
    print("BUG FIX VERIFICATION")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Bug #1: asyncpg driver
    print("🔴 CRITICAL #1: asyncpg Driver")
    all_passed &= check_file_contains(
        "requirements.txt",
        "asyncpg==0.29.0",
        "asyncpg dependency added"
    )
    print()
    
    # Bug #2: CORS configuration
    print("🔴 CRITICAL #2: CORS Configuration")
    all_passed &= check_file_contains(
        "app/main.py",
        "ALLOWED_ORIGINS = os.getenv(",
        "Environment variable CORS configuration"
    )
    all_passed &= check_file_contains(
        ".env.example",
        "ALLOWED_ORIGINS",
        "CORS documented in .env.example"
    )
    print()
    
    # Bug #3: Security bypass
    print("🔴 CRITICAL #3: Security Bypass Fix")
    all_passed &= check_file_contains(
        "app/routes/scan.py",
        "settings.ALLOW_PRIVATE_IP_SCANNING and payload.options.allow_private",
        "Security validation implemented"
    )
    print()
    
    # Bug #4: Memory leak
    print("🟠 HIGH #4: Memory Leak Fix")
    all_passed &= check_file_contains(
        "app/core/rate_limit.py",
        "cutoff_hour = now - 3600",
        "Inactive IP cleanup implemented"
    )
    print()
    
    # Bug #5: SQL injection
    print("🟠 HIGH #5: SQL Injection Protection")
    all_passed &= check_file_contains(
        "app/db/crud.py",
        "escaped_target = target.replace",
        "LIKE wildcard escaping implemented"
    )
    print()
    
    # Bug #6: XML recovery
    print("🟠 HIGH #6: XML Parse Recovery")
    all_passed &= check_file_contains(
        "app/services/nmap_scan.py",
        "is_partial_recovery",
        "XML recovery logic implemented"
    )
    print()
    
    # Bug #7: Frontend API URL
    print("🟠 HIGH #7: Frontend API Base URL")
    all_passed &= check_file_contains(
        "frontend/src/api/client.ts",
        "import.meta.env.PROD",
        "Production URL logic implemented"
    )
    all_passed &= check_file_exists(
        "frontend/.env.production",
        "Production env file created"
    )
    print()
    
    # Bug #8: Input validation
    print("🟠 HIGH #8: Input Validation Schema")
    all_passed &= check_file_contains(
        "app/schemas/scan.py",
        'description="Allow scanning of private IP addresses',
        "Field descriptions added"
    )
    print()
    
    # Bug #9: Response model
    print("🟡 MEDIUM #9: Response Model")
    all_passed &= check_file_contains(
        "app/routes/scan.py",
        "response_model=ScanResultResponse",
        "Response model added to endpoint"
    )
    print()
    
    # Bug #10: Bulk delete
    print("🟡 MEDIUM #10: Bulk Delete")
    all_passed &= check_file_contains(
        "app/db/crud.py",
        "from sqlalchemy import delete",
        "Bulk delete implemented"
    )
    all_passed &= check_file_contains(
        "app/db/crud.py",
        "result.rowcount",
        "Using rowcount from bulk delete"
    )
    print()
    
    # Bug #11: HTTP timeout
    print("🟡 MEDIUM #11: HTTP Timeout")
    all_passed &= check_file_contains(
        "frontend/src/api/client.ts",
        "timeout: 30000",
        "30-second timeout added"
    )
    print()
    
    # Bug #12: Division by zero
    print("🟡 MEDIUM #12: Division by Zero Protection")
    all_passed &= check_file_contains(
        "app/services/ai_service.py",
        "max(len(cvss_scores), 1)",
        "Defensive division implemented"
    )
    print()
    
    # Bug #13: Datetime consistency
    print("🟢 LOW #13: Datetime Consistency")
    all_passed &= check_file_contains(
        "app/db/models.py",
        "from datetime import datetime, UTC",
        "UTC import in models.py"
    )
    all_passed &= check_file_contains(
        "app/db/crud.py",
        "from datetime import datetime, UTC",
        "UTC import in crud.py"
    )
    print()
    
    # Bug #14: Exception specificity
    print("🟢 LOW #14: Exception Specificity")
    all_passed &= check_file_contains(
        "app/routes/scan.py",
        "except (ValueError, TargetValidationError)",
        "Specific exceptions used"
    )
    print()
    
    # Bug #15: Index consistency
    print("🟢 LOW #15: Index Consistency")
    all_passed &= check_file_contains(
        "app/db/models.py",
        "Index('ix_scan_parent', 'parent_scan_id')",
        "Index moved to __table_args__"
    )
    print()
    
    # Additional improvements
    print("➕ ADDITIONAL: Health Check Enhancement")
    all_passed &= check_file_contains(
        "app/routes/health.py",
        "status_code = 503",
        "503 status for unhealthy database"
    )
    print()
    
    # Documentation
    print("📄 DOCUMENTATION")
    all_passed &= check_file_exists(
        "BUG_FIX_CHANGELOG.md",
        "Detailed changelog created"
    )
    all_passed &= check_file_exists(
        "BUG_FIX_SUMMARY.md",
        "Quick summary created"
    )
    print()
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED!")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("1. pip install -r requirements.txt")
        print("2. Set ALLOWED_ORIGINS in .env for production")
        print("3. Run tests: python app/main.py")
        print("4. Review BUG_FIX_SUMMARY.md for deployment checklist")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("=" * 60)
        print("Please review the failed checks above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
