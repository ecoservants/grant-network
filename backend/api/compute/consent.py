from flask import Flask, request, jsonify
from utils import phase2_db  # Importing from your new utils folder
import logging

# Configure basic logging for auditing [Requirement: Log consent event]
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/compute/consent', methods=['POST'])
def record_consent():
    # 1. Validate node API token [Requirement]
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        logging.warning("[CONSENT] Missing API token in request")
        return jsonify({"error": "Unauthorized: API token missing"}), 401

    data = request.json
    consent_version = data.get('consent_version')
    consent_hash = data.get('consent_hash')

    # Validate payload content [Requirement: Accept version and hash]
    if not consent_version or not consent_hash:
        return jsonify({"error": "consent_version and consent_hash are required"}), 400

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # Verify node existence [Requirement: Validate node API token]
        cur.execute("SELECT id, node_public_id FROM community_nodes WHERE api_token = %s", (api_token,))
        node = cur.fetchone()
        
        if not node:
            logging.warning(f"[CONSENT] Invalid token attempt: {api_token}")
            return jsonify({"error": "Invalid or expired token"}), 403

        node_id = node[0]
        node_public_id = node[1]

        # 2. Update community_nodes with consent values [Requirement]
        # Acceptance Criteria: Consent updates overwrite previous versions safely
        cur.execute("""
            UPDATE community_nodes 
            SET consent_provided = 1,
                consent_version = %s,
                consent_hash = %s,
                consent_updated_at = NOW()
            WHERE id = %s
        """, (consent_version, consent_hash, node_id))

        # 3. Audit Logging [Requirement: Log consent event]
        logging.info(f"[CONSENT] Node {node_public_id} recorded consent version {consent_version}")

        db.commit()
        return jsonify({"status": "success", "message": "Consent recorded successfully"}), 200

    except Exception as e:
        db.rollback()
        logging.error(f"[CONSENT] System error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5002)
