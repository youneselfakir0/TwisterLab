# TwisterLab on Windows - Deployment Guide

## 🪟 Windows Environment Setup

TwisterLab requires **Linux containers** which are not compatible with native Windows Docker Engine. You have **3 options**:

---

## ✅ Option 1: WSL 2 + Docker Desktop (RECOMMENDED)

### Prerequisites
- Windows 10/11 (64-bit)
- WSL 2 installed (✅ **Already installed on your system!**)
- Docker Desktop for Windows

### Steps

1. **Install Docker Desktop for Windows**
   ```powershell
   # Download from: https://www.docker.com/products/docker-desktop
   # Or install with Chocolatey:
   choco install docker-desktop
   ```

2. **Configure Docker Desktop for WSL 2**
   - Open Docker Desktop
   - Go to **Settings** → **General**
   - Enable: ✅ **Use the WSL 2 based engine**
   - Click **Apply & Restart**

3. **Enable WSL Integration**
   - Settings → **Resources** → **WSL Integration**
   - Enable integration with your Ubuntu distro: ✅ **Ubuntu**
   - Click **Apply & Restart**

4. **Start WSL and Deploy**
   ```powershell
   # Start Ubuntu WSL
   wsl
   
   # Navigate to project (WSL can access Windows drives)
   cd /mnt/c/Users/Administrator/Documents/twisterlab
   
   # Deploy with Docker Compose
   docker-compose -f docker-compose.production.yml up -d
   ```

5. **Access Services**
   - API: http://localhost:8000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

---

## ⚡ Option 2: Pure WSL 2 (Native Linux)

Deploy entirely within WSL Ubuntu without Docker Desktop.

### Steps

1. **Start WSL Ubuntu**
   ```powershell
   wsl
   ```

2. **Install Docker in WSL**
   ```bash
   # Update packages
   sudo apt-get update
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   
   # Start Docker service
   sudo service docker start
   ```

3. **Install Docker Compose**
   ```bash
   sudo apt-get install docker-compose-plugin
   ```

4. **Clone Project (if needed)**
   ```bash
   # Option A: Use Windows filesystem
   cd /mnt/c/Users/Administrator/Documents/twisterlab
   
   # Option B: Clone to WSL home
   cd ~
   git clone https://github.com/youneselfakir0/twisterlab.git
   cd twisterlab
   ```

5. **Deploy Stack**
   ```bash
   # Pull images
   docker compose -f docker-compose.production.yml pull
   
   # Start services
   docker compose -f docker-compose.production.yml up -d
   
   # Check status
   docker compose -f docker-compose.production.yml ps
   ```

6. **Access from Windows**
   - API: http://localhost:8000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

---

## 🌐 Option 3: Remote Linux Server

Deploy to a remote Linux server (VM, cloud instance, or K8s cluster when auth resolved).

### Quick Deploy

```bash
# SSH to Linux server
ssh user@your-server

# Clone repository
git clone https://github.com/youneselfakir0/twisterlab.git
cd twisterlab

# Configure environment
cp .env.production.example .env
nano .env  # Edit passwords

# Deploy
docker-compose -f docker-compose.production.yml up -d

# Verify
curl http://localhost/health
```

### Access Remotely

Set up SSH tunneling:
```powershell
# From Windows, tunnel ports
ssh -L 8000:localhost:8000 -L 3000:localhost:3000 -L 9090:localhost:9090 user@your-server
```

Then access:
- API: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

---

## 🧪 Current System Status

**Your Environment**:
- OS: Windows 10/11 (build 26100)
- Docker: 28.5.2 (Windows mode)
- WSL: ✅ Installed (Ubuntu, version 2)
- Status: ❌ Docker running in Windows containers mode

**What Works Now**:
- ✅ Git repository cloned
- ✅ Code and configuration ready
- ✅ WSL 2 Ubuntu installed
- ✅ Documentation complete

**What's Needed**:
- Switch Docker to Linux containers (Option 1), OR
- Deploy within WSL Ubuntu (Option 2), OR
- Deploy to remote Linux server (Option 3)

---

## 🚀 Quick Start (After Setup)

Once Docker is configured for Linux containers:

```bash
# 1. Configure environment
cp .env.production.example .env
nano .env  # Change passwords!

# 2. Start stack
docker-compose -f docker-compose.production.yml up -d

# 3. Verify deployment
curl http://localhost/health

# 4. Test sentiment analysis
curl -X POST http://localhost/v1/mcp/tools/analyze_sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "This is amazing!", "detailed": true}'

# 5. Access Grafana
# Open http://localhost:3000
# Login: admin / (your password from .env)
```

---

## 🔍 Troubleshooting

### Docker "no matching manifest" Error

**Cause**: Docker Desktop running in Windows containers mode

**Solutions**:
1. Right-click Docker Desktop system tray icon
2. Click **"Switch to Linux containers..."**
3. Wait for Docker to restart
4. Retry: `docker-compose -f docker-compose.production.yml up -d`

### WSL Ubuntu Not Starting

```powershell
# Check WSL status
wsl --list --verbose

# Start Ubuntu
wsl --distribution Ubuntu

# Set as default
wsl --set-default Ubuntu
```

### Docker Not Found in WSL

```bash
# Install Docker in WSL
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start Docker daemon
sudo service docker start
```

### Port Already in Use

```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```

---

## 📋 Verification Checklist

- [ ] Docker Desktop installed (if using Option 1)
- [ ] Docker configured for Linux containers
- [ ] WSL 2 Ubuntu accessible
- [ ] .env file created with secure passwords
- [ ] docker-compose.production.yml present
- [ ] Port 80, 443, 3000, 8000, 9090 available
- [ ] Firewall allows Docker traffic

---

## 🎯 Recommended Path for Your System

**Based on your current setup, we recommend: Option 1 (WSL 2 + Docker Desktop)**

**Why?**:
- ✅ WSL 2 already installed and configured
- ✅ Best integration with Windows
- ✅ GUI for Docker management
- ✅ Easiest networking (localhost works seamlessly)
- ✅ Auto-starts with Windows

**Next Steps**:
1. Install Docker Desktop for Windows
2. Enable "Use WSL 2 based engine" in settings
3. Enable integration with Ubuntu distro
4. Restart Docker Desktop
5. Run deployment commands from WSL or PowerShell

---

## 📚 Additional Resources

- **Docker Desktop**: https://docs.docker.com/desktop/wsl/
- **WSL 2 Setup**: https://learn.microsoft.com/en-us/windows/wsl/install
- **TwisterLab Docs**: `DEPLOYMENT.md`, `QUICKSTART.md`
- **Kubernetes Alternative**: Wait for cluster auth resolution

---

## ✅ Success Criteria

After setup, you should be able to:
- [ ] Run `docker ps` and see Linux containers
- [ ] Access http://localhost:8000/health
- [ ] See 8 services running in Docker Desktop
- [ ] Test all MCP tools via API
- [ ] View metrics in Grafana at http://localhost:3000

---

**Need Help?** Check `DEPLOYMENT.md` for detailed troubleshooting or open a GitHub issue.
