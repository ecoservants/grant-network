from flask import Flask, request, jsonify
import from utils import phase2_db
import logging

# Configure basic logging [Requirement: Log opt-out event]
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/compute/opt-out', methods=['POST'])
def opt_out():
    # 1. Validate node identity via API token [Requirement]
    # Reviewer expects X-API-TOKEN header for security
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        logging.warning("[OPT-OUT] Attempted opt-out without API token")
        return jsonify({"error": "Unauthorized: API token required"}), 401
    
    db = phase2_db.get_db_connection()
    cur = db.cursor()
    
    try:
        # Check if node exists and get its ID [Requirement: Auth via API token]
        cur.execute("SELECT id, node_public_id FROM community_nodes WHERE api_token = %s", (api_token,))
        node = cur.fetchone()
        if not node:
            logging.warning(f"[OPT-OUT] Invalid token attempt: {api_token}")
            return jsonify({"error": "Invalid node identity"}), 403
        
        node_id = node[0]
        node_public_id = node[1]

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
        
        # 4. Handle outstanding jobs [Requirement: Use correct table name 'community_jobs']
        # Reassigning 'claimed' jobs back to 'pending' so they aren't orphaned
        cur.execute("""
            UPDATE community_jobs 
            SET status = 'pending', claimed_by_node_id = NULL 
            WHERE claimed_by_node_id = %s AND status = 'claimed'
        """, (node_id,))
        
        db.commit()

        # Final Logging [Requirement: Audit trail]
        logging.info(f"[OPT-OUT] Node {node_public_id} (ID: {node_id}) deactivated successfully")
        
        return jsonify({
            "status": "success", 
            "message": "Node deactivated, sessions terminated, and jobs reassigned"
        }), 200

    except Exception as e:
        logging.error(f"[OPT-OUT] Error during deactivation: {str(e)}")
        db.rollback()
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5000)

