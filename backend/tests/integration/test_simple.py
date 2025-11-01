#!/usr/bin/env python3
"""
Simple test to verify our Agno control-plane setup is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agno_imports():
    """Test that we can import Agno framework components"""
    print("🔍 Testing Agno Framework Imports...")
    
    try:
        from agno.agent import Agent
        print("✅ Agent import successful")
        
        from agno.models.anthropic import Claude
        print("✅ Claude model import successful")
        
        from agno.storage.postgres import PostgresStorage
        print("✅ PostgresStorage import successful")
        
        from agno.workflow.v2 import Workflow, Step, Parallel
        print("✅ Workflow v2 imports successful")
        
        from agno.app.fastapi import FastAPIApp
        print("✅ FastAPIApp import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_agent_creation():
    """Test basic agent creation"""
    print("\n🤖 Testing Agent Creation...")
    
    try:
        from agno.agent import Agent
        from agno.models.anthropic import Claude
        
        agent = Agent(
            name="TestAgent",
            model=Claude(id="claude-3-sonnet-20241022"),
            description="A simple test agent"
        )
        
        print("✅ Agent created successfully")
        print(f"   Agent name: {agent.name}")
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing Environment Setup...")
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ Anthropic API key found: {'*' * 20}{api_key[-4:]}")
    else:
        print("⚠️  No Anthropic API key found")
        return False
    
    # Check directories
    required_dirs = ["tmp", "tmp/uploads", "tmp/mappings", "tmp/validation"]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Agno Control-Plane Simple Test")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(test_agno_imports())
    
    # Test environment
    results.append(test_environment())
    
    # Test agent creation
    results.append(test_agent_creation())
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    tests = ["Agno Imports", "Environment Setup", "Agent Creation"]
    
    for i, (test_name, result) in enumerate(zip(tests, results)):
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Agno control-plane setup is working.")
    else:
        print("🔧 Some tests failed. Please check the configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)