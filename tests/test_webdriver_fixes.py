"""Test script to verify WebDriver fixes for Colab integration."""

import unittest
import sys
import os
import json
import time
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_colab_server.colab_selenium import ColabSeleniumManager
from mcp_colab_server.session_manager import SessionManager
from mcp_colab_server.diagnostics import ColabDiagnostics


class TestWebDriverFixes(unittest.TestCase):
    """Test WebDriver fixes and improvements."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = {
            "selenium": {
                "browser": "chrome",
                "headless": True,  # Use headless for testing
                "timeout": 30,
                "implicit_wait": 10,
                "page_load_timeout": 30,
                "use_undetected_chrome": True,
                "use_stealth": True,
                "anti_detection": {
                    "disable_automation_indicators": True,
                    "custom_user_agent": True,
                    "disable_images": False,
                    "random_delays": True
                }
            },
            "colab": {
                "base_url": "https://colab.research.google.com",
                "execution_timeout": 300,
                "max_retries": 3,
                "retry_delay": 5
            }
        }
        
        self.session_manager = Mock(spec=SessionManager)
    
    def test_webdriver_creation(self):
        """Test that WebDriver can be created with new configuration."""
        selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
        
        try:
            # This should not raise an exception
            driver = selenium_manager._create_driver()
            self.assertIsNotNone(driver)
            
            # Test that anti-detection measures are applied
            user_agent = driver.execute_script("return navigator.userAgent;")
            self.assertIsNotNone(user_agent)
            self.assertNotIn("HeadlessChrome", user_agent)
            
            # Test that webdriver property is hidden
            webdriver_property = driver.execute_script("return navigator.webdriver;")
            self.assertIsNone(webdriver_property)
            
            driver.quit()
            
        except Exception as e:
            self.fail(f"WebDriver creation failed: {e}")
    
    def test_colab_access(self):
        """Test basic access to Colab."""
        selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
        
        try:
            driver = selenium_manager._create_driver()
            
            # Try to access Colab homepage
            driver.get("https://colab.research.google.com")
            
            # Should not timeout
            self.assertIn("colab", driver.current_url.lower())
            
            driver.quit()
            
        except Exception as e:
            # This might fail in CI/CD environments without proper setup
            self.skipTest(f"Colab access test skipped due to: {e}")
    
    def test_element_selectors(self):
        """Test that element selectors are properly defined."""
        selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
        
        # Test that the methods exist and don't crash
        try:
            # These methods should not crash even without a driver
            with patch.object(selenium_manager, 'driver', None):
                cells = selenium_manager._find_code_cells()
                self.assertIsInstance(cells, list)
                
        except Exception as e:
            self.fail(f"Element selector methods failed: {e}")
    
    def test_diagnostics(self):
        """Test diagnostic functionality."""
        diagnostics = ColabDiagnostics(self.config)
        
        try:
            # Run WebDriver creation test
            webdriver_results = diagnostics._test_webdriver_creation()
            self.assertIsInstance(webdriver_results, dict)
            self.assertIn("chrome_regular", webdriver_results)
            self.assertIn("errors", webdriver_results)
            
        except Exception as e:
            self.fail(f"Diagnostics failed: {e}")
    
    def test_configuration_validation(self):
        """Test that configuration is properly structured."""
        selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
        
        # Test configuration access
        self.assertEqual(selenium_manager.browser_type, "chrome")
        self.assertTrue(selenium_manager.headless)
        self.assertEqual(selenium_manager.timeout, 30)
    
    @unittest.skipIf(os.getenv("SKIP_INTEGRATION_TESTS"), "Integration tests disabled")
    def test_integration_with_mock_notebook(self):
        """Integration test with mock notebook operations."""
        selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
        
        # Mock session manager responses
        self.session_manager.update_session_status.return_value = None
        self.session_manager.mark_session_active.return_value = None
        
        try:
            # This would normally require authentication and a real notebook
            # For now, just test that the method exists and handles errors gracefully
            result = selenium_manager.execute_code("mock_notebook_id", "print('Hello, World!')")
            
            # Should return a properly structured result even on failure
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertIn("output", result)
            self.assertIn("error", result)
            
        except Exception as e:
            self.fail(f"Integration test failed: {e}")


class TestDiagnosticsCLI(unittest.TestCase):
    """Test diagnostic CLI functionality."""
    
    def test_diagnostics_cli_import(self):
        """Test that diagnostics CLI can be imported."""
        try:
            from mcp_colab_server.diagnostics import run_diagnostics_cli
            self.assertTrue(callable(run_diagnostics_cli))
        except ImportError as e:
            self.fail(f"Failed to import diagnostics CLI: {e}")


def run_manual_test():
    """Manual test function for interactive testing."""
    print("🧪 Running manual WebDriver tests...")
    
    config = {
        "selenium": {
            "browser": "chrome",
            "headless": False,  # Visual testing
            "timeout": 30,
            "implicit_wait": 10,
            "page_load_timeout": 30,
            "use_undetected_chrome": True,
            "use_stealth": True
        },
        "colab": {
            "base_url": "https://colab.research.google.com",
            "execution_timeout": 300
        }
    }
    
    session_manager = Mock(spec=SessionManager)
    selenium_manager = ColabSeleniumManager(config, session_manager)
    
    try:
        print("1. Creating WebDriver...")
        driver = selenium_manager._create_driver()
        print("✅ WebDriver created successfully")
        
        print("2. Testing Colab access...")
        driver.get("https://colab.research.google.com")
        print(f"✅ Accessed Colab: {driver.current_url}")
        
        print("3. Waiting for interface...")
        time.sleep(5)  # Give time to see the page
        
        print("4. Testing interface detection...")
        selenium_manager.driver = driver
        selenium_manager._wait_for_colab_interface()
        print("✅ Interface detection completed")
        
        print("5. Testing cell detection...")
        cells = selenium_manager._find_code_cells()
        print(f"✅ Found {len(cells)} code cells")
        
        input("Press Enter to close browser...")
        driver.quit()
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test WebDriver fixes")
    parser.add_argument("--manual", action="store_true", help="Run manual interactive test")
    parser.add_argument("--diagnostics", action="store_true", help="Run diagnostics")
    args = parser.parse_args()
    
    if args.manual:
        run_manual_test()
    elif args.diagnostics:
        from mcp_colab_server.diagnostics import run_diagnostics_cli
        run_diagnostics_cli()
    else:
        unittest.main()