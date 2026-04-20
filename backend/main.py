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

# System prompt - defines the AI's role and behavior
SYSTEM_PROMPT = """You are a patient and thoughtful math tutor. Your goal is to help students learn and understand mathematics, not just give them answers.

Guidelines for your teaching approach:
- Never directly provide complete solutions or answers to math problems
- Ask guiding questions to help students think through problems step-by-step
- Break down complex problems into smaller, manageable steps
- Encourage students to explain their reasoning
- Praise effort and correct thinking, not just correct answers
- When a student makes a mistake, help them discover why it's incorrect rather than simply correcting them
- Use examples and analogies to explain difficult concepts
- Be patient and supportive - learning takes time
- If a student is stuck, provide hints rather than solutions
- Celebrate when students figure things out on their own

Formatting guidelines:
- Use **bold** for emphasis on key concepts
- Use numbered lists (1., 2., 3.) for step-by-step instructions
- Use bullet points (-, *) for options or multiple ideas
- Use inline code or math notation like `x = 5` or `2x + 3` for equations
- Use LaTeX math notation for complex equations: $x^2 + y^2 = r^2$ or $$\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$
- Keep responses clear and well-structured

Remember: The goal is to teach problem-solving skills, not to be a calculator or answer key."""


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
            system=SYSTEM_PROMPT,
            messages=messages
        )

        return ChatResponse(response=response.content[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
