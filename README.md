# 🧠 StressGuard AI: Stateful Emotional & Legal Support Microservice

StressGuard is a production-grade, highly resilient AI microservice designed to analyze user distress, provide empathetic grounding, and deliver context-aware legal support. It combines **FastAPI**, **LangGraph**, and **Google Gemini** with specialized external intelligence layers.

The system features a state-of-the-art "Triple-Layer Failover" architecture, ensuring near-perfect uptime by dynamically switching between 5 different AI models and 3 distinct API keys during peak demand or outages.

---

## ✨ Key Features

### 🌈 Multi-Layer Emotional Intelligence
- **HF Emotion Detection**: Uses a dedicated Hugging Face inference node (`SamLowe/roberta-base-go_emotions`) to extract high-precision core emotions (fear, sadness, anger, etc.) before the LLM pass.
- **Gemini Fallback**: If the HF model fails or times out, the system silently fails over to Gemini's native emotional analysis to ensure zero service interruption.
- **Risk Assessment**: Classifies distress levels from `low` to `critical` with a safety-first conservative bias.

### ⚖️ Smart Legal Support (Indian Kanoon)
- **Automatic Research**: If a user is in a high-risk situation or asks for legal help, the system triggers a background search for **Indian Central Acts and Rules**.
- **Verified Accuracy**: Uses a optimized `POST` search methodology to fetch real-time legal data, citing specific IPC sections and Acts (e.g., IPC 354D for stalking).
- **Jargon-Free Explanations**: Translates complex legal snippets into simple, actionable advice for the end-user.

### 🛡️ Production-Grade Resilience
- **Multi-Model Fallback**: Cycles through Gemini 2.5 Flash Lite → Gemini 2.0 Flash → Gemini 1.5 Flash to ensure a response never stops.
- **Triple API Key Rotation**: Automatically rotates through `GEMINI_API_KEY`, `GEMINI_API_KEY2`, and `GEMINI_API_KEY3` if rate limits are hit.
- **Low Hallucination**: Uses a multi-pass LangGraph workflow to ground AI responses in actual retrieved legal text.

### 📊 Insightful Tracking
- **Cumulative Daily Summaries**: Generates high-quality psychiatric snapshots every day, maintaining a timestamped history.
- **Emergency Help Beacon**: Creates concise 2-4 line messages for the user's support system based on 7-day emotional trends.

### 📸 Visual Incident Reporting
- **Image + Text Analysis**: Accepts optional base64‑encoded image alongside a text description to generate a neutral, factual incident report.
- **AI‑Driven Classification**: Automatically classifies the complaint into one of eight categories (harassment, stalking, touching, abusing, beating, accident, following, other) or respects user‑provided category.
- **Vision‑Capable Models**: Uses Gemini 2.5 Flash (vision‑enabled) with fallback to other Gemini models for robust image understanding.
- **Structured Output**: Returns a concise 30‑word report, risk level (low/medium/high), and confidence score—ideal for formal documentation.

---

## 🏗️ Technical Architecture

1. **Emotion Node**: Calls Hugging Face API for raw emotional data.
2. **Analysis Node (Agent)**: Gemini analyzes the message + HF emotions + user history.
3. **Research Node**: If signaled, fetches data from Indian Kanoon API.
4. **Synthesis Node**: Gemini merges legal data with empathetic response.
5. **Complaint Analysis Node**: Standalone vision‑capable Gemini model analyzes image + text to produce structured incident reports with risk and confidence scores.

---

## 🚀 API Documentation

### 1. Unified Chat Analysis
`POST /analyze-chat`
Analyzes distress, provides empathy, and integrates legal advice if needed.

**Sample Request:**
```json
{
  "user_id": "u001",
  "message": "I feel unsafe, someone is following me.",
  "user_info": "Female, 25, India"
}
```

**Sample Response:**
```json
{
  "user_id": "u001",
  "emotions": ["fear", "anxiety"],
  "risk": "high",
  "stress_score": 85,
  "response": "I'm so sorry you're feeling this way... Under Section 354D of the IPC, stalking is a punishable offense...",
  "should_alert": true,
  "needs_legal_advice": true,
  "legal_query": "laws against stalking india"
}
```

---

### 2. Visual Incident Reporting
`POST /raise-complaint`
Accepts an optional base64‑encoded image and a text description to generate a neutral, factual incident report with risk assessment.

**Verified Test Case (Stalking Analysis):**
*   **Test Image:** [stalking.jpg](../stalking.jpg)
*   **Input:**
```json
{
  "user_id": "U123",
  "complaint_type": "Stalking",
  "image": "<base64_encoded_image>",
  "text": "This person was stalking me near the bus stop"
}
```

**Output:**
```json
{
  "user_id": "U123",
  "complaint_type": "Stalking",
  "user_complaint_written_text": "This person was stalking me near the bus stop",
  "ai_analysis_written_report": "A person in a hooded jacket and scarf appears to be following a woman near a bus stop, potentially indicating stalking behavior.",
  "risk_level": "high",
  "confidence_level": "high"
}
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:

```env
# Google Gemini Config
GEMINI_API_KEY="..."
GEMINI_API_KEY2="..."
GEMINI_API_KEY3="..."
GEMINI_MODEL="gemini-2.5-flash-lite"

# External Intelligence
INDIAN_KANOON_API_KEY="..."
EMOTION_MODEL_HF_KEY="..."
```

---

## 🛠️ Verification Tools

- **`model_report.txt`**: Detailed report on system performance, including hard-example analysis.
- **`kannon.py`**: Standalone script to verify Indian Kanoon connectivity and query accuracy.
- **`final_verification.py`**: Automated end-to-end test for all service endpoints.

---

## 🚢 Deployment (Render)

This repository includes a `render.yaml` blueprint. Connect your GitHub repo to Render, add your environment keys, and deploy instantly using the Gunicorn/Uvicorn production setup.

---

## 📜 Safety Disclaimer
This service is an AI-powered conversational tool. It provides empathetic support and informational legal context. It is **not** a replacement for professional legal, medical, or emergency services. If you are in immediate danger, please contact your local emergency services directly.
