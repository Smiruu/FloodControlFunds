import os
import requests
from time import sleep

BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf/p05/"
SAVE_DIR = "chirps_data"
os.makedirs(SAVE_DIR, exist_ok=True)

years = range(2020, 2026)   # adjust as needed
months = range(1, 13)

def download_file(url, file_path, retries=5):
    """Download file with retries."""
    attempt = 0
    while attempt < retries:
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):  # 1 MB chunks
                        if chunk:
                            f.write(chunk)
            print(f"✅ Downloaded: {file_path}")
            return
        except Exception as e:
            attempt += 1
            print(f"⚠️ Error downloading {url}: {e} (attempt {attempt}/{retries})")
            sleep(5)  # wait before retry
    print(f"❌ Failed after {retries} attempts: {url}")

for year in years:
    for month in months:
        file_name = f"chirps-v2.0.{year}.{month:02d}.days_p05.nc"
        file_path = os.path.join(SAVE_DIR, file_name)
        if os.path.exists(file_path):
            print(f"Already exists: {file_path}")
            continue

        url = f"{BASE_URL}{file_name}"
        print(f"Downloading {file_name}...")
        download_file(url, file_path)
