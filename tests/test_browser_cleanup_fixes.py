#!/usr/bin/env python3
"""Test script for browser cleanup fixes after code execution."""

import asyncio
import json
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
import sys
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from mcp_colab_server.server import ColabMCPServer


async def test_browser_cleanup_fixes():
    """Test browser cleanup fixes to prevent system crashes."""
    print("\n=== Testing Browser Cleanup Fixes ===")
    
    try:
        # Create test server
        print("1. Creating MCP server...")
        server = ColabMCPServer()
        
        # Test with a valid notebook ID (replace with actual)
        test_notebook_id = "1pOmhCFhmh8B3wMF1Fwz0S_jTiOZOfZSn"  # Valid notebook ID from our earlier test
        
        print("\n2. Testing code execution with browser cleanup...")
        
        # Test multiple code executions to verify cleanup works
        test_cases = [
            {
                "name": "Simple print test",
                "code": "print('Hello from headless mode!')"
            },
            {
                "name": "Mathematical operations", 
                "code": "import math\nresult = math.sqrt(16)\nprint(f'Result: {result}')"
            },
            {
                "name": "List operations",
                "code": "numbers = [1, 2, 3, 4, 5]\nprint(f'Numbers: {numbers}')"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {test_case['name']}")
            start_time = time.time()
            
            try:
                result = await server._run_code_cell({
                    "code": test_case['code'],
                    "notebook_id": test_notebook_id,
                    "confirm_execution": True
                })
                
                execution_time = time.time() - start_time
                
                if result.get('success'):
                    print(f"   Success: {result.get('message', 'Code executed')}")
                    print(f"   Execution time: {execution_time:.2f}s")
                else:
                    print(f"   Failed: {result.get('error', 'Unknown error')}")
                    print(f"   Execution time: {execution_time:.2f}s")
                
                # Wait a bit between tests
                time.sleep(2)
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"   Exception: {e}")
                print(f"   Time before exception: {execution_time:.2f}s")
        
        print("\n3. Testing cleanup...")
        
        try:
            await server._cleanup()
            print("   Server cleanup completed successfully")
        except Exception as e:
            print(f"   Server cleanup warning: {e}")
        
        print("\nBrowser cleanup test completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        logger.exception("Browser cleanup test failed")


def main():
    """Main test function."""
    print("Testing Browser Cleanup Fixes")
    print("=" * 50)
    print("\nNOTE: This test requires valid Google authentication")
    
    try:
        # Run the async test
        asyncio.run(test_browser_cleanup_fixes())
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed: {e}")
        logger.exception("Test execution failed")


if __name__ == "__main__":
    main()