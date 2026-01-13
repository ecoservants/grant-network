def validate_row(funder):
    # name is required
    if not funder.name or not funder.name.strip():
        raise ValueError("Missing organization name")
    
    # EIN should be 9 digits
    if not funder.ein or len(funder.ein) != 9 or not funder.ein.isdigit():
        raise ValueError(f"Invalid EIN: {funder.ein}")
    
    # State code should be 2 letters if provided
    if funder.state and len(funder.state) != 2:
        raise ValueError(f"Invalid state code: {funder.state}")
    
    return True
