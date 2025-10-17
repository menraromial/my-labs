# Guide de Configuration des Machines

## 📋 Comment ajouter une nouvelle machine

### 1. Obtenir les informations de la machine

Sur Grid'5000, réservez un nœud et exécutez :
```bash
lscpu
free -g
cat /proc/cpuinfo | grep "model name" | head -1
```

### 2. Ajouter le profil dans `configs/machine_profiles.json`

```json
{
  "nom_cluster": {
    "cluster": "nom_cluster",
    "site": "nom_site",
    "cpu_threads": 128,           # Nombre total de threads logiques
    "cpu_cores": 64,              # Nombre de cœurs physiques
    "sockets": 2,                 # Nombre de sockets/packages
    "threads_per_core": 2,        # Threads par cœur (HT/SMT)
    "memory_gb": 512,             # RAM totale en GB
    "cpu_model": "Intel Xeon ...", # Modèle du CPU
    "cpu_base_mhz": 2600,         # Fréquence de base
    "cpu_max_mhz": 3400,          # Fréquence maximale
    "stress_cpu_threads": 128,    # Threads pour stress CPU
    "stress_vm_workers": 64,      # Workers pour stress mémoire
    "stress_vm_memory": "80%",    # % RAM à utiliser
    "cpu_method": "matrixprod"    # Méthode stress-ng
  }
}
```

### 3. Modifier le profil actif dans le notebook

Dans la cellule de configuration machine :
```python
ACTIVE_PROFILE = "nom_cluster"  # Changer cette ligne
```

Ou charger depuis le fichier JSON :
```python
import json
with open("configs/machine_profiles.json") as f:
    MACHINE_PROFILES = json.load(f)
ACTIVE_PROFILE = "nom_cluster"
machine_config = MACHINE_PROFILES[ACTIVE_PROFILE]
```

## 🎯 Paramètres de stress recommandés

### CPU Threads
- **Conservateur** : 75% des threads totaux
- **Normal** : 100% des threads totaux (recommandé)
- **Agressif** : 100% + oversubscription (non recommandé)

### VM Workers (stress mémoire)
- **Formule** : `cpu_cores / 2` à `cpu_cores`
- Pour chiroples (64 cores) : 32-64 workers

### VM Memory
- **Léger** : 50-60% de la RAM
- **Normal** : 70-80% (recommandé)
- **Intensif** : 85-90% (attention à l'OOM)

### CPU Method
- **matrixprod** : Multiplication de matrices (AVX2/AVX512)
- **fft** : Transformées de Fourier rapides
- **fibonacci** : Calculs récursifs
- **all** : Tous les tests (non recommandé pour mesures)

## 📊 Exemples de machines Grid'5000

| Cluster | Site | Threads | RAM | CPU Model |
|---------|------|---------|-----|-----------|
| chiroples | lille | 128 | 512GB | Xeon Platinum 8358 |
| parasilo | rennes | 96 | 384GB | Xeon Gold 6342 |
| grvingt | nancy | 40 | 192GB | Xeon Gold 5220R |
| gros | nancy | 72 | 384GB | Xeon Gold 6140 |
| grimoire | nancy | 48 | 192GB | Xeon E5-2680 v4 |

## 🔧 Scripts utiles

### Obtenir les infos CPU automatiquement
```bash
lscpu | grep -E "CPU\(s\)|Thread|Socket|Model name|MHz"
```

### Calculer les paramètres de stress
```python
cpu_threads = 128
cpu_cores = 64
sockets = 2

# Recommandations
stress_cpu_threads = cpu_threads  # Utiliser tous les threads
stress_vm_workers = cpu_cores // 2  # La moitié des cœurs
```

## ⚠️ Notes importantes

1. **Toujours vérifier** que `stress_cpu_threads <= cpu_threads`
2. **Tester progressivement** : commencer avec des valeurs conservatrices
3. **Monitorer** l'utilisation CPU/RAM pendant les tests
4. **Adapter** `stress_vm_memory` selon la RAM disponible
5. **Documenter** les résultats pour chaque machine

## 📝 Template vide

```json
{
  "nouveau_cluster": {
    "cluster": "",
    "site": "",
    "cpu_threads": 0,
    "cpu_cores": 0,
    "sockets": 0,
    "threads_per_core": 0,
    "memory_gb": 0,
    "cpu_model": "",
    "cpu_base_mhz": 0,
    "cpu_max_mhz": 0,
    "stress_cpu_threads": 0,
    "stress_vm_workers": 0,
    "stress_vm_memory": "70%",
    "cpu_method": "matrixprod"
  }
}
```
