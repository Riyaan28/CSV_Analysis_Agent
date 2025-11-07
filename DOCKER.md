# 🐳 Docker Deployment Guide

Complete guide to run the CSV Analysis Agent on any computer using Docker.

## 📋 Prerequisites (One-Time Setup)

### 1. Install Docker Desktop

- **Download**: https://www.docker.com/products/docker-desktop/
- **Windows**: Docker Desktop for Windows (requires WSL 2)
- **Mac**: Docker Desktop for Mac
- **Linux**: Docker Engine + Docker Compose

**Verify Installation:**

```bash
docker --version
docker-compose --version
```

### 2. No Other Requirements!

✅ No need to install Python  
✅ No need to install Ollama separately  
✅ No need to download models manually  
✅ Everything runs in containers

---

## 🚀 Setup on New Computer (Step-by-Step)

### Step 1: Clone the Repository

```bash
# Clone the project
git clone <repository-url>
cd rag_agent
```

### Step 2: Start the Application

```bash
# Start all containers (app + Ollama)
docker-compose up -d
```

**What happens on first run:**

1. Docker downloads Python base image (~300MB)
2. Installs all Python dependencies (~1.5GB)
3. Downloads Ollama image (~700MB)
4. Downloads llama3.2 model (~2GB) - **This takes 5-10 minutes**

**Total first-time download: ~4.5GB**

### Step 3: Wait for Model Download

```bash
# Monitor Ollama model download progress
docker logs ollama-server --follow

# Wait until you see:
# "✓ llama3.2 successfully downloaded"
```

Press `Ctrl+C` to stop viewing logs.

### Step 4: Access the Application

Open your browser to: **http://localhost:8501**

---

## 🔄 Daily Usage

### Start the Application

```bash
cd rag_agent
docker-compose up -d
```

**Access:** http://localhost:8501

### Stop the Application

```bash
docker-compose down
```

### View Logs (Troubleshooting)

```bash
# App logs
docker logs csv-analysis-agent --tail=50

# Ollama logs
docker logs ollama-server --tail=50

# Both at once
docker-compose logs --tail=50
```

### Restart (After Code Changes)

```bash
docker-compose restart
```

---

## ⚡ Performance Information

### Why is it slow?

The application runs on **CPU only** (no GPU acceleration in Docker by default):

- **Query Response Time**: 10-30 seconds per query
- **Model Loading**: 2-5 seconds on first query
- **Subsequent Queries**: Faster due to caching

### To Speed Up:

1. **Enable GPU in Docker** (if you have NVIDIA GPU):

   - Install NVIDIA Container Toolkit
   - Uncomment GPU sections in docker-compose.yml

2. **Use Faster Model**:

   ```bash
   # Switch to smaller/faster model
   docker exec ollama-server ollama pull qwen2.5:0.5b  # Faster but less accurate
   ```

3. **Increase Docker Resources**:
   - Open Docker Desktop → Settings → Resources
   - Increase CPU: 4+ cores
   - Increase Memory: 8GB+

---

---

## 📦 Manual Docker Commands

### Build Image

```bash
docker build -t csv-analysis-agent .
```

### Run Container

```bash
docker run -d \
  --name csv-agent \
  -p 8501:8501 \
  -v ${PWD}/data:/app/data \
  -v ${PWD}/cache_db:/app/cache_db \
  csv-analysis-agent
```

### Stop Container

```bash
docker stop csv-agent
docker rm csv-agent
```

---

## 🔧 Ollama Configuration

### Option A: Ollama on Host Machine (Windows)

**1. Update Ollama Client to Use Host IP**

Edit `src/ollama_client.py` and change:

```python
self.base_url = "http://host.docker.internal:11434"
```

**2. Ensure Ollama is listening on all interfaces**

On Windows, Ollama usually listens on `localhost:11434` by default.

**3. Run Docker with host network access**

```bash
docker run -d \
  --name csv-agent \
  --add-host=host.docker.internal:host-gateway \
  -p 8501:8501 \
  -v ${PWD}/data:/app/data \
  -v ${PWD}/cache_db:/app/cache_db \
  csv-analysis-agent
```

### Option B: Ollama in Docker

**1. Uncomment Ollama service in docker-compose.yml**

**2. Update Ollama client URL in code:**

```python
self.base_url = "http://ollama:11434"
```

**3. Run both services:**

```bash
docker-compose up -d
```

**4. Pull models into Ollama container:**

```bash
docker exec -it ollama-server ollama pull llama3.2
```

### Option C: Remote Ollama Server

Set environment variable:

```bash
docker run -d \
  --name csv-agent \
  -e OLLAMA_BASE_URL=http://your-ollama-server:11434 \
  -p 8501:8501 \
  csv-analysis-agent
```

---

## 📁 Volume Mounts & Data Persistence

The Docker setup persists data across restarts:

| Host Path     | Container Path  | Purpose                           |
| ------------- | --------------- | --------------------------------- |
| `./data`      | `/app/data`     | Your CSV files                    |
| `./cache_db`  | `/app/cache_db` | Query cache (speeds up responses) |
| `ollama-data` | `/root/.ollama` | Downloaded models (~2GB)          |

**Your data is safe!** Even after `docker-compose down`, your files and cache are preserved.

---

## 🔍 Troubleshooting

### Application Not Starting

```bash
# Check container status
docker-compose ps

# Should show:
# NAME                  STATUS
# csv-analysis-agent    Up (healthy)
# ollama-server         Up

# If not running, check logs
docker-compose logs
```

### Ollama Not Connecting

```bash
# Test Ollama from app container
docker exec csv-analysis-agent curl http://ollama:11434/api/tags

# Should return JSON with model list
# If fails, restart Ollama:
docker-compose restart ollama
```

### Port 8501 Already in Use

```bash
# Windows - Find and kill process
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# Edit: ports: - "8502:8501"  # Use 8502 instead
```

### Model Not Found Error

```bash
# Download model manually
docker exec ollama-server ollama pull llama3.2

# Verify model exists
docker exec ollama-server ollama list
```

### Clean Restart (Reset Everything)

```bash
# Stop and remove all containers, volumes, and images
docker-compose down -v
docker system prune -a

# Start fresh
docker-compose up -d
```

### Slow Performance

See **Performance Information** section above. Running on CPU is expected to be slower.

---

## 🌐 Setup on Different Operating Systems

### Windows (PowerShell)

```powershell
# Clone and start
git clone <repository-url>
cd rag_agent
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Mac / Linux (Terminal)

```bash
# Clone and start
git clone <repository-url>
cd rag_agent
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**No difference in commands!** Docker Compose works the same on all platforms.

---

## 🎯 Complete Command Reference

```bash
# START APPLICATION
docker-compose up -d              # Start in background
docker-compose up                 # Start with logs visible

# STOP APPLICATION
docker-compose down               # Stop containers (keeps data)
docker-compose down -v            # Stop and delete all data

# VIEW LOGS
docker logs csv-analysis-agent    # App logs
docker logs ollama-server         # Ollama logs
docker-compose logs --tail=50     # Last 50 lines of all logs
docker-compose logs -f            # Live logs (Ctrl+C to exit)

# RESTART
docker-compose restart            # Restart all containers
docker-compose restart rag-agent  # Restart only app

# CHECK STATUS
docker-compose ps                 # Show running containers
docker stats                      # Show resource usage

# REBUILD (after code changes)
docker-compose build              # Rebuild images
docker-compose up -d --build      # Rebuild and start

# CLEAN UP
docker-compose down -v            # Remove containers and volumes
docker system prune -a            # Remove all unused Docker data
```

---

## 🚢 Deploying to Server / Cloud

### Using Docker on Remote Server

```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clone and run
git clone <repository-url>
cd rag_agent
docker-compose up -d

# 4. Access via server IP
# http://your-server-ip:8501
```

### Security for Production

Add reverse proxy with SSL (nginx example):

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## ✅ Setup Checklist for New Computer

- [ ] Install Docker Desktop
- [ ] Clone repository: `git clone <url>`
- [ ] Navigate to folder: `cd rag_agent`
- [ ] Start containers: `docker-compose up -d`
- [ ] Wait for model download (5-10 min first time)
- [ ] Open browser: http://localhost:8501
- [ ] Upload CSV and test query
- [ ] **Done!** Bookmark http://localhost:8501

**Next time:** Just run `docker-compose up -d` and you're ready!

---

## 🚀 Production Deployment

### Environment Variables

Create `.env` file:

```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
OLLAMA_BASE_URL=http://your-ollama-server:11434
```

### Use with Docker Compose

Update `docker-compose.yml`:

```yaml
env_file:
  - .env
```

### Health Checks

The Dockerfile includes a health check. View status:

```bash
docker ps
# Look for (healthy) status
```

---

## 🎯 Development Mode

For live code reloading, uncomment volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./src:/app/src
  - ./app.py:/app/app.py
```

Then:

```bash
docker-compose up
```

---

## 📊 Performance Tips

1. **Use volumes for data persistence** (already configured)
2. **Limit Docker resources** in Docker Desktop settings
3. **Use .dockerignore** to exclude unnecessary files (already configured)
4. **Multi-stage builds** for smaller images (optional enhancement)

---

## 🛡️ Security Notes

- The container runs on port 8501 (HTTP, not HTTPS)
- For production, add a reverse proxy (nginx/traefik) with SSL
- Don't expose sensitive data in environment variables
- Use Docker secrets for production credentials

---

## 📝 Common Commands Reference

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Remove everything
docker-compose down -v --rmi all

# Check status
docker-compose ps
```

---

## 🎉 Success!

Your CSV Analysis Agent is now running at: **http://localhost:8501**

### First Time Using It?

1. **Upload a CSV file** using the sidebar
2. **Ask a question** like: "What are the column names?"
3. **Wait 10-30 seconds** for response (first query is slower)
4. **Subsequent queries** will be faster due to caching

### Why Does It Take Time?

- Running llama3.2 model (2GB) on CPU
- LangChain converts your question → pandas code → executes → formats response
- This is normal for local LLM without GPU

### Tips for Better Experience

- **Use simple questions first**: "Show first 5 rows"
- **Cache helps**: Same/similar questions are instant
- **Be specific**: "What is the average salary?" vs "Tell me about salary"

---

## 📞 Need Help?

Common issues and solutions are in the **Troubleshooting** section above.

**Quick help:**

```bash
# Not working? Check logs
docker-compose logs --tail=50

# Still stuck? Full restart
docker-compose down && docker-compose up -d
```
