"""Tests for the AuthManager class."""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

from src.auth_manager import AuthManager


class TestAuthManager(unittest.TestCase):
    """Test cases for AuthManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.credentials_file = os.path.join(self.temp_dir, "credentials.json")
        self.token_file = os.path.join(self.temp_dir, "token.json")
        
        # Create test config
        test_config = {
            "google_api": {
                "scopes": ["https://www.googleapis.com/auth/drive"],
                "credentials_file": self.credentials_file,
                "token_file": self.token_file
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Create mock credentials file
        mock_credentials = {
            "installed": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(mock_credentials, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test AuthManager initialization."""
        auth_manager = AuthManager(self.config_file)
        
        self.assertEqual(auth_manager.credentials_file, self.credentials_file)
        self.assertEqual(auth_manager.token_file, self.token_file)
        self.assertIn("https://www.googleapis.com/auth/drive", auth_manager.scopes)
        self.assertIsNone(auth_manager.credentials)
    
    @patch('src.auth_manager.Credentials')
    def test_authenticate_with_existing_valid_token(self, mock_credentials_class):
        """Test authentication with existing valid token."""
        # Mock existing valid credentials
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials_class.from_authorized_user_file.return_value = mock_creds
        
        # Create mock token file
        with open(self.token_file, 'w') as f:
            json.dump({"token": "test_token"}, f)
        
        auth_manager = AuthManager(self.config_file)
        result = auth_manager.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(auth_manager.credentials, mock_creds)
        mock_credentials_class.from_authorized_user_file.assert_called_once()
    
    @patch('src.auth_manager.Request')
    @patch('src.auth_manager.Credentials')
    def test_authenticate_with_expired_token(self, mock_credentials_class, mock_request):
        """Test authentication with expired token that can be refreshed."""
        # Mock expired credentials that can be refreshed
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_credentials_class.from_authorized_user_file.return_value = mock_creds
        
        # Create mock token file
        with open(self.token_file, 'w') as f:
            json.dump({"token": "test_token"}, f)
        
        auth_manager = AuthManager(self.config_file)
        
        # Mock the refresh process
        def refresh_side_effect(request):
            mock_creds.valid = True
        
        mock_creds.refresh.side_effect = refresh_side_effect
        
        with patch.object(auth_manager, '_save_credentials'):
            result = auth_manager.authenticate()
        
        self.assertTrue(result)
        mock_creds.refresh.assert_called_once()
    
    @patch('src.auth_manager.InstalledAppFlow')
    @patch('src.auth_manager.Credentials')
    def test_authenticate_new_user(self, mock_credentials_class, mock_flow_class):
        """Test authentication for new user (no existing token)."""
        # Mock no existing credentials
        mock_credentials_class.from_authorized_user_file.side_effect = FileNotFoundError()
        
        # Mock OAuth flow
        mock_flow = Mock()
        mock_creds = Mock()
        mock_creds.valid = True
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_class.from_client_secrets_file.return_value = mock_flow
        
        auth_manager = AuthManager(self.config_file)
        
        with patch.object(auth_manager, '_save_credentials'):
            result = auth_manager.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(auth_manager.credentials, mock_creds)
        mock_flow_class.from_client_secrets_file.assert_called_once()
        mock_flow.run_local_server.assert_called_once()
    
    def test_authenticate_missing_credentials_file(self):
        """Test authentication fails when credentials file is missing."""
        # Remove credentials file
        os.remove(self.credentials_file)
        
        auth_manager = AuthManager(self.config_file)
        result = auth_manager.authenticate()
        
        self.assertFalse(result)
    
    @patch('src.auth_manager.build')
    def test_get_drive_service(self, mock_build):
        """Test getting Drive service."""
        # Mock authenticated credentials
        mock_creds = Mock()
        mock_creds.valid = True
        
        auth_manager = AuthManager(self.config_file)
        auth_manager.credentials = mock_creds
        
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        service = auth_manager.get_drive_service()
        
        self.assertEqual(service, mock_service)
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
    
    def test_get_drive_service_not_authenticated(self):
        """Test getting Drive service when not authenticated."""
        auth_manager = AuthManager(self.config_file)
        
        with patch.object(auth_manager, 'authenticate', return_value=False):
            with self.assertRaises(Exception):
                auth_manager.get_drive_service()
    
    def test_is_authenticated(self):
        """Test authentication status check."""
        auth_manager = AuthManager(self.config_file)
        
        # Not authenticated initially
        self.assertFalse(auth_manager.is_authenticated())
        
        # Mock authenticated state
        mock_creds = Mock()
        mock_creds.valid = True
        auth_manager.credentials = mock_creds
        
        self.assertTrue(auth_manager.is_authenticated())
        
        # Mock invalid credentials
        mock_creds.valid = False
        self.assertFalse(auth_manager.is_authenticated())
    
    @patch('src.auth_manager.Request')
    def test_revoke_credentials(self, mock_request):
        """Test credential revocation."""
        # Create mock token file
        with open(self.token_file, 'w') as f:
            json.dump({"token": "test_token"}, f)
        
        # Mock credentials
        mock_creds = Mock()
        
        auth_manager = AuthManager(self.config_file)
        auth_manager.credentials = mock_creds
        
        result = auth_manager.revoke_credentials()
        
        self.assertTrue(result)
        self.assertIsNone(auth_manager.credentials)
        self.assertFalse(os.path.exists(self.token_file))
        mock_creds.revoke.assert_called_once()
    
    def test_save_credentials(self):
        """Test saving credentials to file."""
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"token": "test_token"}'
        
        auth_manager = AuthManager(self.config_file)
        auth_manager.credentials = mock_creds
        
        auth_manager._save_credentials()
        
        self.assertTrue(os.path.exists(self.token_file))
        
        with open(self.token_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data["token"], "test_token")


if __name__ == '__main__':
    unittest.main()