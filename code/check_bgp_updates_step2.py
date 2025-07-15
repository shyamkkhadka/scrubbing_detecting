# Check every 5 minutes BGP updates to see how many new prefixes were announced by a scrubber.
# 1. Find new prefixes originated. NOTE: Code borrowed from github_attack_2018.ipynb.
import pybgpstream
import pandas as pd
from datetime import datetime, timedelta, date
import csv
import os
import re

scrubber = "32787"
mon = "may"
year = "2025"

# dates = ["2025-09-08", "2024-09-15", "2024-09-22", "2024-09-29"]
# , "2025-09-01", "2024-09-09", "2024-09-15", "2024-02-22", "2024-02-29"] # For update files

# Generate list of date strings for May 2025
start_date = date(2025, 5, 25)
end_date = date(2025, 5, 26)

dates = []
current_date = start_date
while current_date <= end_date:
    dates.append(current_date.strftime("%Y-%m-%d"))
    current_date += timedelta(days=1)

INTERVAL_MINUTES = 60
path = "data/as" + scrubber + "_" + mon + "_" + year + "/"

for date in dates:

    df = pd.read_csv(path + "as_" + scrubber + "_originated_prefix_" + date + ".csv")
    prefixes = df["prefix"]
    update_time = []

    # Time setup
    start_time = datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S")  # 01 is done to make UTC time.
    end_time = start_time + timedelta(days=1)
    # Subtract 1 minute from end_time to make it 23:59:00
    end_time = end_time - timedelta(minutes=1)

    interval = timedelta(minutes=INTERVAL_MINUTES)

    current_time = start_time

    prefix_all_details = []  # List to store prefixes for throughout a day
    while current_time < end_time:
        from_time = int(current_time.timestamp())
        until_time = int((current_time + interval).timestamp())
        stream = pybgpstream.BGPStream(
            from_time=from_time,
            until_time=until_time,
            record_type="updates",
            project="ris",
            filter="path _" + scrubber + "$"
        )

        # stream.set_data_interface_option("broker", "cache-dir", "/home/shyam/jupy/cache")

        prefix_details = []  # For storing prefixes
        # Find paths from DDoS scrubber to route collectors
        for rec in stream.records():
            time = rec.time
            collector = rec.collector
            for elem in rec:
                pfx = elem.fields["prefix"]

                # Find upstream ASN in an AS path
                as_path = elem.fields["as-path"]
                as_path = as_path.split()
                orig = as_path[-1]

                # Store origin asn and announcement time in a dictionary
                asn_time = {}

                # Convert to UTC time
                time_utc = datetime.utcfromtimestamp(time)
                #             print("Prefix %s, Origin %s , time %s elem %s" %(pfx, orig, time, elem))

                # Convert UTC datetime to string
                time_utc_str = time_utc.strftime("%Y-%m-%d %H:%M:%S")
                asn_time["time_utc_str"] = time_utc_str
                asn_time["prefix"] = pfx

                prefix_details.append(asn_time)

                #     print("\n Finding new prefixes announced during that time")
        csv_file = path + 'as_' + scrubber + '_originated_prefix_' + date + '_' + str(
            until_time) + '.csv'  # Output file to store

        df = pd.read_csv(path + 'as_' + scrubber + '_originated_prefix_' + date + '.csv')
        prefixes_original = set(df["prefix"])  # Previously presented prefixes

        # Dictionary to hold unique prefixes with their first timestamp
        unique_prefixes = {}

        for entry in prefix_details:
            prefix = entry['prefix']
            timestamp = entry['time_utc_str']
            if prefix not in unique_prefixes and prefix not in prefixes_original:  # Store prefix if it is unique and not stored in previous timestamp.
                unique_prefixes[prefix] = timestamp

        # print("Unique prefixes are %s" %unique_prefixes)
        # Write to CSV if we find new prefix origniated from the scrubber
        if len(unique_prefixes) != 0:
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['prefix', 'time_utc_str'])  # Header
                for prefix, timestamp in unique_prefixes.items():
                    writer.writerow([prefix, timestamp])
            print(f"Data has been written to {csv_file} with number of new originated prefixes {len(unique_prefixes)}")
        print("Checked until %s" % until_time)
        current_time += interval  # Update time by interval
    print("Completed for %s." % date)

    # Now storing only the unique prefixes in a file
    print("Merging all the unique prefixes on %s in a single file.." % date)
    pattern = r"as_" + scrubber + "_originated_prefix_" + date + "_(\d)+.csv$"

    # List to hold dataframes
    dfs = []

    for filename in os.listdir(path):
        # Read only processed files
        if re.search(pattern, filename):
            # Read the CSV file and append the dataframe to the list
            df = pd.read_csv(path + filename)
            dfs.append(df)

            # Concatenate all DataFrames into a single one
            merged_df = pd.concat(dfs, ignore_index=True)
            merged_df.to_csv(path + 'as_' + scrubber + '_originated_prefix_merged_' + date + '.csv', index=False)
            unique_merged_prefixes = merged_df["prefix"].unique()
            print("Saved to a file with number of new prefixes on %s are %s and are %s" % (date,
                                                                                           len(unique_merged_prefixes),
                                                                                           unique_merged_prefixes))
