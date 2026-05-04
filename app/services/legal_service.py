"""
Legal assistance service.
Provides structured legal advice based on Indian Kanoon API.
Primary model: Groq, Fallback: Gemini.
"""

import os
import logging
from typing import Optional, List
from dotenv import load_dotenv

from app.models.schemas import LegalAssistanceRequest, LegalAssistanceResponse
from app.utils.prompts import LEGAL_ASSISTANT_SYSTEM_PROMPT
from app.services.kanoon_service import search_legal_context

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()
logger = logging.getLogger(__name__)

# Fallback mechanism configuration
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash"
]

def _format_history(history) -> str:
    if not history:
        return "No prior history."
    lines = []
    for msg in history:
        role = "User" if msg.role.lower() == "user" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


from app.services.legal_graph import legal_agent_app

async def generate_legal_advice(request: LegalAssistanceRequest) -> LegalAssistanceResponse:
    """
    Generate legal advice using LangGraph for persistent short-term memory.
    thread_id = user_Id ensures continuity.
    """
    config = {"configurable": {"thread_id": request.user_Id}}
    
    # Check current state to see if we need to seed history
    state = await legal_agent_app.aget_state(config)
    
    # If state is empty and user provided history, seed it
    if not state.values and request.history:
        seed_messages = []
        for msg in request.history:
            if msg.role.lower() == "user":
                seed_messages.append(HumanMessage(content=msg.content))
            else:
                seed_messages.append(AIMessage(content=msg.content))
        
        await legal_agent_app.aupdate_state(config, {"messages": seed_messages})
        logger.info("Seeded Legal LangGraph state with provided history for thread: %s", request.user_Id)

    # Prepare input (the NEW query)
    input_data = {
        "messages": [HumanMessage(content=request.user_query)],
    }
    
    # Run the graph
    result = await legal_agent_app.ainvoke(input_data, config=config)
    
    # The last message is the Assistant's response
    response_text = result["messages"][-1].content
    
    return LegalAssistanceResponse(
        user_Id=request.user_Id,
        user_query=request.user_query,
        response=response_text
    )

