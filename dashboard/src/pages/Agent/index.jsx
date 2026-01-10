import React, { useState, useRef, useEffect } from 'react';
import { agentService, chatService } from '../../services/api';
import { Bot, Send, User, Sparkles, Loader2, MessageSquare, Plus, Trash2, X, Edit2, Check } from 'lucide-react';
import PageHeader from '../../components/Common/PageHeader';
import './Agent.css';

const Agent = () => {
    const [conversations, setConversations] = useState([]);
    const [activeConversationId, setActiveConversationId] = useState(null);
    const [messages, setMessages] = useState([{
        role: 'assistant',
        text: "Hello! I'm your assistant AI Agent. How can I help you analyze the tracking data today?"
    }]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [loadingConversations, setLoadingConversations] = useState(true);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [editingTitleId, setEditingTitleId] = useState(null);
    const [tempTitle, setTempTitle] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Load conversations on mount
    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            const response = await chatService.listConversations();
            setConversations(response.data.conversations);


        } catch (error) {
            console.error('Error loading conversations:', error);
        } finally {
            setLoadingConversations(false);
        }
    };

    const loadConversation = async (conversationId) => {
        try {
            const response = await chatService.getConversation(conversationId);
            setActiveConversationId(conversationId);

            // Convert stored messages format to display format
            const displayMessages = response.data.messages.map(msg => ({
                role: msg.role,
                text: msg.content,
                status: msg.status
            }));

            // Add welcome message if conversation is empty
            if (displayMessages.length === 0) {
                displayMessages.push({
                    role: 'assistant',
                    text: "Hello! I'm your assistant AI Agent. How can I help you analyze the tracking data today?"
                });
            }

            setMessages(displayMessages);
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    };

    const createNewConversation = () => {
        // Don't persist to backend yet - only create local UI state
        // Conversation will be created when user sends their first message
        setActiveConversationId(null);
        setMessages([{
            role: 'assistant',
            text: "Hello! I'm your assistant AI Agent. How can I help you analyze the tracking data today?"
        }]);
    };

    const deleteConversation = async (conversationId, e) => {
        e.stopPropagation();

        try {
            await chatService.deleteConversation(conversationId);
            setConversations(prev => prev.filter(c => c.id !== conversationId));

            // If deleted the active conversation, select another or clear
            if (activeConversationId === conversationId) {
                const remaining = conversations.filter(c => c.id !== conversationId);
                if (remaining.length > 0) {
                    loadConversation(remaining[0].id);
                } else {
                    setActiveConversationId(null);
                    setMessages([]);
                }
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
        }
    };

    const startEditingTitle = (conv, e) => {
        e.stopPropagation();
        setEditingTitleId(conv.id);
        setTempTitle(conv.title);
    };

    const handleUpdateTitle = async (conversationId, e) => {
        if (e) e.stopPropagation();
        if (!tempTitle.trim()) {
            setEditingTitleId(null);
            return;
        }

        try {
            await chatService.updateConversationTitle(conversationId, tempTitle.trim());
            setConversations(prev => prev.map(c =>
                c.id === conversationId ? { ...c, title: tempTitle.trim() } : c
            ));
            setEditingTitleId(null);
        } catch (error) {
            console.error('Error updating title:', error);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');

        // Ensure we have an active conversation
        let currentConversationId = activeConversationId;
        if (!currentConversationId) {
            try {
                const response = await chatService.createConversation();
                currentConversationId = response.data.id;
                setConversations(prev => [response.data, ...prev]);
                setActiveConversationId(currentConversationId);
            } catch (error) {
                console.error('Error creating conversation:', error);
                return;
            }
        }

        // Add user message to UI and persist
        setMessages(prev => [...prev, { role: 'user', text: userMessage }]);

        try {
            await chatService.addMessage(currentConversationId, 'user', userMessage);
        } catch (error) {
            console.error('Error saving user message:', error);
        }

        setLoading(true);

        try {
            const response = await agentService.runTask(userMessage, currentConversationId);
            const assistantMessage = {
                role: 'assistant',
                text: response.data.result,
                status: response.data.status
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Persist assistant response
            await chatService.addMessage(currentConversationId, 'assistant', response.data.result, response.data.status);

            // Refresh conversation list to update titles
            loadConversations();
        } catch (error) {
            console.error('Agent error:', error);
            const errorMessage = {
                role: 'assistant',
                text: "I encountered an error while processing your request. Please ensure the backend is running and try again.",
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();

        // Reset times to compare dates only
        const dateJust = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        const nowJust = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        const diffTime = nowJust - dateJust;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="agent-page">
            <PageHeader
                title="AI Agent"
                icon={Bot}
                description="Harness AI power to analyze your tracking data through your language."
                gradient="linear-gradient(to right, #a78bfa, #c084fc)"
                iconColor="#a78bfa"
                iconBgColor="rgba(167, 139, 250, 0.1)"
            />

            <div className="agent-layout">
                {/* Conversation Sidebar */}
                <div className={`conversation-sidebar ${sidebarOpen ? 'open' : 'collapsed'}`}>
                    <div className="sidebar-header">
                        <h3>Conversations</h3>
                        <button className="new-chat-btn" onClick={createNewConversation} title="New Chat">
                            <Plus size={18} />
                        </button>
                    </div>

                    <div className="conversation-list">
                        {loadingConversations ? (
                            <div className="loading-conversations">
                                <Loader2 size={20} className="spin" />
                                <span>Loading...</span>
                            </div>
                        ) : conversations.length === 0 ? (
                            <div className="no-conversations">
                                <MessageSquare size={32} />
                                <p>No conversations yet</p>
                                <button onClick={createNewConversation}>Start a new chat</button>
                            </div>
                        ) : (
                            conversations.map(conv => (
                                <div
                                    key={conv.id}
                                    className={`conversation-item ${activeConversationId === conv.id ? 'active' : ''}`}
                                    onClick={() => loadConversation(conv.id)}
                                >
                                    <div className="conversation-info">
                                        {editingTitleId === conv.id ? (
                                            <div className="title-edit-wrapper" onClick={e => e.stopPropagation()}>
                                                <input
                                                    type="text"
                                                    value={tempTitle}
                                                    onChange={e => setTempTitle(e.target.value)}
                                                    onKeyPress={e => e.key === 'Enter' && handleUpdateTitle(conv.id)}
                                                    onBlur={() => handleUpdateTitle(conv.id)}
                                                    autoFocus
                                                />
                                                <button onClick={() => handleUpdateTitle(conv.id)} className="save-title-btn">
                                                    <Check size={14} />
                                                </button>
                                            </div>
                                        ) : (
                                            <>
                                                <span className="conversation-title">{conv.title}</span>
                                                <span className="conversation-date">{formatDate(conv.updated_at)}</span>
                                            </>
                                        )}
                                    </div>
                                    <div className="conversation-actions">
                                        {editingTitleId !== conv.id && (
                                            <button
                                                className="action-btn edit-btn"
                                                onClick={(e) => startEditingTitle(conv, e)}
                                                title="Edit title"
                                            >
                                                <Edit2 size={14} />
                                            </button>
                                        )}
                                        <button
                                            className="action-btn delete-btn"
                                            onClick={(e) => deleteConversation(conv.id, e)}
                                            title="Delete conversation"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Toggle Sidebar Button */}
                <button
                    className="sidebar-toggle"
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    title={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
                >
                    {sidebarOpen ? <X size={16} /> : <MessageSquare size={16} />}
                </button>

                {/* Chat Container */}
                <div className="chat-container glass">
                    <div className="chat-messages">
                        {messages.length === 0 && !loadingConversations ? (
                            <div className="empty-chat">
                                <Bot size={48} />
                                <h3>Start a New Conversation</h3>
                                <p>Ask me anything about your tracking data!</p>
                            </div>
                        ) : (
                            messages.map((msg, index) => (
                                <div key={index} className={`message-wrapper ${msg.role}`}>
                                    <div className="message-icon">
                                        {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
                                    </div>
                                    <div className={`message-bubble ${msg.isError ? 'error' : ''}`}>
                                        <div className="message-text">{msg.text}</div>
                                    </div>
                                </div>
                            ))
                        )}
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
                                placeholder="Ask me anything (e.g., 'Who is the most frequently late?')"
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
                        <p className="input-hint">LLMs can make your life easier by automating tasks and providing insights but also can make mistakes.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Agent;
