def test_node_registration_success(client):
    """Node should register successfully and return credentials."""
    # In production, this will accept ANY valid user-agent string (Chrome, Safari, CLI clients, etc.)
    response = client.post("/compute/register-node", json={
        "user_agent": "Chrome-Node/1.0",   
        "consent_flag": True
    })
    assert response.status_code == 200
    data = response.json()
    assert "node_public_id" in data
    assert "api_token" in data
    assert "session_token" in data


def test_missing_consent_rejected(client):
    """Registration must fail if consent is not provided."""
    response = client.post("/compute/register-node", json={
        "user_agent": "CLI-Node",
        "consent_flag": False              # intentionally rejecting case
    })
    assert response.status_code == 400


def test_session_created_on_registration(mock_db):
    """A session entry must be created automatically after registration."""
    NodeRegistrationService.register("Test-Agent", True)
    assert mock_db.last_insert_table == "community_node_sessions"
    assert mock_db.last_record["is_active"] == 1
