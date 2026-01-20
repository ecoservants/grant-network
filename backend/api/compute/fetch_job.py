from flask import Flask, request, jsonify
from utils import phase2_db
from utils.logger import setup_logger

app = Flask(__name__)
logger = setup_logger("JobFetchAPI")

@app.route('/compute/job', methods=['GET'])
def fetch_job():
    # 1. Validate API Token
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        return jsonify({"error": "Unauthorized: API token missing"}), 401

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 2. Node Eligibility Checks (Active + Consent)
        cur.execute("""
            SELECT id, is_active, consent_provided 
            FROM community_nodes 
            WHERE api_token = %s
        """, (api_token,))
        node = cur.fetchone()

        if not node:
            return jsonify({"error": "Unauthorized: Node not found"}), 401 # Changed to 401/403 consistency
        
        node_id, is_active, consent_provided = node

        if not is_active:
            return jsonify({"error": "Forbidden: Node is inactive"}), 403
        if not consent_provided:
            return jsonify({"error": "Forbidden: Consent required (CC-11)"}), 403

        # 3. Prevent Over-Assignment (One active job per node)
        cur.execute("""
            SELECT id FROM community_jobs 
            WHERE claimed_by_node_id = %s AND status = 'claimed'
        """, (node_id,))
        
        if cur.fetchone():
            return jsonify({"error": "Rate Limit: Node already has an active job"}), 429

        # 4. Atomic Job Scheduling (MySQL Compatible)
        # Step A: Find and Lock the next available job
        cur.execute("""
            SELECT id, job_type, payload 
            FROM community_jobs 
            WHERE status = 'pending' 
            LIMIT 1 
            FOR UPDATE SKIP LOCKED
        """)
        job = cur.fetchone()

        if not job:
            db.commit() # Commit the empty read
            return jsonify({"message": "No pending jobs available"}), 404

        job_id, job_type, payload = job

        # Step B: Mark it as claimed
        cur.execute("""
            UPDATE community_jobs 
            SET status = 'claimed',
                claimed_by_node_id = %s,
                claimed_at = NOW()
            WHERE id = %s
        """, (node_id, job_id))

        db.commit()

        # 5. Success Response & Log
        logger.info(f"[JOB-FETCH] Success: Job {job_id} assigned to Node {node_id}")
        
        return jsonify({
            "job_id": job_id,
            "type": job_type,
            "data": payload
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"[JOB-FETCH] System Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5001)
