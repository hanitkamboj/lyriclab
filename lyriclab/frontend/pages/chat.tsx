import { useState, useEffect, useRef } from 'react';
import { chatApi } from '../lib/api';
import { useStore } from '../lib/store';
import { HiOutlineSend, HiOutlineChat, HiOutlineLightningBolt, HiOutlineCommandLine } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function ChatPage() {
  const user = useStore((s) => s.user);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user) loadHistory();
  }, [user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const res = await chatApi.history(user!.uid);
      const msgs = res.data.messages || [];
      setMessages(msgs.map((m: any) => ({
        role: m.role,
        content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content),
        timestamp: m.timestamp,
      })));
      if (msgs.length > 0) {
        setSessionId(msgs[0].session_id);
      }
    } catch {}
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatApi.send(input, user!.uid, sessionId || undefined);
      const data = res.data.response;
      setSessionId(res.data.session_id);

      const assistantMsg = {
        role: 'assistant',
        content: typeof data === 'string' ? data : formatResponse(data),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      if (data?.command === 'help') {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `Available commands:\n• research - Find trending songs\n• create title=Song Artist=Artist song_url=URL - New project\n• preview project_id=ID - Generate preview\n• render project_id=ID - Full render\n• upload project_id=ID - Upload to YouTube\n• bulk auto_mode=true - Batch process\n• auto - Enable auto mode\n• status - Check progress\n• analyze video_id=ID - Analyze style`,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (err: any) {
      toast.error('Failed to send message');
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error: Failed to process command', timestamp: new Date().toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const formatResponse = (data: any): string => {
    if (!data) return 'No response';
    if (typeof data === 'string') return data;

    let text = data.message || '';
    if (data.songs) {
      text += '\n\nTrending songs:\n';
      data.songs.slice(0, 10).forEach((s: any, i: number) => {
        text += `${i + 1}. ${s.title} - ${s.artist || 'Unknown'} [${s.source}]\n`;
      });
    }
    if (data.preview_path) text += `\nPreview: ${data.preview_path}`;
    if (data.output_path) text += `\nOutput: ${data.output_path}`;
    if (data.video_id) text += `\nYouTube: https://youtube.com/watch?v=${data.video_id}`;
    if (data.project_id) text += `\nProject ID: ${data.project_id}`;

    return text;
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Agent Chat</h1>
          <p className="text-slate-400">Control LyricLab with natural language</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <HiOutlineCommandLine size={14} />
          Type "help" for commands
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 mb-4 card">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <HiOutlineChat size={48} className="mb-3" />
            <p className="text-lg">Welcome to LyricLab Agent!</p>
            <p className="text-sm">Try: "research", "create title=..., "auto", or "help"</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-700 text-slate-200'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 rounded-xl px-4 py-2.5">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a command (e.g., 'create title=Hello artist=World')"
          className="input flex-1"
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()} className="btn-primary px-6">
          <HiOutlineSend size={18} />
        </button>
      </div>
    </div>
  );
}
