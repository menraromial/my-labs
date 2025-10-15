#!/usr/bin/env python3
"""
Script pour tracer les courbes de puissance de chirop-5
à partir des fichiers JSON de métriques PowerCap.

Les valeurs négatives dans les fichiers sont converties en positives.
Le graphique est dimensionné pour un article sur deux colonnes.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

def load_config_info(txt_file):
    """
    Charge les informations de configuration depuis le fichier txt
    Extrait UNE limite Package et UNE limite DRAM (pas de somme)
    
    Args:
        txt_file: Chemin vers le fichier de configuration
        
    Returns:
        dict: Informations extraites de la configuration
    """
    info = {
        'package_limit': None,
        'dram_limit': None
    }
    
    try:
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        
        current_zone = None
        in_dram = False
        
        for i, line in enumerate(lines):
            # Détecter les zones package
            if 'name: package-' in line:
                current_zone = 'package'
                in_dram = False
            elif 'name: dram' in line:
                in_dram = True
                current_zone = 'dram'
            
            # Extraire la première limite de puissance de chaque type
            if 'power_limit_uw:' in line and 'long_term' in lines[i-1]:
                value = int(line.split(':')[1].strip()) / 1e6  # Conversion en W
                if in_dram and info['dram_limit'] is None:
                    info['dram_limit'] = value
                elif current_zone == 'package' and info['package_limit'] is None:
                    info['package_limit'] = value
        
        print(f"   📋 Config: Package={info['package_limit']}W, DRAM={info['dram_limit']}W")
    except Exception as e:
        print(f"   ⚠️  Impossible de lire la config: {e}")
    
    return info

def plot_power_curves(data_files, config_files, output_file='chirop5_power_curves.pdf'):
    """
    Trace les courbes de puissance pour les trois expériences
    
    Args:
        data_files: Liste des fichiers JSON
        config_files: Liste des fichiers de configuration
        output_file: Nom du fichier de sortie
    """
    print(f"\n📊 Création du graphique de puissance pour chirop-5...")
    
    # Créer la figure avec 3 subplots (un par expérience)
    fig, axes = plt.subplots(3, 1, figsize=(7, 8), sharex=False)
    
    # Couleurs élégantes et contrastées
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    for idx, (data_file, config_file, color) in enumerate(zip(data_files, config_files, colors)):
        ax = axes[idx]
        
        # Charger les données
        timestamps, power_values = load_chirop5_data(data_file)
        config_info = load_config_info(config_file)
        
        # Convertir timestamps en secondes à partir du début
        time_seconds = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # Tracer la courbe de puissance avec style amélioré
        ax.plot(time_seconds, power_values, color=color, linewidth=1.8, 
                alpha=0.95, antialiased=True)
        
        # Préparer les labels pour la légende (sans tracer les lignes)
        legend_labels = []
        if config_info['package_limit']:
            legend_labels.append(f'Package: {config_info["package_limit"]:.0f}W')
        if config_info['dram_limit'] and config_info['dram_limit'] > 0:
            legend_labels.append(f'DRAM: {config_info["dram_limit"]:.0f}W')
        
        # Créer une légende personnalisée sans lignes visibles, centrée en bas
        if legend_labels:
            from matplotlib.patches import Patch
            legend_elements = [Patch(facecolor='none', edgecolor='none', label=label) for label in legend_labels]
            ax.legend(handles=legend_elements, loc='lower center', frameon=True, 
                     fontsize=9, ncol=len(legend_labels), fancybox=True, 
                     shadow=False, framealpha=0.95, edgecolor='#CCCCCC')
        
        # Configuration de l'axe avec style amélioré
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
    
    # Label X seulement sur le dernier subplot
    axes[-1].set_xlabel('Time (s)', fontsize=11, fontweight='normal', color='#333333')
    
    # Ajuster l'espacement
    plt.tight_layout(pad=1.5)
    
    # Sauvegarder en PDF (haute qualité pour article)
    plt.savefig(output_file, format='pdf', dpi=300, bbox_inches='tight')
    print(f"\n💾 Graphique sauvegardé: {output_file}")
    
    # Sauvegarder aussi en PNG pour prévisualisation
    png_file = output_file.replace('.pdf', '.png')
    plt.savefig(png_file, format='png', dpi=300, bbox_inches='tight')
    print(f"💾 Version PNG sauvegardée: {png_file}")
    
    # Afficher aussi le graphique
    plt.show()
    
    return fig, axes

def plot_combined_view(data_files, config_files, output_file='chirop5_power_combined.pdf'):
    """
    Trace toutes les courbes sur le même graphique pour comparaison
    
    Args:
        data_files: Liste des fichiers JSON
        config_files: Liste des fichiers de configuration
        output_file: Nom du fichier de sortie
    """
    print(f"\n📊 Création du graphique combiné...")
    
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    # Couleurs élégantes et contrastées
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    all_configs = []
    
    for idx, (data_file, config_file, color) in enumerate(zip(data_files, config_files, colors)):
        timestamps, power_values = load_chirop5_data(data_file)
        config_info = load_config_info(config_file)
        all_configs.append(config_info)
        
        # Normaliser le temps à partir de 0
        time_seconds = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        ax.plot(time_seconds, power_values, color=color, linewidth=1.8, 
                alpha=0.95, antialiased=True)
    
    # Créer une légende avec les informations de configuration et les couleurs des courbes
    from matplotlib.lines import Line2D
    legend_elements = []
    
    for idx, (config_info, color) in enumerate(zip(all_configs, colors)):
        if config_info['package_limit']:
            label = f'Package: {config_info["package_limit"]:.0f}W'
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
    
    # Légende avec les configurations
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                 fontsize=9, fancybox=True, shadow=False, framealpha=0.95, 
                 edgecolor='#CCCCCC')
    
    plt.tight_layout(pad=1.2)
    
    # Sauvegarder
    plt.savefig(output_file, format='pdf', dpi=300, bbox_inches='tight')
    print(f"💾 Graphique combiné sauvegardé: {output_file}")
    
    png_file = output_file.replace('.pdf', '.png')
    plt.savefig(png_file, format='png', dpi=300, bbox_inches='tight')
    print(f"💾 Version PNG sauvegardée: {png_file}")
    
    plt.show()
    
    return fig, ax

def main():
    """Fonction principale"""
    print("="*80)
    print("📈 TRACÉ DES COURBES DE PUISSANCE - chirop-5")
    print("="*80)
    
    # Répertoire des données
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Fichiers à traiter (0001, 0002, 0003)
    data_files = [
        os.path.join(data_dir, 'metrics_powercap_lille_chirop_0001.json'),
        os.path.join(data_dir, 'metrics_powercap_lille_chirop_0002.json'),
        os.path.join(data_dir, 'metrics_powercap_lille_chirop_0003.json')
    ]
    
    config_files = [
        os.path.join(data_dir, 'id_0001.txt'),
        os.path.join(data_dir, 'id_0002.txt'),
        os.path.join(data_dir, 'id_0003.txt')
    ]
    
    # Vérifier que les fichiers existent
    for f in data_files + config_files:
        if not os.path.exists(f):
            print(f"❌ Fichier manquant: {f}")
            return
    
    print(f"\n✅ Tous les fichiers trouvés\n")
    
    # Créer les graphiques
    print("\n" + "="*80)
    print("1️⃣  Graphiques séparés (3 subplots)")
    print("="*80)
    fig1, axes1 = plot_power_curves(data_files, config_files, 
                                     output_file='chirop5_power_separate.pdf')
    
    print("\n" + "="*80)
    print("2️⃣  Graphique combiné (comparaison)")
    print("="*80)
    fig2, ax2 = plot_combined_view(data_files, config_files,
                                    output_file='chirop5_power_combined.pdf')
    
    print("\n" + "="*80)
    print("✅ TRACÉ TERMINÉ AVEC SUCCÈS!")
    print("="*80)
    print(f"""
📊 Fichiers générés:
   • chirop5_power_separate.pdf (3 subplots)
   • chirop5_power_separate.png
   • chirop5_power_combined.pdf (vue combinée)
   • chirop5_power_combined.png

📐 Format: Adapté pour article deux colonnes
🎨 Résolution: 300 DPI
📏 Largeur: ~7 inches (adapté IEEE two-column)
    """)

if __name__ == "__main__":
    main()
