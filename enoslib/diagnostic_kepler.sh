
#!/bin/bash

echo "======================================================================"
echo "🔍 DIAGNOSTIC COMPLET: Prometheus ↔ Kepler"
echo "======================================================================"

echo ""
echo "--- 1. Vérification des Pods Kepler ---"
kubectl get pods -n kepler -o wide

echo ""
echo "--- 2. Vérification du Service Kepler ---"
kubectl get svc -n kepler -o wide

echo ""
echo "--- 3. Vérification des Labels du Service Kepler ---"
echo "Les labels sont CRITIQUES pour que le ServiceMonitor fonctionne!"
kubectl get svc -n kepler -o yaml | grep -A 10 "labels:"

echo ""
echo "--- 4. Vérification du ServiceMonitor Kepler ---"
kubectl get servicemonitor -n kepler -o wide

echo ""
echo "--- 5. Détails du ServiceMonitor (selector et labels) ---"
kubectl get servicemonitor -n kepler -o yaml | grep -A 20 "selector:"

echo ""
echo "--- 6. Vérification que Prometheus-Operator voit le ServiceMonitor ---"
echo "Prometheus doit être dans le même namespace ou avec les bonnes règles RBAC"
kubectl get servicemonitor -A

echo ""
echo "--- 7. Configuration de Prometheus pour ServiceMonitor ---"
echo "Vérification des serviceMonitorSelector dans Prometheus:"
kubectl get prometheus -n monitoring -o yaml | grep -A 5 "serviceMonitorSelector:"

echo ""
echo "--- 8. Vérification des Endpoints Kepler ---"
echo "Si pas d'endpoints, le service ne pointe vers rien!"
kubectl get endpoints -n kepler

echo ""
echo "--- 9. Test direct du endpoint Kepler ---"
KEPLER_POD=`kubectl get pods -n kepler -l app.kubernetes.io/name=kepler -o jsonpath='{.items[0].metadata.name}'`
if [ -n "$KEPLER_POD" ]; then
    echo "Test de l'endpoint metrics sur le pod $KEPLER_POD:"
    kubectl exec -n kepler $KEPLER_POD -- curl -s localhost:9102/metrics | head -20
else
    echo "❌ Aucun pod Kepler trouvé!"
fi

echo ""
echo "--- 10. Vérification des Logs Prometheus ---"
echo "Recherche d'erreurs liées à Kepler dans les logs Prometheus:"
PROM_POD=`kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus -o jsonpath='{.items[0].metadata.name}'`
if [ -n "$PROM_POD" ]; then
    kubectl logs -n monitoring $PROM_POD -c prometheus --tail=50 | grep -i kepler || echo "Aucune mention de Kepler dans les logs récents"
else
    echo "❌ Pod Prometheus non trouvé!"
fi

echo ""
echo "--- 11. Configuration Actuelle des Targets Prometheus ---"
echo "Vérifiez si Kepler apparaît dans les targets de Prometheus"
echo "💡 Accédez à l'UI Prometheus: Status → Targets"
echo "💡 Ou utilisez l'API: curl http://prometheus-ip:port/api/v1/targets"

echo ""
echo "======================================================================"
echo "🎯 CAUSES COMMUNES ET SOLUTIONS:"
echo "======================================================================"
echo ""
echo "❌ PROBLÈME 1: Labels incompatibles"
echo "   Le ServiceMonitor cherche des labels spécifiques sur le Service"
echo "   Solution: Vérifiez que les labels du Service matchent le selector du ServiceMonitor"
echo ""
echo "❌ PROBLÈME 2: Namespace incorrect"
echo "   Le ServiceMonitor doit être dans un namespace que Prometheus surveille"
echo "   Solution: Soit mettre le ServiceMonitor dans 'monitoring', soit configurer Prometheus"
echo ""
echo "❌ PROBLÈME 3: serviceMonitorSelector vide"
echo "   Prometheus n'est configuré pour surveiller AUCUN ServiceMonitor"
echo "   Solution: Configurer prometheus.serviceMonitorSelector: {}"
echo ""
echo "❌ PROBLÈME 4: Port incorrect"
echo "   Le ServiceMonitor pointe vers un port qui n'existe pas"
echo "   Solution: Vérifier que le port dans ServiceMonitor = port du Service"
echo ""
echo "======================================================================"
