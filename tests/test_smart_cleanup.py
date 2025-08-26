#!/usr/bin/env python3
"""Test script for smart browser cleanup implementation."""

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


async def test_smart_cleanup():
    """Test the new smart cleanup implementation."""
    print("\n=== Testing Smart Browser Cleanup Implementation ===")
    
    try:
        # Create test server
        print("1. Creating MCP server...")
        server = ColabMCPServer()
        
        # Use our test notebook
        test_notebook_id = "1xKtdxSGt4haLwRNq1S_Mcrj-sH5qEMN6"
        
        print("\n2. Testing multiple consecutive code executions...")
        
        # Test multiple code executions to verify session persistence
        test_cases = [
            {
                "name": "Test 1: Basic print",
                "code": "print('Hello from Test 1!')\nprint('Smart cleanup test initiated...')"
            },
            {
                "name": "Test 2: Variables and computation",
                "code": "x = 10\ny = 20\nresult = x + y\nprint(f'Computation result: {x} + {y} = {result}')"
            },
            {
                "name": "Test 3: List operations",
                "code": "numbers = [1, 2, 3, 4, 5]\nsquares = [n**2 for n in numbers]\nprint(f'Numbers: {numbers}')\nprint(f'Squares: {squares}')"
            },
            {
                "name": "Test 4: String operations",
                "code": "text = 'MCP Google Colab Test'\nwords = text.split()\nprint(f'Original: {text}')\nprint(f'Words: {words}')\nprint(f'Reversed: {text[::-1]}')"
            },
            {
                "name": "Test 5: Session persistence check",
                "code": "# This should work if session persisted from Test 2\ntry:\n    print(f'Previous result still available: {result}')\nexcept NameError:\n    print('Previous variables not available - new session')"
            }
        ]
        
        success_count = 0
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Running {test_case['name']}...")
            start_time = time.time()
            
            try:
                # Execute code using the server's method
                arguments = {
                    "code": test_case["code"],
                    "notebook_id": test_notebook_id,
                    "confirm_execution": True
                }
                
                result = await server._run_code_cell(arguments)
                execution_time = time.time() - start_time
                
                if result.get('success', False):
                    print(f"   ✅ Success: {test_case['name']}")
                    print(f"   📊 Execution time: {execution_time:.2f}s")
                    if result.get('output'):
                        print(f"   📝 Output preview: {result['output'][:100]}...")
                    success_count += 1
                else:
                    print(f"   ❌ Failed: {test_case['name']}")
                    print(f"   📊 Execution time: {execution_time:.2f}s")
                    if result.get('error'):
                        print(f"   ❌ Error: {result['error']}")
                
                # Small delay between tests
                time.sleep(1)
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"   ❌ Exception in {test_case['name']}: {e}")
                print(f"   📊 Time before exception: {execution_time:.2f}s")
        
        print(f"\n3. Test Results Summary:")
        print(f"   ✅ Successful executions: {success_count}/{len(test_cases)}")
        print(f"   📈 Success rate: {(success_count/len(test_cases)*100):.1f}%")
        
        if success_count >= 4:  # At least 4 out of 5 should work
            print("   🎉 Smart cleanup implementation is working well!")
        elif success_count >= 2:
            print("   ⚠️ Smart cleanup shows improvement but needs optimization")
        else:
            print("   ❌ Smart cleanup implementation needs fixes")
        
        # Test browser session health
        print("\n4. Testing browser session health...")
        if hasattr(server, 'selenium_manager') and server.selenium_manager:
            health_status = server.selenium_manager.check_session_health()
            print(f"   Browser health status: {'✅ Healthy' if health_status else '❌ Unhealthy'}")
            
            if health_status:
                print("   Browser session is maintained and responsive")
            else:
                cleanup_performed = server.selenium_manager.cleanup_if_unhealthy()
                print(f"   Automatic cleanup performed: {cleanup_performed}")
        
        print("\n5. Testing cleanup...")
        try:
            await server._cleanup()
            print("   ✅ Server cleanup completed successfully")
        except Exception as e:
            print(f"   ⚠️ Server cleanup warning: {e}")
        
        print("\nSmart cleanup test completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        logger.exception("Smart cleanup test failed")


def main():
    """Main test function."""
    print("Testing Smart Browser Cleanup Implementation")
    print("=" * 60)
    print("\nNOTE: This test requires valid Google authentication")
    print("The test will run multiple code executions to verify session persistence")
    
    try:
        # Run the async test
        asyncio.run(test_smart_cleanup())
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed: {e}")
        logger.exception("Test execution failed")


if __name__ == "__main__":
    main()