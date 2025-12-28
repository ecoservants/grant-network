from flask import Flask, request, jsonify
import phase2_db

app = Flask(__name__)

@app.route('/compute/opt-out', methods=['POST'])
def opt_out():
    # 1. Validate node identity via API token [Requirement]
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        return jsonify({"error": "API token required"}), 401
    
    db = phase2_db.get_db_connection()
    cur = db.cursor()
    
    try:
        # Check if node exists and get its ID
        cur.execute("SELECT id FROM community_nodes WHERE api_token = %s", (api_token,))
        node = cur.fetchone()
        if not node:
            return jsonify({"error": "Invalid node identity"}), 403
        
        node_id = node[0]

        # 2. Mark node as inactive (is_active = 0) & Log event [Requirement]
        cur.execute("""
            UPDATE community_nodes 
            SET is_active = 0, opt_out_at = NOW() 
            WHERE id = %s
        """, (node_id,))
        
        # 3. Terminate all active sessions [Requirement]
        cur.execute("""
            UPDATE community_node_sessions 
            SET is_active = 0 
            WHERE node_id = %s
        """, (node_id,))
        
        # 4. Handle outstanding jobs (mark as abandoned/pending again) [Requirement]
        # This prevents jobs from being "orphaned"
        cur.execute("""
            UPDATE jobs 
            SET status = 'pending', claimed_by_node_id = NULL 
            WHERE claimed_by_node_id = %s AND status = 'claimed'
        """, (node_id,))
        
        db.commit()
        return jsonify({"status": "success", "message": "Node opted out and jobs reassigned"}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5000)
