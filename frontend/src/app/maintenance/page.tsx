'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Maintenance {
  id: number;
  equipment?: { id: number; code?: string; name?: string } | null;
  description?: string | null;
  date?: string | null;
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

        <div className="bg-white rounded-lg shadow-sm border p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Listado</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Equipo</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Descripción</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {maintenances.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-500">No hay mantenimientos registrados</td>
                  </tr>
                )}
                {maintenances.map((m) => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{m.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{m.equipment?.code ?? m.equipment?.name ?? 'Sin equipo'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 truncate">{m.description ?? '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{m.date ? new Date(m.date).toLocaleString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination controls */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => goToPage(page - 1)}
                disabled={page <= 1}
                className={`px-3 py-1.5 rounded-md text-sm ${page <= 1 ? 'bg-gray-200 text-gray-500' : 'bg-white border'}`}
              >
                Anterior
              </button>

              <div className="hidden sm:flex items-center gap-1">
                {(() => {
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
                })()}
              </div>

              <button
                onClick={() => goToPage(page + 1)}
                disabled={page >= totalPages}
                className={`px-3 py-1.5 rounded-md text-sm ${page >= totalPages ? 'bg-gray-200 text-gray-500' : 'bg-white border'}`}
              >
                Siguiente
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Página {page} de {totalPages}</span>
              <select
                value={pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
