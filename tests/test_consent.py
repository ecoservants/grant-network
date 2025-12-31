import unittest
from unittest.mock import MagicMock, patch
from api.compute.consent import app 

class TestConsentEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_missing_api_token(self):
        """Test 401 Unauthorized when X-API-TOKEN is missing"""
        response = self.app.post('/compute/consent', json={
            "consent_version": "1.0", 
            "consent_hash": "a"*64
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("API token missing", response.get_json()['error'])

    @patch('utils.phase2_db.get_db_connection')
    def test_invalid_api_token(self, mock_db_conn):
        """Test 403 Forbidden when token does not exist in DB"""
        # Mock DB to return None (no node found)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.app.post('/compute/consent', 
                                 headers={'X-API-TOKEN': 'bad-token'},
                                 json={"consent_version": "1.0", "consent_hash": "a"*64})
        
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.get_json()['error'])

    def test_invalid_hash_format(self):
        """Test 400 Bad Request when hash contains invalid chars"""
        response = self.app.post('/compute/consent', 
                                 headers={'X-API-TOKEN': 'valid-token'},
                                 json={
                                     "consent_version": "1.0", 
                                     "consent_hash": "INVALID_HASH_!@#$" 
                                 })
        self.assertEqual(response.status_code, 400)

    @patch('utils.phase2_db.get_db_connection')
    def test_successful_consent(self, mock_db_conn):
        """Test 200 OK and correct response on success"""
        # Mock DB to return a valid node
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Return (id, node_public_id)
        mock_cursor.fetchone.return_value = (1, "node_123_pub")
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.app.post('/compute/consent', 
                                 headers={'X-API-TOKEN': 'valid-token'},
                                 json={
                                     "consent_version": "1.0", 
                                     "consent_hash": "a"*64
                                 })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['node_public_id'], 'node_123_pub')

if __name__ == '__main__':
    unittest.main()
