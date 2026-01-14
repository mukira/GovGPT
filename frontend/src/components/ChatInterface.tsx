import { useState, useEffect, useRef } from 'react'
import { FormattedResponse } from './FormattedResponse'
import { DecisionReport } from './DecisionReport'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: Array<{
        type: string
        title: string
        source?: string
        url?: string
        relevance?: number
    }>
}

const API_BASE_URL = 'http://localhost:8000'

// Helper to detect if content is a JSON decision report
const isDecisionReport = (content: string): boolean => {
    try {
        const parsed = JSON.parse(content)
        return !!(parsed.decision_required && parsed.options && parsed.executive_summary)
    } catch {
        return false
    }
}

export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const examplePrompts = [
        "What is the impact of the health policy on rural areas?",
        "Which counties benefit most from the agriculture budget?",
        "What is public sentiment on education reforms?",
        "What happens if infrastructure funding is reduced by 10%?"
    ]

    const sendMessage = async (messageText: string) => {
        if (!messageText.trim()) return

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: messageText
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    include_news: true,
                    include_sentiment: true
                })
            })

            if (!response.ok) throw new Error('Failed to send message')

            const reader = response.body?.getReader()
            const decoder = new TextDecoder()

            let assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: '',
                sources: []
            }

            setMessages(prev => [...prev, assistantMessage])

            while (reader) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value)
                const lines = chunk.split('\n')

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6))

                            if (data.type === 'content') {
                                assistantMessage = {
                                    ...assistantMessage,
                                    content: assistantMessage.content + data.data
                                }
                                setMessages(prev => [...prev.slice(0, -1), assistantMessage])
                            } else if (data.type === 'report') {
                                // Decision report - store as JSON string for DecisionReport component
                                assistantMessage = {
                                    ...assistantMessage,
                                    content: JSON.stringify(data.data, null, 2)
                                }
                                setMessages(prev => [...prev.slice(0, -1), assistantMessage])
                            } else if (data.type === 'citations') {
                                assistantMessage = {
                                    ...assistantMessage,
                                    sources: data.data
                                }
                                setMessages(prev => [...prev.slice(0, -1), assistantMessage])
                            }
                        } catch (e) {
                            console.error('Error parsing SSE:', e)
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: 'Sorry, there was an error processing your request.'
            }])
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900">
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-4 shadow-lg">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur">
                        <span className="text-2xl">🇰🇪</span>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold">GovGPT Policy Analysis</h1>
                        <p className="text-sm text-emerald-100">AI-powered Kenya policy insights with RAG + News + Sentiment</p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 && (
                    <div className="max-w-4xl mx-auto">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl font-bold text-gray-200 mb-2">
                                Welcome to GovGPT Policy Analysis
                            </h2>
                            <p className="text-gray-400">
                                Get data-driven insights on Kenya government policies with RAG, news, and sentiment analysis
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {examplePrompts.map((prompt, i) => (
                                <button
                                    key={i}
                                    onClick={() => sendMessage(prompt)}
                                    className="p-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-left transition-all hover:shadow-lg hover:shadow-emerald-500/20 border border-gray-700 hover:border-emerald-500/50"
                                >
                                    <p className="text-sm text-gray-300">{prompt}</p>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-3xl ${message.role === 'user'
                                ? 'bg-emerald-600 text-white rounded-2xl rounded-tr-sm'
                                : 'bg-gray-800 text-gray-100 rounded-2xl rounded-tl-sm border border-gray-700'
                                } px-6 py-4 shadow-lg`}
                        >
                            {message.role === 'user' ? (
                                <p className="text-sm leading-relaxed">{message.content}</p>
                            ) : (
                                <>
                                    {isDecisionReport(message.content) ? (
                                        <DecisionReport report={JSON.parse(message.content)} />
                                    ) : (
                                        <FormattedResponse content={message.content} />
                                    )}

                                    {message.sources && message.sources.length > 0 && (
                                        <div className="mt-6 pt-4 border-t border-gray-700">
                                            <h4 className="text-sm font-semibold text-emerald-400 mb-3">📚 Sources</h4>
                                            <div className="space-y-2">
                                                {message.sources.map((source, idx) => (
                                                    <div key={idx} className="text-xs text-gray-400 pl-3 border-l-2 border-emerald-500/30">
                                                        <span className="font-medium text-gray-300">{source.title}</span>
                                                        {source.source && <span className="ml-2">({source.source})</span>}
                                                        {source.relevance && (
                                                            <span className="ml-2 text-emerald-400">
                                                                {(source.relevance * 100).toFixed(0)}% relevant
                                                            </span>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-6 py-4 border border-gray-700">
                            <div className="flex items-center gap-2 text-gray-400">
                                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse delay-75"></div>
                                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse delay-150"></div>
                                <span className="ml-2 text-sm">Analyzing...</span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-800 bg-gray-900/50 backdrop-blur p-6">
                <form
                    onSubmit={(e) => {
                        e.preventDefault()
                        sendMessage(input)
                    }}
                    className="max-w-4xl mx-auto flex gap-3"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about Kenya policies, budgets, impact analysis..."
                        className="flex-1 bg-gray-800 text-white px-6 py-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 border border-gray-700 placeholder-gray-500"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-4 rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-emerald-500/50"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    )
}
