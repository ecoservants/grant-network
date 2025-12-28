import hashlib
import json

def validate_result_payload(result_json, result_checksum):
    """
    Validate JSON result + checksum integrity
    - result_json must be valid JSON serializable content
    - SHA256(result_json) must match result_checksum
    """

    try:
        normalized = json.dumps(result_json, sort_keys=True)
    except:
        return "Invalid JSON payload format"

    generated_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    if generated_hash != result_checksum:
        return "Checksum mismatch — integrity validation failed"

    return True
