/** @type {import('next').NextConfig} */
const isStaticExport = process.env.EXPORT_MODE === 'static';
const isPages = process.env.DEPLOY_TARGET === 'github-pages';
const basePath = isPages ? '/lyriclab' : '';

const nextConfig = {
  reactStrictMode: true,
  basePath,
  images: {
    unoptimized: isStaticExport,
    domains: ['firebasestorage.googleapis.com', 'lh3.googleusercontent.com', 'i.ytimg.com', 'images.pexels.com'],
  },
  env: {
    NEXT_PUBLIC_FIREBASE_API_KEY: 'AIzaSyCrqBsnd5T539L3V7PCC_FeBeAJFMA4y0s',
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: 'sonifall.firebaseapp.com',
    NEXT_PUBLIC_FIREBASE_PROJECT_ID: 'sonifall',
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: 'sonifall.firebasestorage.app',
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: '822971265775',
    NEXT_PUBLIC_FIREBASE_APP_ID: '1:822971265775:web:c2bed1b390f7b9cb12e11a',
    NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID: 'G-7VPTJCSHST',
    NEXT_PUBLIC_YOUTUBE_API_KEY: 'AIzaSyDbt70OPPr-teRTsPRf6lEsfRo6mOdSj-nU',
  },
};

if (isStaticExport) {
  nextConfig.output = 'export';
  nextConfig.trailingSlash = true;
} else {
  nextConfig.rewrites = async () => [
    {
      source: '/api/:path*',
      destination: `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/:path*`,
    },
  ];
}

module.exports = nextConfig;
