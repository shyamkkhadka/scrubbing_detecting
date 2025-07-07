import pandas as pd
from datetime import datetime, timedelta

start_date = datetime.strptime("2025-05-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-05-31", "%Y-%m-%d")

base_path = "as19905_may_2025"

for i in range((end_date - start_date).days + 1):
    current_date = start_date + timedelta(days=i)
    date_str = current_date.strftime("%Y-%m-%d")
    file_path = f"{base_path}/as_19905_originated_prefix_{date_str}.csv"

    try:
        df = pd.read_csv(file_path)
        total_prefix = df["prefix"].unique()
        print(f"{date_str}: {len(total_prefix)} unique prefixes")
    except FileNotFoundError:
        print(f"{date_str}: File not found.")
