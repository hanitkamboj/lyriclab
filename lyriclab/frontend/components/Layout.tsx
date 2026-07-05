import { ReactNode, useState } from 'react';
import { useRouter } from 'next/router';
import { signOut } from 'firebase/auth';
import { auth } from '../lib/firebase';
import { useStore } from '../lib/store';
import {
  HiOutlineHome, HiOutlineMusicNote, HiOutlineTrendingUp,
  HiOutlineChat, HiOutlineCog, HiOutlineVideoCamera,
  HiOutlineUpload, HiOutlineMenu, HiOutlineX,
  HiOutlineLogout, HiOutlineCollection, HiOutlineLightningBolt,
} from 'react-icons/hi';

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: HiOutlineHome },
  { name: 'Projects', path: '/projects', icon: HiOutlineMusicNote },
  { name: 'Create', path: '/create', icon: HiOutlineVideoCamera },
  { name: 'Trending', path: '/trending', icon: HiOutlineTrendingUp },
  { name: 'Chat', path: '/chat', icon: HiOutlineChat },
  { name: 'Bulk', path: '/bulk', icon: HiOutlineCollection },
  { name: 'Settings', path: '/settings', icon: HiOutlineCog },
];

export default function Layout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const user = useStore((s) => s.user);
  const sidebarOpen = useStore((s) => s.sidebarOpen);
  const setSidebarOpen = useStore((s) => s.setSidebarOpen);

  const handleLogout = async () => {
    await signOut(auth);
    router.push('/');
  };

  return (
    <div className="flex h-screen bg-slate-900">
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-slate-800 border-r border-slate-700 transition-all duration-200 flex flex-col`}>
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          {sidebarOpen && (
            <h2 className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-green-400 bg-clip-text text-transparent">
              LyricLab
            </h2>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-slate-400 hover:text-white p-1">
            {sidebarOpen ? <HiOutlineX size={20} /> : <HiOutlineMenu size={20} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-1">
          {navItems.map((item) => {
            const isActive = router.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => router.push(item.path)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                }`}
              >
                <item.icon size={20} />
                {sidebarOpen && <span>{item.name}</span>}
              </button>
            );
          })}
        </nav>

        <div className="p-2 border-t border-slate-700">
          {sidebarOpen && user && (
            <div className="px-3 py-2 text-xs text-slate-400 truncate">
              {user.email}
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-slate-700 hover:text-red-400 transition-all"
          >
            <HiOutlineLogout size={20} />
            {sidebarOpen && <span>Sign Out</span>}
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="p-6 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
