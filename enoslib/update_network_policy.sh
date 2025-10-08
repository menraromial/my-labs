
#!/bin/bash -e

echo "--- 1. Mise à jour de la NetworkPolicy de Grafana ---"
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: grafana
  namespace: monitoring
  labels:
    app.kubernetes.io/component: grafana
    app.kubernetes.io/name: grafana
    app.kubernetes.io/part-of: kube-prometheus
    app.kubernetes.io/version: 12.2.0
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: grafana
      app.kubernetes.io/name: grafana
      app.kubernetes.io/part-of: kube-prometheus
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    # On autorise le trafic depuis n'importe quelle adresse IP (externe/interne)
    - ipBlock:
        cidr: 0.0.0.0/0
    # On garde la règle existante qui autorise Prometheus
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: prometheus
    ports:
    - port: 3000
      protocol: TCP
  egress:
  - {}
EOF

echo ""
echo "--- 2. Mise à jour de la NetworkPolicy de Prometheus ---"
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: prometheus-k8s
  namespace: monitoring
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: prometheus
      app.kubernetes.io/instance: k8s
      app.kubernetes.io/name: prometheus
      app.kubernetes.io/part-of: kube-prometheus
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          app.kubernetes.io/name: prometheus
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 9090
  - from:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          app.kubernetes.io/name: prometheus-adapter
    ports:
    - protocol: TCP
      port: 9090
  - from:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          app.kubernetes.io/name: grafana
    ports:
    - protocol: TCP
      port: 9090
  egress:
  - to:
    - podSelector: {}
EOF

echo ""
echo "NetworkPolicies mises à jour avec succès pour autoriser l'accès externe."
