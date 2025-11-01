#!/usr/bin/env python3
"""
Test our control-plane agents and tools directly
"""

import os
import sys
import csv
from dotenv import load_dotenv

# Add control-plane to path
sys.path.append('control-plane')

# Load environment variables
load_dotenv()

def create_test_csv():
    """Create a test CSV file for testing"""
    os.makedirs("tmp/test_data", exist_ok=True)
    
    test_data = [
        ["customer_id", "first_name", "last_name", "email", "age", "city", "balance"],
        ["1", "John", "Doe", "john@example.com", "25", "New York", "1500.50"],
        ["2", "Jane", "Smith", "jane@example.com", "30", "Los Angeles", "2200.75"],
        ["3", "Bob", "Johnson", "bob@example.com", "35", "Chicago", "1800.00"],
        ["4", "Alice", "Brown", "", "28", "San Francisco", "3500.25"],  # Missing email
        ["5", "Charlie", "Wilson", "charlie@example.com", "42", "Seattle", "2900.00"]
    ]
    
    csv_file = "tmp/test_data/test_customers.csv"
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(test_data)
    
    return csv_file

def test_file_ingestion_tools():
    """Test file ingestion tools directly"""
    print("🔍 Testing File Ingestion Tools...")
    
    try:
        from tools.file_ingestion import FileIngestionTools
        
        tools = FileIngestionTools(working_directory="tmp/uploads")
        csv_file = create_test_csv()
        
        # Test file type detection
        file_type = tools.detect_file_type(csv_file)
        print(f"   File type detected: {file_type}")
        
        # Test CSV reading
        result = tools.read_csv_file(csv_file)
        print(f"   CSV read successful: {len(result)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ File ingestion tools failed: {e}")
        return False

def test_agents():
    """Test our control-plane agents"""
    print("\n🤖 Testing Control-Plane Agents...")
    
    try:
        from agents.file_ingestion_agent import FileIngestionAgent
        
        # Create agent
        agent = FileIngestionAgent()
        print(f"✅ FileIngestionAgent created: {agent.agent.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🌐 Testing FastAPI App Creation...")
    
    try:
        from agent_os import setup_data_onboarding_platform
        
        agent_os, agents, workflow = setup_data_onboarding_platform()
        print(f"✅ FastAPI app created with {len(agents)} agents")
        print(f"   Available agents: {list(agents.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False

def main():
    """Run all control-plane tests"""
    print("🎛️  Control-Plane Components Test")
    print("=" * 50)
    
    # Check API key first
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ No ANTHROPIC_API_KEY found in environment")
        return False
    
    results = []
    
    # Test file tools
    results.append(test_file_ingestion_tools())
    
    # Test agents
    results.append(test_agents())
    
    # Test FastAPI app
    results.append(test_fastapi_app())
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Control-Plane Test Results:")
    tests = ["File Ingestion Tools", "Agent Creation", "FastAPI App"]
    
    for i, (test_name, result) in enumerate(zip(tests, results)):
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Summary: {passed}/{total} control-plane tests passed")
    
    if passed == total:
        print("🎉 All control-plane components working correctly!")
        print("🚀 Ready to process data onboarding workflows!")
    else:
        print("🔧 Some control-plane components need attention.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)