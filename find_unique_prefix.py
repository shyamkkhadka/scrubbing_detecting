# Merge each time slots originated prefixes into one
import pandas as pd
import csv
import os
import re

scrubber = "13335"
path = "/data/shared_dir/"
DATE = "2024-05-01" # For update files
pattern = r"as_"+scrubber+"_originated_prefix_"+DATE+"_(\d)+.csv$" 


# List to hold dataframes
dfs = []

for filename in os.listdir(path):
    # Read only processed files
    if re.search(pattern, filename):
        #print(filename)
#         Read the CSV file and append the dataframe to the list
        df = pd.read_csv(path+filename)
        dfs.append(df)

# Concatenate all DataFrames into a single one
merged_df = pd.concat(dfs, ignore_index=True)
merged_df.to_csv(path + 'as_'+scrubber+'_originated_prefix_merged_'+DATE+'.csv', index=False)
unique_merged_prefixes = merged_df["prefix"].unique()
print("Saved to a file with number of new prefixes on %s are %s and are %s" %(DATE, len(unique_merged_prefixes), unique_merged_prefixes))
