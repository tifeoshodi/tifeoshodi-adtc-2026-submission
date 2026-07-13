import { useState, useRef, useEffect } from 'react';
import { 
  Sprout, 
  WifiOff, 
  Cpu, 
  Send, 
  Leaf, 
  Bug, 
  CloudRain,
  User,
  Bot
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  context?: string[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello. I am your Offline Agricultural Assistant. I am running locally on this device. How can I help you with your farm today?',
      sender: 'bot'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Skip the first welcome message to save tokens
    const history = messages.slice(1).map(m => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.text
    }));

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history })
      });
      
      const data = await response.json();
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.reply,
        sender: 'bot',
        context: data.context_used
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error fetching response:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm having trouble connecting to the local AI engine. Please ensure the backend is running.",
        sender: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriage = (query: string) => {
    handleSend(query);
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Sprout size={24} />
          </div>
          <span>AgriTriage AI</span>
        </div>

        <div className="status-panel">
          <div className="status-item">
            <div className="status-indicator"></div>
            <span>Offline Mode Active</span>
            <WifiOff size={16} style={{ marginLeft: 'auto' }} />
          </div>
          <div className="status-item">
            <Cpu size={16} />
            <span>Llama-3.2-1B (4-bit)</span>
          </div>
        </div>

        <div className="quick-triage">
          <h3>Quick Triage</h3>
          <button className="triage-btn" onClick={() => handleTriage("Identify Cassava Mosaic Disease")}>
            <Leaf size={18} />
            Cassava Disease
          </button>
          <button className="triage-btn" onClick={() => handleTriage("Pest control for Maize")}>
            <Bug size={18} />
            Maize Pests
          </button>
          <button className="triage-btn" onClick={() => handleTriage("Optimal Yam storage techniques")}>
            <CloudRain size={18} />
            Yam Storage
          </button>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="main-chat">
        <div className="chat-header">
          <h2>Extension Officer Dashboard</h2>
          <p>Local RAG enabled • Zero latency • Privacy preserved</p>
        </div>

        <div className="messages-container">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              <div className="avatar">
                {msg.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div className="message-content">
                {msg.sender === 'bot' ? (
                  <div className="markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.text}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p>{msg.text}</p>
                )}
                {msg.context && msg.context.length > 0 && (
                  <details className="context-box">
                    <summary><strong>View Source Material ({msg.context.length} chunks)</strong></summary>
                    <div className="context-content">
                      {msg.context.map((ctx, idx) => (
                        <div key={idx} className="context-chunk">
                          <p>{ctx}</p>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message bot">
              <div className="avatar"><Bot size={20} /></div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <form 
            className="input-wrapper" 
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(inputValue);
            }}
          >
            <input 
              type="text" 
              placeholder="Ask about crops, diseases, or market prices..." 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="send-btn" 
              disabled={isLoading || !inputValue.trim()}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
