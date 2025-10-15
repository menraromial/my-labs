#!/usr/bin/env python3
"""
Script pour convertir les fichiers JSON de métriques PowerCap en CSV.
Crée un fichier CSV par device_id pour chaque fichier JSON.
"""

import json
import csv
import os
from collections import defaultdict
from datetime import datetime

def json_to_csv(json_file):
    """
    Convertit un fichier JSON en fichiers CSV (un par device_id)
    
    Args:
        json_file: Chemin vers le fichier JSON
    """
    print(f"\n📂 Traitement de {os.path.basename(json_file)}...")
    
    # Charger le fichier JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"   ✅ {len(data)} entrées chargées")
    
    # Grouper les données par device_id
    devices_data = defaultdict(list)
    for entry in data:
        device_id = entry['device_id']
        devices_data[device_id].append(entry)
    
    print(f"   📊 {len(devices_data)} device(s) trouvé(s): {', '.join(devices_data.keys())}")
    
    # Nom de base du fichier (sans extension)
    base_name = os.path.splitext(json_file)[0]
    
    # Créer un CSV pour chaque device_id
    csv_files = []
    for device_id, entries in devices_data.items():
        # Nom du fichier CSV
        csv_file = f"{base_name}_{device_id}.csv"
        
        # Écrire le CSV
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # En-tête
            writer.writerow(['timestamp', 'device_id', 'value', 'value_abs'])
            
            # Données
            for entry in entries:
                writer.writerow([
                    entry['timestamp'],
                    entry['device_id'],
                    entry['value'],
                    abs(entry['value'])  # Valeur absolue (positive)
                ])
        
        csv_files.append(csv_file)
        print(f"   💾 {os.path.basename(csv_file)}: {len(entries)} mesures")
    
    return csv_files

def process_all_json_files(directory='.'):
    """
    Traite tous les fichiers JSON de métriques PowerCap dans le répertoire
    
    Args:
        directory: Répertoire contenant les fichiers JSON
    """
    print("="*80)
    print("📊 CONVERSION JSON → CSV")
    print("="*80)
    
    # Trouver tous les fichiers JSON de métriques PowerCap
    json_files = []
    for filename in os.listdir(directory):
        if filename.startswith('metrics_powercap_') and filename.endswith('.json'):
            json_files.append(os.path.join(directory, filename))
    
    json_files.sort()
    
    if not json_files:
        print("❌ Aucun fichier JSON de métriques trouvé")
        return
    
    print(f"\n✅ {len(json_files)} fichier(s) JSON trouvé(s)\n")
    
    all_csv_files = []
    for json_file in json_files:
        csv_files = json_to_csv(json_file)
        all_csv_files.extend(csv_files)
    
    print("\n" + "="*80)
    print("✅ CONVERSION TERMINÉE!")
    print("="*80)
    print(f"\n📊 {len(all_csv_files)} fichier(s) CSV créé(s):")
    for csv_file in all_csv_files:
        size_kb = os.path.getsize(csv_file) / 1024
        print(f"   • {os.path.basename(csv_file)} ({size_kb:.1f} KB)")
    print()

def main():
    """Fonction principale"""
    # Obtenir le répertoire du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Traiter tous les fichiers JSON
    process_all_json_files(script_dir)

if __name__ == "__main__":
    main()
