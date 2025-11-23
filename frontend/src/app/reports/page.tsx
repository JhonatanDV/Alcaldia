"use client";

import { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import ReportDownloader from '@/components/ReportDownloader';

export default function ReportsPage() {
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;

    if (!token) {
      setIsAuthenticated(false);
      window.location.href = '/';
      return;
    }

    setIsAuthenticated(true);
    setUserRole(role);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || '' : '';

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-semibold">Reportes</h1>
          <p className="text-sm text-gray-500">Genera y descarga reportes del sistema.</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <ReportDownloader token={token || ''} userRole={userRole} />
        </div>
      </div>
    </Layout>
  );
}
