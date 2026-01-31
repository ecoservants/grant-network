import unittest
from unittest.mock import MagicMock, patch

from backend.api.compute.register_node import app


class TestRegisterNodeEndpoint(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_missing_consent_flag(self):
        resp = self.client.post("/compute/register-node", json={"user_agent": "Chrome"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.get_json()["status"], "error")

    def test_consent_rejected_when_false(self):
        resp = self.client.post("/compute/register-node", json={"user_agent": "Chrome", "consent_flag": False})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.get_json()["status"], "error")

    @patch("backend.api.compute.register_node.get_db_connection")
    @patch("backend.api.compute.register_node.register_node")
    def test_register_success(self, mock_register_node, mock_db_conn):
        mock_db = MagicMock()
        mock_db_conn.return_value = mock_db

        mock_register_node.return_value = {
            "node_public_id": "123e4567-e89b-12d3-a456-426614174000",
            "api_token": "a" * 64,
            "session_token": "b" * 64,
        }

        resp = self.client.post("/compute/register-node", json={"user_agent": "Chrome", "consent_flag": True})
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("node_public_id", data)
        self.assertIn("api_token", data)
        self.assertIn("session_token", data)
        self.assertIn("server_time", data)


if __name__ == "__main__":
    unittest.main()
