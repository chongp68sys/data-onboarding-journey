#!/usr/bin/env python3
"""
Test script for the Data Pipeline Workflow

This script validates that our Agno workflow implementation works correctly
by testing it with sample data and configurations.
"""

import os
import sys
import asyncio
import csv
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'control-plane'))

from workflows.data_pipeline_workflow import DataPipelineWorkflow, DataPipelineInput

# Load environment variables
load_dotenv()

def create_sample_csv():
    """Create a sample CSV file for testing"""
    sample_data = [
        ["Name", "Age", "Email", "City", "Balance"],
        ["John Doe", "25", "john@example.com", "New York", "1500.50"],
        ["Jane Smith", "30", "jane@example.com", "Los Angeles", "2200.75"], 
        ["Bob Johnson", "35", "bob@example.com", "Chicago", "1800.00"],
        ["Alice Brown", "28", "alice@example.com", "San Francisco", "3500.25"],
        ["Charlie Wilson", "42", "charlie@example.com", "Seattle", "2900.00"],
        ["Diana Davis", "31", "", "Miami", "2100.50"],  # Missing email to test validation
        ["Eve Miller", "27", "eve@example.com", "Denver", "1750.00"],
        ["Frank Garcia", "38", "frank@example.com", "Austin", "2400.75"],
        ["Grace Lee", "29", "grace@example.com", "Portland", "1950.00"],
        ["Henry Taylor", "33", "henry@example.com", "Boston", "2650.25"]
    ]
    
    # Ensure tmp directory exists
    os.makedirs("tmp/test_data", exist_ok=True)
    
    csv_file = "tmp/test_data/sample_customers.csv"
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(sample_data)
    
    return csv_file

async def test_workflow_basic():
    """Test basic workflow execution"""
    print("🧪 Testing Basic Workflow Execution")
    print("=" * 50)
    
    # Create sample data
    csv_file = create_sample_csv()
    print(f"📄 Created sample CSV file: {csv_file}")
    
    # Test input configuration
    test_input = DataPipelineInput(
        file_path=csv_file,
        file_type="csv",
        delimiter=",",
        naming_convention="snake_case",
        perform_quality_analysis=True,
        detect_duplicates=True,
        detect_outliers=True,
        pipeline_name="Test Customer Data Pipeline",
        created_by="test_user"
    )
    
    print(f"🔧 Configuration: {test_input.pipeline_name}")
    print(f"📊 File: {test_input.file_path}")
    print(f"⚙️  Quality Analysis: {test_input.perform_quality_analysis}")
    
    try:
        # Execute workflow
        print("\n🚀 Starting workflow execution...")
        result = await DataPipelineWorkflow.run(test_input)
        
        print("\n✅ Workflow completed successfully!")
        print(f"📋 Execution ID: {result.execution_id}")
        print(f"⏱️  Duration: {result.duration_seconds:.2f} seconds")
        print(f"📊 Rows Processed: {result.rows_processed}")
        print(f"📈 Quality Score: {result.quality_score}")
        
        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow execution failed: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

async def test_workflow_with_mapping():
    """Test workflow with column mapping"""
    print("\n🧪 Testing Workflow with Column Mapping")
    print("=" * 50)
    
    csv_file = create_sample_csv()
    
    # Test with target schema mapping
    test_input = DataPipelineInput(
        file_path=csv_file,
        target_schema=["customer_name", "customer_age", "email_address", "location", "account_balance"],
        column_mapping={
            "Name": "customer_name",
            "Age": "customer_age", 
            "Email": "email_address",
            "City": "location",
            "Balance": "account_balance"
        },
        naming_convention="snake_case",
        similarity_threshold=0.8,
        perform_quality_analysis=True,
        pipeline_name="Customer Data Mapping Test"
    )
    
    try:
        print("🚀 Starting workflow with mapping...")
        result = await DataPipelineWorkflow.run(test_input)
        
        print("✅ Mapping workflow completed!")
        print(f"🔄 Mappings applied: {result.column_mapping_applied}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mapping workflow failed: {str(e)}")
        return False

def test_agent_tools():
    """Test individual agent tools"""
    print("\n🧪 Testing Individual Agent Tools")
    print("=" * 50)
    
    try:
        from tools.file_ingestion import FileIngestionTools
        from tools.data_mapping import DataMappingTools
        from tools.data_validation import DataValidationTools
        
        # Test file ingestion tools
        file_tools = FileIngestionTools()
        csv_file = create_sample_csv()
        
        print("🔍 Testing file type detection...")
        file_type = file_tools.detect_file_type(csv_file)
        print(f"   Detected: {file_type}")
        
        print("🔍 Testing encoding detection...")
        encoding = file_tools.detect_encoding(csv_file)
        print(f"   Detected: {encoding}")
        
        print("📊 Testing CSV reading...")
        csv_result = file_tools.read_csv_file(csv_file)
        print(f"   Result: {csv_result[:100]}...")
        
        # Test mapping tools
        print("\n🔄 Testing column mapping tools...")
        mapping_tools = DataMappingTools()
        
        source_cols = "Name,Age,Email,City,Balance"
        target_cols = "customer_name,customer_age,email_address,location,account_balance"
        
        mapping_result = mapping_tools.suggest_column_mapping(source_cols, target_cols)
        print(f"   Mapping suggestions: {mapping_result[:100]}...")
        
        print("✅ All tool tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Tool testing failed: {str(e)}")
        return False

def check_environment():
    """Check environment setup"""
    print("🔍 Checking Environment Setup")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ Anthropic API key: {'*' * 20}{api_key[-4:]}")
    else:
        print("⚠️  No Anthropic API key found in environment")
        print("   Please set ANTHROPIC_API_KEY in .env file")
    
    # Check directories
    required_dirs = ["tmp", "tmp/uploads", "tmp/test_data"]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")
    
    return api_key is not None

async def main():
    """Main test function"""
    print("🚀 Data Pipeline Workflow Test Suite")
    print("=" * 60)
    
    # Check environment
    env_ok = check_environment()
    
    # Test tools first
    tools_ok = test_agent_tools()
    
    if not env_ok:
        print("\n⚠️  Environment not properly configured")
        print("Please set up your .env file with ANTHROPIC_API_KEY")
        return
    
    if not tools_ok:
        print("\n⚠️  Tool tests failed - workflow tests may not work properly")
    
    # Test workflows
    print("\n" + "=" * 60)
    basic_test = await test_workflow_basic()
    
    if basic_test:
        mapping_test = await test_workflow_with_mapping()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   Tools: {'✅' if tools_ok else '❌'}")
    print(f"   Basic Workflow: {'✅' if basic_test else '❌'}")
    if basic_test:
        print(f"   Mapping Workflow: {'✅' if 'mapping_test' in locals() and mapping_test else '❌'}")
    
    if env_ok and tools_ok and basic_test:
        print("\n🎉 All tests passed! Your Agno workflow is ready.")
    else:
        print("\n🔧 Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    asyncio.run(main())