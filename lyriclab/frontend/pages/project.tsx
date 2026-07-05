import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { projectApi, youtubeApi } from '../lib/api';
import { useStore } from '../lib/store';
import { HiOutlinePlay, HiOutlineDownload, HiOutlineUpload, HiOutlineTrash, HiOutlineRefresh, HiOutlineEye } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function ProjectDetail() {
  const router = useRouter();
  const { id } = router.query;
  const user = useStore((s) => s.user);
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [seo, setSeo] = useState({ title: '', description: '', tags: [] as string[], category_id: '10' });
  const [privacy, setPrivacy] = useState('public');

  useEffect(() => {
    if (id && user) loadProject();
  }, [id, user]);

  const loadProject = async () => {
    try {
      const res = await projectApi.get(id as string);
      setProject(res.data);
      if (res.data.title) {
        const seoRes = await youtubeApi.generateSeo(res.data.title, res.data.artist || '', '[]');
        setSeo(seoRes.data);
      }
    } catch {
      toast.error('Project not found');
      router.push('/projects');
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    try {
      const res = await projectApi.process(id as string, user!.uid);
      toast.success('Processing complete!');
      loadProject();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Processing failed');
    } finally {
      setProcessing(false);
    }
  };

  const handlePreview = async () => {
    setProcessing(true);
    try {
      const res = await projectApi.preview(id as string, user!.uid);
      toast.success('Preview ready!');
      loadProject();
    } catch (err: any) {
      toast.error(err.message || 'Preview failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleRender = async () => {
    setProcessing(true);
    try {
      const res = await projectApi.render(id as string, user!.uid);
      toast.success('Render complete!');
      loadProject();
    } catch (err: any) {
      toast.error(err.message || 'Render failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleUpload = async () => {
    setProcessing(true);
    try {
      const channelsRes = await youtubeApi.channels(user!.uid);
      const channels = channelsRes.data.channels;
      if (!channels || channels.length === 0) {
        toast.error('Connect YouTube channel first in Settings');
        setProcessing(false);
        return;
      }
      const tokenJson = JSON.stringify({
        token: channels[0].access_token,
        refresh_token: channels[0].refresh_token,
      });
      const res = await projectApi.upload(id as string, tokenJson, privacy, user!.uid);
      toast.success(res.data.message || 'Uploaded!');
      loadProject();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleDelete = async () => {
    await projectApi.delete(id as string);
    toast.success('Project deleted');
    router.push('/projects');
  };

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      pending: 'badge-warning', processing: 'badge-info',
      preview_ready: 'badge-info', rendered: 'badge-info',
      published: 'badge-success', failed: 'badge-error',
    };
    return map[status] || 'badge';
  };

  if (loading) return <div className="flex justify-center py-20"><div className="loading h-10 w-10"></div></div>;
  if (!project) return null;

  const steps = [
    { label: 'Process', done: !!project.audio_path, action: handleProcess, icon: HiOutlineRefresh },
    { label: 'Preview', done: !!project.preview_path, action: handlePreview, icon: HiOutlineEye },
    { label: 'Render', done: !!project.output_path, action: handleRender, icon: HiOutlineDownload },
    { label: 'Upload', done: !!project.youtube_video_id, action: handleUpload, icon: HiOutlineUpload },
  ];

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{project.title}</h1>
          <p className="text-slate-400">{project.artist || 'Unknown Artist'}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={statusBadge(project.status)}>{project.status}</span>
          <button onClick={handleDelete} className="btn-danger text-sm py-1 px-3"><HiOutlineTrash size={14} /></button>
        </div>
      </div>

      <div className="flex gap-3">
        {steps.map((step, i) => (
          <div key={i} className="flex-1">
            <button
              onClick={step.action}
              disabled={processing || step.done}
              className={`w-full py-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-all ${
                step.done ? 'bg-green-600 text-white cursor-default' : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
              } ${processing ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <step.icon size={16} />
              {step.done ? `${step.label} ✓` : step.label}
            </button>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-3">Video Preview</h2>
            {project.preview_path ? (
              <video controls className="w-full rounded-lg" src={`${backendUrl}/output/${project.preview_path.split('/').pop()}`}>
                Your browser does not support video.
              </video>
            ) : (
              <div className="bg-slate-700 rounded-lg h-64 flex items-center justify-center text-slate-500">
                <HiOutlinePlay size={48} />
                <p className="ml-2">Preview not generated yet</p>
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-3">SEO & Metadata</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Title</label>
                <input className="input" value={seo.title} onChange={(e) => setSeo({...seo, title: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Description</label>
                <textarea className="input h-24 resize-none" value={seo.description} onChange={(e) => setSeo({...seo, description: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Tags</label>
                <input className="input" value={seo.tags.join(', ')} onChange={(e) => setSeo({...seo, tags: e.target.value.split(',').map(t => t.trim())})} />
              </div>
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-sm text-slate-400 mb-1">Privacy</label>
                  <select className="select" value={privacy} onChange={(e) => setPrivacy(e.target.value)}>
                    <option value="public">Public</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="private">Private</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="block text-sm text-slate-400 mb-1">Category</label>
                  <select className="select" value={seo.category_id} onChange={(e) => setSeo({...seo, category_id: e.target.value})}>
                    <option value="10">Music</option>
                    <option value="22">Entertainment</option>
                    <option value="23">Comedy</option>
                    <option value="24">Education</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-3">Details</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-400">Style</span><span>{project.style}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Resolution</span><span>{project.resolution}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">FPS</span><span>{project.fps}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Bitrate</span><span>{project.bitrate}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Created</span><span>{new Date(project.created_at).toLocaleDateString()}</span></div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-3">Files</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Audio</span>
                <span className={project.audio_path ? 'text-green-400' : 'text-yellow-400'}>{project.audio_path ? '✓' : 'Pending'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Lyrics</span>
                <span className={project.lyrics_path ? 'text-green-400' : 'text-yellow-400'}>{project.lyrics_path ? '✓' : 'Pending'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Background</span>
                <span className={project.background_path ? 'text-green-400' : 'text-yellow-400'}>{project.background_path ? '✓' : 'Auto'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Thumbnail</span>
                <span className={project.thumbnail_path ? 'text-green-400' : 'text-yellow-400'}>{project.thumbnail_path ? '✓' : 'Pending'}</span>
              </div>
            </div>
          </div>

          {project.youtube_video_id && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">Published</h2>
              <a
                href={`https://youtube.com/watch?v=${project.youtube_video_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-400 hover:text-green-300 text-sm break-all"
              >
                youtube.com/watch?v={project.youtube_video_id}
              </a>
            </div>
          )}

          {project.error && (
            <div className="card border-red-600">
              <h2 className="text-lg font-semibold text-red-400 mb-2">Error</h2>
              <p className="text-sm text-red-300">{project.error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
