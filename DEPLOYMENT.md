# RepoMesh AI - Deployment Guide

## Overview

This guide provides instructions for deploying RepoMesh AI in various environments.

---

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB free space
- **OS**: Linux, macOS, or Windows

### Required Services

- **Git**: For repository cloning
- **OpenAI API**: For LLM features (optional but recommended)

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/repomesh/repomesh-ai.git
cd repomesh-ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set required variables:
```env
OPENAI_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Deployment Options

### Option 1: Local Development

**Best for**: Development and testing

```bash
# Using uvicorn directly
uvicorn repomesh.api.main:app --reload --host 0.0.0.0 --port 8000

# Or using make
make run-dev
```

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

### Option 2: Production Server

**Best for**: Single-server production deployment

#### Using Uvicorn with Workers

```bash
uvicorn repomesh.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

#### Using Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn repomesh.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

---

### Option 3: Docker Deployment

**Best for**: Containerized environments

#### Build Image

```bash
docker build -t repomesh-ai:latest .
```

#### Run Container

```bash
docker run -d \
  --name repomesh-ai \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/repos:/app/repos \
  -v $(pwd)/data:/app/data \
  repomesh-ai:latest
```

#### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  repomesh:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./repos:/app/repos
      - ./data:/app/data
      - ./traces:/app/traces
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

---

### Option 4: Kubernetes Deployment

**Best for**: Large-scale production deployments

#### Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: repomesh-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: repomesh-ai
  template:
    metadata:
      labels:
        app: repomesh-ai
    spec:
      containers:
      - name: repomesh-ai
        image: repomesh-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: repomesh-secrets
              key: openai-api-key
        volumeMounts:
        - name: repos
          mountPath: /app/repos
        - name: data
          mountPath: /app/data
      volumes:
      - name: repos
        persistentVolumeClaim:
          claimName: repomesh-repos-pvc
      - name: data
        persistentVolumeClaim:
          claimName: repomesh-data-pvc
```

#### Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: repomesh-ai
spec:
  selector:
    app: repomesh-ai
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `API_HOST` | No | 0.0.0.0 | API host |
| `API_PORT` | No | 8000 | API port |
| `REPOS_BASE_PATH` | No | ./repos | Repository storage path |
| `CHROMA_PERSIST_DIRECTORY` | No | ./data/chroma | ChromaDB data path |
| `LOG_LEVEL` | No | INFO | Logging level |
| `MAX_CONCURRENT_AGENTS` | No | 5 | Max concurrent agents |

### Performance Tuning

#### Workers

- **Development**: 1 worker
- **Production**: 2-4 workers per CPU core
- **High Load**: 4-8 workers per CPU core

#### Memory

- **Minimum**: 4GB RAM
- **Recommended**: 8GB RAM
- **High Load**: 16GB+ RAM

#### Storage

- **Repositories**: ~100MB per repository
- **ChromaDB**: ~50MB per 1000 context entries
- **Traces**: ~1MB per orchestration run

---

## Monitoring

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "RepoMesh AI"
}
```

### Logs

```bash
# View logs (Docker)
docker logs -f repomesh-ai

# View logs (Kubernetes)
kubectl logs -f deployment/repomesh-ai
```

### Metrics

Enable metrics in `.env`:
```env
ENABLE_METRICS=true
```

---

## Security

### API Security

1. **Use HTTPS** in production
2. **Configure CORS** properly
3. **Implement rate limiting**
4. **Use API keys** (future feature)

### Environment Security

1. **Never commit** `.env` files
2. **Use secrets management** (Kubernetes Secrets, AWS Secrets Manager)
3. **Rotate API keys** regularly
4. **Limit file system access**

### Network Security

1. **Use firewall rules**
2. **Restrict port access**
3. **Use VPN** for internal access
4. **Enable TLS/SSL**

---

## Backup and Recovery

### Backup Strategy

```bash
# Backup repositories
tar -czf repos-backup.tar.gz repos/

# Backup ChromaDB data
tar -czf data-backup.tar.gz data/

# Backup traces
tar -czf traces-backup.tar.gz traces/
```

### Recovery

```bash
# Restore repositories
tar -xzf repos-backup.tar.gz

# Restore data
tar -xzf data-backup.tar.gz

# Restore traces
tar -xzf traces-backup.tar.gz
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn repomesh.api.main:app --port 8001
```

#### Out of Memory

```bash
# Reduce concurrent agents
export MAX_CONCURRENT_AGENTS=2

# Increase Docker memory
docker run --memory=8g ...
```

#### ChromaDB Errors

```bash
# Clear ChromaDB data
rm -rf data/chroma

# Restart application
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Run multiple API instances
3. **Shared Storage**: Use network storage for repositories
4. **Distributed Cache**: Use Redis for context caching

### Vertical Scaling

1. **Increase CPU**: More workers
2. **Increase Memory**: Larger context cache
3. **Increase Storage**: More repositories

---

## Maintenance

### Regular Tasks

- **Update dependencies**: Monthly
- **Rotate logs**: Weekly
- **Clean old traces**: Monthly
- **Backup data**: Daily
- **Monitor disk space**: Daily

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
systemctl restart repomesh-ai
```

---

## Support

For deployment issues:
- GitHub Issues: https://github.com/repomesh/repomesh-ai/issues
- Documentation: https://docs.repomesh.ai
- Email: support@repomesh.ai