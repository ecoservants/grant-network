from flask import Flask, request, jsonify
from utils import phase2_db
from services.result_validation import validate_result_payload
from services.job_result_handler import store_job_result
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/compute/job/result', methods=['POST'])
def submit_job_result():

    api_token = request.headers.get("X-API-TOKEN")
    if not api_token:
        return jsonify({"error": "Unauthorized: Missing API token"}), 401

    data = request.json or {}
    job_id = data.get("job_id")
    result_json = data.get("result_json")
    result_checksum = data.get("result_checksum")

    # Basic input validation
    if not job_id or not result_json or not result_checksum:
        return jsonify({"error": "job_id, result_json, result_checksum required"}), 400

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # Validate ownership and active claim
        cur.execute("""
            SELECT cj.id, cn.id
            FROM community_jobs cj
            JOIN community_nodes cn ON cj.claimed_by_node_id = cn.id
            WHERE cj.id = %s AND cn.api_token = %s AND cj.status = 'claimed'
        """, (job_id, api_token))
        
        record = cur.fetchone()
        if not record:
            return jsonify({"error": "Job not owned by node or not in claimed state"}), 403

        node_id = record[1]

        # Validate checksum/payload format
        validation = validate_result_payload(result_json, result_checksum)
        if validation != True:
            return jsonify({"error": validation}), 400

        # Insert job result + mark completed
        store_job_result(cur, job_id, node_id, result_json, result_checksum)

        db.commit()
        logging.info(f"[RESULT] Job {job_id} completed by node {node_id}")

        return jsonify({"status": "success", "message": "Job result submitted"}), 200

    except Exception as e:
        db.rollback()
        logging.error(f"[RESULT_ERROR] {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        cur.close()
        db.close()

if __name__ == "__main__":
    app.run(port=5003)
