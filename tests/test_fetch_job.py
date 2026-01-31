import unittest
from unittest.mock import MagicMock, patch
from backend.api.compute.fetch_job import app

class TestJobFetchEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_missing_token(self):
        """Should return 401 if X-API-TOKEN is missing"""
        response = self.app.get('/compute/job')
        self.assertEqual(response.status_code, 401)

    @patch('utils.phase2_db.get_db_connection')
    def test_node_inactive(self, mock_db_conn):
        """Should return 403 if node is inactive"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Mock Node: (id=1, is_active=0, consent=1)
        mock_cursor.fetchone.return_value = (1, 0, 1)
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.app.get('/compute/job', headers={'X-API-TOKEN': 'valid'})
        self.assertEqual(response.status_code, 403)
        self.assertIn("inactive", response.get_json()['error'])

    @patch('utils.phase2_db.get_db_connection')
    def test_job_assignment_success(self, mock_db_conn):
        """Should return 200 and job data when successful"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # 1. Node Check: Active and Consented
        # 2. Over-assignment Check: None (None active jobs)
        # 3. Job Fetch: Found Job (101, 'render', '{}')
        mock_cursor.fetchone.side_effect = [
            (1, 1, 1),      # Node Query
            None,           # Over-assignment Query
            (101, 'render', '{}') # Job Query
        ]
        
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.app.get('/compute/job', headers={'X-API-TOKEN': 'valid'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['job_id'], 101)

if __name__ == '__main__':
    unittest.main()
