import pandas as pd

scrubber = "32787"
from datetime import date, timedelta

# Start and end dates for May 2025
start_date = date(2025, 5, 1)
end_date = date(2025, 5, 31)
current_date = start_date
while current_date <= end_date:
    df = pd.read_csv(path + 'optimized_raw_as' + scrubber + '_' + date_str + '.csv', low_memory=False)
    # Remove duplicate rows in dataframe
    df = df.drop_duplicates()
    # Find unique prefixes that the scrubber comes as a transit provider
    df2 = df.loc[df['provider'] == scrubber]
    unique_prefixes = df2["prefix"].unique()

    # Convert the numpy array of unique values to a DataFrame
    unique_prefixes_df = pd.DataFrame(unique_prefixes, columns=['prefix'])
    unique_prefixes_df['time'] = date_str

    # Save the unique values to a CSV file
    unique_prefixes_df.to_csv(path + 'as_' + scrubber + '_transited_prefix_' + date_str + '.csv', index=False)

    print(f"Done for {date_str}.")
    current_date += timedelta(days=1)

