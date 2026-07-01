import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, getAIStatus, getAutoInsights } from '../api/assistant';
import useDashboardStore from '../store/useDashboardStore';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Loader from '../components/ui/Loader';
import { Send, Bot, Sparkles, RefreshCcw } from 'lucide-react';
import './AIAssistant.css';

const AIAssistant = () => {
  const { overview } = useDashboardStore();
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "Hello! I am your Sentry Fab AI assistant. I can analyze sensor anomalies, recommend maintenance windows, or evaluate your inventory forecasting. Ask me anything about the factory floor operations.",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [aiAvailable, setAiAvailable] = useState(false);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([
    "What equipment needs maintenance soon?",
    "Summarize today's defect detections",
    "Show inventory status overview",
  ]);
  const [insightsLoading, setInsightsLoading] = useState(false);

  const historyEndRef = useRef(null);

  useEffect(() => {
    getAIStatus()
      .then((status) => setAiAvailable(status.available))
      .catch(console.error);
  }, []);

  useEffect(() => {
    // Scroll chat history to bottom
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const text = textToSend || inputText;
    if (!text.trim() || loading) return;

    // Append user message
    const userMsg = {
      sender: 'user',
      text: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    // Prepare context
    const context = overview ? {
      total_equipment: overview.total_equipment,
      operational_count: overview.operational_count,
      avg_health_score: overview.avg_health_score,
      total_defects_today: overview.total_defects_today,
      low_stock_items: overview.inventory_low_stock,
    } : null;

    try {
      const reply = await sendChatMessage(text, context);
      const assistantMsg = {
        sender: 'assistant',
        text: reply.response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (reply.suggestions) {
        setSuggestions(reply.suggestions);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: "I encountered a communication error with the LLM API. Please check your network and settings.",
          timestamp: new Date().toISOString(),
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleGetInsights = async () => {
    setInsightsLoading(true);
    setMessages((prev) => [
      ...prev,
      {
        sender: 'user',
        text: "Generate automated plant insights summary",
        timestamp: new Date().toISOString(),
      }
    ]);
    try {
      const data = await getAutoInsights();
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: data.response,
          timestamp: new Date().toISOString(),
        }
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setInsightsLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ position: 'relative' }}>
      <div className="starfield-bg"></div>

      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
            AI <span style={{ backgroundColor: 'var(--color-accent-lime)', color: 'var(--color-ink-deep)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Assistant</span>
          </h2>
          <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
            Natural language analysis of telemetry anomalies, defects records, and supply status.
          </p>
        </div>

        {aiAvailable && (
          <Button variant="ghost" onClick={handleGetInsights} disabled={insightsLoading}>
            <Sparkles size={16} style={{ color: 'var(--color-accent-lime)' }} />
            {insightsLoading ? 'Analyzing...' : 'Generate Insights'}
          </Button>
        )}
      </div>

      <div className="assistant-layout">
        {/* Chat History Panel */}
        <div className="chat-panel">
          <div className="chat-history">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.sender}`}>
                <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
                <span className="chat-message-meta">{msg.sender}</span>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <Loader type="spinner" />
                <span className="chat-message-meta">LLM THINKING...</span>
              </div>
            )}
            <div ref={historyEndRef}></div>
          </div>

          {/* Input Area */}
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }} 
            className="chat-input-area"
          >
            <input 
              type="text" 
              className="chat-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={aiAvailable ? "Ask about anomalies, defects, or inventory..." : "AI configured prompts display. Connect Groq key in Settings."}
              disabled={loading || !aiAvailable}
            />
            <Button type="submit" disabled={loading || !inputText.trim() || !aiAvailable} style={{ padding: '12px' }}>
              <Send size={18} />
            </Button>
          </form>
        </div>

        {/* Suggestion Prompts Column */}
        <div className="prompt-suggestions-panel">
          <h4 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>
            Suggested Queries
          </h4>
          {suggestions.map((s, idx) => (
            <button 
              key={idx} 
              className="suggestion-pill"
              onClick={() => handleSend(s)}
              disabled={loading || !aiAvailable}
            >
              {s}
            </button>
          ))}

          {!aiAvailable && (
            <Card style={{ backgroundColor: 'var(--color-ink-deep)', borderStyle: 'dashed', marginTop: '16px' }}>
              <h5 style={{ color: 'var(--color-accent-pink)', marginBottom: '8px' }}>Groq Offline</h5>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-on-dark-muted)' }}>
                Please set a valid <strong>GROQ_API_KEY</strong> environment variable in your backend config to enable this feature.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
