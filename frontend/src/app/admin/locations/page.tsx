 'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Layout from '../../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Sede {
  id: number;
  nombre: string;
  direccion?: string;
  dependencias_count?: number;
  activo: boolean;
}

interface Dependencia {
  id: number;
  sede: number;
  sede_nombre: string;
  nombre: string;
  codigo?: string;
  subdependencias_count?: number;
  activo: boolean;
}

interface Subdependencia {
  id: number;
  dependencia: number;
  dependencia_nombre: string;
  sede_nombre: string;
  nombre: string;
  activo: boolean;
}

type TabType = 'sedes' | 'dependencias' | 'subdependencias';

export default function LocationManagementPage() {
  const [activeTab, setActiveTab] = useState<TabType>('sedes');

  // useSearchParams from next/navigation can cause prerendering issues
  // when Next tries to statically render the page. Use a client-only
  // approach based on window.location.search inside useEffect so it
  // only runs on the client and avoids the need for Suspense.
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab');
    if (tab && ['sedes', 'dependencias', 'subdependencias'].includes(tab)) {
      setActiveTab(tab as TabType);
    }
  }, []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>('admin');

  // Estados para Sedes
  const [sedes, setSedes] = useState<Sede[]>([]);
  const [sedeDependenciasMap, setSedeDependenciasMap] = useState<Record<number, Dependencia[]>>({});
  const [showSedeModal, setShowSedeModal] = useState(false);
  const [editingSede, setEditingSede] = useState<Sede | null>(null);
  const [sedeForm, setSedeForm] = useState({
    nombre: '',
    direccion: '',
    activo: true,
  });

  // Estados para Dependencias
  const [dependencias, setDependencias] = useState<Dependencia[]>([]);
  const [dependenciaSubMap, setDependenciaSubMap] = useState<Record<number, Subdependencia[]>>({});
  const [showDependenciaModal, setShowDependenciaModal] = useState(false);
  const [editingDependencia, setEditingDependencia] = useState<Dependencia | null>(null);
  const [dependenciaForm, setDependenciaForm] = useState({
    sede: 0,
    nombre: '',
    activo: true,
  });

  // Estados para Subdependencias
  const [subdependencias, setSubdependencias] = useState<Subdependencia[]>([]);
  const [expandedSedes, setExpandedSedes] = useState<number[]>([]);
  const [expandedDependencias, setExpandedDependencias] = useState<number[]>([]);
  const [showSubdependenciaModal, setShowSubdependenciaModal] = useState(false);
  const [editingSubdependencia, setEditingSubdependencia] = useState<Subdependencia | null>(null);
  const [subdependenciaForm, setSubdependenciaForm] = useState({
    dependencia: 0,
    nombre: '',
    activo: true,
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  const fetchData = async () => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
    if (!token) {
      window.location.href = '/';
      return;
    }
    setUserRole(role);

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };

      if (activeTab === 'sedes') {
        const response = await axios.get(`${API_URL}/api/ubicaciones/sedes/`, { headers });
        setSedes(response.data.results || response.data);
      } else if (activeTab === 'dependencias') {
        const [sedesRes, depRes] = await Promise.all([
          axios.get(`${API_URL}/api/ubicaciones/sedes/`, { headers }),
          axios.get(`${API_URL}/api/ubicaciones/dependencias/`, { headers }),
        ]);
        setSedes(sedesRes.data.results || sedesRes.data);
        setDependencias(depRes.data.results || depRes.data);
      } else if (activeTab === 'subdependencias') {
        const [depRes, subRes] = await Promise.all([
          axios.get(`${API_URL}/api/ubicaciones/dependencias/`, { headers }),
          axios.get(`${API_URL}/api/ubicaciones/subdependencias/`, { headers }),
        ]);
        setDependencias(depRes.data.results || depRes.data);
        setSubdependencias(subRes.data.results || subRes.data);
      }
      setError(null);
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const fetchDependenciasForSede = async (sedeId: number) => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const resp = await axios.get(`${API_URL}/api/ubicaciones/sedes/${sedeId}/dependencias/`, { headers });
      setSedeDependenciasMap((m) => ({ ...m, [sedeId]: resp.data }));
    } catch (err) {
      console.error('Error fetching dependencias for sede', err);
    }
  };

  const fetchSubdependenciasForDependencia = async (dependenciaId: number) => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const resp = await axios.get(`${API_URL}/api/ubicaciones/dependencias/${dependenciaId}/subdependencias/`, { headers });
      setDependenciaSubMap((m) => ({ ...m, [dependenciaId]: resp.data }));
    } catch (err) {
      console.error('Error fetching subdependencias for dependencia', err);
    }
  };

  // ==================== SEDES ====================
  const handleCreateSede = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };

      if (editingSede) {
        // send nombre, direccion and activo
        await axios.put(`${API_URL}/api/ubicaciones/sedes/${editingSede.id}/`, {
          nombre: sedeForm.nombre,
          direccion: sedeForm.direccion,
          activo: sedeForm.activo,
        }, { headers });
        setSuccess('Sede actualizada correctamente');
      } else {
        await axios.post(`${API_URL}/api/ubicaciones/sedes/`, {
          nombre: sedeForm.nombre,
          direccion: sedeForm.direccion,
          activo: sedeForm.activo,
        }, { headers });
        setSuccess('Sede creada correctamente');
      }

      setShowSedeModal(false);
      setEditingSede(null);
      resetSedeForm();
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar la sede');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSede = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar esta sede?')) return;

    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      setLoading(true);
      await axios.delete(`${API_URL}/api/ubicaciones/sedes/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess('Sede eliminada correctamente');
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar la sede');
    } finally {
      setLoading(false);
    }
  };

  const openSedeModal = (sede?: Sede) => {
    if (sede) {
      setEditingSede(sede);
      setSedeForm({
        nombre: sede.nombre,
        direccion: sede.direccion || '',
        activo: sede.activo,
      });
    } else {
      resetSedeForm();
    }
    setShowSedeModal(true);
  };

  const resetSedeForm = () => {
    setSedeForm({
      nombre: '',
      direccion: '',
      activo: true,
    });
    setEditingSede(null);
  };

  // ==================== DEPENDENCIAS ====================
  const handleCreateDependencia = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) return;

    if (!dependenciaForm.sede) {
      setError('Debe seleccionar una sede');
      return;
    }

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };

      if (editingDependencia) {
        await axios.put(`${API_URL}/api/ubicaciones/dependencias/${editingDependencia.id}/`, {
          sede: dependenciaForm.sede,
          nombre: dependenciaForm.nombre,
          activo: dependenciaForm.activo,
        }, { headers });
        setSuccess('Dependencia actualizada correctamente');
      } else {
        await axios.post(`${API_URL}/api/ubicaciones/dependencias/`, {
          sede: dependenciaForm.sede,
          nombre: dependenciaForm.nombre,
          activo: dependenciaForm.activo,
        }, { headers });
        setSuccess('Dependencia creada correctamente');
      }

      setShowDependenciaModal(false);
      setEditingDependencia(null);
      resetDependenciaForm();
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar la dependencia');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDependencia = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar esta dependencia?')) return;

    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      setLoading(true);
      await axios.delete(`${API_URL}/api/ubicaciones/dependencias/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess('Dependencia eliminada correctamente');
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar la dependencia');
    } finally {
      setLoading(false);
    }
  };

  const openDependenciaModal = (dependencia?: Dependencia) => {
    if (dependencia) {
      setEditingDependencia(dependencia);
      setDependenciaForm({
        sede: dependencia.sede,
        nombre: dependencia.nombre,
        activo: (dependencia as any).activo ?? true,
      });
    } else {
      resetDependenciaForm();
    }
    setShowDependenciaModal(true);
  };

  const resetDependenciaForm = () => {
    setDependenciaForm({
      sede: 0,
      nombre: '',
      activo: true,
    });
    setEditingDependencia(null);
  };

  // ==================== SUBDEPENDENCIAS ====================
  const handleCreateSubdependencia = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) return;

    if (!subdependenciaForm.dependencia) {
      setError('Debe seleccionar una dependencia');
      return;
    }

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };

      if (editingSubdependencia) {
        await axios.put(`${API_URL}/api/ubicaciones/subdependencias/${editingSubdependencia.id}/`, {
          dependencia: subdependenciaForm.dependencia,
          nombre: subdependenciaForm.nombre,
          activo: subdependenciaForm.activo,
        }, { headers });
        setSuccess('Subdependencia actualizada correctamente');
      } else {
        await axios.post(`${API_URL}/api/ubicaciones/subdependencias/`, {
          dependencia: subdependenciaForm.dependencia,
          nombre: subdependenciaForm.nombre,
          activo: subdependenciaForm.activo,
        }, { headers });
        setSuccess('Subdependencia creada correctamente');
      }

      setShowSubdependenciaModal(false);
      setEditingSubdependencia(null);
      resetSubdependenciaForm();
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar la subdependencia');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSubdependencia = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar esta subdependencia?')) return;

    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      setLoading(true);
      await axios.delete(`${API_URL}/api/ubicaciones/subdependencias/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess('Subdependencia eliminada correctamente');
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar la subdependencia');
    } finally {
      setLoading(false);
    }
  };

  const openSubdependenciaModal = (subdependencia?: Subdependencia) => {
    if (subdependencia) {
      setEditingSubdependencia(subdependencia);
      setSubdependenciaForm({
        dependencia: subdependencia.dependencia,
        nombre: subdependencia.nombre,
        activo: (subdependencia as any).activo ?? true,
      });
    } else {
      resetSubdependenciaForm();
    }
    setShowSubdependenciaModal(true);
  };

  const resetSubdependenciaForm = () => {
    setSubdependenciaForm({
      dependencia: 0,
      nombre: '',
      activo: true,
    });
    setEditingSubdependencia(null);
  };

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-black">Gestión de Ubicaciones</h1>
          <p className="text-sm text-black mt-1">
            Administre sedes, dependencias y subdependencias de la organización
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
            <button onClick={() => setError(null)} className="float-right font-bold">×</button>
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {success}
            <button onClick={() => setSuccess(null)} className="float-right font-bold">×</button>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {(['sedes', 'dependencias', 'subdependencias'] as TabType[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Cargando...</p>
          </div>
        ) : (
          <>
            {/* SEDES TAB */}
            {activeTab === 'sedes' && (
              <div>
                <div className="mb-4 flex justify-between items-center">
                  <h2 className="text-xl font-semibold">Sedes</h2>
                  <button
                    onClick={() => openSedeModal()}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    + Nueva Sede
                  </button>
                </div>

                <div className="bg-white shadow-md rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Nombre</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Dirección</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Estado</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Dependencias</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {sedes.map((sede) => (
                        <React.Fragment key={sede.id}>
                          <tr>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{sede.nombre}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{sede.direccion || '-'}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {sede.activo ? (
                                <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">Activo</span>
                              ) : (
                                <span className="px-2 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">Inactivo</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{sede.dependencias_count || 0}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <button
                                  onClick={() => openSedeModal(sede)}
                                className="text-blue-600 hover:text-blue-900 mr-3"
                                title="Editar"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                  <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleDeleteSede(sede.id)}
                                className="text-red-600 hover:text-red-900"
                                title="Eliminar"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                  <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                </svg>
                              </button>
                              <button
                                onClick={async () => {
                                  // toggle expand
                                  if (expandedSedes.includes(sede.id)) {
                                    setExpandedSedes((arr) => arr.filter((x) => x !== sede.id));
                                  } else {
                                    await fetchDependenciasForSede(sede.id);
                                    setExpandedSedes((arr) => [...arr, sede.id]);
                                  }
                                }}
                                className="ml-3 text-gray-600 hover:text-gray-900"
                                title="Ver dependencias"
                              >
                                Ver dependencias
                              </button>
                            </td>
                          </tr>
                          {expandedSedes.includes(sede.id) && (
                            <tr>
                              <td colSpan={5} className="bg-gray-50 px-6 py-4">
                                <div className="text-sm text-black">
                                  <strong>Dependencias de {sede.nombre}:</strong>
                                  <ul className="mt-2 list-disc list-inside">
                                    {(sedeDependenciasMap[sede.id] || []).map((d) => (
                                      <li key={d.id}>{d.nombre} {d.codigo ? `(${d.codigo})` : ''}</li>
                                    ))}
                                  </ul>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* DEPENDENCIAS TAB */}
            {activeTab === 'dependencias' && (
              <div>
                <div className="mb-4 flex justify-between items-center">
                  <h2 className="text-xl font-semibold">Dependencias</h2>
                  <button
                    onClick={() => openDependenciaModal()}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    + Nueva Dependencia
                  </button>
                </div>

                <div className="bg-white shadow-md rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Sede</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Nombre</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Subdependencias</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {dependencias.map((dep) => (
                        <React.Fragment key={dep.id}>
                          <tr>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{dep.sede_nombre}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{dep.nombre}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{dep.subdependencias_count || 0}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <button
                                onClick={() => openDependenciaModal(dep)}
                                className="text-blue-600 hover:text-blue-900 mr-3"
                                title="Editar"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                  <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleDeleteDependencia(dep.id)}
                                className="text-red-600 hover:text-red-900"
                                title="Eliminar"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                  <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                </svg>
                              </button>
                              <button
                                onClick={async () => {
                                  if (expandedDependencias.includes(dep.id)) {
                                    setExpandedDependencias((arr) => arr.filter((x) => x !== dep.id));
                                  } else {
                                    await fetchSubdependenciasForDependencia(dep.id);
                                    setExpandedDependencias((arr) => [...arr, dep.id]);
                                  }
                                }}
                                className="ml-3 text-gray-600 hover:text-gray-900"
                                title="Ver subdependencias"
                              >
                                Ver subdependencias
                              </button>
                            </td>
                          </tr>
                          {expandedDependencias.includes(dep.id) && (
                            <tr>
                              <td colSpan={4} className="bg-gray-50 px-6 py-4">
                                <div className="text-sm text-black">
                                  <strong>Subdependencias de {dep.nombre}:</strong>
                                  <ul className="mt-2 list-disc list-inside">
                                    {(dependenciaSubMap[dep.id] || []).map((s) => (
                                      <li key={s.id}>{s.nombre}</li>
                                    ))}
                                  </ul>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* SUBDEPENDENCIAS TAB */}
            {activeTab === 'subdependencias' && (
              <div>
                <div className="mb-4 flex justify-between items-center">
                  <h2 className="text-xl font-semibold">Subdependencias</h2>
                  <button
                    onClick={() => openSubdependenciaModal()}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    + Nueva Subdependencia
                  </button>
                </div>

                <div className="bg-white shadow-md rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Sede</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Dependencia</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Nombre</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {subdependencias.map((sub) => (
                        <tr key={sub.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{sub.sede_nombre}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-black">{sub.dependencia_nombre}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{sub.nombre}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <button
                              onClick={() => openSubdependenciaModal(sub)}
                              className="text-blue-600 hover:text-blue-900 mr-3"
                              title="Editar"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleDeleteSubdependencia(sub.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Eliminar"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                              </svg>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {/* Modal Sede */}
        {showSedeModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">
                {editingSede ? 'Editar Sede' : 'Nueva Sede'}
              </h2>
              <form onSubmit={handleCreateSede}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                  <input
                    type="text"
                    required
                    value={sedeForm.nombre}
                    onChange={(e) => setSedeForm({ ...sedeForm, nombre: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Dirección</label>
                  <input
                    type="text"
                    value={sedeForm.direccion}
                    onChange={(e) => setSedeForm({ ...sedeForm, direccion: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4 flex items-center">
                  <input
                    id="sede-activo"
                    type="checkbox"
                    checked={sedeForm.activo}
                    onChange={(e) => setSedeForm({ ...sedeForm, activo: e.target.checked })}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <label htmlFor="sede-activo" className="ml-2 text-sm text-gray-700">Activo</label>
                </div>
                {/* Only nombre and direccion are required for sedes */}
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowSedeModal(false);
                      resetSedeForm();
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {loading ? 'Guardando...' : 'Guardar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Dependencia */}
        {showDependenciaModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">
                {editingDependencia ? 'Editar Dependencia' : 'Nueva Dependencia'}
              </h2>
              <form onSubmit={handleCreateDependencia}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Sede *</label>
                  <select
                    required
                    value={dependenciaForm.sede}
                    onChange={(e) => setDependenciaForm({ ...dependenciaForm, sede: Number(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  >
                    <option value="">Seleccione una sede</option>
                    {sedes.map((sede) => (
                      <option key={sede.id} value={sede.id}>
                        {sede.nombre}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                  <input
                    type="text"
                    required
                    value={dependenciaForm.nombre}
                    onChange={(e) => setDependenciaForm({ ...dependenciaForm, nombre: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4 flex items-center">
                  <input
                    id="dependencia-activo"
                    type="checkbox"
                    checked={dependenciaForm.activo}
                    onChange={(e) => setDependenciaForm({ ...dependenciaForm, activo: e.target.checked })}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <label htmlFor="dependencia-activo" className="ml-2 text-sm text-gray-700">Activo</label>
                </div>
                {/* Only sede + nombre for dependencias */}
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowDependenciaModal(false);
                      resetDependenciaForm();
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {loading ? 'Guardando...' : 'Guardar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Subdependencia */}
        {showSubdependenciaModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">
                {editingSubdependencia ? 'Editar Subdependencia' : 'Nueva Subdependencia'}
              </h2>
              <form onSubmit={handleCreateSubdependencia}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Dependencia *</label>
                  <select
                    required
                    value={subdependenciaForm.dependencia}
                    onChange={(e) => setSubdependenciaForm({ ...subdependenciaForm, dependencia: Number(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  >
                    <option value="">Seleccione una dependencia</option>
                    {dependencias.map((dep) => (
                      <option key={dep.id} value={dep.id}>
                        {dep.sede_nombre} - {dep.nombre}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                  <input
                    type="text"
                    required
                    value={subdependenciaForm.nombre}
                    onChange={(e) => setSubdependenciaForm({ ...subdependenciaForm, nombre: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4 flex items-center">
                  <input
                    id="subdependencia-activo"
                    type="checkbox"
                    checked={subdependenciaForm.activo}
                    onChange={(e) => setSubdependenciaForm({ ...subdependenciaForm, activo: e.target.checked })}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <label htmlFor="subdependencia-activo" className="ml-2 text-sm text-gray-700">Activo</label>
                </div>
                {/* Only dependencia + nombre for subdependencias */}
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowSubdependenciaModal(false);
                      resetSubdependenciaForm();
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {loading ? 'Guardando...' : 'Guardar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        </div>
      </div>
    </Layout>
  );
}
