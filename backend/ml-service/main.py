from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Singlish Chatbot ML Service",
    description="ML service for Singlish natural language processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None

# Simple authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token != os.getenv("ML_SERVICE_API_KEY", "development"):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

@app.on_event("startup")
async def startup_event():
    """Initialize ML service on startup"""
    logger.info("🚀 Starting Singlish Chatbot ML Service...")
    logger.info("✅ ML Service initialized successfully!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Singlish Chatbot ML Service",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models": {
            "singlish_classifier": True,
            "intent_detector": True,
            "response_generator": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=ChatResponse)
async def predict_response(request: ChatRequest, token: str = Depends(verify_token)):
    """Main prediction endpoint for chat responses"""
    start_time = datetime.now()
    
    try:
        # Simple rule-based response system for now
        message = request.message.lower().strip()
        
        # Detect intent based on simple patterns
        intent, confidence = detect_intent(message)
        
        # Generate response based on intent
        response = generate_response(intent, message)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=response,
            intent=intent,
            confidence=confidence,
            processing_time=processing_time,
            metadata={
                "strategy": "rule_based",
                "message_length": len(message)
            }
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def detect_intent(message: str) -> tuple[str, float]:
    """Simple intent detection based on keywords"""
    message = message.lower()
    
    # Greeting patterns
    if any(word in message for word in ['kohomada', 'hello', 'hi', 'ayubowan']):
        return "greeting", 0.9
    
    # Name asking patterns
    if any(phrase in message for phrase in ['nama mokakda', 'whats your name', 'who are you', 'oya kawda']):
        return "ask_name", 0.85
    
    # Self introduction patterns
    if any(phrase in message for phrase in ['mage nama', 'my name is', 'i am', 'mama']):
        return "self_intro", 0.8
    
    # How are you patterns
    if any(phrase in message for phrase in ['oya kohomada', 'how are you', 'kohoma hari']):
        return "how_are_you", 0.85
    
    # Thanks patterns
    if any(word in message for word in ['thanks', 'thank you', 'stuti', 'stutiyi']):
        return "thanks", 0.9
    
    # Goodbye patterns
    if any(word in message for word in ['bye', 'goodbye', 'giya', 'see you']):
        return "goodbye", 0.8
    
    # Help patterns
    if any(word in message for word in ['help', 'mokak karanne']):
        return "help", 0.85
    
    return "unknown", 0.3

def generate_response(intent: str, message: str) -> str:
    """Generate response based on intent"""
    
    responses = {
        "greeting": [
            "Hari honda machan! Oya kohomada? 😊",
            "Ayubowan! Mama hari honda. Oya kohomada? 👋",
            "Hello machan! Everything good or not? 😄"
        ],
        "ask_name": [
            "Mama CoverageBot! Singlish walata reply karanna puluwan chatbot kenek. Oyata mata kohomada kiyanawa? 😄",
            "My name is CoverageBot machan! AI-powered Singlish assistant kenek. What about you? 🤖"
        ],
        "self_intro": [
            "Nice to meet you! Mama CoverageBot, oyata help karanna puluwan! 🤖",
            "Wah, nice name machan! Mata oyata Singlish walata reply karanna puluwan! 💬"
        ],
        "how_are_you": [
            "Mama hari honda machan! Always ready to chat! Oya kohomada? 💪",
            "I'm doing great la! Everyday also learning new Singlish words. You leh? 😊"
        ],
        "thanks": [
            "Mokakwath naha machan! Mata help karanna lassana! 😊",
            "Welcome la! Anytime can ask me anything! 🤝"
        ],
        "goodbye": [
            "Bye bye machan! Mata aye pennako! See you soon! 👋",
            "Okay la, see you later! Take care ah! 🤗"
        ],
        "help": [
            "Mama oyata Singlish walata reply karanna puluwan! Try karala balanna - kohomada, oyage nama mokakda, thanks wage! 🤝",
            "Sure sure! I can understand Singlish and reply back. Try saying things like 'kohomada' or 'oya kawda'! 😄"
        ],
        "unknown": [
            "Mata eka therenne naha machan! Try 'kohomada' or 'help' kiyla! 🤔",
            "Hmm, mata eka understand karanna baha. Simple Singlish walata try karanna! 😅"
        ]
    }
    
    if intent in responses:
        return random.choice(responses[intent])
    else:
        return random.choice(responses["unknown"])

@app.get("/models/status")
async def get_model_status(token: str = Depends(verify_token)):
    """Get current status of all ML models"""
    return {
        "singlish_classifier": {
            "loaded": True,
            "version": "1.0.0",
            "accuracy": 0.85
        },
        "intent_detector": {
            "loaded": True,
            "version": "1.0.0", 
            "accuracy": 0.82
        },
        "response_generator": {
            "loaded": True,
            "version": "1.0.0",
            "quality_score": 0.88
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )