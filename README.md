# 🕷️ BADSHAH AI

<p align="center">

### Local AI Cybersecurity Assistant & Security Assessment Tool

**Scan • Analyze • Understand • Defend**

</p>

<p align="center">

`Python` • `FastAPI` • `Ollama` • `Local AI` • `Cybersecurity`




## 🧠 What is BADSHAH AI?

**BADSHAH AI** is a personal/local cybersecurity project that combines system diagnostics, security scanning, evidence analysis and a locally hosted AI assistant.

The AI layer uses **Ollama**, allowing the project to work with local AI models without requiring a cloud AI API.

```text
System
   ↓
Diagnostic / Scanner
   ↓
Evidence
   ↓
Risk Analysis
   ↓
Local AI
   ↓
Security Explanation
   ↓
Finding / Recommendation
   ↓
Report
```

---

## ⚙️ How BADSHAH AI Works

```text
              🕷️ BADSHAH AI
                    │
                    ▼
            Platform Detection
                    │
                    ▼
          Security Diagnostics
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Wi-Fi                 Web
       Scan                 Scan
          │                   │
          └─────────┬─────────┘
                    ▼
             Evidence Data
                    │
                    ▼
              Risk Engine
                    │
                    ▼
             Local Ollama AI
                    │
                    ▼
             Security Result
                    │
                    ▼
                 Report
```

---

## 📁 Project Structure

```text
BADSHAH-AI/
│
├── badshah.py
├── requirements.txt
├── .env
├── README.md
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── ai/
│   ├── api/
│   ├── commands/
│   ├── models/
│   ├── scanners/
│   ├── services/
│   ├── platforms/
│   └── utils/
│
├── data/
│   ├── evidence/
│   ├── reports/
│   └── scans/
│
└── tests/
    └── test_core.py
```

---

## 📦 Required Software

```text
Python 3.11+
Git
Ollama
pip
Virtual Environment
```

Python packages:

```text
requests
python-dotenv
pydantic
rich
questionary
psutil
bleak
httpx
beautifulsoup4
fastapi
uvicorn
pytest
```

---

## 🪟 Windows Setup

```powershell
git clone https://github.com/YOUR_USERNAME/BADSHAH-AI.git
cd BADSHAH-AI

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Ollama, then:

```powershell
ollama pull gemma3:4b
ollama list
ollama serve
```

Run:

```powershell
python badshah.py
```

---

## 🐉 Kali Linux Setup

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

git clone https://github.com/YOUR_USERNAME/BADSHAH-AI.git
cd BADSHAH-AI

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:4b
ollama serve
```

Run:

```bash
python badshah.py
```

---

## 🚀 FastAPI Backend

```bash
python -m uvicorn backend.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

```text
GET  /api/health
GET  /api/environment
POST /api/chat
POST /api/diagnostics/{diagnostic}
POST /api/analyze
GET  /api/wifi/adapters
GET  /api/wifi/discovery
```

---

## 🔍 Diagnostic Commands

BADSHAH AI uses **predefined read-only diagnostic commands**. It does not accept arbitrary shell commands from the user.

### Linux

```bash
ip -br link
ip route
iw dev
nmcli device status
```

### Windows

```text
PowerShell
netsh
route
```

---

## 📡 Wi-Fi Security

BADSHAH AI can collect authorized Wi-Fi discovery information and analyze security-related configuration such as authentication and encryption.

---

## 🌐 Web Security

The web-security modules can analyze authorized targets for:

```text
HTTPS
TLS
HTTP Security Headers
Response Information
Security Evidence
```

---

## 📄 Reports

Generated reports are stored under:

```text
data/reports/
```

Reports include findings, severity, evidence, remediation, verification guidance and AI security analysis.

---

## 🧪 Testing

```bash
python -m pytest -q
python -m compileall -q backend
```

---

## 🚧 Development Status

### Completed

* [x] Platform detection
* [x] Tool detection
* [x] Safe diagnostic command service
* [x] Ollama integration
* [x] Local AI security agent
* [x] AI chat
* [x] Wi-Fi foundation
* [x] Bluetooth foundation
* [x] Web scanner foundation
* [x] TLS scanner foundation
* [x] Header analysis
* [x] Risk engine
* [x] Evidence processing
* [x] Report generation
* [x] FastAPI backend
* [x] Tests

### Next

* [ ] 🕷️ Final spider logo
* [ ] 🎨 Professional graphical UI
* [ ] 📊 Security dashboard
* [ ] 🔍 Findings interface
* [ ] 🤖 AI Security Center
* [ ] 📄 Advanced reports
* [ ] ⚙️ Settings panel

---

## ⚠️ Disclaimer & Responsibility

Please use BADSHAH AI for **your own testing, personal security research, education, or systems for which you have clear permission**.

Do not use this software for illegal, unauthorized, malicious, privacy-invasive, or disruptive activities.

If BADSHAH AI is used without permission against another person's or organization's computer, network, website, server, application, device, account, personal property, or private information, **you are solely responsible for your actions and their consequences.**

The developer is **not responsible for illegal activity, unauthorized access, privacy damage, personal-property damage, misuse, or any other consequences resulting from the use of this software.**

**Use BADSHAH AI responsibly and at your own risk.**
