import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { projectApi } from '../lib/api';
import { useStore } from '../lib/store';
import { HiOutlinePlus, HiOutlineTrash, HiOutlineEye } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function Projects() {
  const router = useRouter();
  const user = useStore((s) => s.user);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (user) loadProjects();
  }, [user]);

  const loadProjects = async () => {
    try {
      const res = await projectApi.list(user!.uid);
      setProjects(res.data.projects || []);
    } catch (err) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (id: string) => {
    try {
      await projectApi.delete(id);
      setProjects(projects.filter((p) => p.id !== id));
      toast.success('Project deleted');
    } catch {
      toast.error('Failed to delete');
    }
  };

  const filtered = filter === 'all' ? projects : projects.filter((p) => p.status === filter);
  const counts = {
    all: projects.length,
    pending: projects.filter((p) => p.status === 'pending').length,
    processing: projects.filter((p) => ['processing', 'preview_ready', 'rendered'].includes(p.status)).length,
    published: projects.filter((p) => p.status === 'published').length,
    failed: projects.filter((p) => p.status === 'failed').length,
  };

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      pending: 'badge-warning', processing: 'badge-info',
      preview_ready: 'badge-info', rendered: 'badge-info',
      published: 'badge-success', failed: 'badge-error',
    };
    return map[status] || 'badge';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-slate-400">{projects.length} total projects</p>
        </div>
        <button onClick={() => router.push('/create')} className="btn-primary flex items-center gap-2">
          <HiOutlinePlus size={18} /> New Project
        </button>
      </div>

      <div className="flex gap-2 flex-wrap">
        {Object.entries(counts).map(([key, count]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === key ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            {key.charAt(0).toUpperCase() + key.slice(1)} ({count})
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="loading h-10 w-10"></div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-20 text-slate-500">
          <HiOutlineEye size={48} className="mx-auto mb-4" />
          <p className="text-lg">No projects found</p>
          <button onClick={() => router.push('/create')} className="btn-primary mt-4">
            Create your first project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((project) => (
            <div key={project.id} className="card hover:border-indigo-500/50 transition-colors cursor-pointer group"
                 onClick={() => router.push(`/project?id=${project.id}`)}>
              <div className="flex items-start justify-between mb-3">
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold truncate">{project.title}</h3>
                  <p className="text-sm text-slate-400 truncate">{project.artist || 'Unknown'}</p>
                </div>
                <span className={statusBadge(project.status)}>{project.status}</span>
              </div>

              {project.song_url && (
                <p className="text-xs text-slate-500 truncate mb-2">{project.song_url}</p>
              )}

              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>{project.resolution || '1920x1080'} • {project.fps || 60}fps</span>
                <span>{new Date(project.created_at).toLocaleDateString()}</span>
              </div>

              {project.youtube_video_id && (
                <div className="mt-2 text-xs text-green-400">
                  Published: youtube.com/watch?v={project.youtube_video_id}
                </div>
              )}

              <div className="mt-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="btn-primary text-xs py-1 px-3" onClick={(e) => {
                  e.stopPropagation();
                  router.push(`/project?id=${project.id}`);
                }}>
                  View
                </button>
                <button className="btn-danger text-xs py-1 px-3" onClick={(e) => {
                  e.stopPropagation();
                  deleteProject(project.id);
                }}>
                  <HiOutlineTrash size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
