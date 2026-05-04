# 🧠 StressGuard AI: Stateful Emotional & Legal Support Microservice

StressGuard is a production-grade, highly resilient AI microservice designed to analyze user distress, provide empathetic grounding, and deliver context-aware legal support. It combines **FastAPI**, **LangGraph**, **Hugging Face**, **Google Gemini** and **Groq** with specialized external intelligence layers. It also uses **Indian Kanoon API** for legal support.

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
- **Multi-Model Fallback**: Cycles through`llama-3.1-8b-instant` → `gemini-2.5-flash-lite` → `gemini-2.0-flash` → `gemini-1.5-flash`  →  to ensure a response never stops.
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
2. **Analysis Node (Agent)**: LLM analyzes the message + HF emotions + user history.
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
  "user_id": "report_user_001",
  "user_info": "Female, 25, Delhi, India",
  "message": "I am a 25-year-old woman living in Delhi. For the last two weeks, a man from my neighborhood has been following me to my metro station and even wait for me in the evening. Today he tried to block my path and asked for my number aggressively. I feel very unsafe and stressed. Is there any law in India that can protect me from this stalking?",
  "history": [],
  "memory_summary": "User has mentioned feeling uneasy about her commute previously."
}
```

**Sample Response:**
```json
{
  "user_id": "report_user_001",
  "emotions": [
    "fear",
    "anxiety",
    "distress"
  ],
  "risk": "high",
  "stress_score": 85,
  "response": "That sounds incredibly frightening and stressful. It's completely understandable that you feel unsafe. No one should have to go through this. You are right to be concerned, and there are laws in India that can help protect you from stalking and harassment. The Indian Penal Code, 1860, specifically has provisions against stalking, which is defined as 'intentionally following, watching, or spying on another person' (Section 354D). There's also the Protection of Women from Domestic Violence Act, 2005, which covers harassment and stalking. The Criminal Law (Amendment) Act, 2013, further strengthened laws against sexual harassment and stalking. Would you like me to share more information about these laws and what steps you can consider taking to ensure your safety?",
  "should_alert": false,
  "needs_legal_advice": true,
  "legal_query": "laws against stalking and harassment in India for women"
}
```

---

### 2. Cumulative Daily Summary
`POST /daily-summary`
Generates a narrative psychiatric snapshot of the user's wellbeing across a 24-hour period.

**Sample Request:**
```json
{
  "user_id": "report_user_001",
  "date": "2026-05-03",
  "messages": [
    {"role": "user", "content": "I'm feeling a bit anxious about the commute today.", "timestamp": "2026-05-03T09:00:00"},
    {"role": "assistant", "content": "I understand. What specifically is making you feel anxious?", "timestamp": "2026-05-03T09:01:00"},
    {"role": "user", "content": "That man is following me again. I'm at the station now.", "timestamp": "2026-05-03T18:30:00"}
  ],
  "old_summary": {}
}
```

**Sample Response:**
```json
{
  "user_id": "report_user_001",
  "summary": {
    "2026-05-03": "Today's emotional arc was marked by escalating anxiety and fear. The user began the day feeling anxious about their commute... The user's fear and anxiety peaked at 18:30, indicating a significant risk trend."
  },
  "dominant_emotion": "fear",
  "avg_stress": 80,
  "risk_trend": "increasing"
}
```

---

### 3. Emergency Help Beacon
`POST /i-need-help`
Transforms complex clinical summaries into a short, urgent message suitable for friends and family.

**Sample Request:**
```json
{
  "user_id": "report_user_001",
  "summary_0_7_days": "The user has been experiencing repeated stalking by a neighbor over the last 14 days. Stress levels have escalated from mild anxiety to extreme fear. Today the stalker physically blocked her path."
}
```

**Sample Response:**
```json
{
  "user_id": "report_user_001",
  "message": "Your loved one needs urgent help. They are being stalked by a neighbor and feel extremely unsafe. Please reach out to them immediately to help."
}
```

---

### 4. Legal Assistance
`POST /legal-assistance`
A stateful Indian legal assistant grounded in the **Indian Kanoon API**. It uses **LangGraph memory (checkpointing)** to maintain conversation context across multiple turns.

**Core Rules:**
- **Dynamic Grounding**: If the Kanoon API returns data, the AI is strictly bound to use only that data. If the API fails, it falls back to general LLM legal knowledge.
- **Persistent Memory**: Uses `user_Id` as a `thread_id`. It remembers previous turns, documents mentioned, and questions asked.
- **Step-by-Step Guidance**: Asks 2-3 short follow-up questions if details are missing. 
- **Structured Output**: Once sufficient data is gathered, it provides a structured report with: Problem Summary, Applicable Laws, Steps to Take, Documents Required, Where to Go, and Warning.

**Sample Request (Stateful):**
```json
{
  "user_Id": "U123",
  "user_query": "I have been working here for 4 years. What specific acts protect me from my employer firing me for pregnancy?",
  "history": []
}
```

**Sample Response:**
```json
{
  "user_Id": "U123",
  "user_query": "I have been working here for 4 years. What specific acts protect me from my employer firing me for pregnancy?",
  "response": "- **Problem Summary**: Termination of employment due to pregnancy.\n- **Applicable Laws**: Maternity Benefit Act, 1961.\n- **Steps to Take**: 1. Review your employment contract... 2. File a formal complaint with the Labour Department.\n..."
}
```

---

### 5. Visual Incident Reporting
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

# GROQ API KEY
GROQ_API_KEY = "..."
GROQ_MODEL = "llama-3.1-8b-instant"

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