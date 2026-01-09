import logging

def setup_logger(name=__name__):
    """
    Centralized logging configuration to ensure consistent formats
    across all API endpoints.
    """
    logger = logging.getLogger(name)
    
    # Only add handler if it doesn't exist (prevents duplicate logs)
    if not logger.handlers:
        handler = logging.StreamHandler()
        # Format: Time - Module - Level - Message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    return logger
