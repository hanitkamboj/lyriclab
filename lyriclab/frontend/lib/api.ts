import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL ||
  (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' :
   'https://lyriclab-backend.onrender.com');

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const projectApi = {
  list: (userId: string) => api.get(`/projects/?user_id=${userId}`),
  get: (id: string) => api.get(`/projects/${id}`),
  create: (data: any) => api.post('/projects/', data),
  process: (projectId: string, userId: string) => api.post(`/projects/process?project_id=${projectId}&user_id=${userId}`),
  preview: (projectId: string, userId: string) => api.post(`/projects/preview?project_id=${projectId}&user_id=${userId}`),
  render: (projectId: string, userId: string) => api.post(`/projects/render?project_id=${projectId}&user_id=${userId}`),
  upload: (projectId: string, tokenJson: string, privacy: string, userId: string) =>
    api.post(`/projects/upload?project_id=${projectId}&token_json=${encodeURIComponent(tokenJson)}&privacy=${privacy}&user_id=${userId}`),
  delete: (id: string) => api.delete(`/projects/${id}`),
  uploadAudio: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/projects/upload-audio', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  },
  uploadLyrics: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/projects/upload-lyrics', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  },
};

export const youtubeApi = {
  authUrl: () => api.get('/youtube/auth-url'),
  connect: (authCode: string, userId: string) => api.post('/youtube/connect', { auth_code: authCode, user_id: userId }),
  channels: (userId: string) => api.get(`/youtube/channels/${userId}`),
  disconnect: (channelId: string) => api.delete(`/youtube/channels/${channelId}`),
  generateSeo: (title: string, artist: string, tags: string) =>
    api.post(`/youtube/seo?title=${encodeURIComponent(title)}&artist=${encodeURIComponent(artist)}&tags=${encodeURIComponent(tags)}`),
};

export const chatApi = {
  send: (message: string, userId: string, sessionId?: string, params?: any) =>
    api.post('/chat/', { message, user_id: userId, session_id: sessionId, params: params || {} }),
  history: (userId: string, sessionId?: string) =>
    api.get(`/chat/history/${userId}${sessionId ? `?session_id=${sessionId}` : ''}`),
  sessions: (userId: string) => api.get(`/chat/sessions/${userId}`),
};

export const trendingApi = {
  get: (platforms?: string, limit?: number) =>
    api.get(`/trending/?platforms=${platforms || 'youtube,billboard'}&limit=${limit || 20}`),
  discover: () => api.get('/trending/discover'),
};

export const bulkApi = {
  create: (userId: string, items: any[], autoUpload: boolean) =>
    api.post('/bulk/create', { user_id: userId, items, auto_upload: autoUpload }),
  autoStart: (userId: string) => api.post('/bulk/auto', null, { params: { user_id: userId } }),
  fromTrending: (userId: string, count: number, autoUpload: boolean) =>
    api.post('/bulk/from-trending', null, { params: { user_id: userId, count, auto_upload: autoUpload } }),
  status: (userId: string) => api.get(`/bulk/status/${userId}`),
};

export const ollamaApi = {
  chat: (baseUrl: string, model: string, prompt: string, system?: string) =>
    api.post('/ollama/chat', { base_url: baseUrl, model, prompt, system }),
  saveConfig: (userId: string, name: string, baseUrl: string, modelName: string) =>
    api.post('/ollama/config', { user_id: userId, name, base_url: baseUrl, model_name: modelName }),
  getConfigs: (userId: string) => api.get(`/ollama/configs/${userId}`),
  getActive: (userId: string) => api.get(`/ollama/active/${userId}`),
  deleteConfig: (configId: string) => api.delete(`/ollama/config/${configId}`),
};

export default api;
