import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useStore } from '../lib/store';
import { projectApi, trendingApi, bulkApi } from '../lib/api';
import {
  HiOutlineMusicNote, HiOutlineVideoCamera, HiOutlineUpload,
  HiOutlineTrendingUp, HiOutlineCollection, HiOutlineLightningBolt,
} from 'react-icons/hi';

export default function Dashboard() {
  const router = useRouter();
  const user = useStore((s) => s.user);
  const autoMode = useStore((s) => s.autoMode);
  const setAutoMode = useStore((s) => s.setAutoMode);
  const [stats, setStats] = useState({ projects: 0, published: 0, trending: 0 });
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    try {
      const [projRes, trendRes, bulkRes] = await Promise.all([
        projectApi.list(user?.uid || ''),
        trendingApi.get('youtube,billboard', 5),
        bulkApi.status(user?.uid || ''),
      ]);
      setStats({
        projects: projRes.data.projects?.length || 0,
        published: projRes.data.projects?.filter((p: any) => p.status === 'published').length || 0,
        trending: trendRes.data.trending?.length || 0,
      });
      setRecent(projRes.data.projects?.slice(0, 5) || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { label: 'New Project', icon: HiOutlineVideoCamera, path: '/create', color: 'bg-indigo-600' },
    { label: 'Trending', icon: HiOutlineTrendingUp, path: '/trending', color: 'bg-purple-600' },
    { label: 'Bulk Process', icon: HiOutlineCollection, path: '/bulk', color: 'bg-green-600' },
    { label: 'Chat Agent', icon: HiOutlineLightningBolt, path: '/chat', color: 'bg-orange-600' },
  ];

  const statusColors: Record<string, string> = {
    pending: 'badge-warning',
    processing: 'badge-info',
    preview_ready: 'badge-info',
    rendered: 'badge-info',
    published: 'badge-success',
    failed: 'badge-error',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-slate-400">Welcome back, {user?.displayName || user?.email}</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-slate-400">
            <input
              type="checkbox"
              checked={autoMode}
              onChange={(e) => setAutoMode(e.target.checked)}
              className="toggle"
            />
            Auto Mode
          </label>
          <button onClick={() => router.push('/create')} className="btn-primary">
            + New Project
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <HiOutlineMusicNote className="text-indigo-400" size={24} />
            <div>
              <p className="text-2xl font-bold">{stats.projects}</p>
              <p className="text-xs text-slate-400">Total Projects</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <HiOutlineUpload className="text-green-400" size={24} />
            <div>
              <p className="text-2xl font-bold">{stats.published}</p>
              <p className="text-xs text-slate-400">Published</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <HiOutlineTrendingUp className="text-purple-400" size={24} />
            <div>
              <p className="text-2xl font-bold">{stats.trending}</p>
              <p className="text-xs text-slate-400">Trending Songs</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <HiOutlineVideoCamera className="text-orange-400" size={24} />
            <div>
              <p className="text-2xl font-bold">
                {recent.filter((p) => p.status === 'rendered' || p.status === 'preview_ready').length}
              </p>
              <p className="text-xs text-slate-400">Ready to Upload</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            {quickActions.map((action) => (
              <button
                key={action.path}
                onClick={() => router.push(action.path)}
                className={`${action.color} hover:opacity-90 text-white rounded-xl p-4 flex flex-col items-center gap-2 transition-opacity`}
              >
                <action.icon size={28} />
                <span className="text-sm font-medium">{action.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Projects</h2>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="loading h-8 w-8"></div>
            </div>
          ) : recent.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <HiOutlineMusicNote size={40} className="mx-auto mb-2" />
              <p>No projects yet. Create your first one!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {recent.map((project: any) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors"
                  onClick={() => router.push(`/project?id=${project.id}`)}
                >
                  <div className="min-w-0">
                    <p className="font-medium truncate">{project.title}</p>
                    <p className="text-xs text-slate-400">{project.artist || 'Unknown Artist'}</p>
                  </div>
                  <span className={statusColors[project.status] || 'badge'}>
                    {project.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
