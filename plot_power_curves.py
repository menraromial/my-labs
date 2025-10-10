#!/usr/bin/env python3
"""
Script pour tracer les courbes de puissance en fonction du temps
Utilise les fichiers CSV générés ou directement le JSON
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import argparse
import os
import glob
import sys

def load_data_from_json(json_file):
    """Charge les données depuis le fichier JSON et les organise par device"""
    print(f"📊 Chargement des données depuis {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Organiser par device_id
    devices_data = {}
    for record in data:
        device_id = record.get('device_id')
        timestamp = record.get('timestamp')
        value = record.get('value')
        
        if device_id and timestamp and value is not None:
            if device_id not in devices_data:
                devices_data[device_id] = {'timestamps': [], 'power_watts': []}
            
            devices_data[device_id]['timestamps'].append(pd.to_datetime(timestamp))
            devices_data[device_id]['power_watts'].append(value)
    
    return devices_data

def load_data_from_csv(csv_dir):
    """Charge les données depuis les fichiers CSV"""
    print(f"📊 Chargement des données depuis {csv_dir}")
    
    csv_files = glob.glob(os.path.join(csv_dir, "*_power_metrics.csv"))
    if not csv_files:
        print(f"❌ Aucun fichier CSV trouvé dans {csv_dir}")
        return {}
    
    devices_data = {}
    for csv_file in csv_files:
        # Extraire le device_id du nom de fichier
        filename = os.path.basename(csv_file)
        device_id = filename.replace('_power_metrics.csv', '')
        
        print(f"   📁 Lecture: {filename}")
        df = pd.read_csv(csv_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        devices_data[device_id] = {
            'timestamps': df['timestamp'].tolist(),
            'power_watts': df['power_watt'].tolist()
        }
    
    return devices_data

def create_power_plot(devices_data, output_file=None, title=None):
    """Crée le graphique de puissance"""
    # Style plus moderne
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Couleurs plus élégantes
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#8E44AD']
    
    for i, (device_id, data) in enumerate(devices_data.items()):
        color = colors[i % len(colors)]
        
        # Trier par timestamp
        sorted_data = sorted(zip(data['timestamps'], data['power_watts']))
        timestamps, power_watts = zip(*sorted_data)
        
        # Ligne plus fine et élégante
        ax.plot(timestamps, power_watts, 
                label=f'{device_id}', 
                color=color, 
                linewidth=1.0,  # Plus fin
                alpha=0.85,
                marker='o',      # Points sur la ligne
                markersize=1.5,  # Petits marqueurs
                markeredgewidth=0)
        
        print(f"   📈 {device_id}: {len(power_watts)} points, "
              f"{min(power_watts):.1f}W - {max(power_watts):.1f}W")
    
    # Configuration élégante du graphique
    ax.set_xlabel('Temps', fontsize=13, fontweight='bold')
    ax.set_ylabel('Puissance (Watts)', fontsize=13, fontweight='bold')
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    else:
        ax.set_title('Évolution de la Puissance par Device', fontsize=16, fontweight='bold', pad=20)
    
    # Légende plus élégante
    legend = ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=11)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.9)
    
    # Grille plus subtile
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Format des dates sur l'axe X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=10)
    plt.setp(ax.yaxis.get_majorticklabels(), fontsize=10)
    
    # Bordures plus nettes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    
    # Couleur de fond
    ax.set_facecolor('#FAFAFA')
    
    # Ajustement automatique
    plt.tight_layout()
    
    # Sauvegarder ou afficher
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"💾 Graphique sauvegardé: {output_file}")
    else:
        print("📊 Affichage du graphique...")
        plt.show()

def create_statistics_plot(devices_data, output_file=None):
    """Crée un graphique avec statistiques (moyenne mobile, min/max)"""
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))
    
    # Couleurs élégantes
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#8E44AD']
    
    # Graphique principal
    for i, (device_id, data) in enumerate(devices_data.items()):
        color = colors[i % len(colors)]
        
        # Créer DataFrame pour calculs
        df = pd.DataFrame({
            'timestamp': data['timestamps'],
            'power_watt': data['power_watts']
        }).sort_values('timestamp')
        
        # Moyenne mobile sur 30 secondes
        df['power_ma'] = df['power_watt'].rolling(window=30, center=True).mean()
        
        # Tracé principal - ligne fine
        ax1.plot(df['timestamp'], df['power_watt'], 
                label=f'{device_id}', color=color, alpha=0.5, linewidth=0.8)
        # Moyenne mobile - ligne plus épaisse
        ax1.plot(df['timestamp'], df['power_ma'], 
                color=color, linewidth=2.0, linestyle='-', alpha=0.9)
    
    ax1.set_ylabel('Puissance (Watts)', fontsize=12, fontweight='bold')
    ax1.set_title('Puissance avec Moyenne Mobile (30s)', fontsize=14, fontweight='bold', pad=15)
    
    # Légende élégante
    legend1 = ax1.legend(frameon=True, fancybox=True, shadow=True, fontsize=10)
    legend1.get_frame().set_facecolor('white')
    legend1.get_frame().set_alpha(0.9)
    
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax1.set_facecolor('#FAFAFA')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Graphique des différences
    device_ids = list(devices_data.keys())
    if len(device_ids) >= 2:
        device1, device2 = device_ids[0], device_ids[1]
        
        # Synchroniser les timestamps (prendre l'intersection)
        df1 = pd.DataFrame({
            'timestamp': devices_data[device1]['timestamps'],
            'power': devices_data[device1]['power_watts']
        })
        df2 = pd.DataFrame({
            'timestamp': devices_data[device2]['timestamps'],
            'power': devices_data[device2]['power_watts']
        })
        
        # Merge sur timestamp
        merged = pd.merge(df1, df2, on='timestamp', suffixes=('_1', '_2'))
        merged['diff'] = merged['power_1'] - merged['power_2']
        
        ax2.plot(merged['timestamp'], merged['diff'], 
                color='#E74C3C', linewidth=1.2, alpha=0.8, 
                marker='o', markersize=1.0, markeredgewidth=0)
        ax2.axhline(y=0, color='#34495E', linestyle='-', alpha=0.7, linewidth=1.0)
        ax2.set_ylabel('Différence (Watts)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Temps', fontsize=12, fontweight='bold')
        ax2.set_title(f'Différence de Puissance: {device1} - {device2}', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax2.set_facecolor('#FAFAFA')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Format des dates
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax2.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, fontsize=10)
    
    plt.tight_layout()
    
    if output_file:
        stats_file = output_file.replace('.png', '_stats.png')
        plt.savefig(stats_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"💾 Graphique statistiques sauvegardé: {stats_file}")
    else:
        plt.show()

def create_comparison_plot(devices_data, output_file=None):
    """Crée un graphique de comparaison avec histogrammes"""
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Couleurs élégantes
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#8E44AD']
    
    # 1. Courbes de puissance
    for i, (device_id, data) in enumerate(devices_data.items()):
        color = colors[i % len(colors)]
        ax1.plot(data['timestamps'], data['power_watts'], 
                label=device_id, color=color, linewidth=1.0, alpha=0.9,
                marker='o', markersize=1.0, markeredgewidth=0)
    
    ax1.set_ylabel('Puissance (Watts)', fontsize=11, fontweight='bold')
    ax1.set_title('Consommation de Puissance', fontsize=12, fontweight='bold', pad=10)
    
    # Légende élégante
    legend1 = ax1.legend(frameon=True, fancybox=True, shadow=True, fontsize=9)
    legend1.get_frame().set_facecolor('white')
    legend1.get_frame().set_alpha(0.9)
    
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax1.set_facecolor('#FAFAFA')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # 2. Histogrammes de distribution
    for i, (device_id, data) in enumerate(devices_data.items()):
        color = colors[i % len(colors)]
        ax2.hist(data['power_watts'], bins=30, alpha=0.7, label=device_id, 
                color=color, edgecolor='white', linewidth=0.5)
    
    ax2.set_xlabel('Puissance (Watts)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Fréquence', fontsize=11, fontweight='bold')
    ax2.set_title('Distribution de la Puissance', fontsize=12, fontweight='bold', pad=10)
    
    legend2 = ax2.legend(frameon=True, fancybox=True, shadow=True, fontsize=9)
    legend2.get_frame().set_facecolor('white')
    legend2.get_frame().set_alpha(0.9)
    
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax2.set_facecolor('#FAFAFA')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # 3. Box plots
    box_data = [data['power_watts'] for data in devices_data.values()]
    box_labels = list(devices_data.keys())
    
    bp = ax3.boxplot(box_data, tick_labels=box_labels, patch_artist=True, 
                     notch=True, showmeans=True, meanline=True)
    
    # Colorer les box plots
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor('#2C3E50')
        patch.set_linewidth(1.5)
    
    # Personnaliser autres éléments
    for element in ['whiskers', 'fliers', 'medians', 'caps']:
        plt.setp(bp[element], color='#2C3E50', linewidth=1.5)
    plt.setp(bp['means'], color='#E74C3C', linewidth=2)
    
    ax3.set_ylabel('Puissance (Watts)', fontsize=11, fontweight='bold')
    ax3.set_title('Statistiques par Appareil', fontsize=12, fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax3.set_facecolor('#FAFAFA')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # 4. Tableau de statistiques
    ax4.axis('off')
    stats_data = []
    for device_id, data in devices_data.items():
        power_data = data['power_watts']
        stats_data.append([
            device_id,
            f"{np.mean(power_data):.1f}",
            f"{np.median(power_data):.1f}",
            f"{np.std(power_data):.1f}",
            f"{np.min(power_data):.1f}",
            f"{np.max(power_data):.1f}"
        ])
    
    headers = ['Device', 'Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max']
    table = ax4.table(cellText=stats_data, colLabels=headers, loc='center',
                     cellLoc='center', bbox=[0, 0, 1, 1])
    
    # Style du tableau
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Colorer l'en-tête
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#34495E')
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(0, i)].set_height(0.15)
    
    # Colorer les lignes alternées
    for i in range(1, len(stats_data) + 1):
        color = '#ECF0F1' if i % 2 == 0 else 'white'
        for j in range(len(headers)):
            table[(i, j)].set_facecolor(color)
            table[(i, j)].set_height(0.12)
    
    ax4.set_title('Statistiques Détaillées', fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if output_file:
        comp_file = output_file.replace('.png', '_comparison.png')
        plt.savefig(comp_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"💾 Graphique comparaison sauvegardé: {comp_file}")
    else:
        plt.show()

def print_summary(devices_data):
    """Affiche un résumé des données"""
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES DONNÉES")
    print("="*60)
    
    for device_id, data in devices_data.items():
        power_watts = data['power_watts']
        timestamps = data['timestamps']
        
        print(f"\n🖥️  {device_id}:")
        print(f"   📈 Points de données: {len(power_watts)}")
        print(f"   ⚡ Puissance min: {min(power_watts):.2f}W")
        print(f"   ⚡ Puissance max: {max(power_watts):.2f}W")
        print(f"   ⚡ Puissance moyenne: {sum(power_watts)/len(power_watts):.2f}W")
        print(f"   🕐 Période: {min(timestamps)} → {max(timestamps)}")
        
        # Durée
        duration = max(timestamps) - min(timestamps)
        print(f"   ⏱️  Durée: {duration}")

def main():
    parser = argparse.ArgumentParser(description="Tracer les courbes de puissance")
    parser.add_argument('input', 
                       help="Fichier JSON ou répertoire CSV d'entrée",
                       nargs='?',
                       default="metrics_paradoxe_8_9.json")
    parser.add_argument('-o', '--output', 
                       help="Fichier de sortie PNG (optionnel)")
    parser.add_argument('-t', '--title',
                       help="Titre personnalisé pour le graphique")
    parser.add_argument('--stats', action='store_true',
                       help="Créer aussi un graphique avec statistiques")
    parser.add_argument('--comparison', action='store_true',
                       help="Créer aussi un graphique de comparaison complet")
    parser.add_argument('--csv-dir',
                       default="csv_output",
                       help="Répertoire des fichiers CSV (défaut: csv_output)")
    
    args = parser.parse_args()
    
    print(f"🚀 Génération des graphiques de puissance")
    
    # Déterminer le type d'entrée
    if args.input.endswith('.json') and os.path.isfile(args.input):
        devices_data = load_data_from_json(args.input)
    elif os.path.isdir(args.input):
        devices_data = load_data_from_csv(args.input)
    elif os.path.isdir(args.csv_dir):
        print(f"📁 Fichier JSON non trouvé, utilisation de {args.csv_dir}")
        devices_data = load_data_from_csv(args.csv_dir)
    else:
        print(f"❌ Entrée non trouvée: {args.input}")
        sys.exit(1)
    
    if not devices_data:
        print("❌ Aucune donnée trouvée")
        sys.exit(1)
    
    # Afficher le résumé
    print_summary(devices_data)
    
    # Créer le graphique principal
    print(f"\n📊 Création du graphique principal...")
    create_power_plot(devices_data, args.output, args.title)
    
    # Créer le graphique avec statistiques si demandé
    if args.stats:
        print(f"\n📈 Création du graphique avec statistiques...")
        create_statistics_plot(devices_data, args.output)
    
    # Créer le graphique de comparaison si demandé
    if args.comparison:
        print(f"\n🔍 Création du graphique de comparaison...")
        create_comparison_plot(devices_data, args.output)
    
    print(f"\n✅ Graphiques créés avec succès!")

if __name__ == "__main__":
    main()