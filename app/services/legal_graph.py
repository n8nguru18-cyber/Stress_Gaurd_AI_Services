import os
import logging
from typing import Annotated, List, TypedDict, Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableConfig

from app.utils.prompts import LEGAL_ASSISTANT_SYSTEM_PROMPT
from app.services.kanoon_service import search_legal_context

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------

class LegalAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    legal_context: str

# ---------------------------------------------------------------------------
# Graph Logic
# ---------------------------------------------------------------------------

FALLBACK_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash"
]

async def fetch_kanoon_context(state: LegalAgentState):
    """Node to fetch legal context for the latest query."""
    # Get the last user message
    last_msg = [m for m in state["messages"] if isinstance(m, HumanMessage)][-1]
    query = last_msg.content
    
    logger.info(f"--- FETCHING KANOON CONTEXT FOR: {query[:50]}... ---")
    context = await search_legal_context(query)
    
    if not context or context.strip() == "No specific laws found for this query.":
        formatted_context = "No specific laws were found in the Indian Kanoon database, or the API failed. RULE 5: Rely ENTIRELY on your general Indian legal knowledge to answer."
    else:
        formatted_context = f"Here is the retrieved legal context for this query:\n{context}\n\nRULE 5: Your legal advice MUST be strictly based ONLY on the provided retrieved context from Indian Kanoon."
        
    return {"legal_context": formatted_context}

async def call_legal_model(state: LegalAgentState):
    """Node to invoke LLM (Groq -> Gemini) with legal prompt."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", LEGAL_ASSISTANT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Primary model from env
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    last_exception = None
    
    # 1. Primary Attempt: Groq
    if groq_api_key:
        try:
            llm = ChatGroq(
                model=groq_model_name,
                groq_api_key=groq_api_key,
                temperature=0.3,
            )
            chain = prompt | llm
            
            response = await chain.ainvoke({
                "messages": state["messages"],
                "legal_context": state["legal_context"],
                "history": "" # History is handled by MessagesPlaceholder
            })
            
            if not response.content:
                raise ValueError("Groq returned an empty response.")
                
            return {"messages": [response]}
        except Exception as e:
            logger.warning(f"Groq failed: {e}. Falling back to Gemini.")
            last_exception = e

    # 2. Fallback Attempt: Gemini Sequence
    api_keys = [
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GEMINI_API_KEY2"),
        os.getenv("GEMINI_API_KEY3"),
    ]
    api_keys = [k for k in api_keys if k]
    
    for api_key in api_keys:
        for model_name in FALLBACK_MODELS:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.3,
                )
                chain = prompt | llm
                
                response = await chain.ainvoke({
                    "messages": state["messages"],
                    "legal_context": state["legal_context"],
                    "history": ""
                })
                
                if not response.content:
                    raise ValueError("Gemini returned an empty response.")
                    
                return {"messages": [response]}
            except Exception as e:
                logger.warning(f"Gemini {model_name} failed: {e}.")
                last_exception = e
                
    raise Exception(f"All AI models failed in legal graph. Last error: {last_exception}")

# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

def create_legal_graph():
    workflow = StateGraph(LegalAgentState)
    
    workflow.add_node("fetch_context", fetch_kanoon_context)
    workflow.add_node("agent", call_legal_model)
    
    workflow.add_edge(START, "fetch_context")
    workflow.add_edge("fetch_context", "agent")
    workflow.add_edge("agent", END)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

legal_agent_app = create_legal_graph()
