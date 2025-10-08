
#!/bin/bash -e

# --- 1. Installation de Helm (si non présent) ---
if ! command -v helm &> /dev/null
then
    echo "Helm non trouvé. Installation de Helm..."
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
    chmod 700 get_helm.sh
    ./get_helm.sh
else
    echo "Helm est déjà installé."
fi

# --- 2. Ajout du dépôt Helm de Kepler ---
echo ""
echo "--- Ajout et mise à jour du dépôt Helm de Kepler ---"
helm repo add kepler https://sustainable-computing-io.github.io/kepler-helm-chart
helm repo update

# --- 3. Installation ou Mise à Jour de Kepler ---
echo ""
echo "--- Déploiement/Mise à jour de Kepler dans le namespace 'kepler' ---"
# CORRECTION : On utilise 'serviceMonitor.enabled=true'
helm upgrade --install kepler kepler/kepler --namespace kepler --create-namespace     --set serviceMonitor.enabled=true     --set service.type=NodePort

# --- 4. Vérification de l'installation ---
echo ""
echo "--- Attente des composants Kepler ---"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kepler -n kepler --timeout=300s

echo ""
echo "--- Vérification des pods Kepler ---"
kubectl get pods -n kepler

echo ""
echo "--- Vérification que le ServiceMonitor a bien été créé ---"
kubectl get servicemonitor -n kepler

echo "--- Vérification que le service est bien de type NodePort ---"
kubectl get service -n kepler

echo ""
echo "🎉 Kepler est maintenant correctement configuré avec un ServiceMonitor et un NodePort !"
