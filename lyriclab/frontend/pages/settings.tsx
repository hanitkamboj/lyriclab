import { useState, useEffect } from 'react';
import { youtubeApi, ollamaApi } from '../lib/api';
import { useStore } from '../lib/store';
import { HiOutlineLink, HiOutlineTrash, HiOutlineChip, HiOutlineKey, HiOutlineGlobe } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const user = useStore((s) => s.user);
  const [channels, setChannels] = useState<any[]>([]);
  const [ollamaConfigs, setOllamaConfigs] = useState<any[]>([]);
  const [ollamaForm, setOllamaForm] = useState({ name: '', baseUrl: 'http://localhost:11434', modelName: 'llama3.1' });
  const [authUrl, setAuthUrl] = useState('');

  useEffect(() => {
    if (user) {
      loadChannels();
      loadOllamaConfigs();
    }
  }, [user]);

  const loadChannels = async () => {
    try {
      const res = await youtubeApi.channels(user!.uid);
      setChannels(res.data.channels || []);
    } catch {}
  };

  const loadOllamaConfigs = async () => {
    try {
      const res = await ollamaApi.getConfigs(user!.uid);
      setOllamaConfigs(res.data.configs || []);
    } catch {}
  };

  const connectYouTube = async () => {
    try {
      const res = await youtubeApi.authUrl();
      setAuthUrl(res.data.auth_url);
      window.open(res.data.auth_url, '_blank', 'width=600,height=700');
    } catch {
      toast.error('Failed to get auth URL');
    }
  };

  const handleAuthCode = async () => {
    const code = prompt('Paste the authorization code from the URL:');
    if (!code) return;
    try {
      const res = await youtubeApi.connect(code, user!.uid);
      toast.success(`Connected to ${res.data.channel.title}`);
      loadChannels();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Connection failed');
    }
  };

  const disconnectChannel = async (channelId: string) => {
    try {
      await youtubeApi.disconnect(channelId);
      toast.success('Disconnected');
      loadChannels();
    } catch {
      toast.error('Failed to disconnect');
    }
  };

  const saveOllamaConfig = async () => {
    if (!ollamaForm.name || !ollamaForm.baseUrl || !ollamaForm.modelName) {
      toast.error('All fields required');
      return;
    }
    try {
      await ollamaApi.saveConfig(user!.uid, ollamaForm.name, ollamaForm.baseUrl, ollamaForm.modelName);
      toast.success('Ollama config saved');
      loadOllamaConfigs();
      setOllamaForm({ name: '', baseUrl: 'http://localhost:11434', modelName: 'llama3.1' });
    } catch {
      toast.error('Failed to save config');
    }
  };

  const deleteOllamaConfig = async (configId: string) => {
    try {
      await ollamaApi.deleteConfig(configId);
      toast.success('Config deleted');
      loadOllamaConfigs();
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-slate-400">Configure integrations and preferences</p>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <HiOutlineLink className="text-red-400" size={20} />
          <h2 className="text-lg font-semibold">YouTube Channels</h2>
        </div>

        {channels.length > 0 ? (
          <div className="space-y-3">
            {channels.map((ch) => (
              <div key={ch.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <div>
                  <p className="font-medium">{ch.channel_name || 'YouTube Channel'}</p>
                  <p className="text-xs text-slate-400">ID: {ch.channel_id}</p>
                </div>
                <button onClick={() => disconnectChannel(ch.id)} className="btn-danger text-sm py-1 px-3">
                  <HiOutlineTrash size={14} /> Disconnect
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500">
            <p className="mb-3">No YouTube channels connected</p>
            <button onClick={connectYouTube} className="btn-primary">
              Connect YouTube
            </button>
            <button onClick={handleAuthCode} className="btn-secondary ml-2">
              Paste Auth Code
            </button>
          </div>
        )}
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <HiOutlineChip className="text-purple-400" size={20} />
          <h2 className="text-lg font-semibold">Custom AI (Ollama)</h2>
        </div>
        <p className="text-sm text-slate-400 mb-4">
          Connect your own Ollama instance running on Kaggle or any server. Provide the base URL and model name.
        </p>

        <div className="grid grid-cols-3 gap-3 mb-4">
          <input className="input" placeholder="Config name" value={ollamaForm.name}
            onChange={(e) => setOllamaForm({...ollamaForm, name: e.target.value})} />
          <input className="input" placeholder="Base URL (e.g., https://xxx.cloudflare.dev)"
            value={ollamaForm.baseUrl} onChange={(e) => setOllamaForm({...ollamaForm, baseUrl: e.target.value})} />
          <input className="input" placeholder="Model name (e.g., llama3.1)"
            value={ollamaForm.modelName} onChange={(e) => setOllamaForm({...ollamaForm, modelName: e.target.value})} />
        </div>
        <button onClick={saveOllamaConfig} className="btn-primary">Save Config</button>

        {ollamaConfigs.length > 0 && (
          <div className="mt-4 space-y-2">
            {ollamaConfigs.map((cfg) => (
              <div key={cfg.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <div>
                  <p className="font-medium">{cfg.name || cfg.model_name}</p>
                  <p className="text-xs text-slate-400">{cfg.base_url} / {cfg.model_name}</p>
                </div>
                <button onClick={() => deleteOllamaConfig(cfg.id)} className="btn-danger text-sm py-1 px-3">
                  <HiOutlineTrash size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <HiOutlineKey className="text-yellow-400" size={20} />
          <h2 className="text-lg font-semibold">API Keys</h2>
        </div>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between p-2 bg-slate-700/50 rounded">
            <span className="text-slate-400">YouTube Data API</span>
            <span className="text-green-400">Configured ✓</span>
          </div>
          <div className="flex justify-between p-2 bg-slate-700/50 rounded">
            <span className="text-slate-400">Pexels API</span>
            <span className="text-green-400">Configured ✓</span>
          </div>
          <div className="flex justify-between p-2 bg-slate-700/50 rounded">
            <span className="text-slate-400">Firebase</span>
            <span className="text-green-400">Configured ✓</span>
          </div>
          <div className="flex justify-between p-2 bg-slate-700/50 rounded">
            <span className="text-slate-400">GitHub Token</span>
            <span className="text-green-400">Configured ✓</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <HiOutlineGlobe className="text-blue-400" size={20} />
          <h2 className="text-lg font-semibold">About LyricLab</h2>
        </div>
        <div className="text-sm text-slate-400 space-y-2">
          <p>Version: 1.0.0</p>
          <p>Status: {user ? 'Signed in' : 'Not signed in'}</p>
          <p>User: {user?.email || 'N/A'}</p>
          <p className="text-xs text-slate-500 mt-3">
            LyricLab is a non-profit project. All videos are created for educational and entertainment purposes.
          </p>
        </div>
      </div>
    </div>
  );
}
