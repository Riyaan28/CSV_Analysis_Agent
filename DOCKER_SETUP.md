# 🚀 Complete Step-by-Step Guide to Run CSV Analysis Agent with Docker

## ✅ Prerequisites Checklist

Before starting, make sure you have:

- [ ] Docker Desktop installed and running
- [ ] Ollama installed and running
- [ ] At least one Ollama model pulled (llama3.2 recommended)
- [ ] Git installed (to clone the repository)

---

## 📦 Step-by-Step Installation & Running

### Step 1: Install Docker Desktop (if not installed)

**Windows:**

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Restart your computer if prompted
4. Open Docker Desktop and wait for it to start
5. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

### Step 2: Install and Start Ollama (if not installed)

**Windows:**

1. Download from: https://ollama.ai/download
2. Install Ollama
3. Ollama will start automatically
4. Verify it's running:
   ```bash
   ollama list
   ```

### Step 3: Pull Required Ollama Model

```bash
# Pull recommended model (2GB)
ollama pull llama3.2

# Verify model is available
ollama list
```

You should see `llama3.2:latest` in the list.

### Step 4: Navigate to Project Directory

```bash
cd C:\Users\sharm\Desktop\code\projects\rag_agent
```

### Step 5: Run with Docker (EASIEST METHOD)

**Option A: Using the Batch Script (Recommended)**

```bash
# Simply double-click docker-start.bat in File Explorer
# Or run from PowerShell terminal:
.\docker-start.bat
```

This will:

- ✅ Check if Docker is running
- ✅ Check Ollama connection
- ✅ Build the Docker image
- ✅ Start the container
- ✅ Open browser automatically

**Option B: Using Docker Compose Manually**

```bash
# Build and start containers
docker-compose up -d

# View logs (optional)
docker-compose logs -f

# Access the app
# Open browser: http://localhost:8501
```

### Step 6: Access the Application

1. Open your web browser
2. Go to: **http://localhost:8501**
3. You should see the CSV Analysis Agent interface!

---

## 🎯 Using the Application

### Upload CSV File

1. Click "Browse files" in the sidebar
2. Select your CSV file
3. Wait for it to load and process

### Ask Questions

Type natural language queries like:

- "Show me the first 5 rows"
- "What columns are in this dataset?"
- "Show distribution of the gender column"
- "How many missing values are in each column?"
- "Show me rows where age > 40"

---

## 🛑 Stopping the Application

### Stop Docker Containers

```bash
# Stop the containers
docker-compose down

# Stop and remove all data (clean reset)
docker-compose down -v
```

### Or Use Windows

1. Open Docker Desktop
2. Find "csv-analysis-agent" container
3. Click "Stop"

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to Ollama"

**Solution:**

```bash
# Check if Ollama is running
ollama list

# If not, start Ollama (it should auto-start)
# On Windows, search for "Ollama" in Start menu and run it

# Verify connection
curl http://localhost:11434/api/tags
```

### Problem: "Port 8501 is already in use"

**Solution 1: Kill existing process**

```bash
# Find what's using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Solution 2: Use different port**

Edit `docker-compose.yml`:

```yaml
ports:
  - "8502:8501" # Use 8502 instead
```

Then access at: http://localhost:8502

### Problem: "Docker is not running"

**Solution:**

1. Open Docker Desktop application
2. Wait for it to fully start (whale icon should be steady)
3. Try again

### Problem: Container builds but app doesn't load

**Check logs:**

```bash
docker-compose logs -f rag-agent
```

**Common issues:**

- Ollama not accessible → Check if Ollama is running
- Missing dependencies → Rebuild: `docker-compose build --no-cache`

---

## 📊 Verifying Everything Works

### 1. Check Docker Container Status

```bash
docker ps
```

You should see:

```
CONTAINER ID   IMAGE                    STATUS         PORTS
abc123...      csv-analysis-agent       Up X minutes   0.0.0.0:8501->8501/tcp
```

### 2. Check Application Health

```bash
# Should return healthy status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 3. Check Ollama Connection

```bash
# From inside container
docker exec -it csv-analysis-agent curl http://host.docker.internal:11434/api/tags
```

### 4. Test the Application

1. Open http://localhost:8501
2. Upload sample CSV from `data/sample_data.csv`
3. Ask: "How many rows?"
4. Should return: "**10**" or the actual row count

---

## 🎓 Understanding the Docker Setup

### What Gets Created?

```
rag_agent/
├── Dockerfile              # Instructions to build the image
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore          # Files to exclude from image
├── docker-start.bat       # Windows startup script
└── DOCKER.md              # Detailed Docker documentation
```

### How It Works

1. **Dockerfile** builds an image with:

   - Python 3.11
   - All dependencies from requirements.txt
   - Your application code
   - Streamlit configured to run on port 8501

2. **docker-compose.yml** orchestrates:

   - Building the image
   - Starting the container
   - Mapping ports (8501)
   - Mounting volumes for data persistence
   - Network configuration

3. **Container connects to Ollama** on your host machine via:
   - Windows: `http://host.docker.internal:11434`

---

## 📁 Data Persistence

Your data is persisted through Docker volumes:

| Data Type   | Location      | Persisted? |
| ----------- | ------------- | ---------- |
| CSV Files   | `./data/`     | ✅ Yes     |
| Query Cache | `./cache_db/` | ✅ Yes     |
| Feedback    | `./cache_db/` | ✅ Yes     |

**This means:**

- Upload CSV files once, they stay available
- Query cache persists across restarts
- Feedback data is preserved

---

## 🚀 Advanced: Development Mode

Want to modify code and see changes instantly?

**1. Edit docker-compose.yml:**

Uncomment these lines:

```yaml
volumes:
  - ./data:/app/data
  - ./cache_db:/app/cache_db
  - ./src:/app/src # Add this
  - ./app.py:/app/app.py # Add this
```

**2. Restart container:**

```bash
docker-compose restart
```

Now code changes are reflected immediately!

---

## 🎉 Success Checklist

- [ ] Docker Desktop is running
- [ ] Ollama is running with llama3.2 model
- [ ] Container is running (`docker ps` shows it)
- [ ] Browser shows app at http://localhost:8501
- [ ] CSV upload works
- [ ] Queries return results
- [ ] No error messages in logs

---

## 📚 Additional Resources

- **Detailed Docker Guide**: See [DOCKER.md](DOCKER.md)
- **Application Guide**: See [README.md](README.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Query Examples**: See [QUERY_EXAMPLES.md](QUERY_EXAMPLES.md)

---

## 💡 Quick Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker ps

# Access container shell
docker exec -it csv-analysis-agent bash
```

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: `docker-compose logs -f`
2. **Verify Ollama**: `ollama list`
3. **Check Docker**: `docker ps`
4. **Review troubleshooting** section above
5. **Rebuild clean**: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`

---

**🎊 Congratulations! You now have a fully Dockerized CSV Analysis Agent running!**
