import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { bulkApi } from '../lib/api';
import { useStore } from '../lib/store';
import { HiOutlineCollection, HiOutlinePlay, HiOutlineStop, HiOutlineRefresh } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function BulkPage() {
  const router = useRouter();
  const user = useStore((s) => s.user);
  const autoMode = useStore((s) => s.autoMode);
  const setAutoMode = useStore((s) => s.setAutoMode);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (user) loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, [user]);

  const loadStatus = async () => {
    try {
      const res = await bulkApi.status(user!.uid);
      setStatus(res.data);
    } catch {} finally {
      setLoading(false);
    }
  };

  const startAutoMode = async () => {
    setProcessing(true);
    try {
      await bulkApi.autoStart(user!.uid);
      setAutoMode(true);
      toast.success('Auto mode enabled!');
    } catch {
      toast.error('Failed to start auto mode');
    } finally {
      setProcessing(false);
    }
  };

  const processFromTrending = async () => {
    setProcessing(true);
    try {
      const res = await bulkApi.fromTrending(user!.uid, 10, false);
      toast.success(`Created ${res.data.count} projects from trending!`);
      loadStatus();
    } catch {
      toast.error('Failed');
    } finally {
      setProcessing(false);
    }
  };

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-500/20 text-yellow-300',
    processing: 'bg-blue-500/20 text-blue-300',
    preview_ready: 'bg-blue-500/20 text-blue-300',
    rendered: 'bg-blue-500/20 text-blue-300',
    published: 'bg-green-500/20 text-green-300',
    failed: 'bg-red-500/20 text-red-300',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Bulk Processing</h1>
          <p className="text-slate-400">Process multiple songs automatically</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Auto Mode</span>
            <div
              className={`w-10 h-6 rounded-full cursor-pointer transition-colors ${
                autoMode ? 'bg-green-600' : 'bg-slate-600'
              }`}
              onClick={() => setAutoMode(!autoMode)}
            >
              <div className={`w-4 h-4 bg-white rounded-full m-1 transition-transform ${autoMode ? 'translate-x-4' : ''}`} />
            </div>
          </div>
          <button onClick={loadStatus} className="btn-secondary text-sm"><HiOutlineRefresh size={16} /></button>
        </div>
      </div>

      {status && (
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total', value: status.total, color: 'text-blue-400' },
            { label: 'Completed', value: status.completed, color: 'text-green-400' },
            { label: 'Processing', value: status.processing, color: 'text-yellow-400' },
            { label: 'Failed', value: status.failed, color: 'text-red-400' },
          ].map((s) => (
            <div key={s.label} className="card text-center">
              <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-sm text-slate-400">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={processFromTrending}
          disabled={processing}
          className="card hover:border-indigo-500/50 transition-colors text-left group"
        >
          <HiOutlineCollection size={32} className="text-indigo-400 mb-3" />
          <h3 className="font-semibold">Process Trending Songs</h3>
          <p className="text-sm text-slate-400">Create projects from the latest trending songs</p>
        </button>

        <button
          onClick={startAutoMode}
          disabled={processing}
          className="card hover:border-green-500/50 transition-colors text-left group"
        >
          <HiOutlinePlay size={32} className="text-green-400 mb-3" />
          <h3 className="font-semibold">Start Auto Mode</h3>
          <p className="text-sm text-slate-400">Continuously discover, create, render, and upload</p>
          {autoMode && <span className="badge-success mt-2 inline-block">Active</span>}
        </button>
      </div>

      {status?.projects?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">Recent Bulk Projects</h2>
          <div className="space-y-2">
            {status.projects.map((p: any) => (
              <div
                key={p.id}
                className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors"
                onClick={() => router.push(`/project?id=${p.id}`)}
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate">{p.title}</p>
                  <p className="text-xs text-slate-400">{new Date(p.created_at).toLocaleString()}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[p.status] || 'bg-slate-600 text-slate-300'}`}>
                  {p.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && !status?.projects?.length && (
        <div className="card text-center py-12 text-slate-500">
          <HiOutlineCollection size={48} className="mx-auto mb-3" />
          <p>No bulk projects yet</p>
          <p className="text-sm">Start by processing trending songs or enabling auto mode</p>
        </div>
      )}
    </div>
  );
}
