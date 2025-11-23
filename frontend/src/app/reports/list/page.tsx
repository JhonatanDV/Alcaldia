'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import Layout from '@/components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ReportsListPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
    if (!token) {
      window.location.href = '/';
      return;
    }
    setUserRole(role);

    (async () => {
      try {
        const res = await axios.get(`${API_URL}/api/reports/`, { headers: { Authorization: `Bearer ${token}` } });
        setReports(res.data || []);
      } catch (err) {
        console.error('Error fetching reports list', err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const download = (url: string) => {
    window.open(url, '_blank');
  };

  return (
    <Layout userRole={userRole} onLogout={() => { localStorage.clear(); window.location.href = '/'; }}>
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-semibold">Reportes Generados</h1>
          <p className="text-sm text-gray-500">Lista de reportes generados por el sistema.</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          {loading ? (
            <p>Cargando...</p>
          ) : (
            <div className="divide-y">
              {reports.length === 0 && <p className="text-sm text-gray-500">No hay reportes generados aún.</p>}
              {reports.map((r) => (
                <div key={r.id} className="py-3 flex items-center justify-between">
                  <div>
                    <div className="font-medium">{r.title}</div>
                    <div className="text-sm text-gray-500">Generado: {new Date(r.generated_at).toLocaleString()}</div>
                  </div>
                  <div>
                    {r.pdf_file ? (
                      <button onClick={() => download(r.pdf_file)} className="px-3 py-1 bg-blue-600 text-white rounded">Descargar</button>
                    ) : (
                      <span className="text-sm text-gray-500">Sin archivo</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
