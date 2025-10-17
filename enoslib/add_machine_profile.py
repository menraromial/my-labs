#!/usr/bin/env python3
"""
Script pour ajouter automatiquement un profil de machine depuis lscpu
Usage: python3 add_machine_profile.py <cluster_name> <site_name>
"""

import sys
import subprocess
import json
from pathlib import Path

def get_cpu_info():
    """Récupère les infos CPU depuis lscpu"""
    result = subprocess.run(['lscpu'], capture_output=True, text=True)
    info = {}
    
    for line in result.stdout.split('\n'):
        if 'CPU(s):' in line and 'NUMA' not in line and 'On-line' not in line:
            info['cpu_threads'] = int(line.split(':')[1].strip())
        elif 'Thread(s) per core:' in line:
            info['threads_per_core'] = int(line.split(':')[1].strip())
        elif 'Core(s) per socket:' in line:
            info['cores_per_socket'] = int(line.split(':')[1].strip())
        elif 'Socket(s):' in line:
            info['sockets'] = int(line.split(':')[1].strip())
        elif 'Model name:' in line:
            info['cpu_model'] = line.split(':')[1].strip()
        elif 'CPU max MHz:' in line:
            info['cpu_max_mhz'] = int(float(line.split(':')[1].strip()))
        elif 'CPU min MHz:' in line:
            info['cpu_min_mhz'] = int(float(line.split(':')[1].strip()))
    
    info['cpu_cores'] = info['cores_per_socket'] * info['sockets']
    
    return info

def get_memory_info():
    """Récupère les infos mémoire depuis free"""
    result = subprocess.run(['free', '-g'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    mem_line = lines[1]
    memory_gb = int(mem_line.split()[1])
    return memory_gb

def create_profile(cluster_name, site_name, cpu_info, memory_gb):
    """Crée un profil de machine"""
    # Calculs automatiques pour le stress
    stress_cpu_threads = cpu_info['cpu_threads']
    stress_vm_workers = cpu_info['cpu_cores'] // 2
    
    # Ajuster la mémoire selon la RAM disponible
    if memory_gb >= 500:
        stress_vm_memory = "80%"
    elif memory_gb >= 300:
        stress_vm_memory = "75%"
    else:
        stress_vm_memory = "70%"
    
    profile = {
        "cluster": cluster_name,
        "site": site_name,
        "cpu_threads": cpu_info['cpu_threads'],
        "cpu_cores": cpu_info['cpu_cores'],
        "sockets": cpu_info['sockets'],
        "threads_per_core": cpu_info['threads_per_core'],
        "memory_gb": memory_gb,
        "cpu_model": cpu_info.get('cpu_model', 'Unknown'),
        "cpu_base_mhz": cpu_info.get('cpu_min_mhz', 2000),
        "cpu_max_mhz": cpu_info.get('cpu_max_mhz', 3000),
        "stress_cpu_threads": stress_cpu_threads,
        "stress_vm_workers": stress_vm_workers,
        "stress_vm_memory": stress_vm_memory,
        "cpu_method": "matrixprod"
    }
    
    return profile

def add_to_config(cluster_name, profile):
    """Ajoute le profil au fichier de configuration"""
    config_file = Path(__file__).parent / "configs" / "machine_profiles.json"
    
    # Charger la config existante
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {}
    
    # Ajouter le nouveau profil
    config[cluster_name] = profile
    
    # Sauvegarder
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Profil '{cluster_name}' ajouté à {config_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 add_machine_profile.py <cluster_name> <site_name>")
        print("Exemple: python3 add_machine_profile.py chiroples lille")
        sys.exit(1)
    
    cluster_name = sys.argv[1]
    site_name = sys.argv[2]
    
    print(f"🔍 Détection des caractéristiques de la machine...")
    print("")
    
    # Récupérer les infos
    cpu_info = get_cpu_info()
    memory_gb = get_memory_info()
    
    # Créer le profil
    profile = create_profile(cluster_name, site_name, cpu_info, memory_gb)
    
    # Afficher le résumé
    print("📊 Profil détecté :")
    print("="*80)
    print(f"Cluster        : {profile['cluster']}")
    print(f"Site           : {profile['site']}")
    print(f"CPU Threads    : {profile['cpu_threads']}")
    print(f"CPU Cores      : {profile['cpu_cores']}")
    print(f"Sockets        : {profile['sockets']}")
    print(f"Threads/Core   : {profile['threads_per_core']}")
    print(f"Memory         : {profile['memory_gb']} GB")
    print(f"CPU Model      : {profile['cpu_model']}")
    print(f"CPU Freq       : {profile['cpu_base_mhz']}-{profile['cpu_max_mhz']} MHz")
    print("")
    print("Stress Config  :")
    print(f"  CPU Threads  : {profile['stress_cpu_threads']}")
    print(f"  VM Workers   : {profile['stress_vm_workers']}")
    print(f"  VM Memory    : {profile['stress_vm_memory']}")
    print(f"  CPU Method   : {profile['cpu_method']}")
    print("="*80)
    print("")
    
    # Demander confirmation
    response = input("Ajouter ce profil à la configuration ? (y/n): ")
    if response.lower() == 'y':
        add_to_config(cluster_name, profile)
        print("")
        print("✅ Profil ajouté avec succès !")
        print("")
        print("Pour l'utiliser dans le notebook :")
        print(f"  ACTIVE_PROFILE = '{cluster_name}'")
    else:
        print("❌ Opération annulée")

if __name__ == "__main__":
    main()
