import pandas as pd
import requests, zipfile, io, os, logging

# Setup logger
os.makedirs("ingest_logs", exist_ok=True)
logger = logging.getLogger("irs_990_ingest")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("ingest_logs/990_errors.log")
fh.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

YEARS = list(range(2012, 2025))  # 2012-2024

def validate_ein(ein: str) -> bool:
    """Check if EIN is 9 digits."""
    return ein is not None and ein.isdigit() and len(ein) == 9

def download_and_extract_990(year: int) -> pd.DataFrame:
    """Download IRS 990 CSV or DAT ZIP for the given year and extract EINs only."""
    
    urls = [
        f"https://www.irs.gov/pub/irs-soi/{str(year)[-2:]}eoextract990.zip",   # CSV
        f"https://www.irs.gov/pub/irs-soi/{str(year)[-2:]}eofinextract990.zip" # DAT
    ]
    
    for url in urls:
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()  # <-- This ensures 404 or 500 triggers an exception
            z = zipfile.ZipFile(io.BytesIO(r.content))
            print(f"{year}: Found files in ZIP -> {z.namelist()}")

            # zip can have dat or CSV file
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            dat_files = [f for f in z.namelist() if f.endswith(".dat")]

            if csv_files:
                file_name = csv_files[0]
                df = pd.read_csv(z.open(file_name), dtype=str)
            elif dat_files:
                file_name = dat_files[0]
                try:
                    df = pd.read_fwf(z.open(file_name), colspecs=[(0,9)], names=['EIN'], dtype=str)
                    df['EIN'] = df['EIN'].str.strip()
                except Exception:
                    df = pd.read_csv(z.open(file_name), sep=r"\s+", header=None, names=['EIN'], dtype=str)
                    df['EIN'] = df['EIN'].str.strip()
            else:
                raise ValueError("No CSV or DAT file found in ZIP")
            
            # normalize column names
            df.columns = df.columns.str.upper()  
            if 'EIN' not in df.columns:
                logger.error(f"EIN column missing for IRS 990 {year}")
                return pd.DataFrame(columns=['EIN'])

            df = df[['EIN']]

            # Make sure EIN is string of digits only
            df['EIN'] = df['EIN'].astype(str).str.strip()

            # Validate EINs (must be 9 digits)
            valid_mask = df['EIN'].apply(validate_ein)
            df = df[valid_mask]

            return df.reset_index(drop=True)

        except requests.HTTPError as e:
            logger.warning(f"{year}: HTTP error {e} at {url}, trying next URL...")
            continue  # try next URL
        except Exception as e:
            logger.warning(f"{year}: Failed to download/extract from {url}: {e}, trying next URL...")
            continue  # try next URL

    # If all URLs fail
    logger.error(f"All attempts failed for IRS 990 {year}")
    return pd.DataFrame(columns=['EIN'])


def ingest_irs_990() -> None:
    """Ingest IRS 990 files for all years and save EIN-only Parquet files year by year."""
    output_dir = os.path.join("datasets", "irs_990", "normalized")
    os.makedirs(output_dir, exist_ok=True)

    for year in YEARS:
        df_990 = download_and_extract_990(year)
        output_file = os.path.join(output_dir, f"irs_990_{year}.parquet")
        try:
            if(df_990.shape[0] > 0):
                df_990.to_parquet(output_file, index=False)
            logger.info(f"IRS 990 {year} saved: {df_990.shape[0]} valid EINs (overwrite if exists)")
            print(f"Year {year} processed, saved {df_990.shape[0]} EINs.")
        except Exception as e:
            logger.error(f"Failed to save IRS 990 parquet for {year}: {e}")
            print(f"Failed to save IRS 990 parquet for {year}: {e}")

if __name__ == "__main__":
    ingest_irs_990()
    print("IRS 990 ingestion complete for all years.")
