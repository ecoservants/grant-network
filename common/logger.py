import os, logging

# Setup logger
def get_logger(filename: str):
    os.makedirs("ingest_logs", exist_ok=True)
    logger = logging.getLogger("bmf_ingest")
    logger.setLevel(logging.INFO)
    if not logger.handlers: 
        fh = logging.FileHandler("ingest_logs/" + filename)
        fh.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger