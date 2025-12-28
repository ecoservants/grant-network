from flask import Flask, request, jsonify
import from utils import phase2_db
import logging  # Added logging for debugging/monitoring [Reviewer Requirement]

# Set up simple logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/compute/job', methods=['GET'])
def fetch_job():
    # 1. Validate node authorization via API token
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        return jsonify({"error": "Unauthorized"}), 401

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 2. Node Eligibility Checks: Active status + Consent
        cur.execute("""
            SELECT id, is_active, consent_provided 
            FROM community_nodes 
            WHERE api_token = %s
        """, (api_token,))
        node = cur.fetchone()

        if not node:
            return jsonify({"error": "Node not found"}), 404
        if not node[1]: # is_active check
            return jsonify({"error": "Node is inactive"}), 403
        if not node[2]: # consent check
            return jsonify({"error": "Valid consent required"}), 403

        node_id = node[0]

        # 3. Check for over-assignment (At most one job at a time)
        # Updated table name to 'community_jobs' [Reviewer Requirement]
        cur.execute("""
            SELECT id FROM community_jobs 
            WHERE claimed_by_node_id = %s AND status = 'claimed'
        """, (node_id,))
        if cur.fetchone():
            return jsonify({"error": "Node already has an active job"}), 429

        # 4. Fetch, Lock, and Mark Job
        # Updated table name to 'community_jobs'
        cur.execute("""
            UPDATE community_jobs 
            SET status = 'claimed', 
                claimed_by_node_id = %s,
                claimed_at = NOW()
            WHERE id = (
                SELECT id FROM community_jobs 
                WHERE status = 'pending' 
                LIMIT 1 
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, job_type, payload;
        """, (node_id,))
        
        job = cur.fetchone()
        db.commit()

        # 5. Return standardized JSON payload with logging
        if job:
            logging.info(f"Job {job[0]} claimed by node {node_id}") # [Reviewer Requirement]
            return jsonify({
                "job_id": job[0],
                "type": job[1],
                "data": job[2]
            }), 200
        else:
            return jsonify({"message": "No pending jobs available"}), 404

    except Exception as e:
        logging.error(f"Error in job fetch: {str(e)}") # [Reviewer Requirement]
        db.rollback()
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5001)
