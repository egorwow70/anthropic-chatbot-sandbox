from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables - prefer .env.local over .env
env_local = Path(__file__).parent.parent / ".env.local"
env_file = Path(__file__).parent.parent / ".env"

if env_local.exists():
    load_dotenv(dotenv_path=env_local, override=True)
else:
    load_dotenv(dotenv_path=env_file, override=True)

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


class Task(BaseModel):
    task: str


class GenerateTasksResponse(BaseModel):
    tasks: list[Task]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Convert pydantic models to dicts for Anthropic API
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            temperature=0.6,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        return ChatResponse(response=response.content[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/generate-evaluation-tasks", response_model=GenerateTasksResponse)
async def generate_evaluation_tasks(num_tasks: int = 3):
    """
    Generate evaluation dataset tasks for prompt evaluation.
    Returns an array of tasks for Python, JSON, or Regex AWS-related exercises.

    Args:
        num_tasks: Number of tasks to generate (default: 3)
    """
    try:
        # Construct the prompt
        prompt = f"""Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {{
        "task": "Description of task",
    }},
    ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code

Please generate {num_tasks} objects."""

        # Create system prompt for JSON output
        json_system_prompt = """You are a helpful AI assistant that generates evaluation tasks.
You MUST respond with valid JSON only. Do not include any text before or after the JSON.
Your response must be a JSON array of objects, where each object has a "task" field containing a string description."""

        # Call Claude API with JSON mode instructions
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            temperature=0.8,  # Higher temperature for more creative task generation
            system=json_system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the JSON response
        response_text = response.content[0].text

        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response_text:
            # Extract JSON from code block
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            # Extract from generic code block
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        # Parse JSON
        tasks_data = json.loads(response_text)

        # Validate it's an array
        if not isinstance(tasks_data, list):
            raise ValueError("Response is not a JSON array")

        # Convert to response model
        tasks = [Task(task=item["task"]) for item in tasks_data]

        return GenerateTasksResponse(tasks=tasks)

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            messages = message_data.get("messages", [])

            # Optional JSON format parameters
            use_json_mode = message_data.get("json_mode", False)
            json_schema = message_data.get("json_schema", None)

            if not messages:
                await websocket.send_json({"type": "error", "content": "No messages provided"})
                continue

            try:
                # Prepare system prompt with JSON mode instructions if needed
                system_prompt = SYSTEM_PROMPT
                if use_json_mode:
                    json_instruction = "\n\nIMPORTANT: You MUST respond with valid JSON only. Do not include any text before or after the JSON."
                    if json_schema:
                        # Add schema specification
                        schema_str = json.dumps(json_schema, indent=2)
                        json_instruction += f"\n\nYour response must conform to this JSON schema:\n{schema_str}"
                    system_prompt = SYSTEM_PROMPT + json_instruction

                # Prepare API parameters
                api_params = {
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 1024,
                    "temperature": 0.6,
                    "system": system_prompt,
                    "messages": messages,
                }

                # Stream response from Claude API
                with client.messages.stream(**api_params) as stream:
                    # Send start signal
                    await websocket.send_json({"type": "start", "json_mode": use_json_mode})

                    # Stream text chunks
                    for text in stream.text_stream:
                        await websocket.send_json({
                            "type": "content",
                            "content": text
                        })

                    # Send completion signal
                    await websocket.send_json({"type": "done"})

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error: {str(e)}"
                })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}
