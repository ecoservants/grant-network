import requests
import json
import logging
import os
from jsonschema import validate, ValidationError


BASE_URL = "https://api.grants.gov/v1/api/search2"
with open("../../../docs/schema/grants_gov_schema.json") as f:
    GRANT_SCHEMA = json.load(f)

def fetch_all_grants(rows_per_call=50):
    """
    Fetch all grant listings from the Grants.gov API using pagination.

    Args:
        rows_per_call (int, optional): Number of grant records to fetch per API request. Defaults to 50.

    Returns:
        list: A list of all grant records returned by the API, where each record is a dictionary.

    Notes:
        - Uses POST requests to the Grants.gov search endpoint.
        - Handles pagination until all available grants are retrieved.
        - Does not apply any filtering; all grants with default API parameters are fetched. Default search params in api - "oppStatuses": "forecasted|posted"
    """
    all_grants = []
    start = 0

    while True:
        payload = {
            "rows": rows_per_call,
            "startRecordNum": start
        }

        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        grants = data["data"]["oppHits"]

        if not grants:
            break

        all_grants.extend(grants)
        start += len(grants)

        print(f"Fetched {len(all_grants)} grants so far...")

    return all_grants

def save_raw(data, folder="../../../datasets/grants_gov/raw"):
    """
    Save raw grant data to a JSON file, creating directories if needed.

    Args:
        data (dict or list): The raw grant data to be saved.
        folder (str, optional): Path to the folder where the JSON file will be stored.
            Defaults to '../../../datasets/grants_gov/raw'.

    Returns:
        None

    Notes:
        - Creates the target directory if it does not exist.
        - The file is saved with a fixed name 'grants_raw.json'.
        - Pretty-prints JSON with indentation for readability.
    """
    os.makedirs(folder, exist_ok=True)

    # Clean timestamp for filename (remove colon and dot)
    file_path = os.path.join(folder, f"grants_raw.json")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved raw data to {file_path}")


def normalize_grant(grant):
    """
    Normalize a single grant record from Grants.gov API to the OGN standard schema.

    Args:
        grant (dict): A raw grant record as returned by the Grants.gov API.

    Returns:
        dict: A normalized grant record with standardized field names, including:
            - id
            - number
            - title
            - agency_code
            - agency
            - open_date
            - close_date
            - opportunity_status
            - document_type
            - cfda_list

    Notes:
        - Maps raw API field names to OGN standard field names.
        - Missing fields will be set to None.
    """
    normalized = {
        "id": grant.get("id"),
        "number": grant.get("number"),
        "title": grant.get("title"),
        "agency_code": grant.get("agencyCode"),
        "agency": grant.get("agency"),
        "open_date": grant.get("openDate"),
        "close_date": grant.get("closeDate"),
        "opportunity_status": grant.get("oppStatus"),
        "document_type": grant.get("docType"),
        "cfda_list": grant.get("cfdaList"),
    }
    return normalized

def normalize_all(raw_data):
    """
    Normalize all grant records from the Grants.gov API response.

    Args:
        raw_data (dict): The raw API response containing multiple grant opportunities,
            typically under raw_data["data"]["oppHits"].

    Returns:
        list: A list of normalized grant records (dicts), where each record follows
            the OGN standard schema with fields like id, number, title, agency_code,
            agency, open_date, close_date, opportunity_status, document_type, and cfda_list.

    Notes:
        - Uses the `normalize_grant` function to normalize each individual grant.
        - Handles only the 'oppHits' list inside the API response.
        - Returns an empty list if no opportunities are found.
    """
    return [normalize_grant(r) for r in raw_data]


def save_normalized(data, folder = "../../../datasets/grants_gov/normalized"):
    """
    Save normalized grant data to a JSON file, creating directories if needed.

    Args:
        data (list): A list of normalized grant records (dicts) following the OGN standard schema.
        folder (str, optional): Path to the folder where the JSON file will be stored.
            Defaults to '../../../datasets/grants_gov/normalized'.

    Returns:
        None

    Notes:
        - Creates the target directory if it does not exist.
        - Saves the file with a fixed name 'grants_normalized.json'.
        - Pretty-prints JSON with indentation for readability.
    """
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"grants_normalized.json")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved normalized data to {file_path}")


# validation and error logging.

def validate_grant(grant, folder="../../../logs"):
    """
    Validate a single normalized grant record and log any missing required fields.

    Args:
        grant (dict): A normalized grant record following the OGN standard schema.
        folder (str, optional): Path to the folder where the log file will be saved.
            Defaults to "../../../logs".

    Returns:
        bool: True if all required fields are present, False if any required field is missing.

    Notes:
        - Required fields include:
            id, number, title, agency_code, agency, open_date,
            opportunity_status, document_type, cfda_list
        - optional: close_date
        - Creates the log directory if it does not exist.
        - Logs warnings to 'grants_ingest.log' for any missing fields.
        - Does not raise exceptions; simply returns False if validation fails.
    """
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "grants_ingest.log")

    logging.basicConfig(
        filename=file_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    # -------------------------
    # Schema validation
    # -------------------------
    try:
        validate(instance=grant, schema=GRANT_SCHEMA)
    except ValidationError as e:
        logging.error(
            f"Schema validation failed for grant {grant.get('id')}: {e.message}"
        )
        return False

    # -------------------------
    # Business validation
    # -------------------------
    required_fields = [
        "id", "number", "title", "agency_code", "agency",
        "open_date", "opportunity_status",
        "document_type", "cfda_list"
    ]

    missing = [f for f in required_fields if not grant.get(f)]

    if missing:
        logging.warning(
            f"Missing required fields {missing} in grant {grant.get('id')}"
        )
        return False

    return True

def main():
    raw_data = fetch_all_grants()
    save_raw(raw_data)

    normalized = normalize_all(raw_data)
    for opp in normalized:
        validate_grant(opp)

    save_normalized(normalized)

    # proof for 30 sample records
    sample_records = normalized[:30]  # records 30 to 59
    valid_count = sum(validate_grant(r) for r in sample_records)
    print(f"{valid_count} out of {len(sample_records)} records passed schema validation")

if __name__ == "__main__":
    main()
