#!/usr/bin/env python3
"""
Script simple pour convertir rapidement JSON metrics → CSV
Usage: python3 json_to_csv_simple.py fichier.json
"""

import json
import csv
import sys
import os
from collections import defaultdict

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 json_to_csv_simple.py <fichier.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Charger JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Grouper par device_id
    devices = defaultdict(list)
    for record in data:
        if 'device_id' in record and 'timestamp' in record and 'value' in record:
            devices[record['device_id']].append({
                'timestamp': record['timestamp'],
                'power_watt': record['value']
            })
    
    # Créer les CSV
    os.makedirs('csv_output', exist_ok=True)
    
    for device_id, records in devices.items():
        filename = f"csv_output/{device_id}_power_metrics.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'power_watt'])
            writer.writeheader()
            writer.writerows(sorted(records, key=lambda x: x['timestamp']))
        
        print(f"✅ {filename} créé ({len(records)} enregistrements)")

if __name__ == "__main__":
    main()