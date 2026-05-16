'use client'

import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import VoiceButton from './VoiceButton'
import LanguageSelector from './LanguageSelector'
import { chatMessage, transcribeAudio, synthesizeVoice } from '@/lib/api'
import styles from './ChatWindow.module.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatWindowProps {
  sessionId: string
  isOwner: boolean
  onLogout: () => void
}

export default function ChatWindow({ sessionId, isOwner, onLogout }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: isOwner
        ? 'Welcome back, Lenoir! How can I help you today?'
        : 'Hello! I\'m here to chat. How can I assist you?',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input
    setInput('')
    setLoading(true)

    try {
      // Add user message to UI
      const userMsg: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMsg])

      // Send to backend
      const response = await chatMessage(sessionId, userMessage, language)

      // Add assistant response
      const assistantMsg: Message = {
        id: response.message_id || Date.now().toString(),
        role: 'assistant',
        content: response.content || 'Sorry, I couldn\'t understand that.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMsg])

      // Play audio response if not already playing
      if (language !== 'en' || Math.random() > 0.5) {
        // Optionally play voice response
        try {
          const audioBlob = await synthesizeVoice(
            assistantMsg.content,
            sessionId,
            language
          )
          if (audioRef.current) {
            audioRef.current.src = URL.createObjectURL(audioBlob)
            audioRef.current.play().catch(() => {})
          }
        } catch (error) {
          console.error('Failed to synthesize voice:', error)
        }
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceRecording = async (audioBlob: Blob) => {
    setLoading(true)

    try {
      // Transcribe audio
      const transcript = await transcribeAudio(audioBlob, sessionId, language)

      // Use transcript as message
      setInput(transcript.transcript)

      // Optionally auto-send or let user review
      // For now, populate input and let user send
    } catch (error) {
      console.error('Transcription error:', error)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Sorry, I couldn\'t understand the audio. Please try again.',
          timestamp: new Date(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage)
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.title}>
          <h1>Lenoir Chatbot</h1>
          {isOwner && <span className={styles.badge}>Owner</span>}
        </div>
        <div className={styles.controls}>
          <LanguageSelector currentLanguage={language} onLanguageChange={handleLanguageChange} />
          <button onClick={onLogout} className={styles.logoutBtn}>
            Logout
          </button>
        </div>
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((msg) => (
          <div key={msg.id} className={styles.messageWrapper}>
            <MessageBubble
              role={msg.role}
              content={msg.content}
              timestamp={msg.timestamp}
            />
          </div>
        ))}
        {loading && (
          <div className={styles.messageWrapper}>
            <div className={styles.typing}>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputArea}>
        <form onSubmit={handleSendMessage} className={styles.inputForm}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={loading}
            className={styles.input}
            autoFocus
          />
          <VoiceButton
            onRecordingComplete={handleVoiceRecording}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className={styles.sendBtn}
          >
            Send
          </button>
        </form>
      </div>

      <audio
        ref={audioRef}
        style={{ display: 'none' }}
      />
    </div>
  )
}
