# Check the provider of those prefixes for the next day using RIBs record except the scrubber
import pybgpstream
import pandas as pd
from datetime import datetime, timedelta
import csv
import re
import os
import glob

scrubber = "198949"
mon = "may"
year = "2025"

path = "/data/shared_dir/scrubber_activation/as"+scrubber+"_"+mon+"_"+year+"/"

# Define start and end dates
start_date = datetime.strptime("2025-05-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-05-30", "%Y-%m-%d")

# Regex pattern to extract dates from filenames containing 'merged'
pattern = re.compile(r".*transited_prefix_merged_(\d{4}-\d{2}-\d{2})\.csv")

# Get filenames matching the pattern
cur_dates = []
for filename in os.listdir(path):
    match = pattern.match(filename)
    if match:
        cur_dates.append(match.group(1))

# Sort the extracted dates
cur_dates = sorted(cur_dates)
#cur_dates = ["2025-05-04", "2025-05-13","2025-05-14", "2025-05-28"]

# Generate next_dates (+1 day)
next_dates = [
    (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    for date in cur_dates
]

# cur_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end_date - start_date).days + 1)]
# next_dates = [(start_date + timedelta(days=i+1)).strftime("%Y-%m-%d") for i in range((end_date - start_date).days + 1)]

for idx, date in enumerate(cur_dates):
    cur_date = cur_dates[idx]
    next_date = next_dates[idx]
    start_time = datetime.strptime(f"{next_date} 00:00:00", "%Y-%m-%d %H:%M:%S")

    df = pd.read_csv(path + 'as_' + scrubber + '_transited_prefix_merged_' + cur_date + '.csv')
    prefixes = df["prefix"].unique()
    for idx_prefix, prefix in enumerate(prefixes):
        stream = pybgpstream.BGPStream(
            from_time=str(start_time) + " UTC",
            until_time=str(start_time) + " UTC",
            record_type="ribs",
            project="ris",
            # filter="prefix exact " + prefix
            filter="prefix less " + prefix

        )
        stream.set_data_interface_option("broker", "cache-dir", "/data/shared_dir/scrubber_activation/cache")

        prefix_provider_asns = []  # For storing prefixes and their origin ASNs
        siblings_map = {
            "32787": ["35994", "16625", "36183", "12222", "31984", "17204", "26008",
                        "18717", "393234", "393560", "33047", "23454", "36029", "18680",
                        "17334", "22207", "16702", "23455", "22452", "30675", "20189",
                        "35993"],  # Akamai
            "13335": ["209242", "395747", "14789", "394536", "132892"],  # Cloudflare
            "19905": ["12008", "19911", "397224", "399163", "399156", "397219", "399169", "399170",
                        "399164", "397233", "399167", "397229", "397239", "397222", "397235", "397243",
                        "399161", "399165", "397232", "397238", "397215", "397223", "399168", "397225",
                        "399155", "397218", "397221", "399158", "397237", "399154", "397213", "399159",
                        "399153", "397220", "397226", "399160", "399157", "397231", "397227", "397241",
                        "397234", "399173", "397240", "397228", "397214", "399177", "397230", "22701",
                        "399171", "397216", "397242", "399180", "399162", "399179", "397236", "399176",
                        "399172", "399175", "399151", "399166", "397217", "399178", "399152", "399174"
                        ],  # Vercara

            "19551": [],  # Imperva
            "198949": ["48851", "213232", "25773"],  # Radware
            "25773": ["48851", "213232", "198949"],  # Radware
            "35280": ["43767", "55002"],  # F5
            "20052": [],  # Arbour Network (Netscout) # No prefixes registered in RPKI TALs
            "10690": []
        }
        siblings = siblings_map.get(scrubber, [])

        print("Checking provider of prefix %s" % prefix)
        # Find paths from DDoS scrubber to route collectors
        for rec in stream.records():
            time = rec.time
            collector = rec.collector
            for elem in rec:
                pfx = elem.fields["prefix"]
                mask_len = int(pfx.split('/')[1])

                # Find upstream ASN in an AS path
                as_path = elem.fields["as-path"]
                as_path = as_path.split()
                orig = as_path[-1]
                if len(as_path) >= 2:
                    provider = as_path[-2]
                else:
                    provider = scrubber # Instead of None, it is done to ensure that provider != scrubber

                # Store origin asn and announcement time in a dictionary
                asn_time = {"origin": orig, "prefix": pfx}

                if provider != scrubber: #and orig not in siblings and provider not in siblings and pfx != '0.0.0.0/0' and pfx != '::/0':
                    asn_time["origin"] = orig
                    asn_time["provider"] = provider

                    # Convert to UTC time
                    #                 print("Prefix %s,AS19905 Origin %s , time %s elem %s" %(pfx, orig, time, elem))

                    asn_time["prefix"] = pfx

                    asn_time["scrubber_transited_prefix"] = prefix  # The Scrubber transited_prefix

                    # print("Provider is different than %s for  %s." % (scrubber, asn_time))
                    prefix_provider_asns.append(asn_time)

        # print("Prefix origin list is %s ." % prefix_provider_asns)

        if len(prefix_provider_asns) > 0:
            # Remove duplicates by converting list of dicts to a set of tuples, then back
            unique_prefix_provider_asns = list(
                {(d['origin'], d['provider'], d['prefix'], d['scrubber_transited_prefix']) for d in prefix_provider_asns})
            unique_dicts = [
                {'origin': origin, 'provider' : provider, 'prefix': prefix, 'scrubber_transited_prefix': scrubber_transited_prefix} for
                origin, provider, prefix, scrubber_transited_prefix in unique_prefix_provider_asns]

            # Changed filename from *_transited_prefix_origin_check_* to *_originated_prefix_origin_check_less_exact* to cover the cases of less specific prefix announcement.

            filename = path + 'as_' + scrubber + '_transited_prefix_origin_check_less_exact' + next_date + '_' + str(
                idx_prefix) + '.csv'

            # Write to CSV
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['origin', 'provider', 'prefix', 'scrubber_transited_prefix']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in unique_dicts:
                    writer.writerow(row)
            print(f"Results are stored in {filename}.")
        print("Done for prefix %s for next date %s." % (prefix, next_date))


print("\n Merging all the files into a single file.")

# Merge all the files of the format as_<scrubber>_transited_prefix_origin_check_<yyyy-mm-dd_idx> (e.g. as_13335_transited_prefix_origin_check_2025-05-02_1.csv)
# that were created by check_provider_asn_asn_next_day_step4_old.py 
# Then count the number of prefixes each day from the merged file. 

# List all files in path
all_files = glob.glob(os.path.join(path, "*"))

# Regex pattern
pattern = re.compile(r".*transited_prefix_origin_check_less_exact.*\.csv$")

# Filter only matching files
files = [f for f in all_files if pattern.match(os.path.basename(f))]

# Get only matching CSV files
files = [f for f in glob.glob(os.path.join(path, "*.csv")) if pattern.match(os.path.basename(f))]
merged_data = []

for file in files:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", file)
    if not match:
        continue
    date_str = match.group(1)
    # Read CSV
    df = pd.read_csv(file)

    # Drop duplicates for (origin, prefix)
    df_unique = df[["origin", "prefix"]].drop_duplicates()

    # Add date column
    df_unique.insert(0, "date", date_str)

    merged_data.append(df_unique)

# Merge & sort
final_df = pd.concat(merged_data, ignore_index=True)
final_df = final_df.sort_values(by=["date", "origin", "prefix"], ascending=[True, True, True])

# Save
final_df.to_csv(path + "as_"+scrubber+"_may_less_exact.csv", index=False)

print(f"Created 'as_"+scrubber+"_may_less_exact.csv' with {len(final_df)} rows.")


# Count unique prefixes per day from the final DataFrame
prefix_counts = final_df.groupby("date")["prefix"].nunique().reset_index(name="prefix_count")

# Generate full date range for May 2025
full_dates = pd.date_range("2025-05-01", "2025-05-31").strftime("%Y-%m-%d")

# Convert to DataFrame and merge
all_dates_df = pd.DataFrame({"date": full_dates})
prefix_counts_full = all_dates_df.merge(prefix_counts, on="date", how="left").fillna(0)

# Ensure count is integer
prefix_counts_full["prefix_count"] = prefix_counts_full["prefix_count"].astype(int)

# Print without index
print(prefix_counts_full["prefix_count"].to_string(index=False))

