'use client';

import { ReactNode, useEffect, useState, useCallback } from 'react';
import Sidebar from './Sidebar';
import initAuth from '@/lib/auth';
import IdleWarning from './IdleWarning';

interface LayoutProps {
  children: ReactNode;
  userRole: 'admin' | 'technician' | null;
  onLogout: () => void;
}

export default function Layout({ children, userRole, onLogout }: LayoutProps) {
  const [warningVisible, setWarningVisible] = useState(false);
  const [warningRemainingMs, setWarningRemainingMs] = useState(0);
  const [extendFn, setExtendFn] = useState<() => void>(() => () => {});

  const handleWarn = useCallback((show: boolean, remainingMs: number, extend: () => void) => {
    setWarningVisible(show);
    setWarningRemainingMs(remainingMs);
    setExtendFn(() => extend);
  }, []);

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    setIsAuthenticated(!!token);

    const onStorage = (e: StorageEvent) => {
      if (e.key === 'access_token') {
        setIsAuthenticated(!!e.newValue);
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  useEffect(() => {
    // Initialize global auth: axios 401 handling and inactivity logout
    const cleanup = initAuth(onLogout, handleWarn);
    return () => cleanup();
  }, [onLogout, handleWarn]);

  useEffect(() => {
    // Configure pdfjs worker to avoid "Setting up fake worker failed" errors.
    // We expect `pdf.worker.min.js` to be served from the Next `public/` folder
    // at `/pdf.worker.min.js`. Copy the worker from `node_modules/pdfjs-dist/...`
    // to `frontend/public/pdf.worker.min.js` (see repo instructions).
    if (typeof window !== 'undefined') {
      import('pdfjs-dist/legacy/build/pdf').then((pdfjs) => {
        try {
          // Serve worker from public root
          pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';
        } catch (e) {
          // ignore
        }
      }).catch(() => {
        // pdfjs not installed; ignore
      });
    }
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {isAuthenticated && <Sidebar userRole={userRole} onLogout={onLogout} />}
      <main className="flex-1 lg:ml-64 p-4 sm:p-6 lg:p-8">
        {children}
      </main>
      {warningVisible && (
        <IdleWarning remainingMs={warningRemainingMs} onExtend={() => extendFn()} onLogout={onLogout} />
      )}
    </div>
  );
}
