from fastapi import HTTPException

class RegisterNodeRequest(BaseModel):
    user_agent: str
    consent_flag: bool
    user_id: int | None = None  # optional

def validate_request(data):
    if not data.consent_flag:
        raise HTTPException(status_code=400, detail="Consent required")
    if not data.user_agent or len(data.user_agent) < 2:
        raise HTTPException(status_code=400, detail="Invalid user agent")
