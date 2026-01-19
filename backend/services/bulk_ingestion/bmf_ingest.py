import pandas as pd
import requests, io, os
from common.schemas import Funder
from common.validators import validate_row
from common.logger import get_logger

logger = get_logger("bmf_errors.log")

STATES = [
    "al","ak","az","ar","ca","co","ct","de","dc","fl","ga","hi","id","il","in",
    "ia","ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh",
    "nj","nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut",
    "vt","va","wa","wv","wi","wy"
]

def download_bmf_state(state: str) -> pd.DataFrame:
    """Download a single state's BMF CSV and return only required columns
    Parse EIN, organization names, addresses, NTEE codes"""
    url = f"https://www.irs.gov/pub/irs-soi/eo_{state}.csv"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')), dtype=str)

        # Keep only required columns
        # added safe check for missing columns to avoid failure of pipeline if cols missings
        expected_cols = ['EIN', 'NAME', 'STREET', 'CITY', 'STATE', 'ZIP', 'NTEE_CD']

        missing_cols = set(expected_cols) - set(df.columns)

        if missing_cols:
            logger.warning(f"Missing expected columns: {missing_cols}")

        df = df.reindex(columns=expected_cols)
        return df
    except Exception as e:
        logger.error(f"Failed to download/load BMF for {state}: {e}")
        return pd.DataFrame(columns=['EIN','NAME', 'STREET', 'CITY', 'STATE', 'ZIP', 'NTEE_CD'])

def ingest_bmf() -> pd.DataFrame:
    """Download all states BMF, normalize into Funder model, save Parquet"""
    all_dfs = []
    for state in STATES:
        df_state = download_bmf_state(state)
        all_dfs.append(df_state)
        logger.info(f"BMF {state.upper()} loaded: {df_state.shape[0]} rows")

    bmf_df = pd.concat(all_dfs, ignore_index=True)
    logger.info(f"All states BMF combined: {bmf_df.shape[0]} rows")

    # Normalize into Funder model
    normalized_rows = []
    for _, row in bmf_df.iterrows():
        try:
            funder = Funder(
                ein=row['EIN'].zfill(9),
                name=row['NAME'],
                street=row.get('STREET'),
                city=row.get('CITY'),
                state=row.get('STATE'),
                zip=row.get('ZIP'),
                ntee_code=row.get('NTEE_CD')
            )
            # setup validation
            validate_row(funder)
            normalized_rows.append(funder.model_dump())
        except Exception as e:
            logger.error(f"EIN={row.get('EIN')} | Error={str(e)}")

    df_norm = pd.DataFrame(normalized_rows)
    output_dir = os.path.join("datasets", "bmf", "normalized")
    os.makedirs(output_dir, exist_ok=True)

    # Save parquet
    output_file = os.path.join(output_dir, "bmf_all_states.parquet")
    df_norm.to_parquet(output_file, index=False)    
    logger.info(f"BMF ingestion complete: {df_norm.shape[0]} normalized rows")
    return df_norm

if __name__ == "__main__":
    df_bmf = ingest_bmf()
    print(f"BMF ingestion done: {df_bmf.shape}")
