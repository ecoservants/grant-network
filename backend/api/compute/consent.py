from flask import Flask, request, jsonify
from utils import phase2_db
from utils.logger import setup_logger 
import re
import logging

app = Flask(__name__)

# Initialize the centralized logger
logger = setup_logger("ConsentAPI")

def validate_hash_format(hash_str):
    """
    Security Check: Validates that the hash contains only safe characters
    (hexadecimal or alphanumeric) and is of a reasonable length (32-128 chars).
    """
    if not hash_str:
        return False
    # Regex checks for 32-128 characters, numbers 0-9 and letters a-f (hex)
    pattern = re.compile(r'^[a-fA-F0-9]{32,128}$')
    return bool(pattern.fullmatch(hash_str))

@app.route('/compute/consent', methods=['POST'])
def record_consent():
    # 1. Validate API Token Presence
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        logger.warning("[CONSENT] Unauthorized: Missing X-API-TOKEN header")
        return jsonify({"error": "Unauthorized: API token missing"}), 401

    # 2. Extract and Validate Payload
    data = request.json or {}
    consent_version = data.get('consent_version')
    consent_hash = data.get('consent_hash')

    if not consent_version or not consent_hash:
        return jsonify({"error": "Missing required fields: consent_version, consent_hash"}), 400

    # 3. Security: Hash Format Validation (Reviewer Requirement)
    if not validate_hash_format(consent_hash):
        logger.warning(f"[CONSENT] Security alert: Malformed hash received: {consent_hash}")
        return jsonify({"error": "Invalid consent_hash format"}), 400

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 4. Verify Node Token in DB
        cur.execute("SELECT id, node_public_id FROM community_nodes WHERE api_token = %s", (api_token,))
        node = cur.fetchone()

        if not node:
            # Addressing "Consider separating 401 vs 403" feedback
            logger.warning(f"[CONSENT] Forbidden: Invalid token {api_token[:5]}...")
            return jsonify({"error": "Forbidden: Invalid or expired token"}), 403

        node_id = node[0]
        node_public_id = node[1]

        # 5. Update Consent (Overwrite previous version safely)
        cur.execute("""
            UPDATE community_nodes 
            SET consent_provided = TRUE,
                consent_version = %s,
                consent_hash = %s,
                consent_updated_at = NOW()
            WHERE id = %s
        """, (consent_version, consent_hash, node_id))

        db.commit()

        # 6. Audit Log & Response (Addressing "Add response payload including node_public_id")
        logger.info(f"[CONSENT] Success: Node {node_public_id} agreed to v{consent_version}")
        
        return jsonify({
            "status": "success", 
            "message": "Consent recorded successfully",
            "node_public_id": node_public_id
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"[CONSENT] Critical Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    app.run(port=5002)
