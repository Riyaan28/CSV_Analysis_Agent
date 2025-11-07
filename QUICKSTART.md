# Quick Start Guide

## 🚀 Get Started in 5 Minutes

Choose your preferred method: **Docker** (easiest) or **Local** (more control)

---

## Method 1: Docker (Recommended - Easiest)

### Prerequisites

✅ Docker Desktop installed from [docker.com](https://www.docker.com/products/docker-desktop/)

### Setup (One-Time)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd rag_agent

# 2. Start everything with one command
docker-compose up -d

# 3. Wait for model download (first time: ~5-10 minutes)
docker logs ollama-server --follow
# Press Ctrl+C when you see "successfully downloaded"
```

### Running the Application

```bash
# Start (after first setup)
docker-compose up -d

# Stop
docker-compose down
```

**Access:** http://localhost:8501

### Quick Launcher (Windows)

Just double-click: **`docker-start.bat`**

---

## Method 2: Local Installation

### Prerequisites

✅ Python 3.9+ installed  
✅ Ollama installed from [ollama.ai](https://ollama.ai)

### Setup (One-Time)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd rag_agent

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Pull Ollama model
ollama pull llama3.2
```

### Running the Application

**Option A: Using Scripts (Easiest)**

Windows:

```bash
# Double-click one of these:
run.bat        # Command Prompt
run.ps1        # PowerShell (recommended)
```

Or in terminal:

```bash
.\run.bat
# OR
.\run.ps1
```

**Option B: Manual**

```bash
# 1. Activate virtual environment
.\venv\Scripts\activate

# 2. Run the app
streamlit run app.py
```

**Access:** http://localhost:8501

---

---

## 🎯 First Query (Both Methods)

1. **Open browser:** http://localhost:8501
2. **Upload CSV:** Click "📁 Data Upload" → Select `data/sample_data.csv`
3. **Wait for initialization:** ~10 seconds
4. **Ask a question:** "What is the average salary?"
5. **Provide feedback:** Click 👍 or 👎

---

## 📊 Example Queries

Try these with the sample data:

**Basic Information:**

```
- What are the column names?
- Show me the first 10 rows
- How many rows and columns?
```

**Statistics:**

```
- What is the average salary by department?
- Show me the median age
- What is the correlation between age and salary?
```

**Analysis:**

```
- How many missing values?
- Show distribution of gender
- Group by department and show average salary
- Filter rows where age is greater than 30
```

---

## 🔄 Switching Between Methods

### From Local to Docker:

```bash
# Stop local app (Ctrl+C in terminal)
# Stop local Ollama
Stop-Process -Name "ollama" -Force

# Start Docker
docker-compose up -d
```

### From Docker to Local:

```bash
# Stop Docker
docker-compose down

# Run locally
.\run.bat
# OR
.\run.ps1
```

**No code changes needed!** The app automatically detects which method you're using.

---

## ⚡ Performance Note

**Response Time:** 10-30 seconds per query (CPU-based inference)

- First query: Slower (model loading)
- Cached queries: Instant
- Complex queries: 20-30 seconds

This is normal for local LLM without GPU acceleration.

---

## 🛠️ Troubleshooting

### Docker Method

**Containers not starting?**

```bash
docker-compose logs
```

**Port 11434 already in use?**

```bash
# Stop local Ollama
Stop-Process -Name "ollama" -Force
docker-compose up -d
```

**Model not found?**

```bash
docker exec ollama-server ollama pull llama3.2
```

### Local Method

**Ollama not connecting?**

```bash
curl http://localhost:11434
# If no response:
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
```

**Port 8501 already in use?**

```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

**Module not found?**

```bash
.\venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

**Virtual environment not found?**

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📚 Features to Explore

1. **RAG Context**: Expand "Context Used (RAG)" to see retrieved information
2. **Caching**: Ask the same question twice - see the ⚡ cache indicator
3. **Feedback System**: Rate responses with 👍 or 👎
4. **Analytics Dashboard**: Check sidebar for feedback statistics with charts
5. **Model Selection**: Try different Ollama models (llama3.2, mistral, etc.)
6. **Export Data**: Export feedback as CSV for analysis
7. **Clear Cache**: Use sidebar button to clear query cache

---

## 📖 Learn More

- **Full Documentation:** [README.md](README.md)
- **Docker Guide:** [DOCKER.md](DOCKER.md) or [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)
- **Implementation Details:** [VERIFICATION.md](VERIFICATION.md)
- **Query Examples:** [QUERY_EXAMPLES.md](QUERY_EXAMPLES.md)

---

## 🎉 You're All Set!

**Quick Commands Cheat Sheet:**

| Action      | Docker                   | Local                      |
| ----------- | ------------------------ | -------------------------- |
| **Start**   | `docker-compose up -d`   | `.\run.bat` or `.\run.ps1` |
| **Stop**    | `docker-compose down`    | `Ctrl+C` in terminal       |
| **Logs**    | `docker-compose logs -f` | Check terminal output      |
| **Restart** | `docker-compose restart` | Re-run script              |

**Enjoy exploring your data with natural language! 🚀**
