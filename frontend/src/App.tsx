import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isConnectingRef = useRef(false)

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Connect to WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      // Prevent multiple simultaneous connection attempts
      if (isConnectingRef.current || (wsRef.current && wsRef.current.readyState === WebSocket.OPEN)) {
        console.log('WebSocket already connecting or connected, skipping...')
        return
      }

      isConnectingRef.current = true
      console.log('Creating new WebSocket connection...')

      const ws = new WebSocket('ws://localhost:8000/ws/chat')
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        isConnectingRef.current = false
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'start') {
          // Start streaming - add empty assistant message
          setMessages(prev => [...prev, { role: 'assistant', content: '', streaming: true }])
          setLoading(false)
        } else if (data.type === 'content') {
          // Append content to the last message
          setMessages(prev => {
            const updated = [...prev]
            const lastMsg = updated[updated.length - 1]
            if (lastMsg && lastMsg.role === 'assistant') {
              lastMsg.content += data.content
            }
            return updated
          })
        } else if (data.type === 'done') {
          // Mark streaming as complete
          setMessages(prev => {
            const updated = [...prev]
            const lastMsg = updated[updated.length - 1]
            if (lastMsg && lastMsg.role === 'assistant') {
              lastMsg.streaming = false
            }
            return updated
          })
        } else if (data.type === 'error') {
          console.error('WebSocket error:', data.content)
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: 'Sorry, there was an error processing your request.',
            streaming: false
          }])
          setLoading(false)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        isConnectingRef.current = false
        setIsConnected(false)
        setLoading(false)
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason)
        wsRef.current = null
        isConnectingRef.current = false
        setIsConnected(false)

        // Only attempt to reconnect if it wasn't a clean close
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = window.setTimeout(() => {
            console.log('Attempting to reconnect...')
            connectWebSocket()
          }, 3000)
        }
      }
    }

    connectWebSocket()

    // Cleanup on unmount
    return () => {
      console.log('Cleaning up WebSocket...')
      isConnectingRef.current = false

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }

      if (wsRef.current) {
        // Close with code 1000 (normal closure) to prevent reconnection
        wsRef.current.close(1000, 'Component unmounting')
        wsRef.current = null
      }
    }
  }, [])

  const sendMessage = () => {
    if (!input.trim()) {
      return
    }

    const userMessage: Message = { role: 'user', content: input }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInput('')

    // Check if WebSocket is connected
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      // Show error message if not connected
      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '⚠️ Not connected to server. Trying to reconnect...',
          streaming: false
        }])
      }, 100)
      return
    }

    setLoading(true)

    // Send message through WebSocket
    try {
      wsRef.current.send(JSON.stringify({
        messages: updatedMessages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      }))
    } catch (error) {
      console.error('Failed to send message:', error)
      setLoading(false)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Failed to send message. Please try again.',
        streaming: false
      }])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearConversation = () => {
    setMessages([])
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-content">
          <div>
            <h1>Math Tutor</h1>
            <p>Your patient AI math tutor powered by Claude</p>
            <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
          {messages.length > 0 && (
            <button
              className="clear-button"
              onClick={clearConversation}
              disabled={loading}
            >
              Clear Chat
            </button>
          )}
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>👋 Hi! I'm your math tutor. Ask me a math question to get started!</p>
            <p style={{ fontSize: '14px', marginTop: '10px', opacity: 0.8 }}>
              I'll help guide you through problems step-by-step.
            </p>
          </div>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role}`}
          >
            <div className="message-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {message.content || ' '}
              </ReactMarkdown>
              {message.streaming && (
                <span className="streaming-cursor">▋</span>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content loading">
              Connecting...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a math question... (e.g., 'How do I solve 2x + 5 = 15?')"
          disabled={loading}
          rows={3}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default App
