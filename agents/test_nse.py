import requests
import zipfile
import io
import pandas as pd
from datetime import datetime

date = datetime.now()

url = f"https://archives.nseindia.com/content/historical/EQUITIES/{date.strftime('%Y')}/{date.strftime('%b').upper()}/cm{date.strftime('%d%b%Y').upper()}bhav.csv.zip"

print("URL:", url)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com"
}

r = requests.get(url, headers=headers, timeout=20)
print("Status code:", r.status_code)

if r.status_code != 200:
    print("Blocked or not found")
    exit()

with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    name = z.namelist()[0]
    print("CSV file:", name)
    df = pd.read_csv(z.open(name))
    print(df.head())
    print("Columns:", df.columns.tolist())
