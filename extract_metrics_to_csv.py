#!/usr/bin/env python3
"""
Script pour extraire les métriques JSON en fichiers CSV séparés par device_id.
Chaque device_id aura son propre fichier CSV avec les colonnes : timestamp, power_watt
"""

import json
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
import argparse

def load_json_data(json_file):
    """Charge les données depuis le fichier JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Chargé {len(data)} enregistrements depuis {json_file}")
        return data
    except FileNotFoundError:
        print(f"❌ Erreur: Fichier {json_file} introuvable")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        sys.exit(1)

def extract_and_group_data(data):
    """Groupe les données par device_id"""
    grouped_data = defaultdict(list)
    
    for record in data:
        device_id = record.get('device_id')
        timestamp = record.get('timestamp')
        value = record.get('value')
        
        # Vérification des champs requis
        if device_id and timestamp and value is not None:
            grouped_data[device_id].append({
                'timestamp': timestamp,
                'power_watt': value
            })
        else:
            print(f"⚠️  Enregistrement incomplet ignoré: {record}")
    
    return grouped_data

def write_csv_files(grouped_data, output_dir="output"):
    """Écrit un fichier CSV pour chaque device_id"""
    
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    summary = {}
    
    for device_id, records in grouped_data.items():
        # Nom du fichier CSV
        csv_filename = os.path.join(output_dir, f"{device_id}_power_metrics.csv")
        
        # Trier les enregistrements par timestamp
        records.sort(key=lambda x: x['timestamp'])
        
        # Écrire le fichier CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'power_watt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Écrire l'en-tête
            writer.writeheader()
            
            # Écrire les données
            writer.writerows(records)
        
        summary[device_id] = {
            'filename': csv_filename,
            'records': len(records),
            'first_timestamp': records[0]['timestamp'] if records else 'N/A',
            'last_timestamp': records[-1]['timestamp'] if records else 'N/A',
            'min_power': min(r['power_watt'] for r in records) if records else 'N/A',
            'max_power': max(r['power_watt'] for r in records) if records else 'N/A',
            'avg_power': sum(r['power_watt'] for r in records) / len(records) if records else 'N/A'
        }
        
        print(f"✅ Créé: {csv_filename} ({len(records)} enregistrements)")
    
    return summary

def print_summary(summary):
    """Affiche un résumé des fichiers créés"""
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DE L'EXTRACTION")
    print("="*80)
    
    for device_id, info in summary.items():
        print(f"\n🖥️  Device: {device_id}")
        print(f"   📁 Fichier: {info['filename']}")
        print(f"   📈 Enregistrements: {info['records']}")
        print(f"   🕐 Période: {info['first_timestamp']} → {info['last_timestamp']}")
        if isinstance(info['min_power'], (int, float)):
            print(f"   ⚡ Puissance: {info['min_power']:.2f}W - {info['max_power']:.2f}W (moy: {info['avg_power']:.2f}W)")
    
    print(f"\n✅ Total: {len(summary)} fichiers CSV créés")
    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description="Extraire les métriques JSON en fichiers CSV par device_id"
    )
    parser.add_argument(
        'json_file', 
        help="Fichier JSON d'entrée (par défaut: metrics_paradoxe_8_9.json)",
        nargs='?',
        default="metrics_paradoxe_8_9.json"
    )
    parser.add_argument(
        '-o', '--output-dir',
        default="csv_output",
        help="Répertoire de sortie pour les fichiers CSV (défaut: csv_output)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Mode verbeux"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Extraction des métriques de {args.json_file}")
    print(f"📁 Répertoire de sortie: {args.output_dir}")
    
    # 1. Charger les données JSON
    data = load_json_data(args.json_file)
    
    # 2. Grouper par device_id
    grouped_data = extract_and_group_data(data)
    print(f"📊 Devices trouvés: {list(grouped_data.keys())}")
    
    # 3. Écrire les fichiers CSV
    summary = write_csv_files(grouped_data, args.output_dir)
    
    # 4. Afficher le résumé
    print_summary(summary)
    
    print(f"\n🎉 Extraction terminée! Fichiers disponibles dans: {args.output_dir}/")

if __name__ == "__main__":
    main()