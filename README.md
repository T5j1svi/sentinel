# 🛡️ SENTINEL v3 — OSINT Intelligence Lab

**SENTINEL v3** is an advanced, fully-integrated Open Source Intelligence (OSINT) platform designed for narrative hunting, bot detection, infrastructure attribution, and disinformation analysis.

It is built for cybersecurity researchers and intelligence analysts to track information operations (IO), map influence networks, and cryptographically secure evidence.

---

## 🚀 Features & Intelligence Modules

SENTINEL v3 features 10 distinct intelligence modules, all powered by real-world data and AI:

1. **🎯 Narrative Hunt**: Cross-platform semantic search (X, Telegram, YouTube, Regional News). Automatically translates your query into 12 languages (including Urdu, Hindi, Chinese) and aggregates results across platforms using a time-budgeted algorithm.
2. **👤 Identity Profiler**: Investigate specific usernames and handles. Correlates account presence across 7 different platforms to detect sockpuppets.
3. **🖼️ Media Forensics**: Analyze images and videos for EXIF metadata, reverse image search across Google/Yandex, and AI deepfake detection. *(Backend endpoint in development)*.
4. **📈 Velocity Monitor**: Tracks narrative spread velocity over 24h/7d/30d periods. Powered by the **GDELT Global Knowledge Graph API** to detect coordinated amplification spikes and anomaly events.
5. **🕸️ Network Mapper**: Dynamically builds influence networks (Sources → Amplifiers → Bot clusters). Click nodes to inspect their roles, confidence scores, and community structures.
6. **🤖 Behaviour Profiler**: Analyzes public behavioral signals to identify bots, sockpuppets, and coordinated networks, scoring accounts from 0-100 on Bot Risk.
7. **🛡️ DISARM Tactics Classifier**: Maps identified content against the **DISARM Framework** (the MITRE ATT&CK equivalent for disinformation). Uses **Groq's Llama-3** to accurately classify tactics like *Emotional Manipulation (T0006)* and *Astroturfing (T0004)*.
8. **🏗️ Infrastructure OSINT**: Extracts domains from hunt results and analyzes WHOIS, DNS, and hosting data (via Shodan & Urlscan) to find shared infrastructure and state-sponsored hosting anomalies.
9. **🌍 Geo Intelligence**: Maps the geographic origin of content and infrastructure, visualizing the data to highlight geographic mismatches (e.g., an Indian handle hosted on a Pakistani server).
10. **🔒 Evidence Locker**: Lock items with one click. Generates cryptographically secure SHA-256 hashes, captures Wayback Machine archives, and maintains a chain of custody.

---

## 🏗️ Architecture

SENTINEL is built on a modern, decoupled architecture:
- **Frontend**: React 18 + Vite + Tailwind CSS. Features a premium "dark mode" intelligence lab aesthetic, glassmorphism, and live global state via `AppContext`.
- **Backend**: FastAPI (Python). Highly concurrent and asynchronous.
- **AI Inference**: Groq (Llama-3) for instantaneous, free AI classification.
- **Search Engine**: DuckDuckGo Search (`ddgs`) for free, unlimited, cross-platform web scraping without relying on expensive Google Custom Search APIs.
- **Global Event Data**: GDELT 2.0 Doc API for timeline volume analysis.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (3.10+)

### 2. Environment Variables (`.env`)
Create a `.env` file in the root directory (next to `run_sentinel.bat`). The core engine (Hunt, Velocity, Network, Bots) works **completely free without any API keys**, but you can unlock advanced features by adding them:

```env
# Server
SENTINEL_HOST=127.0.0.1
SENTINEL_PORT=8000
SENTINEL_DEBUG=true
SENTINEL_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Advanced AI (DISARM Classification)
GROK_API_key=gsk_your_groq_api_key_here  # Get free at console.groq.com

# Infrastructure OSINT (Optional but Recommended)
SHODAN_API_KEY=your_shodan_key           # Get free at account.shodan.io
URLSCAN_API_KEY=your_urlscan_key         # Get free at urlscan.io

# Evidence Forensics (Optional)
VIRUSTOTAL_API_KEY=your_vt_key           # Get free at virustotal.com

# Native Telegram Scraping (Optional)
TELEGRAM_API_ID=your_telegram_id         # Get free at my.telegram.org
TELEGRAM_API_HASH=your_telegram_hash
```

### 3. Running the Platform
For Windows users, we provide a unified startup script that automatically installs dependencies and starts both the frontend and backend.

Simply double-click or run:
```bash
./run_sentinel.bat
```

Alternatively, to run manually:
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## 📖 How to Use (Workflow Example)

1. **Launch a Hunt**: Go to the **Narrative Hunt** page. Type a description of the disinformation narrative you are tracking (e.g., *"Reports of military troop movements on the Kashmir border"*). Select your target platforms and hit "Launch Hunt".
2. **Review Results**: The system searches globally across 12 languages. Once it finishes, review the results. If a result is critical, click **🔒 Lock** to save it to the Evidence Locker.
3. **Analyze Spread**: Switch to the **Velocity Monitor** to see if this narrative is spiking right now (powered by GDELT).
4. **Map the Network**: Go to the **Network Mapper**. SENTINEL will automatically draw an influence map showing which accounts are Patient Zero and who is amplifying them.
5. **Classify Tactics**: Go to the **DISARM Tactic Classifier**. Click "Classify Results" to have the Groq AI analyze the psychology of the posts.
6. **Export Intelligence**: Finally, go to the **Report Generator** to export all findings into a professional PDF/HTML report.

---

## 🛡️ License & Disclaimer
SENTINEL is built for cybersecurity and OSINT research. Ensure you comply with the Terms of Service of the platforms you are investigating. 