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