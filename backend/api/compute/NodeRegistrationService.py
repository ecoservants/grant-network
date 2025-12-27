import uuid, secrets
from db import db

class NodeRegistrationService:
    @staticmethod
    def register(user_agent, consent_flag, user_id=None):
        # 1. Consent validation
        if not consent_flag:
            return {"error": "Consent required"}, 400
        
        # 2. Credential generation
        node_public_id = uuid.uuid4().hex
        api_token = secrets.token_hex(32)
        session_token = secrets.token_hex(32)

        # 3. Create node record
        db.insert("community_nodes", {
            "node_public_id": node_public_id,
            "wp_user_id": user_id,
            "api_token": api_token,
            "consented_at": "NOW()",
            "is_active": 1
        })

        # 4. Create initial session
        db.insert("community_node_sessions", {
            "session_token": session_token,
            "node_id": db.last_id(),
            "user_agent": user_agent,
            "is_active": 1
        })

        # 5. Return issued tokens
        return {
            "node_public_id": node_public_id,
            "api_token": api_token,
            "session_token": session_token
        }, 200
