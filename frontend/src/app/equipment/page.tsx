'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Equipment {
  id: number;
  code: string;
  name: string;
  location?: string | null;
}

export default function EquipmentListPage() {
  const [equipments, setEquipments] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);

  // Pagination state
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    const fetchEquipments = async () => {
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

        const res: any = await axios.get(`${API_URL}/api/equipments/?page=${page}&page_size=${pageSize}`, { headers });

        if (res.data.results) {
          setEquipments(res.data.results);
          // calculate total pages
          const count = res.data.count ?? res.data.total ?? res.data.length ?? 0;
          setTotalPages(Math.max(1, Math.ceil(count / pageSize)));
        } else if (Array.isArray(res.data)) {
          setEquipments(res.data);
          setTotalPages(1);
        } else {
          setEquipments([]);
          setTotalPages(1);
        }
      } catch (err: any) {
        console.error('Error fetching equipments:', err);
        setError(err.response?.data?.detail || 'Error al cargar equipos');
      } finally {
        setLoading(false);
      }
    };

    fetchEquipments();
  }, [page, pageSize]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  const goToPage = (p: number) => {
    if (p < 1 || p > totalPages) return;
    setPage(p);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">Equipos</h1>
          <p className="text-sm text-gray-500 mt-1">Lista de equipos registrados</p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm border p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Listado</h2>
            <div className="flex items-center gap-2">
              <a href="/equipment/new" className="px-3 py-1.5 bg-indigo-600 text-white rounded-md text-sm">Nuevo Equipo</a>
              <a href="/dashboard" className="px-3 py-1.5 border border-gray-300 rounded-md text-sm">Dashboard</a>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Código</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Nombre</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Ubicación</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {loading && (
                  <tr>
                    <td colSpan={3} className="px-4 py-6 text-center text-sm text-gray-500">Cargando...</td>
                  </tr>
                )}
                {!loading && equipments.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-4 py-6 text-center text-sm text-gray-500">No hay equipos registrados</td>
                  </tr>
                )}
                {equipments.map((eq) => (
                  <tr key={eq.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{eq.code}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 truncate">{eq.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{eq.location || 'Sin ubicación'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación estilizada */}
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">Página {page} de {totalPages}</div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => goToPage(page - 1)}
                disabled={page <= 1}
                className="px-3 py-1 rounded-md border bg-white text-sm hover:bg-gray-50 disabled:opacity-50"
              >Anterior</button>

              {/* show simple page numbers with max 5 visible */}
              <div className="hidden sm:flex items-center gap-1">
                {Array.from({ length: totalPages }).map((_, i) => {
                  const p = i + 1;
                  if (totalPages > 7) {
                    // show first, last, neighbors
                    if (p === 1 || p === totalPages || Math.abs(p - page) <= 1) {
                      return (
                        <button key={p} onClick={() => goToPage(p)} className={`px-2 py-1 text-sm rounded ${p === page ? 'bg-indigo-600 text-white' : 'bg-white border'}`}>
                          {p}
                        </button>
                      );
                    }
                    if (p === 2 && page > 3) return <span key={p} className="px-2">...</span>;
                    if (p === totalPages - 1 && page < totalPages - 2) return <span key={p} className="px-2">...</span>;
                    return null;
                  }
                  return (
                    <button key={p} onClick={() => goToPage(p)} className={`px-2 py-1 text-sm rounded ${p === page ? 'bg-indigo-600 text-white' : 'bg-white border'}`}>
                      {p}
                    </button>
                  );
                })}
              </div>

              <button
                onClick={() => goToPage(page + 1)}
                disabled={page >= totalPages}
                className="px-3 py-1 rounded-md border bg-white text-sm hover:bg-gray-50 disabled:opacity-50"
              >Siguiente</button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
