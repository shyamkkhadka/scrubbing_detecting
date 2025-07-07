# Check the originator of those prefixes for the next day using RIBs record except the scrubber
import pybgpstream
import pandas as pd
from datetime import datetime, timedelta
import csv
import re
import os

scrubber = "19905"
mon = "may"
year = "2025"

path = "as" + scrubber + "_" + mon + "_" + year + "/"

# Define start and end dates
start_date = datetime.strptime("2025-05-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-05-30", "%Y-%m-%d")

# Generate date lists
# Set your target directory path

# Regex pattern to extract dates from filenames containing 'merged'
pattern = re.compile(r".*merged_(\d{4}-\d{2}-\d{2})\.csv")

# Get filenames matching the pattern
cur_dates = []
for filename in os.listdir(path):
    match = pattern.match(filename)
    if match:
        cur_dates.append(match.group(1))

# Sort the extracted dates
cur_dates = sorted(cur_dates)

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

    df = pd.read_csv(path + 'as_' + scrubber + '_originated_prefix_merged_' + cur_date + '.csv')
    prefixes = df["prefix"].unique()
    for idx_prefix, prefix in enumerate(prefixes):
        stream = pybgpstream.BGPStream(
            from_time=str(start_time) + " UTC",
            until_time=str(start_time) + " UTC",
            record_type="ribs",
            project="ris",
            filter="prefix exact " + prefix
            # filter="prefix less " + prefix

        )
        stream.set_data_interface_option("broker", "cache-dir", "/home/shyam/scrubber_activation/cache")

        prefix_origin_asns = []  # For storing prefixes and their origin ASNs
        siblings_map = {
            "32787": ["35994", "16625", "36183", "12222", "31984", "17204", "26008",
                        "18717", "393234", "393560", "33047", "23454", "36029", "18680",
                        "17334", "22207", "16702", "23455", "22452", "30675", "20189",
                        "35993"],  # Akamai
            "13335": ["209242", "395747", "14789", "394536"],  # Cloudflare
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
            "198949": ["48851", "213232"],  # Radware
            "35280": ["43767"],  # F5
            "20052": [],  # Arbour Network (Netscout) # No prefixes registered in RPKI TALs
            "10690": []
        }
        siblings = siblings_map.get(scrubber, [])

        print("Checking origin of prefix %s" % prefix)
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
                asn_time = {"origin": orig, "prefix": pfx}

                if orig != scrubber and orig not in siblings and pfx != '0.0.0.0/0' and pfx != '::/0' and orig != "209242":
                    asn_time["origin"] = orig

                    # Convert to UTC time
                    #                 print("Prefix %s,AS19905 Origin %s , time %s elem %s" %(pfx, orig, time, elem))

                    asn_time["prefix"] = pfx

                    asn_time["scrubber_originated_prefix"] = prefix  # The Scrubber originated_prefix

                    print("Origin is different than %s for  %s." % (scrubber, asn_time))
                    prefix_origin_asns.append(asn_time)

        # print("Prefix origin list is %s ." % prefix_origin_asns)

        if len(prefix_origin_asns) > 0:
            # Remove duplicates by converting list of dicts to a set of tuples, then back
            unique_prefix_origin_asns = list(
                {(d['origin'], d['prefix'], d['scrubber_originated_prefix']) for d in prefix_origin_asns})
            unique_dicts = [
                {'origin': origin, 'prefix': prefix, 'scrubber_originated_prefix': scrubber_originated_prefix} for
                origin, prefix, scrubber_originated_prefix in unique_prefix_origin_asns]
            filename = path + 'as_' + scrubber + '_originated_prefix_origin_check_' + next_date + '_' + str(
                idx_prefix) + '.csv'

            # Write to CSV
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['origin', 'prefix', 'scrubber_originated_prefix']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in unique_dicts:
                    writer.writerow(row)
            print(f"Results are stored in {filename}.")
        print("Done for prefix %s for next date %s." % (prefix, next_date))
print("\n Completed.")
