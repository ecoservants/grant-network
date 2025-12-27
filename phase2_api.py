from flask import Flask, request, jsonify
import phase2_db  # Import from the same folder

app = Flask(__name__)

@app.route('/compute/opt-out', methods=['POST'])
def opt_out():
    data = request.json
    node_public_id = data.get('node_public_id')
    
    if not node_public_id:
        return jsonify({"error": "node_public_id is required"}), 400
    
    db = phase2_db.get_db_connection()
    cur = db.cursor()
    
    # 1. Deactivate the node and record timestamp
    cur.execute("""
        UPDATE community_nodes 
        SET is_active = 0, opt_out_at = NOW() 
        WHERE node_public_id = %s
    """, (node_public_id,))
    
    # 2. Invalidate all active sessions for this node
    cur.execute("""
        UPDATE community_node_sessions 
        SET is_active = 0 
        WHERE node_id = (SELECT id FROM community_nodes WHERE node_public_id = %s)
    """, (node_public_id,))
    
    db.commit()
    cur.close()
    db.close()
    
    return jsonify({"status": "success", "message": "Node and sessions deactivated"}), 200

if __name__ == '__main__':
    app.run(debug=True)
    # Add this route below your opt_out function
@app.route('/compute/job', methods=['GET'])
def fetch_job():
    # 1. Auth via api_token (Requirement: Auth via api_token)
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        return jsonify({"error": "Unauthorized"}), 401

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 2. Query & 3. Lock (Requirement: Query for pending job and lock it)
        # This uses "FOR UPDATE SKIP LOCKED" to prevent two nodes from taking the same job
        cur.execute("""
            UPDATE jobs 
            SET status = 'claimed', 
                claimed_by_node_id = (SELECT id FROM community_nodes WHERE api_token = %s),
                claimed_at = NOW()
            WHERE id = (
                SELECT id FROM jobs 
                WHERE status = 'pending' 
                LIMIT 1 
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, job_type, payload;
        """, (api_token,))
        
        job = cur.fetchone()
        db.commit()

        # 4. Return (Requirement: Return minimal JSON payload)
        if job:
            return jsonify({
                "job_id": job[0],
                "type": job[1],
                "data": job[2]
            }), 200
        else:
            return jsonify({"message": "No pending jobs"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        db.close()