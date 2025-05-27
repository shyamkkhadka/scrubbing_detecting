# Program to find origin, provider, prefix, its length and version from raw data generated using bgpreader as 
# bgpreader -t ribs -w 1704153600,1704153600 -A _13335$ >> shared_dir/raw_as13335_02_jan_2024.txt
# Use python multicore programming feature
scrubber = "32787"
date = "2018-02-28"
# raw_as32787_2018-02-28.txt
#path = "/home/shyam/data/containers/storage/volumes/shared_dir/_data/"
path = "../data/"

import pandas as pd
import csv
from concurrent.futures import ProcessPoolExecutor

def process_chunk(lines):
    """Process a chunk of lines and extract prefix, AS path, and origin AS."""
    chunk_data = []
    for line in lines:
        fields = line.strip().split('|')
        if len(fields) > 12 and fields[1] == "R":
            try:
               # Extract prefix, AS path, and origin AS
                prefix = fields[9]
                as_path = fields[11].split()


                # Find provider here checking AS repetetitions and the same organization owning multiple ASes
#                 provider = find_immediate_provider(as_path)
                
                provider = as_path[-2] if len(as_path) > 1 else None  # The ASN before the origin AS
                origin_as = as_path[-1] if as_path else None
                
                pfx_len = int(prefix.split('/')[1]) if '/' in prefix else None
                ip_version = "IPv6" if ':' in prefix else "IPv4"

                # Append data to the chunk
                chunk_data.append([prefix, ' '.join(as_path), origin_as, provider, pfx_len, ip_version])
            
            except IndexError:
                continue
    return chunk_data

def process_route_data_parallel(file_path, output_file, num_workers=8, chunk_size=100000):
    with open(file_path, 'r') as file:
        lines = []
        
        # Initialize CSV output
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['prefix', 'as_path', 'origin_as', 'provider', 'pfx_len', 'ip_version'])

        # Process the file in chunks with multiple workers
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for line in file:
                lines.append(line)
                
                # When lines reach chunk size, process them
                if len(lines) >= chunk_size:
                    futures.append(executor.submit(process_chunk, lines))
                    lines = []

            # Process any remaining lines after the loop
            if lines:
                futures.append(executor.submit(process_chunk, lines))

            # Collect results from all futures and write to CSV
            for future in futures:
                chunk_data = future.result()
                if chunk_data:
                    df = pd.DataFrame(chunk_data, columns=['prefix', 'as_path', 'origin_as', 'provider', 'pfx_len', 'ip_version'])
                    df.to_csv(output_file, mode='a', header=False, index=False)

    print(f"Data successfully saved to {output_file}")

# Example usage
file_path = path + 'raw_as'+scrubber+'_'+date+'.txt'
output_file = path + 'optimized_raw_as'+scrubber+'_'+date+'.csv'
process_route_data_parallel(file_path, output_file)

df = pd.read_csv(path+'optimized_raw_as'+scrubber+'_'+date+'.csv', low_memory=False)
# Remove duplicate rows in dataframe
df = df.drop_duplicates()

# Find unique prefixes that the scrubber originates
df2 = df.loc[df['origin_as'] == int(scrubber)]
unique_prefixes = df2["prefix"].unique()

# Convert the numpy array of unique values to a DataFrame
unique_prefixes_df = pd.DataFrame(unique_prefixes, columns=['prefix'])
unique_prefixes_df['time'] = date

# Save the unique values to a CSV file
unique_prefixes_df.to_csv(path+'as_'+scrubber+'_originated_prefix_'+date+'.csv', index=False)
print("Completed.")
