# Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.x installed
- Sufficient cluster resources (see cost estimates in implementation plan)

## Quick Deploy

### 1. Create Namespace and Secrets

```bash
# Apply namespace and quotas
kubectl apply -f k8s/base/namespace.yaml

# Update secrets with real values
# IMPORTANT: Replace placeholder passwords in k8s/base/secrets.yaml
kubectl apply -f k8s/base/secrets.yaml

# Apply ConfigMaps
kubectl apply -f k8s/base/configmap.yaml
```

### 2. Deploy Redis Cluster

```bash
# Deploy Redis StatefulSet
kubectl apply -f k8s/deployments/redis-cluster.yaml

# Wait for Redis pods to be ready
kubectl wait --for=condition=ready pod -l app=redis -n atw-production --timeout=5m

# Initialize Redis cluster
kubectl exec -it redis-cluster-0 -n atw-production -- redis-cli --cluster create \
  $(kubectl get pods -n atw-production -l app=redis -o jsonpath='{range.items[*]}{.status.podIP}:6379 {end}') \
  --cluster-replicas 1
```

### 3. Deploy Django Application

```bash
# Deploy Django
kubectl apply -f k8s/deployments/django.yaml

# Deploy Service
kubectl apply -f k8s/services/django-service.yaml

# Deploy HPA
kubectl apply -f k8s/autoscaling/hpa-django.yaml

# Check deployment
kubectl get deployments -n atw-production
kubectl get pods -n atw-production -l app=django
```

### 4. Deploy Ingress

```bash
# Install NGINX Ingress Controller (if not already installed)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Deploy Ingress resource
kubectl apply -f k8s/ingress/nginx-ingress.yaml
```

### 5. Verify Deployment

```bash
# Check all resources
kubectl get all -n atw-production

# Check HPA status
kubectl get hpa -n atw-production

# View logs
kubectl logs -f deployment/django -n atw-production --tail=100

# Test health endpoint
kubectl port-forward svc/django 8000:8000 -n atw-production
curl http://localhost:8000/api/v1/health/
```

## Deployment Order

1. **Namespace & Configuration** (namespace, configmap, secrets)
2. **Storage & Cache** (Redis cluster)
3. **Application** (Django deployment + service)
4. **Scaling** (HPA)
5. **Ingress** (NGINX ingress)
6. **Monitoring** (Prometheus/Grafana)

## Useful Commands

### Scaling

```bash
# Manual scale
kubectl scale deployment django --replicas=200 -n atw-production

# Check HPA
kubectl describe hpa django-hpa -n atw-production

# Get metrics
kubectl top pods -n atw-production
kubectl top nodes
```

### Debugging

```bash
# View pod details
kubectl describe pod <pod-name> -n atw-production

# Get logs
kubectl logs <pod-name> -n atw-production

# Execute commands in pod
kubectl exec -it <pod-name> -n atw-production -- /bin/bash

# Check events
kubectl get events -n atw-production --sort-by='.lastTimestamp'
```

### Updates

```bash
# Update image
kubectl set image deployment/django django=atw-backend:v2 -n atw-production

# Rollout status
kubectl rollout status deployment/django -n atw-production

# Rollout history
kubectl rollout history deployment/django -n atw-production

# Rollback
kubectl rollout undo deployment/django -n atw-production
```

## Security Notes

- **Replace all secrets** in `k8s/base/secrets.yaml` before deploying
- Use **Sealed Secrets** or **External Secrets Operator** for production
- Enable **Pod Security Standards**
- Configure **Network Policies**
- Use **RBAC** for access control

##Production Checklist

- [ ] Updated all secrets with production values
- [ ] Configured persistent storage with backups
- [ ] Set up monitoring and alerting
- [ ] Configured autoscaling thresholds
- [ ] Tested disaster recovery procedures
- [ ] Reviewed resource quotas and limits
- [ ] Configured log aggregation
- [ ] Set up SSL/TLS certificates
- [ ] Tested health checks and readiness probes
- [ ] Configured network policies

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n atw-production

# Describe pod for events
kubectl describe pod <pod-name> -n atw-production

# Check logs
kubectl logs <pod-name> -n atw-production
```

### HPA Not Scaling

```bash
# Check metrics server
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes

# Check HPA status
kubectl describe hpa django-hpa -n atw-production

# Verify resource requests are set
kubectl get deployment django -n atw-production -o yaml | grep -A5 resources
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n atw-production

# Describe ingress
kubectl describe ingress atw-ingress -n atw-production

# Check NGINX controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

---

For full architecture details, see [ARCHITECTURE-HYPERSCALE.md](./ARCHITECTURE-HYPERSCALE.md)
