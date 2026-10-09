# Troubleshooting labs

| File | Symptom | Where to look | Fix |
|---|---|---|---|
| `broken-image.yaml` | Pod stuck in `ErrImagePull` / `ImagePullBackOff` | `kubectl describe pod` → Events | point to an image tag that exists |
| `broken-service.yaml` | Service has no endpoints, requests time out | `kubectl get endpoints`, `kubectl get pods --show-labels` | selector `app: backend`, `targetPort: 8000` |
