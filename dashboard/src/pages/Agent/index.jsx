import React, { useState, useRef, useEffect } from 'react';
import { agentService } from '../../services/api';
import { Bot, Send, User, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import './Agent.css';

const Agent = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: "Hello! I'm your Orchestration Agent. How can I help you analyze the tracking data today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
        setLoading(true);

        try {
            const response = await agentService.runTask(userMessage);
            setMessages(prev => [...prev, {
                role: 'assistant',
                text: response.data.result,
                status: response.data.status
            }]);
        } catch (error) {
            console.error('Agent error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                text: "I encountered an error while processing your request. Please ensure the backend is running and try again.",
                isError: true
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="agent-page">
            <div className="page-header">
                <h1>Orchestration Agent</h1>
                <p>Harness the power of AI to analyze your tracking data through natural language.</p>
            </div>

            <div className="chat-container glass">
                <div className="chat-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message-wrapper ${msg.role}`}>
                            <div className="message-icon">
                                {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
                            </div>
                            <div className={`message-bubble ${msg.isError ? 'error' : ''}`}>
                                <div className="message-text">{msg.text}</div>
                                {msg.status && <div className="message-status">Status: {msg.status}</div>}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="message-wrapper assistant">
                            <div className="message-icon">
                                <Bot size={18} />
                            </div>
                            <div className="message-bubble loading">
                                <Loader2 size={18} className="spin" />
                                <span>Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    <div className="input-wrapper">
                        <Sparkles size={18} className="input-decorator" />
                        <input
                            type="text"
                            placeholder="Ask me anything (e.g., 'Identify groups in Coaching session')"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        />
                        <button
                            className={`send-btn ${input.trim() ? 'active' : ''}`}
                            onClick={handleSend}
                            disabled={loading || !input.trim()}
                        >
                            <Send size={18} />
                        </button>
                    </div>
                    <p className="input-hint">Enter your task and the agent will coordinate sub-agents to provide results.</p>
                </div>
            </div>
        </div>
    );
};

export default Agent;
