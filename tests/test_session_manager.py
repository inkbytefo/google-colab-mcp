"""Tests for the SessionManager class."""

import time
import unittest
from unittest.mock import Mock, patch

from src.session_manager import SessionManager, SessionStatus, RuntimeType, ColabSession


class TestSessionManager(unittest.TestCase):
    """Test cases for SessionManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "colab": {
                "max_idle_time": 10,  # 10 seconds for testing
                "connection_timeout": 5,
                "max_retries": 3
            }
        }
        self.session_manager = SessionManager(self.config)
    
    def test_create_session(self):
        """Test session creation."""
        notebook_id = "test_notebook_123"
        session = self.session_manager.create_session(notebook_id, RuntimeType.GPU)
        
        self.assertEqual(session.notebook_id, notebook_id)
        self.assertEqual(session.runtime_type, RuntimeType.GPU)
        self.assertEqual(session.status, SessionStatus.DISCONNECTED)
        self.assertIsNone(session.session_id)
        self.assertIsNone(session.connection_time)
        self.assertIsNone(session.error_message)
        
        # Check session is stored
        self.assertIn(notebook_id, self.session_manager.sessions)
        self.assertEqual(self.session_manager.sessions[notebook_id], session)
    
    def test_get_session(self):
        """Test getting existing session."""
        notebook_id = "test_notebook_123"
        
        # No session initially
        self.assertIsNone(self.session_manager.get_session(notebook_id))
        
        # Create session
        created_session = self.session_manager.create_session(notebook_id)
        
        # Get session
        retrieved_session = self.session_manager.get_session(notebook_id)
        self.assertEqual(retrieved_session, created_session)
    
    def test_get_or_create_session(self):
        """Test getting or creating session."""
        notebook_id = "test_notebook_123"
        
        # Should create new session
        session1 = self.session_manager.get_or_create_session(notebook_id, RuntimeType.TPU)
        self.assertEqual(session1.notebook_id, notebook_id)
        self.assertEqual(session1.runtime_type, RuntimeType.TPU)
        
        # Should return existing session
        session2 = self.session_manager.get_or_create_session(notebook_id, RuntimeType.CPU)
        self.assertEqual(session1, session2)
        self.assertEqual(session2.runtime_type, RuntimeType.TPU)  # Original runtime type preserved
    
    def test_update_session_status(self):
        """Test updating session status."""
        notebook_id = "test_notebook_123"
        session = self.session_manager.create_session(notebook_id)
        initial_time = session.last_activity
        
        # Update to connected
        time.sleep(0.1)  # Ensure time difference
        self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
        
        self.assertEqual(session.status, SessionStatus.CONNECTED)
        self.assertIsNotNone(session.connection_time)
        self.assertGreater(session.last_activity, initial_time)
        
        # Update to error
        error_msg = "Test error"
        self.session_manager.update_session_status(notebook_id, SessionStatus.ERROR, error_msg)
        
        self.assertEqual(session.status, SessionStatus.ERROR)
        self.assertEqual(session.error_message, error_msg)
    
    def test_mark_session_active(self):
        """Test marking session as active."""
        notebook_id = "test_notebook_123"
        session = self.session_manager.create_session(notebook_id)
        initial_time = session.last_activity
        
        time.sleep(0.1)
        self.session_manager.mark_session_active(notebook_id)
        
        self.assertGreater(session.last_activity, initial_time)
    
    def test_is_session_idle(self):
        """Test idle session detection."""
        notebook_id = "test_notebook_123"
        session = self.session_manager.create_session(notebook_id)
        
        # Should not be idle initially
        self.assertFalse(self.session_manager.is_session_idle(notebook_id))
        
        # Mock old last_activity time
        session.last_activity = time.time() - 15  # 15 seconds ago
        
        # Should be idle now (max_idle_time is 10 seconds)
        self.assertTrue(self.session_manager.is_session_idle(notebook_id))
        
        # Non-existent session should be considered idle
        self.assertTrue(self.session_manager.is_session_idle("nonexistent"))
    
    def test_is_session_connected(self):
        """Test connected session detection."""
        notebook_id = "test_notebook_123"
        session = self.session_manager.create_session(notebook_id)
        
        # Not connected initially
        self.assertFalse(self.session_manager.is_session_connected(notebook_id))
        
        # Set to connected
        self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
        self.assertTrue(self.session_manager.is_session_connected(notebook_id))
        
        # Make it idle
        session.last_activity = time.time() - 15
        self.assertFalse(self.session_manager.is_session_connected(notebook_id))
        
        # Non-existent session should not be connected
        self.assertFalse(self.session_manager.is_session_connected("nonexistent"))
    
    def test_cleanup_idle_sessions(self):
        """Test cleanup of idle sessions."""
        # Create multiple sessions
        notebook_ids = ["notebook_1", "notebook_2", "notebook_3"]
        for notebook_id in notebook_ids:
            self.session_manager.create_session(notebook_id)
        
        # Make some sessions idle
        current_time = time.time()
        self.session_manager.sessions["notebook_1"].last_activity = current_time - 15
        self.session_manager.sessions["notebook_2"].last_activity = current_time - 5  # Not idle
        self.session_manager.sessions["notebook_3"].last_activity = current_time - 20
        
        # Cleanup
        cleaned_count = self.session_manager.cleanup_idle_sessions()
        
        self.assertEqual(cleaned_count, 2)  # notebook_1 and notebook_3 should be cleaned
        self.assertNotIn("notebook_1", self.session_manager.sessions)
        self.assertIn("notebook_2", self.session_manager.sessions)
        self.assertNotIn("notebook_3", self.session_manager.sessions)
    
    def test_remove_session(self):
        """Test session removal."""
        notebook_id = "test_notebook_123"
        self.session_manager.create_session(notebook_id)
        
        # Session exists
        self.assertIn(notebook_id, self.session_manager.sessions)
        
        # Remove session
        result = self.session_manager.remove_session(notebook_id)
        self.assertTrue(result)
        self.assertNotIn(notebook_id, self.session_manager.sessions)
        
        # Try to remove non-existent session
        result = self.session_manager.remove_session("nonexistent")
        self.assertFalse(result)
    
    def test_get_session_info(self):
        """Test getting session information."""
        notebook_id = "test_notebook_123"
        
        # Non-existent session
        self.assertIsNone(self.session_manager.get_session_info(notebook_id))
        
        # Create session
        session = self.session_manager.create_session(notebook_id, RuntimeType.GPU)
        self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
        self.session_manager.set_session_id(notebook_id, "session_456")
        
        info = self.session_manager.get_session_info(notebook_id)
        
        self.assertIsNotNone(info)
        self.assertEqual(info["notebook_id"], notebook_id)
        self.assertEqual(info["session_id"], "session_456")
        self.assertEqual(info["status"], "connected")
        self.assertEqual(info["runtime_type"], "gpu")
        self.assertIsInstance(info["idle_time"], float)
        self.assertIsInstance(info["connection_duration"], float)
        self.assertIsInstance(info["is_idle"], bool)
        self.assertIsInstance(info["is_connected"], bool)
    
    def test_list_sessions(self):
        """Test listing all sessions."""
        # No sessions initially
        sessions = self.session_manager.list_sessions()
        self.assertEqual(len(sessions), 0)
        
        # Create sessions
        notebook_ids = ["notebook_1", "notebook_2"]
        for notebook_id in notebook_ids:
            self.session_manager.create_session(notebook_id)
        
        sessions = self.session_manager.list_sessions()
        self.assertEqual(len(sessions), 2)
        
        session_ids = [s["notebook_id"] for s in sessions]
        self.assertIn("notebook_1", session_ids)
        self.assertIn("notebook_2", session_ids)
    
    def test_get_active_sessions_count(self):
        """Test counting active sessions."""
        # No sessions initially
        self.assertEqual(self.session_manager.get_active_sessions_count(), 0)
        
        # Create sessions
        notebook_ids = ["notebook_1", "notebook_2", "notebook_3"]
        for notebook_id in notebook_ids:
            self.session_manager.create_session(notebook_id)
        
        # Still no active sessions (not connected)
        self.assertEqual(self.session_manager.get_active_sessions_count(), 0)
        
        # Connect some sessions
        self.session_manager.update_session_status("notebook_1", SessionStatus.CONNECTED)
        self.session_manager.update_session_status("notebook_2", SessionStatus.CONNECTED)
        
        self.assertEqual(self.session_manager.get_active_sessions_count(), 2)
        
        # Make one idle
        self.session_manager.sessions["notebook_1"].last_activity = time.time() - 15
        
        self.assertEqual(self.session_manager.get_active_sessions_count(), 1)
    
    def test_should_reconnect(self):
        """Test reconnection decision logic."""
        notebook_id = "test_notebook_123"
        
        # Non-existent session
        self.assertFalse(self.session_manager.should_reconnect("nonexistent"))
        
        # Create session
        session = self.session_manager.create_session(notebook_id)
        
        # Disconnected session should reconnect
        self.assertTrue(self.session_manager.should_reconnect(notebook_id))
        
        # Connected session should not reconnect
        self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
        self.assertFalse(self.session_manager.should_reconnect(notebook_id))
        
        # Error session should reconnect
        self.session_manager.update_session_status(notebook_id, SessionStatus.ERROR)
        self.assertTrue(self.session_manager.should_reconnect(notebook_id))
        
        # Idle session should reconnect
        self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
        session.last_activity = time.time() - 15
        self.assertTrue(self.session_manager.should_reconnect(notebook_id))
    
    def test_get_runtime_info(self):
        """Test getting runtime information."""
        notebook_id = "test_notebook_123"
        
        # Non-existent session
        info = self.session_manager.get_runtime_info("nonexistent")
        self.assertEqual(info, {})
        
        # Create session
        self.session_manager.create_session(notebook_id, RuntimeType.TPU)
        self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
        
        info = self.session_manager.get_runtime_info(notebook_id)
        
        self.assertEqual(info["runtime_type"], "tpu")
        self.assertEqual(info["status"], "connected")
        self.assertIn("available_types", info)
        self.assertIn("recommended_type", info)
        self.assertIn("cpu", info["available_types"])
        self.assertIn("gpu", info["available_types"])
        self.assertIn("tpu", info["available_types"])


if __name__ == '__main__':
    unittest.main()