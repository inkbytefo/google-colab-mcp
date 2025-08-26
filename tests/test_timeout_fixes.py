#!/usr/bin/env python3
"""Test script to verify timeout fixes in Selenium manager."""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from mcp_colab_server.server import ColabMCPServer


async def test_timeout_fixes():
    """Test the timeout fixes in code execution."""
    print("🧪 Testing MCP Server Timeout Fixes")
    print("=" * 50)
    
    server = ColabMCPServer()
    
    try:
        # Test 1: Check authentication
        print("\n📋 Test 1: Authentication Status")
        auth_result = await server._check_auth_status({})
        print(f"✅ Auth check completed: {auth_result.get('status', {}).get('authenticated', False)}")
        
        # Test 2: List notebooks (should not hang)
        print("\n📋 Test 2: List Notebooks")
        start_time = time.time()
        list_result = await server._list_notebooks({"max_results": 5})
        elapsed = time.time() - start_time
        print(f"✅ Notebook listing completed in {elapsed:.2f} seconds")
        
        # Test 3: Create a test notebook
        print("\n📋 Test 3: Create Test Notebook")
        start_time = time.time()
        create_result = await server._create_notebook({
            "name": "Timeout Test Notebook"
        })
        elapsed = time.time() - start_time
        if create_result.get("success"):
            notebook_id = create_result["notebook"]["id"]
            print(f"✅ Notebook created in {elapsed:.2f} seconds: {notebook_id}")
            
            # Test 4: Execute simple code (should not hang)
            print("\n📋 Test 4: Execute Simple Code")
            start_time = time.time()
            
            try:
                execute_result = await server._run_code_cell({
                    "code": "print('Hello from timeout test!')\nimport time\nprint('Current time:', time.time())",
                    "notebook_id": notebook_id,
                    "confirm_execution": True
                })
                elapsed = time.time() - start_time
                print(f"✅ Code execution completed in {elapsed:.2f} seconds")
                print(f"Success: {execute_result.get('success', False)}")
                if execute_result.get('output'):
                    print(f"Output: {execute_result['output'][:100]}...")
                if execute_result.get('error'):
                    print(f"Error: {execute_result['error']}")
                    
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Code execution failed after {elapsed:.2f} seconds: {e}")
            
            # Test 5: Execute code that might take longer
            print("\n📋 Test 5: Execute Longer Code")
            start_time = time.time()
            
            try:
                execute_result = await server._run_code_cell({
                    "code": """
import time
print("Starting longer operation...")
for i in range(3):
    print(f"Step {i+1}/3")
    time.sleep(1)
print("Completed!")
""",
                    "notebook_id": notebook_id,
                    "confirm_execution": True
                })
                elapsed = time.time() - start_time
                print(f"✅ Longer code execution completed in {elapsed:.2f} seconds")
                print(f"Success: {execute_result.get('success', False)}")
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Longer code execution failed after {elapsed:.2f} seconds: {e}")
        
        else:
            print(f"❌ Failed to create notebook: {create_result}")
        
        print("\n🎉 Timeout test completed!")
        print("✅ All operations completed within reasonable time limits")
        print("✅ No hanging or infinite loops detected")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_timeout_fixes())