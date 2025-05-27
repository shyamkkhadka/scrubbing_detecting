#!/bin/bash

# File containing the list of prefixes (one per line)
prefixes_file="prefixes.txt"

# Output file to save results
output_file="origin_asns.txt"

# Empty the output file before starting
> $output_file

# Loop through each prefix in the list
while IFS= read -r prefix; do
    echo "Querying origin ASN for $prefix..."
    
    # Query the IRR database using whois
    origin_asn=$(whois -h whois.radb.net "$prefix" | grep -i origin | awk '{print $2}')
    
    # Check if an origin ASN was found
    if [ -n "$origin_asn" ]; then
        echo "$prefix - Origin ASN: $origin_asn" >> $output_file
    else
        echo "$prefix - Origin ASN: Not found" >> $output_file
    fi

done < "$prefixes_file"

echo "Origin ASNs have been saved to $output_file"

