# Artifacts of the paper "Detecting and Characterizing DDoS Scrubbing from Global BGP Routing: Insights from Five Leading Scrubbers" accepted in Passive and Active Measurement Conference (PAM) 2026.
## Descripiton of main files
- step1_process_raw_bgp_data.py: Find origin, provider, prefix, its length and version from raw data generated using bgpreader.
- step2_check_bgp_updates.py: Checks how many new prefixes were announced by a scrubber.
- step3_find_unique_prefix.py: Merge each time slots originated prefixes into one.
- step4_check_origin_asn_next_day.py: Check the originator of those prefixes for the next day using RIBs record except the scrubber.
- step4_check_provider_asn_asn_next_day.py: # Check the provider of those prefixes for the next day using RIBs record except the scrubber.
- always-on.ipynb: Find always-on protected prefixes.
- bogons.ipynb: Check bogons from team-cymru.
 check_bgp_updates_transiting_prefix.py: Find the new prefixes that have different upstream than a scrubber in a day.
- check_origin_asn_next_day.py:  Checks the originator of those prefixes for the next day using RIBs record except the scrubber.
 roa.ipynb: Checks RoA records.


