#!/usr/bin/env python3
"""Test script for improved timeout and error handling fixes in Colab Selenium."""

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

from mcp_colab_server.colab_selenium import ColabSeleniumManager
from mcp_colab_server.session_manager import SessionManager


def load_config():
    """Load configuration for testing."""
    config_data = {
        "selenium": {
            "browser": "chrome",
            "headless": False,
            "timeout": 30,
            "implicit_wait": 10,
            "page_load_timeout": 30,
            "use_stealth": True,
            "use_undetected_chrome": False,
            "anti_detection": {
                "disable_images": False,
                "custom_user_agent": True
            },
            "profile": {
                "use_persistent_profile": True,
                "profile_name": "test_profile"
            }
        },
        "colab": {
            "base_url": "https://colab.research.google.com",
            "execution_timeout": 30,  # Shorter timeout for testing
            "max_idle_time": 1800,
            "connection_timeout": 60,
            "max_retries": 3
        },
        "user_config_dir": str(Path.home() / ".mcp-colab")
    }
    return config_data


def test_improved_error_handling():
    """Test improved error handling and timeout management."""
    print("\n=== Testing Improved Error Handling and Timeout Management ===")
    
    config = load_config()
    session_manager = SessionManager(config)
    selenium_manager = ColabSeleniumManager(config, session_manager)
    
    # Test notebook ID (you'll need to replace this with a real notebook ID)
    test_notebook_id = "your_test_notebook_id_here"
    
    try:
        # Test 1: Simple successful execution
        print("\n1. Testing simple successful execution...")
        result = selenium_manager.execute_code(test_notebook_id, "print('Hello, World!')")
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        # Test 2: Code with syntax error
        print("\n2. Testing syntax error handling...")
        result = selenium_manager.execute_code(test_notebook_id, "print('Hello World'")  # Missing closing parenthesis
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        # Test 3: Code that raises runtime error
        print("\n3. Testing runtime error handling...")
        result = selenium_manager.execute_code(test_notebook_id, "1 / 0")  # Division by zero
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        # Test 4: Code that might take some time (but not timeout)
        print("\n4. Testing medium duration execution...")
        result = selenium_manager.execute_code(test_notebook_id, """
import time
print("Starting computation...")
for i in range(5):
    print(f"Step {i+1}")
    time.sleep(1)
print("Computation completed!")
""")
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        # Test 5: Test session status tracking
        print("\n5. Testing session status tracking...")
        session_info = session_manager.get_session_info(test_notebook_id)
        if session_info:
            print(f"   Session info: {json.dumps(session_info, indent=2)}")
        
        # Test 6: Code that would normally timeout (if you want to test this)
        print("\n6. Testing timeout behavior (uncomment to test)...")
        print("   Skipping timeout test - uncomment the code below to test")
        
        # Uncomment to test timeout behavior
        # result = selenium_manager.execute_code(test_notebook_id, """
        # import time
        # print("Starting long computation that will timeout...")
        # time.sleep(60)  # This will timeout with our 30-second limit
        # print("This should not print")
        # """)
        # print(f"   Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"   Error during testing: {e}")
        logger.exception("Test execution failed")
    
    finally:
        # Cleanup
        try:
            selenium_manager.close()
            print("\n✅ Selenium manager closed successfully")
        except Exception as e:
            print(f"❌ Error closing selenium manager: {e}")


def test_session_execution_tracking():
    """Test the new session execution tracking features."""
    print("\n=== Testing Session Execution Tracking ===")
    
    config = load_config()
    session_manager = SessionManager(config)
    
    test_notebook_id = "test_notebook_123"
    
    try:
        # Create a test session
        session = session_manager.create_session(test_notebook_id)
        print(f"1. Created session: {session.notebook_id}")
        
        # Test execution tracking
        print("\n2. Testing execution tracking...")
        session_manager.mark_execution_start(test_notebook_id, is_long_running=False)
        
        # Simulate some work
        time.sleep(2)
        
        # Check execution status
        exec_status = session_manager.get_execution_status(test_notebook_id)
        print(f"   Execution status: {json.dumps(exec_status, indent=2)}")
        
        # End execution
        session_manager.mark_execution_end(test_notebook_id)
        
        # Check final status
        session_info = session_manager.get_session_info(test_notebook_id)
        print(f"   Final session info: {json.dumps(session_info, indent=2)}")
        
        # Test timeout detection
        print("\n3. Testing timeout detection...")
        session_manager.mark_execution_start(test_notebook_id, custom_timeout=1.0)  # 1 second timeout
        time.sleep(2)  # Wait longer than timeout
        
        is_timeout = session_manager.check_execution_timeout(test_notebook_id)
        print(f"   Timeout detected: {is_timeout}")
        
        # Cleanup timed out execution
        timed_out = session_manager.cleanup_timed_out_executions()
        print(f"   Cleaned up sessions: {timed_out}")
        
    except Exception as e:
        print(f"   Error during session testing: {e}")
        logger.exception("Session test execution failed")


def main():
    """Main test function."""
    print("Starting improved timeout and error handling tests...")
    
    # Note: You need to set a valid notebook ID to run the full tests
    print("\n⚠️  NOTE: To run full tests, replace 'your_test_notebook_id_here' with a real Colab notebook ID")
    print("   You can create a test notebook at https://colab.research.google.com")
    
    # Test session tracking (doesn't require real notebook)
    test_session_execution_tracking()
    
    # Test improved error handling (requires real notebook)
    # Uncomment the line below when you have a real notebook ID
    # test_improved_error_handling()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()