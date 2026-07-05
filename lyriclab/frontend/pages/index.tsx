import { useState } from 'react';
import { useRouter } from 'next/router';
import { signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider } from 'firebase/auth';
import { auth, googleProvider, db } from '../lib/firebase';
import { doc, setDoc } from 'firebase/firestore';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      const result = await signInWithPopup(auth, googleProvider);
      await setDoc(doc(db, 'users', result.user.uid), {
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        createdAt: new Date().toISOString(),
      }, { merge: true });
      toast.success('Welcome to LyricLab!');
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (isSignup) {
        const result = await createUserWithEmailAndPassword(auth, email, password);
        await setDoc(doc(db, 'users', result.user.uid), {
          email: result.user.email,
          createdAt: new Date().toISOString(),
        });
        toast.success('Account created!');
      } else {
        await signInWithEmailAndPassword(auth, email, password);
        toast.success('Welcome back!');
      }
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-green-400 bg-clip-text text-transparent">
            LyricLab
          </h1>
          <p className="text-slate-400 mt-2">AI-Powered Lyrics Video Creator</p>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-6">
            {isSignup ? 'Create Account' : 'Sign In'}
          </h2>

          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full btn-secondary flex items-center justify-center gap-3 mb-4 py-3"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-slate-800 text-slate-400">or</span>
            </div>
          </div>

          <form onSubmit={handleEmailAuth} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              required
              minLength={6}
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3"
            >
              {loading ? 'Loading...' : isSignup ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <p className="text-center mt-4 text-slate-400">
            {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => setIsSignup(!isSignup)}
              className="text-indigo-400 hover:text-indigo-300"
            >
              {isSignup ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>

        <p className="text-center text-slate-500 text-xs mt-6">
          LyricLab v1.0 - Non-profit project for creating beautiful lyric videos
        </p>
      </div>
    </div>
  );
}
