from flask import Flask, request, jsonify
from datetime import datetime, timezone

from backend.utils.db import get_db_connection
from backend.utils.logger import setup_logger
from backend.services.node_registration_service import register_node

app = Flask(__name__)
logger = setup_logger("RegisterNodeAPI")


@app.route("/compute/register-node", methods=["POST"])
def register_node_endpoint():
    data = request.json or {}

    user_agent = data.get("user_agent")  # string, optional but recommended
    consent_flag = data.get("consent_flag")  # required boolean
    user_id = data.get("user_id")  # optional -> wp_user_id

    # Uniform error shape (consistent with reviewer feedback)
    if consent_flag is None:
        return jsonify({"status": "error", "message": "Missing required field: consent_flag"}), 400
    if consent_flag is not True:
        return jsonify({"status": "error", "message": "Consent required"}), 400

    # Default user_agent if not provided
    if not user_agent:
        user_agent = request.headers.get("User-Agent", "unknown")

    db = get_db_connection()
    try:
        result = register_node(db=db, user_agent=user_agent, user_id=user_id)
        server_time = datetime.now(timezone.utc).isoformat()

        return jsonify({
            "status": "success",
            "message": "Node registered",
            "node_public_id": result["node_public_id"],
            "api_token": result["api_token"],
            "session_token": result["session_token"],
            "server_time": server_time,
        }), 200
    except ValueError as ve:
        logger.warning(f"[REGISTER] Validation error: {str(ve)}")
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"[REGISTER] Internal error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    finally:
        try:
            db.close()
        except Exception:
            pass


if __name__ == "__main__":
    app.run(port=5004)
