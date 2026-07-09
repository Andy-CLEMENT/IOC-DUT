import { getApp, getApps, initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
  apiKey: "AIzaSyDCqENbA55iQQWUObM5UCV_29s80vb-39A",
  authDomain: "firealarm-77a2c.firebaseapp.com",
  databaseURL: "https://firealarm-77a2c-default-rtdb.firebaseio.com",
  projectId: "firealarm-77a2c",
  storageBucket: "firealarm-77a2c.firebasestorage.app",
  messagingSenderId: "617075055573",
  appId: "1:617075055573:web:3e584ba0a27d6274683b5c",
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();

export const database = getDatabase(app);