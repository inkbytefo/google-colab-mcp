#!/usr/bin/env python3
"""
Script to fix WebDriver issues in Google Colab MCP server.

This script will:
1. Install/update required dependencies
2. Run diagnostics to identify issues
3. Provide recommendations for fixes
4. Test the WebDriver functionality
"""

import subprocess
import sys
import os
import json
import argparse
from pathlib import Path


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing/updating dependencies...")
    
    dependencies = [
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "selenium-stealth>=1.0.6",
        "undetected-chromedriver>=3.5.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"  Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"  ✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {dep}: {e}")
            return False
    
    return True


def run_diagnostics():
    """Run WebDriver diagnostics."""
    print("\n🔍 Running WebDriver diagnostics...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from mcp_colab_server.diagnostics import ColabDiagnostics
        
        # Load config
        user_config_dir = Path.home() / ".mcp-colab"
        config_path = user_config_dir / "server_config.json"
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # Use default config if user config doesn't exist
            config = {
                "selenium": {
                    "browser": "chrome",
                    "headless": False,
                    "timeout": 30
                }
            }
        
        diagnostics = ColabDiagnostics(config)
        results = diagnostics.run_full_diagnostics()
        
        # Print results
        print("\n📊 Diagnostic Results:")
        print("=" * 50)
        
        webdriver_results = results["webdriver_test"]
        print("\n🚗 WebDriver Tests:")
        for test, passed in webdriver_results.items():
            if test != "errors":
                status = "✅" if passed else "❌"
                print(f"  {status} {test}")
        
        if webdriver_results.get("errors"):
            print("\n❌ WebDriver Errors:")
            for error in webdriver_results["errors"]:
                print(f"  - {error}")
        
        colab_results = results["colab_access_test"]
        print("\n🌐 Colab Access Tests:")
        for test, result in colab_results.items():
            if test != "errors":
                status = "✅" if result else "❌"
                print(f"  {status} {test}")
        
        print("\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  {rec}")
        
        return results
        
    except Exception as e:
        print(f"❌ Diagnostics failed: {e}")
        return None


def test_webdriver():
    """Test WebDriver functionality."""
    print("\n🧪 Testing WebDriver functionality...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from mcp_colab_server.colab_selenium import ColabSeleniumManager
        from mcp_colab_server.session_manager import SessionManager
        from unittest.mock import Mock
        
        # Load config
        user_config_dir = Path.home() / ".mcp-colab"
        config_path = user_config_dir / "server_config.json"
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # Use default config if user config doesn't exist
            config = {
                "selenium": {
                    "browser": "chrome",
                    "headless": True,  # Set to True for testing
                    "timeout": 30
                }
            }
        
        # Set headless for testing
        config.setdefault("selenium", {})["headless"] = True
        
        session_manager = Mock(spec=SessionManager)
        selenium_manager = ColabSeleniumManager(config, session_manager)
        
        print("  Creating WebDriver...")
        driver = selenium_manager._create_driver()
        print("  ✅ WebDriver created successfully")
        
        print("  Testing Colab access...")
        driver.get("https://colab.research.google.com")
        print(f"  ✅ Accessed Colab: {driver.current_url}")
        
        print("  Testing anti-detection measures...")
        user_agent = driver.execute_script("return navigator.userAgent;")
        webdriver_property = driver.execute_script("return navigator.webdriver;")
        
        if "HeadlessChrome" not in user_agent:
            print("  ✅ User agent properly masked")
        else:
            print("  ⚠️ User agent may reveal headless mode")
        
        if webdriver_property is None:
            print("  ✅ WebDriver property hidden")
        else:
            print("  ⚠️ WebDriver property still visible")
        
        driver.quit()
        print("  ✅ WebDriver test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ WebDriver test failed: {e}")
        return False


def update_config():
    """Update configuration with new settings."""
    print("\n⚙️ Updating configuration...")
    
    user_config_dir = Path.home() / ".mcp-colab"
    config_path = user_config_dir / "server_config.json"
    
    if not config_path.exists():
        print("  ❌ Configuration file not found. Please run 'google-colab-mcp-setup --init' first")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update selenium configuration
        selenium_config = config.setdefault("selenium", {})
        selenium_config.update({
            "use_undetected_chrome": True,
            "use_stealth": True,
            "anti_detection": {
                "disable_automation_indicators": True,
                "custom_user_agent": True,
                "disable_images": False,
                "random_delays": True
            },
            "retry_config": {
                "max_retries": 3,
                "retry_delay": 2,
                "exponential_backoff": True
            }
        })
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("  ✅ Configuration updated successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to update configuration: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Fix WebDriver issues in Google Colab MCP")
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-test", action="store_true", help="Skip WebDriver testing")
    parser.add_argument("--diagnostics-only", action="store_true", help="Run diagnostics only")
    args = parser.parse_args()
    
    print("🚀 Google Colab MCP WebDriver Fix Script")
    print("=" * 50)
    
    if args.diagnostics_only:
        run_diagnostics()
        return
    
    success = True
    
    # Install dependencies
    if not args.skip_install:
        if not install_dependencies():
            success = False
    
    # Update configuration
    if not update_config():
        success = False
    
    # Run diagnostics
    diagnostic_results = run_diagnostics()
    if diagnostic_results is None:
        success = False
    
    # Test WebDriver
    if not args.skip_test:
        if not test_webdriver():
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 WebDriver fixes applied successfully!")
        print("\n📋 Next steps:")
        print("1. Test the MCP tools with a real Colab notebook")
        print("2. If issues persist, run with --diagnostics-only for detailed analysis")
        print("3. Check the logs for any authentication issues")
    else:
        print("❌ Some fixes failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure you have Chrome or Firefox installed")
        print("2. Check your internet connection")
        print("3. Run 'pip install --upgrade selenium webdriver-manager'")
        print("4. Try running with --diagnostics-only for more details")


if __name__ == "__main__":
    main()