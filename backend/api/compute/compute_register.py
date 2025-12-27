from fastapi import APIRouter, HTTPException, Request
import uuid
from datetime import datetime
from db import get_conn

router = APIRouter()

@router.post("/compute/register-node")
def register_node(request_body: dict, request: Request):
    user_agent = request_body.get("user_agent", request.headers.get("User-Agent"))
    consent_flag = request_body.get("consent_flag")
    user_id = request_body.get("user_id")

    if not consent_flag:
        raise HTTPException(status_code=400, detail="Consent required to join network")

    node_public_id = str(uuid.uuid4())
    api_token = uuid.uuid4().hex
    session_token = uuid.uuid4().hex

    conn = get_conn()
    cur = conn.cursor()

    # Insert node record
    cur.execute("""
        INSERT INTO community_nodes (node_public_id, wp_user_id, api_token, is_active, consented_at)
        VALUES (%s, %s, %s, 1, NOW())
    """, (node_public_id, user_id, api_token))

    node_id = cur.lastrowid

    # Create session record
    cur.execute("""
        INSERT INTO community_node_sessions (session_token, node_id, user_agent, is_active)
        VALUES (%s, %s, %s, 1)
    """, (session_token, node_id, user_agent))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "node_public_id": node_public_id,
        "api_token": api_token,
        "session_token": session_token,
        "server_time": datetime.utcnow().isoformat() + "Z"
    }
