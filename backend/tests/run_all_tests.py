#!/usr/bin/env python3
"""
Test runner for all backend tests
"""

import os
import sys
import subprocess
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def run_test_suite(suite_name, test_dir):
    """Run a specific test suite"""
    print(f"\n🧪 Running {suite_name} Tests")
    print("=" * 50)
    
    test_files = list(Path(test_dir).glob("test_*.py"))
    if not test_files:
        print(f"⚠️  No test files found in {test_dir}")
        return True
    
    results = []
    for test_file in test_files:
        print(f"\n🔍 Running {test_file.name}...")
        try:
            result = subprocess.run([
                sys.executable, str(test_file)
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {test_file.name} PASSED")
                results.append(True)
            else:
                print(f"❌ {test_file.name} FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                results.append(False)
                
        except Exception as e:
            print(f"💥 {test_file.name} ERROR: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\n📊 {suite_name} Summary: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all test suites"""
    print("🚀 Backend Test Suite Runner")
    print("📁 Organized Test Structure:")
    print("   🔧 tests/unit/ - Unit tests")
    print("   🔗 tests/integration/ - Integration tests")
    print("   🌐 tests/e2e/ - End-to-end tests")
    
    # Change to backend directory
    os.chdir(project_root)
    
    suite_results = []
    
    # Run unit tests
    suite_results.append(run_test_suite("Unit", "tests/unit"))
    
    # Run integration tests  
    suite_results.append(run_test_suite("Integration", "tests/integration"))
    
    # Run e2e tests
    suite_results.append(run_test_suite("E2E", "tests/e2e"))
    
    # Overall summary
    print("\n" + "=" * 60)
    print("🎯 Overall Test Results:")
    suites = ["Unit Tests", "Integration Tests", "E2E Tests"]
    
    for i, (suite_name, result) in enumerate(zip(suites, suite_results)):
        status = "✅" if result else "❌"
        print(f"   {status} {suite_name}")
    
    passed = sum(suite_results)
    total = len(suite_results)
    print(f"\n📊 Final Summary: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All test suites passed! Backend is ready for production.")
    else:
        print("🔧 Some test suites failed. Please check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)