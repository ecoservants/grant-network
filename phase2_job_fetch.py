from flask import Flask, request, jsonify
import phase2_db

app = Flask(__name__)

@app.route('/compute/job', methods=['GET'])
def fetch_job():
    # 1. Validate node authorization via API token [Requirement]
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        return jsonify({"error": "Unauthorized"}), 401

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 2. Node Eligibility Checks: Active status + Consent [Requirement]
        # Ineligible nodes must receive correct error codes [Acceptance Criteria]
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

        # 3. Check for over-assignment: Node receives at most one job [Acceptance Criteria]
        cur.execute("SELECT id FROM jobs WHERE claimed_by_node_id = %s AND status = 'claimed'", (node_id,))
        if cur.fetchone():
            return jsonify({"error": "Node already has an active job"}), 429

        # 4. Fetch, Lock, and Mark Job (Scheduling Logic) [Requirement]
        # SKIP LOCKED handles concurrency correctly [Acceptance Criteria]
        cur.execute("""
            UPDATE jobs 
            SET status = 'claimed', 
                claimed_by_node_id = %s,
                claimed_at = NOW()
            WHERE id = (
                SELECT id FROM jobs 
                WHERE status = 'pending' 
                LIMIT 1 
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, job_type, payload;
        """, (node_id,))
        
        job = cur.fetchone()
        db.commit()

        # 5. Return minimal JSON payload [Requirement]
        if job:
            return jsonify({
                "job_id": job[0],
                "type": job[1],
                "data": job[2]
            }), 200
        else:
            return jsonify({"message": "No pending jobs available"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5001)
