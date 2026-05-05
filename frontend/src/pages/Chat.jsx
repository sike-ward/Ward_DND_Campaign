import { useState, useRef, useEffect } from 'react';
import SectionHeader from '@/components/SectionHeader';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { TextArea } from '@/components/Input';
import { ai } from '@/api';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const nextId = () => `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  const handleAsk = async () => {
    if (!prompt.trim() || loading) return;

    const userMessage = { id: nextId(), role: 'user', content: prompt };
    setMessages((prev) => [...prev, userMessage]);
    setPrompt('');
    setLoading(true);

    try {
      const response = await ai.ask(prompt);
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: 'assistant', content: response.response },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: 'error', content: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setPrompt('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAsk();
    }
  };

  return (
    <div className="p-10 space-y-6 flex flex-col h-full">
      {/* Header */}
      <SectionHeader
        title="✦ AI Assistant"
        subtitle="Ask anything about your world, lore, or notes."
      />

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-5xl mb-4">✦</div>
              <p className="text-txt-secondary">
                No messages yet. Ask something to get started.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-4 rounded-xl ${
                  msg.role === 'user'
                    ? 'bg-accent/10 text-txt'
                    : msg.role === 'error'
                      ? 'bg-danger/10 text-danger border border-danger/20'
                      : 'bg-card text-txt'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <Card className="px-4 py-4 max-w-xs lg:max-w-md">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                <p className="text-txt-secondary text-sm">Thinking...</p>
              </div>
            </Card>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <Card className="p-6 space-y-4">
        <TextArea
          placeholder="Ask about your world..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <div className="flex gap-3">
          <Button
            variant="primary"
            onClick={handleAsk}
            disabled={loading || !prompt.trim()}
            className="flex-1"
          >
            {loading ? 'Thinking...' : '✦ Ask AI'}
          </Button>
          <Button
            variant="ghost"
            onClick={handleClear}
            disabled={loading}
            className="flex-1"
          >
            Clear
          </Button>
        </div>
      </Card>
    </div>
  );
}
