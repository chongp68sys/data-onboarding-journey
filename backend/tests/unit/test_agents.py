#!/usr/bin/env python3
"""
Test individual Agno agents functionality
"""

import os
import sys
import asyncio
import csv
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'control-plane'))

from agents.file_ingestion_agent import FileIngestionAgent
from agents.data_mapping_agent import DataMappingAgent
from agents.data_validation_agent import DataValidationAgent
from agents.orchestration_agent import OrchestrationAgent

# Load environment variables
load_dotenv()

def create_test_csv():
    """Create a test CSV file"""
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

async def test_file_ingestion_agent():
    """Test the FileIngestionAgent"""
    print("🔍 Testing FileIngestionAgent")
    print("-" * 30)
    
    agent = FileIngestionAgent()
    csv_file = create_test_csv()
    
    try:
        result = agent.process_file(csv_file)
        print(f"✅ File ingestion result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ File ingestion failed: {e}")
        return False

async def test_data_mapping_agent():
    """Test the DataMappingAgent"""
    print("\n🔄 Testing DataMappingAgent")
    print("-" * 30)
    
    agent = DataMappingAgent()
    
    try:
        # Test column mapping suggestions
        source_cols = "customer_id,first_name,last_name,email,age,city,balance"
        target_cols = "id,fname,lname,email_address,customer_age,location,account_balance"
        
        result = agent.suggest_mappings(source_cols, target_cols)
        print(f"✅ Mapping suggestions: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Data mapping failed: {e}")
        return False

async def test_data_validation_agent():
    """Test the DataValidationAgent"""
    print("\n📊 Testing DataValidationAgent")
    print("-" * 30)
    
    agent = DataValidationAgent()
    csv_file = create_test_csv()
    
    try:
        result = agent.analyze_quality(csv_file)
        print(f"✅ Data validation result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Data validation failed: {e}")
        return False

async def test_orchestration_agent():
    """Test the OrchestrationAgent"""
    print("\n🎯 Testing OrchestrationAgent")
    print("-" * 30)
    
    orchestrator = OrchestrationAgent()
    
    # Create other agents for coordination
    file_agent = FileIngestionAgent()
    mapping_agent = DataMappingAgent()
    validation_agent = DataValidationAgent()
    
    orchestrator.set_agents(file_agent, mapping_agent, validation_agent)
    
    try:
        config = {
            "file_path": create_test_csv(),
            "mapping": {"customer_id": "id", "first_name": "fname"},
            "validation": {"quality_checks": True}
        }
        
        result = orchestrator.execute_data_pipeline(config)
        print(f"✅ Orchestration result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        return False

async def main():
    """Run all agent tests"""
    print("🧪 Agno Agents Test Suite")
    print("=" * 40)
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No ANTHROPIC_API_KEY found in environment")
        return
    
    results = []
    
    # Test each agent
    results.append(await test_file_ingestion_agent())
    results.append(await test_data_mapping_agent())
    results.append(await test_data_validation_agent())
    results.append(await test_orchestration_agent())
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Results:")
    agents = ["FileIngestionAgent", "DataMappingAgent", "DataValidationAgent", "OrchestrationAgent"]
    
    for i, (agent, result) in enumerate(zip(agents, results)):
        status = "✅" if result else "❌"
        print(f"   {status} {agent}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n🎯 Summary: {passed}/{total} agents passed testing")
    
    if passed == total:
        print("🎉 All agents are working correctly!")
    else:
        print("🔧 Some agents need attention.")

if __name__ == "__main__":
    asyncio.run(main())