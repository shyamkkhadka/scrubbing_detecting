import pandas as pd
from datetime import datetime, timedelta

scrubber = "19905"
start_date = datetime.strptime("2025-05-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-05-31", "%Y-%m-%d")

base_path = "as"+scrubber+"_may_2025"

for i in range((end_date - start_date).days + 1):
    current_date = start_date + timedelta(days=i)
    date_str = current_date.strftime("%Y-%m-%d")
    file_path = f"{base_path}/as_{scrubber}_transited_prefix_{date_str}.csv"

    try:
        df = pd.read_csv(file_path)
        total_prefix = df["prefix"].unique()
        print(len(total_prefix))
    except FileNotFoundError:
        print(f"{date_str}: File not found.")
