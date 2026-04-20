from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables - prefer .env.local over .env
env_local = Path(__file__).parent.parent / ".env.local"
env_file = Path(__file__).parent.parent / ".env"

if env_local.exists():
    load_dotenv(dotenv_path=env_local)
else:
    load_dotenv(dotenv_path=env_file)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key == "your-api-key-here":
    raise ValueError(
        "ANTHROPIC_API_KEY not found or invalid. "
        "Please create a .env.local file with your API key. "
        "See README.md for setup instructions."
    )
client = Anthropic(api_key=api_key)


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Convert pydantic models to dicts for Anthropic API
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=messages
        )

        return ChatResponse(response=response.content[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
