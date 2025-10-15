#!/usr/bin/env python3
"""
Script pour tracer les courbes de puissance de chirop-5
pour les expériences 0002, 0004, 0005 avec time windows dans la légende.

Graphique combiné uniquement.
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import os

# Configuration pour article scientifique (two-column format)
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (7, 4),
    'figure.dpi': 300,
    'lines.linewidth': 1.5,
    'axes.linewidth': 1.2,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linestyle': '-',
    'grid.linewidth': 0.8,
    'axes.facecolor': '#FAFAFA',
    'figure.facecolor': 'white',
    'axes.edgecolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'text.color': '#333333'
})

def load_chirop5_data(json_file):
    """
    Charge les données pour chirop-5 depuis un fichier JSON
    
    Args:
        json_file: Chemin vers le fichier JSON
        
    Returns:
        tuple: (timestamps, power_values) où les valeurs sont positives
    """
    print(f"📂 Chargement de {json_file}...")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    timestamps = []
    power_values = []
    
    for entry in data:
        if entry['device_id'] == 'chirop-5':
            # Convertir timestamp en datetime
            ts = datetime.fromisoformat(entry['timestamp'])
            timestamps.append(ts)
            
            # Convertir valeur négative en positive
            power_values.append(abs(entry['value']))
    
    print(f"   ✅ {len(timestamps)} mesures chargées")
    return timestamps, power_values

def load_timewindow_info(txt_file):
    """
    Charge le time window depuis le fichier txt
    
    Args:
        txt_file: Chemin vers le fichier de configuration
        
    Returns:
        dict: Time window en microsecondes et millisecondes
    """
    info = {
        'time_window_us': None,
        'time_window_ms': None
    }
    
    try:
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        
        in_package = False
        found_long_term = False
        
        # Chercher le time_window_us du premier package (long_term)
        for i, line in enumerate(lines):
            if 'name: package-0' in line:
                in_package = True
                continue
            
            if in_package and 'name: long_term' in line:
                found_long_term = True
                continue
            
            if found_long_term and 'time_window_us:' in line:
                time_us = int(line.split(':')[1].strip())
                info['time_window_us'] = time_us
                info['time_window_ms'] = time_us / 1000.0
                break
        
        if info['time_window_us']:
            print(f"   📋 Time Window: {info['time_window_us']} µs ({info['time_window_ms']:.1f} ms)")
        else:
            print(f"   ⚠️  Time Window non trouvé")
    except Exception as e:
        print(f"   ⚠️  Impossible de lire le time window: {e}")
    
    return info

def plot_timewindow_comparison(data_files, config_files, output_file='chirop5_timewindow_comparison.pdf'):
    """
    Trace les courbes de puissance pour comparaison des time windows
    
    Args:
        data_files: Liste des fichiers JSON
        config_files: Liste des fichiers de configuration
        output_file: Nom du fichier de sortie
    """
    print(f"\n📊 Création du graphique de comparaison des time windows...")
    
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    # Couleurs élégantes et contrastées (mêmes que l'autre script)
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    all_timewindows = []
    
    for idx, (data_file, config_file, color) in enumerate(zip(data_files, config_files, colors)):
        timestamps, power_values = load_chirop5_data(data_file)
        tw_info = load_timewindow_info(config_file)
        all_timewindows.append(tw_info)
        
        # Normaliser le temps à partir de 0
        time_seconds = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        ax.plot(time_seconds, power_values, color=color, linewidth=1.8, 
                alpha=0.95, antialiased=True)
    
    # Créer une légende avec les time windows et les couleurs des courbes
    from matplotlib.lines import Line2D
    legend_elements = []
    
    for idx, (tw_info, color) in enumerate(zip(all_timewindows, colors)):
        if tw_info['time_window_ms']:
            # Afficher en ms si < 1000ms, sinon en secondes
            if tw_info['time_window_ms'] < 1000:
                label = f'TW: {tw_info["time_window_ms"]:.1f} ms'
            else:
                label = f'TW: {tw_info["time_window_ms"]/1000:.2f} s'
            
            # Créer une ligne colorée pour la légende
            legend_elements.append(Line2D([0], [0], color=color, linewidth=3, label=label))
    
    # Configuration avec style amélioré
    ax.set_xlabel('Time (s)', fontsize=11, fontweight='normal', color='#333333')
    ax.set_ylabel('Power (W)', fontsize=11, fontweight='normal', color='#333333')
    ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.8, color='#CCCCCC')
    ax.set_facecolor('#FAFAFA')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    ax.spines['left'].set_color('#666666')
    ax.spines['bottom'].set_color('#666666')
    
    # Améliorer les ticks
    ax.tick_params(axis='both', which='major', labelsize=9, 
                  colors='#333333', width=1.2, length=4)
    
    # Commencer l'axe Y à 0
    ax.set_ylim(bottom=0)
    
    # Légende avec les time windows
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                 fontsize=9, fancybox=True, shadow=False, framealpha=0.95, 
                 edgecolor='#CCCCCC')
    
    plt.tight_layout(pad=1.2)
    
    # Sauvegarder
    plt.savefig(output_file, format='pdf', dpi=300, bbox_inches='tight')
    print(f"💾 Graphique sauvegardé: {output_file}")
    
    png_file = output_file.replace('.pdf', '.png')
    plt.savefig(png_file, format='png', dpi=300, bbox_inches='tight')
    print(f"💾 Version PNG sauvegardée: {png_file}")
    
    plt.show()
    
    return fig, ax

def main():
    """Fonction principale"""
    print("="*80)
    print("📈 TRACÉ DES COURBES DE PUISSANCE - chirop-5 (Time Windows)")
    print("="*80)
    
    # Répertoire des données
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Fichiers à traiter (0002, 0004, 0005)
    data_files = [
        os.path.join(data_dir, 'metrics_powercap_lille_chirop_0002.json'),
        os.path.join(data_dir, 'metrics_powercap_lille_chirop_0004.json'),
        os.path.join(data_dir, 'metrics_powercap_lille_chirop_0005.json')
    ]
    
    config_files = [
        os.path.join(data_dir, 'id_0002.txt'),
        os.path.join(data_dir, 'id_0004.txt'),
        os.path.join(data_dir, 'id_0005.txt')
    ]
    
    # Vérifier que les fichiers existent
    for f in data_files + config_files:
        if not os.path.exists(f):
            print(f"❌ Fichier manquant: {f}")
            return
    
    print(f"\n✅ Tous les fichiers trouvés\n")
    
    # Créer le graphique combiné
    print("\n" + "="*80)
    print("📊 Graphique de comparaison des Time Windows")
    print("="*80)
    fig, ax = plot_timewindow_comparison(data_files, config_files,
                                         output_file='chirop5_timewindow_comparison.pdf')
    
    print("\n" + "="*80)
    print("✅ TRACÉ TERMINÉ AVEC SUCCÈS!")
    print("="*80)
    print(f"""
📊 Fichiers générés:
   • chirop5_timewindow_comparison.pdf
   • chirop5_timewindow_comparison.png

📐 Format: Adapté pour article deux colonnes
🎨 Résolution: 300 DPI
📏 Largeur: ~7 inches (adapté IEEE two-column)

🔍 Expériences comparées:
   • 0002: Time Window package (long_term)
   • 0004: Time Window package (long_term)
   • 0005: Time Window package (long_term)
    """)

if __name__ == "__main__":
    main()
