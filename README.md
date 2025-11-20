# Artifacts of the paper "Detecting and Characterizing DDoS Scrubbing from Global BGP Routing: Insights from Five Leading Scrubbers" accepted in Passive and Active Measurement Conference (PAM) 2026.
## File descriptions inside code directory
- always-on.ipynb: Find always-on protected prefixes.
- bogons.ipynb: Check bogons from team-cymru.
- check_bgp_updates_step2.py: Checks how many new prefixes were announced by a scrubber.
- check_bgp_updates_transiting_prefix.py: Find the new prefixes that have different upstream than a scrubber in a day.
- check_origin_asn_next_day.py:  Checks the originator of those prefixes for the next day using RIBs record except the scrubber.
- process_raw_bgp_data_step1.py: Find origin, provider, prefix, its length and version from raw data generated using bgpreader.
- roa.ipynb: Checks RoA records.
- check_origin_asn_next_day_step4_old.py: Check the originator of those prefixes for the next day using RIBs record except the scrubber.
- check_provider_asn_asn_next_day_step4_old.py: # Check the provider of those prefixes for the next day using RIBs record except the scrubber.
- find_unique_prefix_step3.py: Merge each time slots originated prefixes into one.




