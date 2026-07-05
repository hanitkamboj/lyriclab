import { create } from 'zustand';
import { User } from 'firebase/auth';

interface AppState {
  user: User | null;
  setUser: (user: User | null) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  activePage: string;
  setActivePage: (page: string) => void;
  chatSessionId: string | null;
  setChatSessionId: (id: string | null) => void;
  autoMode: boolean;
  setAutoMode: (mode: boolean) => void;
  darkMode: boolean;
  setDarkMode: (mode: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  activePage: 'dashboard',
  setActivePage: (page) => set({ activePage: page }),
  chatSessionId: null,
  setChatSessionId: (id) => set({ chatSessionId: id }),
  autoMode: false,
  setAutoMode: (mode) => set({ autoMode: mode }),
  darkMode: true,
  setDarkMode: (mode) => set({ darkMode: mode }),
}));
