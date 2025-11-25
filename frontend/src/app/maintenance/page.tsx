 'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../components/Layout';
import MaintenanceTable from '../../components/MaintenanceTable';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface Maintenance {
  id: number;
  equipment?: { id: number; code?: string; name?: string } | null;
  description?: string | null;
  date?: string | null;
  placa?: string | null;
  equipo_placa?: string | null; // serializer helper
  scheduled_date?: string | null;
  completion_date?: string | null;
  created_at?: string | null;
  // location fields (legacy strings or related objects/ids)
  sede?: string | null;
  dependencia?: string | null;
  sede_rel?: any;
  dependencia_rel?: any;
}

export default function MaintenanceListPage() {
  const [maintenances, setMaintenances] = useState<Maintenance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);

  // Pagination state
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    const fetchMaintenances = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;

        if (!token) {
          window.location.href = '/';
          return;
        }

        setUserRole(role);

        const headers = { Authorization: `Bearer ${token}` };

        const res: any = await axios.get(`${API_URL}/api/maintenances/?page=${page}&page_size=${pageSize}`, { headers });

        if (res.data.results) {
          setMaintenances(res.data.results);
          const count = res.data.count ?? res.data.total ?? res.data.length ?? 0;
          setTotalPages(Math.max(1, Math.ceil(count / pageSize)));
        } else if (Array.isArray(res.data)) {
          setMaintenances(res.data);
          setTotalPages(1);
        } else {
          setMaintenances([]);
          setTotalPages(1);
        }
      } catch (err: any) {
        console.error('Error fetching maintenances:', err);
        setError(err.response?.data?.detail || 'Error al cargar mantenimientos');
      } finally {
        setLoading(false);
      }
    };

    fetchMaintenances();
  }, [page, pageSize]);

  const goToPage = (p: number) => {
    if (p < 1) return;
    if (p > totalPages) return;
    setPage(p);
    try {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (_) {}
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setPage(1);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  const formatMaintenanceDate = (m: Maintenance) => {
    const dateOnly = m.scheduled_date || m.completion_date || m.created_at;
    if (!dateOnly) return '-';
    const time = (m as any).hora_inicio || (m as any).hora_final || null;
    try {
      if (time) {
        const combined = `${dateOnly}T${time}`;
        const d = new Date(combined);
        if (!isNaN(d.getTime())) return d.toLocaleString();
      }
      const d2 = new Date(dateOnly + 'T00:00:00');
      if (!isNaN(d2.getTime())) return d2.toLocaleDateString();
    } catch (e) {
      // ignore
    }
    return '-';
  };

  const renderPaginationPages = () => {
    const visible = 5;
    const start = Math.max(1, Math.min(page - Math.floor(visible / 2), Math.max(1, totalPages - visible + 1)));
    const pages = [] as number[];
    for (let i = 0; i < Math.min(visible, totalPages); i++) pages.push(start + i);
    return pages.map((p) => (
      <button
        key={p}
        onClick={() => goToPage(p)}
        className={`px-2 py-1 rounded ${p === page ? 'bg-indigo-600 text-white' : 'bg-white border text-gray-700'}`}
      >
        {p}
      </button>
    ));
  };

  if (loading) {
    return (
      <Layout userRole={userRole} onLogout={handleLogout}>
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Mantenimientos</h1>
          <p className="text-gray-600">Cargando mantenimientos...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">Mantenimientos</h1>
          <p className="text-sm text-gray-500 mt-1">Lista de mantenimientos registrados</p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <MaintenanceTable
          maintenances={maintenances}
          page={page}
          totalPages={totalPages}
          pageSize={pageSize}
          setPage={(p) => setPage(p)}
          setPageSize={(s) => setPageSize(s)}
        />
      </div>
    </Layout>
  );
}
