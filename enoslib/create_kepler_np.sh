
#!/bin/bash -e

echo "--- Création d'une NetworkPolicy pour autoriser l'accès à Kepler ---"

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-access-to-kepler
  namespace: kepler
spec:
  # This policy applies to the Kepler exporter pods
  podSelector:
    matchLabels:
      app.kubernetes.io/component: exporter
      app.kubernetes.io/name: kepler
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    # Rule 1: Allow traffic from any pod
    # in the 'monitoring' namespace (for Prometheus)
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: monitoring
    # Rule 2: Allow traffic from any IP address
    # (for external access via NodePort)
    - ipBlock:
        cidr: 0.0.0.0/0
  # Add a permissive egress rule as a good practice
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
EOF

echo ""
echo "--- Vérification de la NetworkPolicy nouvellement créée ---"
kubectl get networkpolicy allow-access-to-kepler -n kepler
