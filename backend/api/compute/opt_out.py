from flask import Flask, request, jsonify
from utils import phase2_db
from utils.logger import setup_logger

app = Flask(__name__)

# Use the centralized logger from CC-11
logger = setup_logger("OptOutAPI")

@app.route('/compute/opt-out', methods=['POST'])
def opt_out():
    # 1. Safety Check: Content-Type [Reviewer Requirement]
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

    # 2. Validate API Token [Requirement]
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        logger.warning("[OPT-OUT] Unauthorized: Attempted opt-out without API token")
        return jsonify({"error": "Unauthorized: API token required"}), 401

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 3. Identify Node
        cur.execute("SELECT id, node_public_id FROM community_nodes WHERE api_token = %s", (api_token,))
        node = cur.fetchone()
        
        if not node:
            logger.warning(f"[OPT-OUT] Forbidden: Invalid token used {api_token[:5]}...")
            return jsonify({"error": "Forbidden: Invalid node identity"}), 403

        node_id = node[0]
        node_public_id = node[1]

        # 4. Deactivate Node (is_active = 0)
        cur.execute("""
            UPDATE community_nodes 
            SET is_active = FALSE, opt_out_at = NOW() 
            WHERE id = %s
        """, (node_id,))

        # 5. Terminate Sessions
        cur.execute("""
            UPDATE community_node_sessions 
            SET is_active = FALSE, ended_at = NOW()
            WHERE node_id = %s AND is_active = TRUE
        """, (node_id,))

        # 6. Reassign Jobs (Prevent "Orphaned" jobs)
        cur.execute("""
            UPDATE community_jobs 
            SET status = 'pending', claimed_by_node_id = NULL 
            WHERE claimed_by_node_id = %s AND status = 'claimed'
        """, (node_id,))

        db.commit()

        # 7. Audit Log & Response [Reviewer Requirement]
        logger.info(f"[OPT-OUT] Success: Node {node_public_id} deactivated. Sessions killed, jobs released.")
        
        return jsonify({
            "status": "success", 
            "message": "Node deactivated, sessions terminated, and jobs reassigned",
            "node_id": node_public_id
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"[OPT-OUT] Critical System Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5003)
