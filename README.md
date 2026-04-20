# Math Tutor - React + Python + Claude

An AI-powered math tutor chatbot with a React frontend and Python FastAPI backend that uses Claude Haiku. The tutor helps students learn math through guided problem-solving rather than just providing answers.

## Project Structure

```
.
├── frontend/          # React + Vite + TypeScript
│   └── src/
│       ├── App.tsx    # Chatbot UI component
│       ├── App.css    # Chatbot styling
│       └── index.css  # Base styles
├── backend/
│   ├── main.py        # FastAPI server with Claude Haiku
│   ├── requirements.txt
│   └── venv/          # Virtual environment
├── .env               # Template (committed to git)
├── .env.local         # Your actual API key (not committed)
└── package.json       # Root npm scripts
```

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- Anthropic API key

## Setup

### 1. Install Dependencies

```bash
npm run install:all
```

Or install separately:
```bash
npm install              # Root dependencies
npm run install:frontend # Frontend dependencies
npm run install:backend  # Backend dependencies (creates venv and installs packages)
```

This will install:
- Root dependencies (concurrently)
- Frontend dependencies (React, Vite, etc.)
- Backend dependencies (FastAPI, Anthropic, etc.) in a Python virtual environment

### 2. Configure Environment Variables

The project uses `.env.local` for local development (not committed to git):

1. Copy `.env` to `.env.local`:
   ```bash
   cp .env .env.local
   ```

2. Edit `.env.local` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY="your-actual-api-key"
   ```

**Note:**
- `.env` - Template file with placeholder values (committed to git)
- `.env.local` - Your actual secrets (ignored by git, used locally)

## Running the Application

### Option 1: Run Both Servers Together (Recommended)

```bash
npm run dev
```

This starts both the backend (port 8000) and frontend (port 5173) concurrently.

### Option 2: Run Servers Separately

**Terminal 1 - Backend:**
```bash
npm run dev:backend
```

**Terminal 2 - Frontend:**
```bash
npm run dev:frontend
```

### 3. Open the Application

Open your browser and go to `http://localhost:5173`

## Available Scripts

- `npm run dev` - Run both frontend and backend concurrently
- `npm run dev:frontend` - Run only the frontend server
- `npm run dev:backend` - Run only the backend server
- `npm run install:all` - Install all dependencies (root, frontend, backend)
- `npm run install:frontend` - Install only frontend dependencies
- `npm run install:backend` - Install only backend dependencies

## Features

- **Math Tutor Persona**: Custom system prompt that makes Claude act as a patient math tutor
  - Guides students through problems with questions instead of giving direct answers
  - Encourages critical thinking and problem-solving skills
  - Provides hints and step-by-step guidance
- **Rich Markdown Formatting**: Both user messages and AI responses support full markdown
  - **Bold**, *italic*, and `code` formatting
  - Numbered lists and bullet points
  - Code blocks with syntax highlighting
  - Math equations with LaTeX/KaTeX rendering (inline and block)
  - Tables, blockquotes, and links
- **Conversation History**: Full context maintained across messages - Claude remembers previous exchanges
- Simple chatbot UI with message history display
- Real-time communication with Claude Haiku
- Response limited to 100 tokens for quick replies
- Modern, responsive design with gradient accents
- Clear conversation button to start fresh
- Loading states and error handling
- Secure environment variable management

## API Endpoints

- `POST /chat` - Send conversation history and get a response from Claude
  ```json
  Request: {
    "messages": [
      { "role": "user", "content": "What is Python?" },
      { "role": "assistant", "content": "Python is a programming language..." },
      { "role": "user", "content": "Tell me more" }
    ]
  }
  Response: { "response": "Python is known for..." }
  ```
- `GET /health` - Health check endpoint

## Technology Stack

**Frontend:**
- React 18
- TypeScript
- Vite
- react-markdown (markdown rendering)
- remark-gfm (GitHub Flavored Markdown)
- remark-math & rehype-katex (LaTeX math equations)
- CSS3 (with animations)

**Backend:**
- FastAPI
- Anthropic Python SDK (claude-haiku-4-5-20251001)
- Python-dotenv
- Uvicorn

## Configuration

The backend is configured to use:
- Model: `claude-haiku-4-5-20251001`
- Max tokens: `100`
- CORS enabled for `http://localhost:5173`

### Customizing the System Prompt

The AI's behavior is controlled by the `SYSTEM_PROMPT` constant in `backend/main.py`. To change the AI's personality or role:

1. Open `backend/main.py`
2. Find the `SYSTEM_PROMPT` variable (around line 40)
3. Edit the prompt to define different behavior
4. Restart the backend server

**Current role**: Patient math tutor who guides students through problems

**Example alternative prompts**:
- Science tutor
- Writing coach
- Programming mentor
- General conversational assistant

## Security Notes

- Never commit `.env.local` to version control
- The `.env` file only contains placeholder values and is safe to commit
- Your actual API key should only be in `.env.local`

## Troubleshooting

**Backend installation fails:**
- If you see "venv is not recognized", the venv might be corrupted
- Delete the `backend/venv` folder and run `npm run install:backend` again

**Backend won't start / API key error:**
- Make sure you've created `.env.local` with your actual API key
- Verify the API key is valid and not the placeholder text

**Frontend can't connect to backend:**
- Ensure the backend is running on port 8000
- Check CORS settings in `backend/main.py`

**Port already in use:**
- Backend: Change port in `scripts/run-backend.js`
- Frontend: Vite will automatically suggest an alternative port

## Using Markdown in Messages

Both you and the AI can use markdown formatting:

**Basic formatting:**
- `**bold text**` → **bold text**
- `*italic text*` → *italic text*
- `` `code` `` → `code`

**Lists:**
```
1. First step
2. Second step
3. Third step

- Bullet point
- Another point
```

**Math equations:**
- Inline: `$x^2 + y^2 = r^2$` → $x^2 + y^2 = r^2$
- Block: `$$\frac{-b \pm \sqrt{b^2-4ac}}{2a}$$`

**Code blocks:**
```
\`\`\`python
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)
\`\`\`
```

The AI is instructed to use markdown formatting to make explanations clearer!

## How It Works

The project uses Node.js scripts (`scripts/install-backend.js` and `scripts/run-backend.js`) to manage the Python backend in a cross-platform way. This ensures the setup works on Windows, Mac, and Linux without shell-specific commands.
