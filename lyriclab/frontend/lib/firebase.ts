import { initializeApp, getApps } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: "AIzaSyCrqBsnd5T539L3V7PCC_FeBeAJFMA4y0s",
  authDomain: "sonifall.firebaseapp.com",
  projectId: "sonifall",
  storageBucket: "sonifall.firebasestorage.app",
  messagingSenderId: "822971265775",
  appId: "1:822971265775:web:c2bed1b390f7b9cb12e11a",
  measurementId: "G-7VPTJCSHST",
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);
const googleProvider = new GoogleAuthProvider();

export { auth, db, storage, googleProvider, signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut };
