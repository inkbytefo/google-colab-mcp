# 🚀 Google Colab MCP Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> 🆕 **Latest Update**: Enhanced timeout handling and error management for robust code execution. System no longer hangs during code execution and provides comprehensive error reporting. [See full changelog](TIMEOUT_ERROR_FIXES_REPORT.md)

A comprehensive **Model Context Protocol (MCP)** server that seamlessly integrates Google Colab with AI assistants like Claude, ChatGPT, and other MCP-compatible tools.

## ✨ Features

- 🔐 **Automatic OAuth2 Authentication** - One-time setup with Google
- 💾 **Persistent Chrome Profile** - Remembers login sessions automatically
- 📚 **Complete Notebook Management** - Create, read, update, and list notebooks
- 🤖 **Code Execution** - Run Python code directly in Colab environments
- 📦 **Package Management** - Install Python packages in Colab
- 📁 **File Operations** - Upload files to Colab environments
- 🔄 **Session Management** - Handle Colab runtime sessions
- 🛡️ **Enhanced Error Handling** - Robust error handling with detailed troubleshooting
- ⏱️ **Smart Timeout Management** - Non-blocking execution with comprehensive timeout handling
- 🔧 **Profile Management** - Tools to manage Chrome profile and session data
- 📊 **Execution Tracking** - Real-time monitoring of code execution status
- 🎯 **Long-Running Support** - Background execution for time-intensive operations

## 🎯 Use Cases

- **AI-Powered Data Science**: Let AI assistants create and run data analysis notebooks
- **Automated ML Workflows**: Build machine learning pipelines through natural language
- **Educational Tools**: Create interactive coding tutorials and examples
- **Research Automation**: Automate repetitive research tasks in Colab
- **Code Generation**: Generate and test code snippets in a cloud environment

## 🚀 Quick Start

### 1. Installation

```bash
pip install google-colab-mcp
```

Or install from source:
```bash
git clone https://github.com/inkbytefo/google-colab-mcp.git
cd google-colab-mcp
pip install -e .
```

### 2. Configuration Setup

Initialize user configuration using the MCP tool (recommended):

**Via AI Assistant:**
```
"Initialize my Google Colab MCP configuration"
```

**Or manually:**
```bash
python -m mcp_colab_server.config_manager --init
```

This creates your personal config directory at `~/.mcp-colab/` with:
- 📁 Configuration files
- 📁 Logs directory  
- 📝 Credentials template

### 3. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Drive API**
4. Create **OAuth 2.0 credentials** (Desktop Application)
5. Download `credentials.json` and place it in `~/.mcp-colab/` folder

### 4. Authentication Setup

Run the automatic setup script:

```bash
python -m mcp_colab_server.setup
```

This will:
- ✅ Validate your credentials file
- 🌐 Open browser for Google authentication
- 💾 Save authentication tokens in `~/.mcp-colab/token.json`
- ✨ Test the connection

Check your configuration status anytime:
```bash
python -m mcp_colab_server.config_manager --status
```

### 5. Chrome Profile Management

The system automatically manages Chrome profiles for persistent sessions:

```bash
# View Chrome profiles summary
python -m mcp_colab_server.config_manager --profile-summary

# Optimize profiles (clean cache, temp files)
python -m mcp_colab_server.config_manager --optimize-profiles

# Clean up old profiles
python -m mcp_colab_server.config_manager --clean-profiles
```

**Benefits:**
- 🔐 **Persistent Login**: Google authentication remembered across sessions
- 🚀 **Faster Startup**: No need to re-authenticate every time
- 🧹 **Automatic Cleanup**: Profiles optimized to save disk space
- 📁 **User Isolation**: Each user has their own profile directory

> 📖 **Detailed Configuration Guide**: See [User Configuration Guide](docs/USER_CONFIG.md) for complete configuration management instructions.

### 4. MCP Integration

Add to your MCP configuration (`.kiro/settings/mcp.json` or similar):

```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "google-colab-mcp",
      "args": [],
      "env": {
        "MCP_COLAB_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🛠️ Available Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `init_user_config` | Initialize user configuration | "Initialize my Google Colab MCP configuration" |
| `check_auth_status` | Check authentication status | "Check my Google authentication status" |
| `setup_google_credentials` | Get setup instructions | "How do I set up Google credentials?" |
| `authenticate_google` | Complete Google authentication | "Authenticate with Google" |
| `create_colab_notebook` | Create a new Colab notebook | "Create a notebook called 'Data Analysis'" |
| `list_notebooks` | List all your Colab notebooks | "Show me my Colab notebooks" |
| `get_notebook_content` | Get notebook content | "Show me the content of my latest notebook" |
| `run_code_cell` | Execute Python code in Colab | "Run this code: import pandas as pd" |
| `install_package` | Install Python packages | "Install matplotlib in my notebook" |
| `upload_file_to_colab` | Upload files to Colab | "Upload data.csv to my notebook" |
| `get_runtime_info` | Get runtime information | "What's the status of my Colab runtime?" |
| `get_session_info` | Get session details | "Show me my current Colab session" |
| `get_chrome_profile_info` | Get Chrome profile information | "Check my browser profile status" |
| `clear_chrome_profile` | Clear Chrome profile data | "Clear my browser data and reset login" |

## 💬 Example Conversations

**With Claude/ChatGPT:**

> **You:** "Create a new Colab notebook for analyzing sales data"
> 
> **AI:** Creates notebook and responds with notebook URL and ID

> **You:** "Install pandas and matplotlib, then create a simple plot"
> 
> **AI:** Installs packages and generates plotting code in your Colab

> **You:** "List all my notebooks and show me the most recent one"
> 
> **AI:** Lists notebooks and displays the content of the latest one

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│  MCP Server      │◄──►│  Google Colab   │
│  (Claude, etc.) │    │  (This Project)  │    │   Notebooks     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Google Drive    │
                       │      API         │
                       └──────────────────┘
```

The server acts as a bridge between AI assistants and Google Colab, using:
- **Google Drive API** for notebook management
- **Selenium WebDriver** for code execution
- **MCP Protocol** for AI assistant communication

## 🔧 Configuration

### Server Configuration (`config/server_config.json`)

```json
{
  "selenium": {
    "browser": "chrome",
    "headless": false,
    "timeout": 30,
    "profile": {
      "use_persistent_profile": true,
      "profile_directory": null,
      "auto_create_profile": true
    }
  },
  "colab": {
    "execution_timeout": 300,
    "max_retries": 3
  },
  "logging": {
    "level": "INFO"
  }
}
```

### 💾 Persistent Chrome Profile

The server now supports persistent Chrome profiles to remember your Google login:

- **Automatic Login**: No need to sign in repeatedly
- **Session Persistence**: Login data saved securely
- **Profile Management**: Tools to manage and clear profile data

**Profile Configuration:**
- `use_persistent_profile`: Enable/disable persistent profiles (default: true)
- `profile_directory`: Custom profile location (default: `~/.colab_selenium_profile`)
- `auto_create_profile`: Automatically create profile directory (default: true)

**Profile Management Tools:**
- `get_chrome_profile_info`: Check profile status and size
- `clear_chrome_profile`: Clear profile data (requires re-authentication)

For detailed information, see [Chrome Profile Guide](CHROME_PROFILE_GUIDE.md).

### MCP Configuration Options

```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "google-colab-mcp",
      "args": [],
      "env": {
        "MCP_COLAB_LOG_LEVEL": "INFO",
        "MCP_COLAB_HEADLESS": "true"
      },
      "autoApprove": [
        "list_notebooks",
        "get_notebook_content"
      ]
    }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Re-run the setup script
python -m mcp_colab_server.setup

# Or manually delete token and re-authenticate
rm ~/.mcp-colab/token.json

# Check configuration status
python -m mcp_colab_server.config_manager --status
```

**Selenium WebDriver Issues**
```bash
# Update Chrome/Firefox to latest version
# Or install specific WebDriver version
pip install webdriver-manager --upgrade
```

**MCP Connection Failed**
```bash
# Check if server starts manually
google-colab-mcp

# Verify MCP configuration
# Ensure package is installed correctly
pip show google-colab-mcp
```

### Debug Mode

Enable detailed logging:

```json
{
  "env": {
    "MCP_COLAB_LOG_LEVEL": "DEBUG",
    "MCP_COLAB_HEADLESS": "false"
  }
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the amazing protocol
- [Google Colab](https://colab.research.google.com/) for the fantastic platform
- [Anthropic](https://www.anthropic.com/) for Claude and MCP development

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/inkbytefo/google-colab-mcp/issues)
- 💬 [Discussions](https://github.com/inkbytefo/google-colab-mcp/discussions)

---

**Author:** inkbytefo  
**Made with ❤️ for the AI and Data Science community**