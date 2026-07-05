import { useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import { useStore } from '../lib/store';
import { projectApi } from '../lib/api';
import { useDropzone } from 'react-dropzone';
import { HiOutlineUpload, HiOutlineMusicNote, HiOutlineDocumentText, HiOutlinePhotograph, HiOutlineLink } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function CreateProject() {
  const router = useRouter();
  const user = useStore((s) => s.user);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [project, setProject] = useState({
    title: '',
    artist: '',
    songUrl: '',
    style: '7clouds',
    resolution: '1920x1080',
    fps: '60',
    bitrate: '10M',
  });
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [lyricsFile, setLyricsFile] = useState<File | null>(null);
  const [bgFile, setBgFile] = useState<File | null>(null);

  const onAudioDrop = useCallback((files: File[]) => {
    if (files[0]) setAudioFile(files[0]);
  }, []);
  const onLyricsDrop = useCallback((files: File[]) => {
    if (files[0]) setLyricsFile(files[0]);
  }, []);
  const onBgDrop = useCallback((files: File[]) => {
    if (files[0]) setBgFile(files[0]);
  }, []);

  const audioDrop = useDropzone({ onDrop: onAudioDrop, accept: { 'audio/*': ['.mp3', '.wav', '.m4a', '.flac'] }, maxFiles: 1 });
  const lyricsDrop = useDropzone({ onDrop: onLyricsDrop, accept: { 'text/plain': ['.lrc', '.srt', '.txt'] }, maxFiles: 1 });
  const bgDrop = useDropzone({ onDrop: onBgDrop, accept: { 'image/*': ['.png', '.jpg', '.jpeg'], 'video/*': ['.mp4', '.webm'] }, maxFiles: 1 });

  const handleCreate = async () => {
    if (!project.title) {
      toast.error('Title is required');
      return;
    }

    setLoading(true);
    try {
      const payload: any = {
        title: project.title,
        artist: project.artist,
        song_url: project.songUrl,
        style: project.style,
        resolution: project.resolution,
        fps: parseInt(project.fps),
        bitrate: project.bitrate,
      };

      if (audioFile) {
        const formData = new FormData();
        formData.append('file', audioFile);
        const uploadRes = await projectApi.uploadAudio(audioFile);
        payload.audio_path = uploadRes.data.path;
      }

      if (lyricsFile) {
        const uploadRes = await projectApi.uploadLyrics(lyricsFile);
        payload.lyrics_path = uploadRes.data.path;
      }

      const res = await projectApi.create(payload);
      const projectId = res.data.id;

      toast.success('Project created! Processing...');
      await projectApi.process(projectId, user!.uid);
      toast.success('Processing complete! Preview ready.');

      router.push(`/project?id=${projectId}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const styles = ['7clouds', 'minimal', 'kpop'];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Create Lyric Video</h1>
        <p className="text-slate-400">Fill in the details and let LyricLab do the magic</p>
      </div>

      <div className="flex gap-2 mb-6">
        {[1, 2, 3].map((s) => (
          <div key={s} className={`flex-1 h-2 rounded-full ${s <= step ? 'bg-indigo-600' : 'bg-slate-700'}`} />
        ))}
      </div>

      <div className="card space-y-4">
        {step === 1 && (
          <>
            <h2 className="text-lg font-semibold">Song Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Title *</label>
                <input className="input" value={project.title} onChange={(e) => setProject({...project, title: e.target.value})} placeholder="Song title" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Artist</label>
                <input className="input" value={project.artist} onChange={(e) => setProject({...project, artist: e.target.value})} placeholder="Artist name" />
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1">Song URL (YouTube/Spotify)</label>
              <div className="flex gap-2">
                <HiOutlineLink className="text-slate-500 mt-3" size={18} />
                <input className="input" value={project.songUrl} onChange={(e) => setProject({...project, songUrl: e.target.value})} placeholder="https://youtube.com/watch?v=..." />
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1">Style</label>
              <div className="flex gap-2">
                {styles.map((s) => (
                  <button
                    key={s}
                    onClick={() => setProject({...project, style: s})}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      project.style === s ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Resolution</label>
                <select className="select" value={project.resolution} onChange={(e) => setProject({...project, resolution: e.target.value})}>
                  <option value="1920x1080">1080p (1920x1080)</option>
                  <option value="2560x1440">1440p (2560x1440)</option>
                  <option value="3840x2160">4K (3840x2160)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">FPS</label>
                <select className="select" value={project.fps} onChange={(e) => setProject({...project, fps: e.target.value})}>
                  <option value="24">24 FPS</option>
                  <option value="30">30 FPS</option>
                  <option value="60">60 FPS</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Bitrate</label>
                <select className="select" value={project.bitrate} onChange={(e) => setProject({...project, bitrate: e.target.value})}>
                  <option value="5M">5 Mbps</option>
                  <option value="10M">10 Mbps</option>
                  <option value="20M">20 Mbps</option>
                  <option value="50M">50 Mbps</option>
                </select>
              </div>
            </div>

            <button onClick={() => setStep(2)} className="btn-primary w-full">Next: Upload Files</button>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-lg font-semibold">Files (Optional)</h2>
            <p className="text-sm text-slate-400">Upload files or LyricLab will auto-fetch them</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div {...audioDrop.getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${audioFile ? 'border-green-500 bg-green-500/10' : 'border-slate-600 hover:border-indigo-500'}`}>
                <input {...audioDrop.getInputProps()} />
                <HiOutlineMusicNote size={32} className="mx-auto mb-2 text-slate-400" />
                <p className="text-sm">{audioFile ? audioFile.name : 'Drop Audio'}</p>
                <p className="text-xs text-slate-500">MP3, WAV, M4A</p>
              </div>

              <div {...lyricsDrop.getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${lyricsFile ? 'border-green-500 bg-green-500/10' : 'border-slate-600 hover:border-indigo-500'}`}>
                <input {...lyricsDrop.getInputProps()} />
                <HiOutlineDocumentText size={32} className="mx-auto mb-2 text-slate-400" />
                <p className="text-sm">{lyricsFile ? lyricsFile.name : 'Drop Lyrics'}</p>
                <p className="text-xs text-slate-500">LRC, SRT, TXT</p>
              </div>

              <div {...bgDrop.getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${bgFile ? 'border-green-500 bg-green-500/10' : 'border-slate-600 hover:border-indigo-500'}`}>
                <input {...bgDrop.getInputProps()} />
                <HiOutlinePhotograph size={32} className="mx-auto mb-2 text-slate-400" />
                <p className="text-sm">{bgFile ? bgFile.name : 'Drop Background'}</p>
                <p className="text-xs text-slate-500">PNG, JPG, MP4</p>
              </div>
            </div>

            <div className="flex gap-3">
              <button onClick={() => setStep(1)} className="btn-secondary flex-1">Back</button>
              <button onClick={() => setStep(3)} className="btn-primary flex-1">Next: Review</button>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h2 className="text-lg font-semibold">Review & Create</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between p-2 bg-slate-700/50 rounded">
                <span className="text-slate-400">Title</span><span>{project.title}</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-700/50 rounded">
                <span className="text-slate-400">Artist</span><span>{project.artist || 'Auto-detect'}</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-700/50 rounded">
                <span className="text-slate-400">Style</span><span>{project.style}</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-700/50 rounded">
                <span className="text-slate-400">Resolution</span><span>{project.resolution}</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-700/50 rounded">
                <span className="text-slate-400">FPS</span><span>{project.fps}</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-700/50 rounded">
                <span className="text-slate-400">Files</span>
                <span>{audioFile ? 'Audio ✓' : 'Auto-fetch'} | {lyricsFile ? 'Lyrics ✓' : 'Auto-fetch'} | {bgFile ? 'BG ✓' : 'Auto-fetch'}</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button onClick={() => setStep(2)} className="btn-secondary flex-1">Back</button>
              <button onClick={handleCreate} disabled={loading} className="btn-primary flex-1">
                {loading ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
