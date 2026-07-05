import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { trendingApi, bulkApi } from '../lib/api';
import { useStore } from '../lib/store';
import { HiOutlineTrendingUp, HiOutlineMusicNote, HiOutlineGlobe, HiOutlineCollection } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function TrendingPage() {
  const router = useRouter();
  const user = useStore((s) => s.user);
  const [trending, setTrending] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [platform, setPlatform] = useState('youtube,billboard');
  const [selected, setSelected] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadTrending();
  }, [platform]);

  const loadTrending = async () => {
    setLoading(true);
    try {
      const res = await trendingApi.get(platform, 30);
      setTrending(res.data.trending || []);
    } catch {
      toast.error('Failed to load trending');
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (index: number) => {
    const newSelected = new Set(selected);
    if (newSelected.has(index)) newSelected.delete(index);
    else newSelected.add(index);
    setSelected(newSelected);
  };

  const createFromSelected = async () => {
    const items = Array.from(selected).map((i) => ({
      title: trending[i].title,
      artist: trending[i].artist,
      song_url: trending[i].source_url,
    }));

    if (items.length === 0) {
      toast.error('Select songs first');
      return;
    }

    try {
      const res = await bulkApi.create(user!.uid, items, false);
      toast.success(`Created ${res.data.count} projects!`);
      router.push('/projects');
    } catch {
      toast.error('Failed to create projects');
    }
  };

  const createAllAndAuto = async () => {
    try {
      const res = await bulkApi.fromTrending(user!.uid, 10, true);
      toast.success(`Auto-processing ${res.data.count} trending songs!`);
      router.push('/bulk');
    } catch {
      toast.error('Failed to start bulk');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Trending Songs</h1>
          <p className="text-slate-400">Discover what's popular and create lyric videos</p>
        </div>
        <div className="flex gap-2">
          <button onClick={createFromSelected} disabled={selected.size === 0} className="btn-primary flex items-center gap-2">
            <HiOutlineMusicNote size={16} />
            Create Selected ({selected.size})
          </button>
          <button onClick={createAllAndAuto} className="btn-accent flex items-center gap-2">
            <HiOutlineCollection size={16} />
            Auto Process All
          </button>
        </div>
      </div>

      <div className="flex gap-2">
        {[
          { key: 'youtube,billboard', label: 'All', icon: HiOutlineGlobe },
          { key: 'youtube', label: 'YouTube', icon: HiOutlineTrendingUp },
          { key: 'billboard', label: 'Billboard', icon: HiOutlineGlobe },
        ].map((p) => (
          <button
            key={p.key}
            onClick={() => setPlatform(p.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
              platform === p.key ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <p.icon size={16} />
            {p.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="loading h-10 w-10"></div>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs text-slate-400 border-b border-slate-700">
                <th className="pb-3 w-10">
                  <input
                    type="checkbox"
                    onChange={() => {
                      if (selected.size === trending.length) setSelected(new Set());
                      else setSelected(new Set(trending.map((_, i) => i)));
                    }}
                    checked={selected.size === trending.length && trending.length > 0}
                  />
                </th>
                <th className="pb-3">#</th>
                <th className="pb-3">Title</th>
                <th className="pb-3">Artist</th>
                <th className="pb-3">Source</th>
                <th className="pb-3">Rank</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {trending.map((song, i) => (
                <tr
                  key={i}
                  className={`text-sm hover:bg-slate-700/30 cursor-pointer transition-colors ${
                    selected.has(i) ? 'bg-indigo-600/20' : ''
                  }`}
                  onClick={() => toggleSelect(i)}
                >
                  <td className="py-3">
                    <input type="checkbox" checked={selected.has(i)} onChange={() => toggleSelect(i)} />
                  </td>
                  <td className="py-3 text-slate-400">{song.rank || i + 1}</td>
                  <td className="py-3 font-medium">{song.title}</td>
                  <td className="py-3 text-slate-400">{song.artist || 'Unknown'}</td>
                  <td className="py-3">
                    <span className="badge-info">{song.source || 'unknown'}</span>
                  </td>
                  <td className="py-3 text-slate-400">{song.views ? `${(song.views / 1000000).toFixed(1)}M` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
