#!/usr/bin/env python3
"""
Script simple pour tracer rapidement les courbes de puissance
Usage: python3 plot_simple.py [fichier.json]
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import sys
from collections import defaultdict

def main():
    # Fichier par défaut ou argument
    json_file = sys.argv[1] if len(sys.argv) > 1 else "metrics_paradoxe_8_9.json"
    
    print(f"📊 Tracé des courbes depuis: {json_file}")
    
    # Charger et organiser les données
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    devices = defaultdict(lambda: {'timestamps': [], 'power': []})
    
    for record in data:
        device_id = record.get('device_id')
        timestamp = record.get('timestamp')
        value = record.get('value')
        
        if device_id and timestamp and value is not None:
            devices[device_id]['timestamps'].append(pd.to_datetime(timestamp))
            devices[device_id]['power'].append(value)
    
    # Créer le graphique
    plt.figure(figsize=(12, 6))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (device_id, data) in enumerate(devices.items()):
        plt.plot(data['timestamps'], data['power'], 
                label=device_id, 
                color=colors[i % len(colors)], 
                linewidth=1.5, 
                alpha=0.8)
        
        print(f"   📈 {device_id}: {len(data['power'])} points")
    
    plt.xlabel('Temps')
    plt.ylabel('Puissance (Watts)')
    plt.title('Évolution de la Puissance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Sauvegarder
    output_file = "power_curves_simple.png"
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"💾 Graphique sauvegardé: {output_file}")
    
    # Statistiques simples
    print(f"\n📊 Résumé:")
    for device_id, data in devices.items():
        power = data['power']
        print(f"   {device_id}: {min(power):.1f}W - {max(power):.1f}W (moy: {sum(power)/len(power):.1f}W)")

if __name__ == "__main__":
    main()