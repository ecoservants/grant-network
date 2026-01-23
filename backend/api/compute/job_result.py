from flask import Flask, request, jsonify
import logging

# NOTE:
# Using absolute package imports to avoid ModuleNotFoundError when the app is
# executed via Flask, CI, or module execution (python -m ...).
# `backend` is now treated as a proper package via __init__.py files.
from backend.utils.db import get_db_connection
from backend.services.result_validation import validate_result_payload
from backend.services.job_result_handler import store_job_result  # <-- UPDATED (absolute import)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- ADDED: uniform response helpers ---
def error_response(message, status_code):
    return jsonify({"status": "error", "message": message}), status_code

def success_response(message, status_code=200):
    return jsonify({"status": "success", "message": message}), status_code
# --------------------------------------

@app.route('/compute/job/result', methods=['POST'])
def submit_job_result():

    api_token = request.headers.get("X-API-TOKEN")
    if not api_token:
        return error_response("Unauthorized: Missing API token", 401)  # <-- UPDATED

    data = request.get_json(silent=True) or {}  # <-- UPDATED (safer than request.json)
    job_id = data.get("job_id")
    result_json = data.get("result_json")
    result_checksum = data.get("result_checksum")

    # Basic input validation
    if not job_id or result_json is None or not result_checksum:  # <-- UPDATED (allow empty dict)
        return error_response("job_id, result_json, and result_checksum are required", 400)  # <-- UPDATED

    db = get_db_connection()
    cur = db.cursor()

    try:
        # Validate ownership and active claim
        cur.execute("""
            SELECT cj.id, cn.id
            FROM community_jobs cj
            JOIN community_nodes cn ON cj.claimed_by_node_id = cn.id
            WHERE cj.id = %s AND cn.api_token = %s AND cj.status = 'in_progress'
        """, (job_id, api_token))  # <-- UPDATED ('claimed' -> 'in_progress' to match schema)

        record = cur.fetchone()
        if not record:
            return error_response("Job not owned by node or not in in_progress state", 403)  # <-- UPDATED

        node_id = record[1]

        # Validate checksum/payload format
        validation = validate_result_payload(result_json, result_checksum)
        if validation is not True:  # <-- UPDATED
            return error_response(str(validation), 400)  # <-- UPDATED

        # Insert job result + mark completed
        store_job_result(cur, job_id, node_id, result_json, result_checksum)

        db.commit()
        logging.info(f"[RESULT] Job {job_id} completed by node {node_id}")

        return success_response("Job result submitted", 200)  # <-- UPDATED

    except Exception as e:
        db.rollback()
        logging.error(f"[RESULT_ERROR] {str(e)}")
        return error_response("Internal Server Error", 500)  # <-- UPDATED

    finally:
        cur.close()
        db.close()

if __name__ == "__main__":
    app.run(port=5003)
