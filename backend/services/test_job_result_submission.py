def test_valid_result_submission(client):
    response = client.post("/compute/job/result",
        headers={"X-API-TOKEN":"valid_token"},
        json={
            "job_id":1,
            "result_json":{"title":"parsed grant"},
            "result_checksum":"valid_sha256_here"
        }
    )
    assert response.status_code == 200

def test_invalid_checksum(client):
    response = client.post("/compute/job/result",
        headers={"X-API-TOKEN":"valid_token"},
        json={
            "job_id":1,
            "result_json":{"wrong":"data"},
            "result_checksum":"incorrect_hash"
        }
    )
    assert response.status_code == 400

def test_unauthorized_submission(client):
    response = client.post("/compute/job/result",
        json={"job_id":1,"result_json":{},"result_checksum":"x"}
    )
    assert response.status_code == 401
