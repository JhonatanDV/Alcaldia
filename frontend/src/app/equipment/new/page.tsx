'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function NewEquipmentPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    serial_number: '',
    brand: '',
    model: '',
    sede: '',
    dependencia: '',
    subdependencia: '',
    location: '',
  });
  const [sedes, setSedes] = useState<any[]>([]);
  const [dependencias, setDependencias] = useState<any[]>([]);
  const [subdependencias, setSubdependencias] = useState<any[]>([]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
    
    if (!token) {
      window.location.href = '/';
      return;
    }

    setUserRole(role);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const fetchSedes = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.get(`${API_URL}/api/ubicaciones/sedes/`, { headers });
      // API may return paginated results
      setSedes(res.data.results || res.data || []);
    } catch (err) {
      console.error('Error cargando sedes', err);
    }
  };

  const fetchDependencias = async (sedeId: string | number) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      // Prefer the nested endpoint that returns dependencias for a sede
      const res = await axios.get(`${API_URL}/api/ubicaciones/sedes/${sedeId}/dependencias/`, { headers });
      setDependencias(res.data || []);
    } catch (err) {
      console.error('Error cargando dependencias', err);
      setDependencias([]);
    }
  };

  const fetchSubdependencias = async (dependenciaId: string | number) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      // Prefer the nested endpoint that returns subdependencias for a dependencia
      const res = await axios.get(`${API_URL}/api/ubicaciones/dependencias/${dependenciaId}/subdependencias/`, { headers });
      setSubdependencias(res.data || []);
    } catch (err) {
      console.error('Error cargando subdependencias', err);
      setSubdependencias([]);
    }
  };

  useEffect(() => {
    fetchSedes();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        window.location.href = '/';
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };

      const payload: any = {
        ...formData,
        sede_rel: formData.sede || null,
        dependencia_rel: formData.dependencia || null,
        subdependencia: formData.subdependencia || null,
      };

      await axios.post(`${API_URL}/api/equipments/`, payload, { headers });
      
      setSuccess(true);
      setFormData({ code: '', name: '', serial_number: '', brand: '', model: '', sede: '', dependencia: '', subdependencia: '', location: '' });
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
    } catch (err: any) {
      console.error('Error creating equipment:', err);
      setError(err.response?.data?.detail || err.response?.data?.code?.[0] || 'Error al crear equipo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Nuevo Equipo
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Registra un nuevo equipo en el sistema
          </p>
        </div>

        {/* Form Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 lg:p-8">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">Agregar Nuevo Equipo</h2>

          {error && (
            <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ✅ Equipo creado exitosamente. Redirigiendo al dashboard...
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
            {/* Grid para campos en 2 columnas en pantallas medianas y grandes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Código del Equipo <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="code"
                  name="code"
                  required
                  value={formData.code}
                  onChange={handleInputChange}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Ej: EQ-001"
                />
                <p className="mt-1 text-xs sm:text-sm text-gray-500">
                  Código único del equipo
                </p>
              </div>

              <div>
                <label htmlFor="serial_number" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Número de Serie <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="serial_number"
                  name="serial_number"
                  required
                  value={formData.serial_number}
                  onChange={handleInputChange}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Ej: SN123456789"
                />
                <p className="mt-1 text-xs sm:text-sm text-gray-500">
                  Número de serie del fabricante
                </p>
              </div>
            </div>

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                Nombre del Equipo <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Ej: Computador de escritorio HP"
              />
              <p className="mt-1 text-xs sm:text-sm text-gray-500">
                Nombre o descripción del equipo
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label htmlFor="brand" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Marca <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="brand"
                  name="brand"
                  required
                  value={formData.brand}
                  onChange={handleInputChange}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Ej: HP, Dell, Lenovo"
                />
                <p className="mt-1 text-xs sm:text-sm text-gray-500">
                  Marca del equipo
                </p>
              </div>

              <div>
                <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Modelo <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="model"
                  name="model"
                  required
                  value={formData.model}
                  onChange={handleInputChange}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Ej: Pavilion 15, Latitude 5420"
                />
                <p className="mt-1 text-xs sm:text-sm text-gray-500">
                  Modelo específico
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label htmlFor="sede" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Sede
                </label>
                <select
                  id="sede"
                  name="sede"
                  value={formData.sede}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({ ...prev, sede: value, dependencia: '', subdependencia: '' }));
                    if (value) fetchDependencias(value);
                    else setDependencias([]);
                    setSubdependencias([]);
                  }}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">-- Seleccione una sede --</option>
                  {sedes.map((s) => (
                    <option key={s.id} value={s.id}>{s.name || s.nombre || s.label || s.id}</option>
                  ))}
                </select>
                <p className="mt-1 text-xs sm:text-sm text-gray-500">Seleccione la sede del equipo (opcional)</p>
              </div>

              <div>
                <label htmlFor="dependencia" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                  Dependencia
                </label>
                <select
                  id="dependencia"
                  name="dependencia"
                  value={formData.dependencia}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({ ...prev, dependencia: value, subdependencia: '' }));
                    if (value) fetchSubdependencias(value);
                    else setSubdependencias([]);
                  }}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">-- Seleccione una dependencia --</option>
                  {dependencias.map((d) => (
                    <option key={d.id} value={d.id}>{d.name || d.nombre || d.label || d.id}</option>
                  ))}
                </select>
                <p className="mt-1 text-xs sm:text-sm text-gray-500">Área o departamento (opcional)</p>
              </div>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1 sm:mb-2">
                Ubicación (Subdependencia) <span className="text-red-500">*</span>
              </label>
              <select
                id="location"
                name="location"
                required
                value={formData.subdependencia}
                onChange={(e) => {
                  const selectedId = e.target.value;
                  const selectedText = e.target.options[e.target.selectedIndex]?.text || '';
                  setFormData((prev) => ({ ...prev, subdependencia: selectedId, location: selectedText }));
                }}
                className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">-- Seleccione una subdependencia --</option>
                {subdependencias.map((s) => (
                  <option key={s.id} value={s.id}>{s.name || s.nombre || s.label || s.id}</option>
                ))}
              </select>
              <p className="mt-1 text-xs sm:text-sm text-gray-500">Seleccione la subdependencia donde se localiza el equipo (obligatorio)</p>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3 sm:gap-4 pt-4 sm:pt-6 border-t">
              <a
                href="/equipment"
                className="px-4 sm:px-6 py-2 sm:py-2.5 text-sm sm:text-base text-center border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </a>
              <button
                type="submit"
                disabled={loading}
                className="px-4 sm:px-6 py-2 sm:py-2.5 text-sm sm:text-base bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Guardando...' : 'Guardar Equipo'}
              </button>
            </div>
          </form>
        </div>

        <div className="mt-4 sm:mt-6 bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 Información</h3>
          <ul className="text-xs sm:text-sm text-blue-800 space-y-1">
            <li>• El código y número de serie deben ser únicos</li>
            <li>• Una vez creado, podrá registrar mantenimientos</li>
            <li>• Los campos con <span className="text-red-500">*</span> son obligatorios</li>
            <li>• La marca y modelo se registrarán automáticamente</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
