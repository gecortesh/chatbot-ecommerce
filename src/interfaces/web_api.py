from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import uuid
from datetime import datetime, timedelta
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from llm.chatbot import ChatBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-commerce Chatbot API",
    version="1.0.0",
    description="AI-powered customer service chatbot for e-commerce orders"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chatbot instance
logger.info("Initializing chatbot...")
chatbot = ChatBot(session_id="web_api")
logger.info("Chatbot initialized successfully!")

# Session storage with automatic cleanup
sessions = {}
SESSION_TIMEOUT = timedelta(hours=1)  # Sessions expire after 1 hour

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    conversation_history: List[ChatMessage]
    model_info: Optional[str] = None
    response_time: Optional[float] = None

class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    created_at: datetime
    last_activity: datetime

def cleanup_expired_sessions():
    """Remove expired sessions"""
    now = datetime.now()
    expired_sessions = [
        sid for sid, data in sessions.items()
        if now - data["last_activity"] > SESSION_TIMEOUT
    ]
    
    for sid in expired_sessions:
        del sessions[sid]
        logger.info(f"Cleaned up expired session: {sid}")

def get_or_create_session(session_id: Optional[str]) -> str:
    """Get existing session or create new one"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    now = datetime.now()
    
    if session_id not in sessions:
        sessions[session_id] = {
            "conversation_history": [],
            "created_at": now,
            "last_activity": now
        }
        logger.info(f"Created new session: {session_id}")
    else:
        sessions[session_id]["last_activity"] = now
    
    return session_id

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(" E-commerce Chatbot API started")
    logger.info(f" Model: {getattr(chatbot, 'current_model', 'rule-based system')}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    model_info = getattr(chatbot, 'current_model', 'rule-based system')
    return {
        "message": "E-commerce Chatbot API",
        "status": "running",
        "model": model_info,
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "sessions": "/sessions",
            "reset": "/reset/{session_id}"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    model_status = "loaded" if hasattr(chatbot, 'llm') and chatbot.llm else "fallback"
    return {
        "status": "healthy",
        "model_status": model_status,
        "active_sessions": len(sessions),
        "timestamp": datetime.now()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat endpoint with enhanced error handling"""
    start_time = datetime.now()
    
    try:
        # Clean up expired sessions in background
        background_tasks.add_task(cleanup_expired_sessions)
        
        # Get or create session
        session_id = get_or_create_session(request.session_id)
        conversation_history = sessions[session_id]["conversation_history"]
        
        logger.info(f"Processing chat request for session: {session_id}")
        
        # Process message with chatbot
        response, updated_history = chatbot.chat(request.message, conversation_history)
        
        # Update session
        sessions[session_id]["conversation_history"] = updated_history
        sessions[session_id]["last_activity"] = datetime.now()
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Convert to response format with timestamps
        history_messages = [
            ChatMessage(
                role=msg["role"], 
                content=msg["content"],
                timestamp=datetime.now()
            )
            for msg in updated_history
        ]
        
        model_info = getattr(chatbot, 'current_model', 'rule-based system')
        
        logger.info(f"Chat response generated in {response_time:.2f}s")
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            conversation_history=history_messages,
            model_info=model_info,
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Chat processing failed",
                "message": str(e),
                "timestamp": datetime.now()
            }
        )

@app.post("/reset/{session_id}")
async def reset_session(session_id: str):
    """Reset conversation history for a session"""
    if session_id in sessions:
        message_count = len(sessions[session_id]["conversation_history"])
        del sessions[session_id]
        logger.info(f"Reset session {session_id} with {message_count} messages")
        return {
            "message": f"Session {session_id} reset successfully",
            "previous_message_count": message_count
        }
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"Session {session_id} not found"
        )

@app.get("/sessions")
async def list_sessions():
    """List all active sessions with details"""
    session_info = []
    
    for sid, data in sessions.items():
        session_info.append(SessionInfo(
            session_id=sid,
            message_count=len(data["conversation_history"]),
            created_at=data["created_at"],
            last_activity=data["last_activity"]
        ))
    
    return {
        "active_sessions": session_info,
        "total_sessions": len(sessions),
        "model_info": getattr(chatbot, 'current_model', 'rule-based system')
    }

@app.get("/session/{session_id}")
async def get_session_details(session_id: str):
    """Get detailed information about a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    return {
        "session_id": session_id,
        "message_count": len(session_data["conversation_history"]),
        "created_at": session_data["created_at"],
        "last_activity": session_data["last_activity"],
        "conversation_preview": session_data["conversation_history"][-5:]  # Last 5 messages
    }

@app.delete("/sessions/cleanup")
async def cleanup_sessions():
    """Manually trigger session cleanup"""
    initial_count = len(sessions)
    cleanup_expired_sessions()
    cleaned_count = initial_count - len(sessions)
    
    return {
        "message": "Session cleanup completed",
        "cleaned_sessions": cleaned_count,
        "active_sessions": len(sessions)
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting E-commerce Chatbot API...")
    print("API will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")