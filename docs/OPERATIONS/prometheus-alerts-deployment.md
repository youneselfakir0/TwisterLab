# Prometheus Alert Rules Deployment Guide

## Overview
This guide covers deploying Prometheus alert rules for SentimentAnalyzer monitoring to Kubernetes.

**Version**: v3.2.0  
**Phase**: 3.3 - Prometheus Alerting  
**Date**: December 17, 2025

---

## Prerequisites

- Prometheus installed in K8s cluster (or use this guide to install)
- kubectl access to cluster
- Alert rules file: `monitoring/prometheus/rules/sentiment-analyzer-alerts.yml`

---

## Option 1: Deploy to Existing Prometheus

If you already have Prometheus running in your cluster:

### Step 1: Create ConfigMap with Alert Rules

```bash
kubectl create configmap sentiment-analyzer-alerts \
  --from-file=sentiment-analyzer-alerts.yml=monitoring/prometheus/rules/sentiment-analyzer-alerts.yml \
  -n monitoring \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Step 2: Update Prometheus Configuration

Edit your Prometheus deployment to mount the ConfigMap:

```yaml
# Add to prometheus-deployment.yaml
spec:
  template:
    spec:
      volumes:
        - name: alert-rules
          configMap:
            name: sentiment-analyzer-alerts
      containers:
        - name: prometheus
          volumeMounts:
            - name: alert-rules
              mountPath: /etc/prometheus/rules/sentiment-analyzer-alerts.yml
              subPath: sentiment-analyzer-alerts.yml
```

### Step 3: Update Prometheus Config to Load Rules

```yaml
# prometheus-config.yaml
rule_files:
  - /etc/prometheus/rules/sentiment-analyzer-alerts.yml
```

Apply changes:

```bash
kubectl apply -f k8s/monitoring/prometheus/prometheus-config.yaml
kubectl rollout restart deployment/prometheus -n monitoring
```

### Step 4: Verify Rules Loaded

```bash
# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Open browser: http://localhost:9090/rules
# Should see "sentiment_analyzer_alerts" and "agent_system_alerts" groups
```

---

## Option 2: Deploy Complete Monitoring Stack (New Installation)

If you don't have Prometheus yet, use this complete deployment:

### Step 1: Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

### Step 2: Create Prometheus ConfigMap

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: twisterlab
        environment: production

    # Load alert rules
    rule_files:
      - /etc/prometheus/rules/*.yml

    # Scrape configs
    scrape_configs:
      # TwisterLab API metrics
      - job_name: 'twisterlab-api'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - twisterlab
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: twisterlab-api
          - source_labels: [__meta_kubernetes_pod_ip]
            target_label: __address__
            replacement: \${1}:8000
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
        metrics_path: /metrics

      # Kubernetes API server metrics
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
          - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: default;kubernetes;https

      # Node metrics
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: /api/v1/nodes/\${1}/proxy/metrics

    # AlertManager configuration
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
                - alertmanager:9093
EOF
```

### Step 3: Create Alert Rules ConfigMap

```bash
kubectl create configmap sentiment-analyzer-alerts \
  --from-file=sentiment-analyzer-alerts.yml=monitoring/prometheus/rules/sentiment-analyzer-alerts.yml \
  -n monitoring
```

### Step 4: Create Prometheus Deployment

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
        - name: prometheus
          image: prom/prometheus:v2.48.0
          args:
            - '--config.file=/etc/prometheus/prometheus.yml'
            - '--storage.tsdb.path=/prometheus'
            - '--storage.tsdb.retention.time=30d'
            - '--web.enable-lifecycle'
          ports:
            - containerPort: 9090
              name: http
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: alert-rules
              mountPath: /etc/prometheus/rules
            - name: storage
              mountPath: /prometheus
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 1000m
              memory: 2Gi
      volumes:
        - name: config
          configMap:
            name: prometheus-config
        - name: alert-rules
          configMap:
            name: sentiment-analyzer-alerts
        - name: storage
          persistentVolumeClaim:
            claimName: prometheus-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  type: NodePort
  ports:
    - port: 9090
      targetPort: 9090
      nodePort: 30090
      name: http
  selector:
    app: prometheus
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
  - apiGroups: [""]
    resources:
      - nodes
      - nodes/proxy
      - services
      - endpoints
      - pods
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources:
      - configmaps
    verbs: ["get"]
  - nonResourceURLs: ["/metrics"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: monitoring
EOF
```

### Step 5: Verify Deployment

```bash
# Check pod status
kubectl get pods -n monitoring

# Check service
kubectl get svc -n monitoring

# Access Prometheus UI
# http://192.168.0.30:30090
```

---

## Testing Alert Rules

### Test 1: Verify Rules Loaded

```bash
# Access Prometheus UI
http://192.168.0.30:30090/rules

# Should see:
# - sentiment_analyzer_alerts (7 rules)
# - agent_system_alerts (2 rules)
```

### Test 2: Trigger High Error Rate Alert

Generate errors to test the `SentimentAnalyzerHighErrorRate` alert:

```powershell
# PowerShell - Send 50 invalid requests
for ($i=1; $i -le 50; $i++) {
    $body = @{text=""; detailed=$false} | ConvertTo-Json
    Invoke-WebRequest -Uri "http://192.168.0.30:30000/api/v1/mcp/analyze_sentiment" `
      -Method POST -ContentType "application/json" -Body $body -UseBasicParsing | Out-Null
    Write-Host "Error request $i sent"
}
```

Wait 5 minutes, then check:

```bash
# Query Prometheus for alert status
curl http://192.168.0.30:30090/api/v1/alerts | jq '.data.alerts[] | select(.labels.component=="sentiment-analyzer")'
```

Expected output:
```json
{
  "labels": {
    "alertname": "SentimentAnalyzerHighErrorRate",
    "severity": "warning",
    "component": "sentiment-analyzer"
  },
  "state": "firing",
  "value": "0.8333",
  "annotations": {
    "summary": "High error rate for SentimentAnalyzer (>10%)"
  }
}
```

### Test 3: Check Alert History

```bash
# Query for fired alerts in last hour
curl 'http://192.168.0.30:30090/api/v1/query?query=ALERTS{alertname=~"SentimentAnalyzer.*"}' | jq
```

---

## Alert Configuration Reference

### Alert Severities

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| **critical** | Immediate (page on-call) | After 10 min |
| **warning** | Within 30 min | After 1 hour |
| **info** | Review daily | None |

### Alert Thresholds

| Alert Name | Metric | Threshold | Duration |
|------------|--------|-----------|----------|
| SentimentAnalyzerDown | Absent requests | 5 min no data | 5 min |
| SentimentAnalyzerHighErrorRate | Error rate | >10% | 5 min |
| SentimentAnalyzerHighLatency | p95 latency | >2s | 5 min |
| SentimentAnalyzerLowConfidence | Confidence <0.5 | >20% of requests | 10 min |
| SentimentAnalyzerErrorSpike | Error rate | >0.5/s | 3 min |
| SentimentAnalyzerUnusualTextLength | Text ≤10 chars | >30% | 15 min |
| SentimentAnalyzerNoKeywordMatches | 0 keywords | >50% | 10 min |

### PromQL Query Examples

```promql
# Current error rate
sum(rate(agent_requests_total{agent_name="sentiment-analyzer",status="error"}[5m])) 
/ 
sum(rate(agent_requests_total{agent_name="sentiment-analyzer"}[5m]))

# p95 latency
histogram_quantile(0.95, 
  rate(agent_execution_time_seconds_bucket{agent_name="sentiment-analyzer"}[5m])
)

# Low confidence rate
sum(rate(sentiment_confidence_score_bucket{le="0.5"}[10m])) 
/ 
sum(rate(sentiment_confidence_score_count[10m]))

# Sentiment distribution
sum(rate(sentiment_analysis_total[5m])) by (sentiment)
```

---

## Troubleshooting

### Rules Not Loading

```bash
# Check ConfigMap exists
kubectl get configmap sentiment-analyzer-alerts -n monitoring

# Check ConfigMap content
kubectl get configmap sentiment-analyzer-alerts -n monitoring -o yaml

# Check Prometheus logs
kubectl logs -l app=prometheus -n monitoring --tail=50
```

### Alerts Not Firing

1. **Check metric availability**:
   ```promql
   # Should return data
   agent_requests_total{agent_name="sentiment-analyzer"}
   ```

2. **Check rule evaluation**:
   - UI: http://192.168.0.30:30090/rules
   - Look for evaluation errors

3. **Verify threshold logic**:
   ```promql
   # Manually run alert expression
   (sum(rate(agent_requests_total{agent_name="sentiment-analyzer",status="error"}[5m])) / sum(rate(agent_requests_total{agent_name="sentiment-analyzer"}[5m]))) > 0.10
   ```

### Reload Prometheus Config

```bash
# Method 1: API reload (requires --web.enable-lifecycle flag)
curl -X POST http://192.168.0.30:30090/-/reload

# Method 2: Restart pod
kubectl rollout restart deployment/prometheus -n monitoring
```

---

## Next Steps

1. ✅ Alert rules deployed
2. ⏸️ **Deploy AlertManager** (Phase 3.3 continuation)
3. ⏸️ Configure notification channels (Slack, email, PagerDuty)
4. ⏸️ Create runbook documentation
5. ⏸️ Load testing (Phase 3.4)

---

## References

- Prometheus Docs: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Alert Best Practices: https://prometheus.io/docs/practices/alerting/
- PromQL Cheat Sheet: https://promlabs.com/promql-cheat-sheet/
