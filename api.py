from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from typing import List, Optional

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="A simple API for interacting with AI agents",
    version="1.0.0"
)

# Add CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"],  # All possible Vite ports
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize the AI model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    model_used: str

class HealthResponse(BaseModel):
    status: str
    message: str

# In-memory conversation storage (use database in production)
conversations = {}

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "status": "ok",
        "message": "AI Agent API is running!",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test OpenAI connection
        test_response = llm.invoke("Hello")
        return HealthResponse(
            status="healthy",
            message="AI Agent API is running and OpenAI connection is working"
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat_message: ChatMessage):
    """
    Send a message to the AI agent and get a response
    """
    try:
        # Create conversation ID if not provided
        conv_id = chat_message.conversation_id or f"conv_{len(conversations) + 1}"
        
        # Get or create conversation history
        if conv_id not in conversations:
            conversations[conv_id] = []
        
        conversation_history = conversations[conv_id]
        
        # Create prompt with conversation history
        system_message = """You are Coach Mike, a certified personal trainer and nutrition expert. 
You help people achieve their fitness goals through exercise, nutrition, and motivation. 
Always provide practical fitness advice, workout routines, and healthy lifestyle tips."""
        
        messages = [("system", system_message)]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            if msg["role"] == "user":
                messages.append(("human", msg["content"]))
            else:
                messages.append(("assistant", msg["content"]))
        
        # Add current message
        messages.append(("human", chat_message.message))
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # Get response from AI
        chain = prompt | llm
        ai_response = chain.invoke({})
        
        # Store conversation
        conversations[conv_id].extend([
            {"role": "user", "content": chat_message.message},
            {"role": "assistant", "content": ai_response.content}
        ])
        
        return ChatResponse(
            response=ai_response.content,
            conversation_id=conv_id,
            model_used="gpt-4o-mini"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del conversations[conversation_id]
    return {"message": f"Conversation {conversation_id} deleted successfully"}

@app.get("/models")
async def get_available_models():
    """Get list of available AI models"""
    return {
        "models": [
            {
                "name": "gpt-4o-mini",
                "description": "Fast, cost-effective model for most tasks",
                "provider": "OpenAI"
            },
            {
                "name": "gpt-4o",
                "description": "Most capable model, higher cost",
                "provider": "OpenAI"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Please create a .env file with your OpenAI API key")
    
    print("🚀 Starting AI Agent API server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

