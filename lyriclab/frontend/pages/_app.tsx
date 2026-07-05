import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { onAuthStateChanged } from 'firebase/auth';
import { Toaster } from 'react-hot-toast';
import { auth } from '../lib/firebase';
import { useStore } from '../lib/store';
import Layout from '../components/Layout';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const setUser = useStore((s) => s.setUser);
  const user = useStore((s) => s.user);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (user) => {
      setUser(user);
    });
    return () => unsub();
  }, [setUser]);

  const isAuthPage = router.pathname === '/';

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#e5e7eb',
            border: '1px solid #334155',
          },
        }}
      />
      {isAuthPage || !user ? (
        <Component {...pageProps} />
      ) : (
        <Layout>
          <Component {...pageProps} />
        </Layout>
      )}
    </>
  );
}
