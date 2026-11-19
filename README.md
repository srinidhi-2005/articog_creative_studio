# Articog Creative Core — AI Engineering Prototype

An AI-native studio operating prototype engineered to eliminate **brief ambiguity**, **creative SKU drift**, and **multi-channel delivery bottlenecks** across commercial AI video and ad production pipelines.

---

## 📌 Executive Summary & Architecture Overview

Traditional agency workflows suffer from high iteration friction due to vague client briefs, manual quality assurance, and fragmented multi-channel re-formatting. The **Articog Creative Core** bridges creative intent and algorithmic execution by mapping production workflows to **4 core AI systems**:

```text
               ┌────────────────────────────────────────────────────────┐
               │                 ARTICOG CREATIVE CORE                  │
               └───────────────────┬────────────────────────────────────┘
                                   │
 ┌─────────────────────────┬───────┴─────────┬─────────────────────────┐
 │                         │                 │                         │
 ▼                         ▼                 ▼                         ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  01. BRIEF SYSTEM │ │ 02. REVIEW SYSTEM │ │ 03. PERFORMANCE   │ │ 04. DELIVERY      │
│                   │ │                   │ │     SYSTEM        │ │     SYSTEM        │
│ • Zero-Ambiguity  │ │ • PyTorch Embed.  │ │ • Creative ROAS   │ │ • 9:16, 1:1, 16:9 │
│   JSON Parser     │ │ • HSV Color Match │ │   Metadata Loop   │ │   Prompts         │
│ • Rejection Rules │ │ • Sharpness QC    │ │ • Visual Pattern  │ │ • Single-Click    │
│ • 4-Shot Script   │ │ • Anti-Drift Gate │ │   Ranking         │ │   JSON Export     │
└───────────────────┘ └───────────────────┘ └───────────────────┘ └───────────────────┘
```

1. **The Brief System (NLP / Structured LLMs):** Transforms unformatted client ideas into locked visual rules, explicit rejection criteria, timed 4-shot storyboards, and 15-second voiceover scripts.
2. **The Review System (Computer Vision / PyTorch):** Evaluates candidate frames against a locked brand reference using deep feature embeddings (MobileNetV3), color histogram similarity (OpenCV HSV), and Laplacian variance sharpness checks to flag SKU drift automatically.
3. **The Performance System (Data Engine):** Connects visual generation parameters back to performance metadata (CTR/ROAS) to refine prompt rules and visual guardrails iteratively.
4. **The Delivery System (FastAPI / Containerized Pipelines):** Programmatically outputs channel-optimized generation prompts (`9:16 Social`, `1:1 Paid Ad`, `16:9 Film`) and production manifests via high-throughput REST APIs.

---

## 🛠 Tech Stack

- **Backend Framework:** FastAPI (Python 3.10+, Uvicorn async ASGI server)
- **Computer Vision & ML Pipeline:** PyTorch (`torchvision` MobileNetV3 Small), OpenCV (`cv2`), NumPy
- **Generative AI Engine:** Google Gemini API (`google-genai` SDK) with automated model discovery, fallback handling, and deterministic rule engine backup
- **Frontend Layer:** Single-Page Interface built with vanilla HTML5, Tailwind CSS (CDN), dynamic DOM handling (`app.js`)
- **Deployment & Containerization:** Docker (Alpine/Slim base), Uvicorn, Hugging Face Spaces compatibility

---

## 📁 Repository Structure

```text
articog-creative-studio/
├── app.py              # FastAPI server, endpoints, Gemini integration, PyTorch/OpenCV QC gate
├── requirements.txt    # Locked production dependencies
├── Dockerfile          # Production container setup (Uvicorn on port 7860)
├── README.md           # Technical documentation and system map
└── static/
    ├── index.html      # Dark-mode Studio UI layout
    ├── style.css       # Clean utility styles & status badges
    └── app.js         # Frontend controller, API calls, JSON export, image handling
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- `pip` package manager
- (Optional) Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/articog-creative-studio.git
cd articog-creative-studio

# 2. Create and activate a virtual environment
# On Windows:
python -m venv venv
.\venv\Scripts\activate

# On Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application

```bash
# Run with Uvicorn (Hot-Reload Enabled)
uvicorn app:app --reload --port 7860
```

Open your browser and navigate to: **`http://localhost:7860`**

---

## 🔑 Environment Variables & API Key Setup

The engine works out-of-the-box in two modes:

1. **Interactive UI Entry:** Click **`⚙ Gemini Key (Optional)`** in the top-right header and paste your key directly.
2. **Environment Variable:** Set `GEMINI_API_KEY` before launch:
   - **PowerShell:** `$env:GEMINI_API_KEY="your_api_key_here"`
   - **Bash/Linux:** `export GEMINI_API_KEY="your_api_key_here"`

*Note: If no key is provided or if network limits are reached, the system gracefully falls back to the internal deterministic structured brief generator.*

---

## 📡 API Reference & Endpoints

### 1. Generate Zero-Ambiguity Brief
`POST /api/generate-brief`

**Request Body:**
```json
{
  "brand_name": "Aether Chrono Smart Ring",
  "service_track": "Ad Creative",
  "audience": "Tech-savvy founders and athletes in Bengaluru & Hyderabad, ages 26–42",
  "offer": "Grade-5 brushed titanium health ring with 7-day battery and zero monthly subscription",
  "rough_idea": "Show the ring floating above dark volcanic basalt with an emerald biometric glow.",
  "api_key": "AIzaSy..."  // Optional
}
```

**Response Schema:**
```json
{
  "source": "Live LLM Engine (gemini-3.1-flash-lite-preview)",
  "brief_spec": {
    "campaign_objective": "...",
    "locked_visual_language": "...",
    "camera_and_motion": "...",
    "rejection_criteria": ["..."]
  },
  "storyboard": [
    { "shot": "Shot 1 · Hook (0–3s)", "visual": "...", "camera": "..." }
  ],
  "voiceover_script": "...",
  "channel_prompts": {
    "social_vertical_9_16": "...",
    "ad_creative_1_1": "...",
    "ai_video_16_9": "..."
  }
}
```

### 2. Run Review & Anti-Drift Gate
`POST /api/review-gate` (Multipart Form Data)

- **`reference_image`:** `File` (Locked Brand Anchor)
- **`candidate_images`:** `List[File]` (Generated Output Frames)

**Evaluation Formula:**
$$\text{Overall Score} = (0.45 \times \text{PyTorch Fidelity}) + (0.35 \times \text{HSV Color Match}) + (0.20 \times \text{Laplacian Sharpness})$$

- **Thresholds:**
  - $\ge 75\%$: `APPROVED` (Ready for master render)
  - $60\% - 74\%$: `REVIEW` (Minor manual touchup needed)
  - $< 60\%$: `REJECTED — Creative Drift Detected`

---

## 🐳 Docker & Hugging Face Spaces Deployment

### Local Docker Build

```bash
# Build Docker image
docker build -t articog-studio .

# Run container on port 7860
docker run -p 7860:7860 articog-studio
```

### Hugging Face Spaces Setup
1. Create a new Space on Hugging Face using the **Docker** SDK.
2. Push repository contents to the Space repository.
3. Add `GEMINI_API_KEY` under **Space Settings $\rightarrow$ Variables and secrets** for instant 1-click execution for external users.

---

## 📄 License

This project is created as an AI Engineering prototype for Articog AI Studio evaluation.

