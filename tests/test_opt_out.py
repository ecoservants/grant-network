import unittest
from unittest.mock import MagicMock, patch
# Import from the file you just created
from backend.api.compute.opt_out import app

class TestOptOutEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_missing_content_type(self):
        """Test 415 if Content-Type is missing (Reviewer Requirement)"""
        response = self.app.post('/compute/opt-out', headers={'X-API-TOKEN': 'valid'})
        self.assertEqual(response.status_code, 415)

    def test_missing_token(self):
        """Test 401 if Token is missing"""
        response = self.app.post('/compute/opt-out', content_type='application/json')
        self.assertEqual(response.status_code, 401)

    @patch('utils.phase2_db.get_db_connection')
    def test_successful_opt_out(self, mock_db_conn):
        """Test 200 OK and correct logic execution"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "node_test_pub")
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.app.post('/compute/opt-out', 
                                 headers={'X-API-TOKEN': 'valid-token'},
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("node_test_pub", response.get_json()['node_id'])

if __name__ == '__main__':
    unittest.main()
