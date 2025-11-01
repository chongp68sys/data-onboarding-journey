#!/usr/bin/env python3
"""
Test the reorganized backend structure
"""

import os
import sys
import csv
from pathlib import Path
from dotenv import load_dotenv

# Set up paths
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Load environment config
load_dotenv(project_root / "config" / ".env")

def create_test_csv():
    """Create test CSV for validation"""
    os.makedirs("tmp/test_data", exist_ok=True)
    
    test_data = [
        ["customer_id", "first_name", "last_name", "email", "age", "city", "balance"],
        ["1", "John", "Doe", "john@example.com", "25", "New York", "1500.50"],
        ["2", "Jane", "Smith", "jane@example.com", "30", "Los Angeles", "2200.75"],
        ["3", "Bob", "Johnson", "bob@example.com", "35", "Chicago", "1800.00"],
        ["4", "Alice", "Brown", "", "28", "San Francisco", "3500.25"],
        ["5", "Charlie", "Wilson", "charlie@example.com", "42", "Seattle", "2900.00"]
    ]
    
    csv_file = "tmp/test_data/reorganized_test.csv"
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(test_data)
    
    return csv_file

def test_new_structure():
    """Test the reorganized backend structure"""
    print("🏗️  Testing Reorganized Backend Structure")
    print("=" * 60)
    
    results = []
    
    # Test 1: Import observability components
    try:
        from observability import get_control_plane_app, setup_data_onboarding_platform
        print("✅ Observability imports working")
        results.append(True)
    except Exception as e:
        print(f"❌ Observability imports failed: {e}")
        results.append(False)
        return results
    
    # Test 2: Environment configuration
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        db_url = os.getenv("DATABASE_URL")
        
        if api_key:
            print(f"✅ Config loaded: API key found")
        else:
            print("⚠️  Config: No API key")
            
        if db_url:
            print(f"✅ Config loaded: Database URL found")
        else:
            print("⚠️  Config: No Database URL")
            
        results.append(bool(api_key))
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        results.append(False)
    
    # Test 3: Control-plane setup
    try:
        app = get_control_plane_app()
        print("✅ Control-plane app created successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ Control-plane setup failed: {e}")
        results.append(False)
        return results
    
    # Test 4: Individual agent functionality
    try:
        # We need to import agents directly due to the new structure
        csv_file = create_test_csv()
        
        # Test with absolute imports that should work
        from observability.agents.file_ingestion_agent import FileIngestionAgent
        
        agent = FileIngestionAgent()
        result = agent.process_file(csv_file)
        
        print(f"✅ Agent execution: {len(str(result.content))} chars output")
        results.append(True)
        
    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    return results

def main():
    """Main test function"""
    print("🚀 Backend Reorganization Test")
    print("📁 New Structure:")
    print("   📊 observability/ - Agno control-plane")
    print("   🗄️  core/ - Database and models")
    print("   🌐 api/ - FastAPI components")
    print("   ⚙️  config/ - Configuration")
    print("   🧪 tests/ - Organized test suites")
    print()
    
    results = test_new_structure()
    
    print("\n" + "=" * 60)
    print("🎯 Test Results:")
    tests = [
        "Observability Imports",
        "Configuration Loading", 
        "Control-plane Setup",
        "Agent Execution"
    ]
    
    for i, (test_name, result) in enumerate(zip(tests, results)):
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Reorganized backend structure working perfectly!")
        print("🚀 Clean separation of concerns achieved:")
        print("   • observability/ contains all Agno control-plane code")
        print("   • core/ contains shared database and model logic")
        print("   • config/ centralizes all configuration")
        print("   • tests/ organized by test type")
    else:
        print("🔧 Some reorganization issues detected")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)