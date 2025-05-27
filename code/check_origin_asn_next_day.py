# Check the originator of those prefixes for the next day using RIBs record except the scrubber
import pybgpstream
import pandas as pd
from datetime import datetime, timedelta
import csv

scrubber = "198949"
path = "/data/shared_dir/"

cur_dates = ["2024-01-01", "2024-01-22", "2024-01-29", "2024-02-01", "2024-02-08",  "2024-02-22",  "2024-02-29"]
next_dates =["2024-01-02", "2024-01-23", "2024-01-30", "2024-02-02", "2024-02-09",  "2024-02-23",  "2024-02-30"]

for idx, date in enumerate(cur_dates):
    cur_date = cur_dates[idx]
    next_date = next_dates[idx]
    start_time = datetime.strptime(f"{next_date} 00:00:00", "%Y-%m-%d %H:%M:%S")

    df = pd.read_csv(path + 'as_' + scrubber + '_originated_prefix_merged_' + cur_date + '.csv')
    prefixes = df["prefix"].unique()
    for prefix in prefixes:
        stream = pybgpstream.BGPStream(
            from_time=str(start_time) + " UTC",
            until_time=str(start_time) + " UTC",
            record_type="ribs",
            project="ris",
            filter="prefix exact " + prefix
            #filter="prefix less " + prefix
 
        )
        # stream.set_data_interface_option("broker", "cache-dir", "/home/shyam/jupy/cache")

        prefix_origin_asns = []  # For storing prefixes and their origin ASNs

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

                if orig != scrubber and pfx != '0.0.0.0/0' and pfx != '::/0' and orig != "209242":
                    asn_time["origin"] = orig

                    # Convert to UTC time
                    #                 print("Prefix %s, Origin %s , time %s elem %s" %(pfx, orig, time, elem))

                    asn_time["prefix"] = pfx
                    
                    asn_time["scrubber_originated_prefix"] = prefix # The Scrubber originated_prefix

                    print("Origin is different than %s for  %s." % (scrubber, asn_time))
                    prefix_origin_asns.append(asn_time)

       # print("Prefix origin list is %s ." % prefix_origin_asns)

        if len(prefix_origin_asns) > 0:
            # Remove duplicates by converting list of dicts to a set of tuples, then back
            unique_prefix_origin_asns = list({(d['origin'], d['prefix']) for d in prefix_origin_asns})
            unique_dicts = [{'origin': origin, 'prefix': prefix} for origin, prefix in unique_prefix_origin_asns]
            filename = path + 'as_' + scrubber + '_originated_prefix_origin_check_' + next_date + '_'+ str(idx) + '.csv'

            # Write to CSV
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['origin', 'prefix']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in unique_dicts:
                    writer.writerow(row)
            print(f"Results are stored in {filename}.")
        print("Done for prefix %s for next date %s." % (prefix, next_date))
print("\n Completed.")
