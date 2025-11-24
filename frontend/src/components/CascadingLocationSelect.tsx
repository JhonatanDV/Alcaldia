'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Sede {
  id: number;
  nombre: string;
  codigo?: string;
  activo: boolean;
}

interface Dependencia {
  id: number;
  nombre: string;
  sede: number;
  sede_nombre: string;
  codigo?: string;
  activo: boolean;
}

interface Subdependencia {
  id: number;
  nombre: string;
  dependencia: number;
  dependencia_nombre: string;
  sede_nombre: string;
  codigo?: string;
  activo: boolean;
}

interface CascadingLocationSelectProps {
  sedeId?: number | null;
  dependenciaId?: number | null;
  subdependenciaId?: number | null;
  onSedeChange: (sedeId: number | null) => void;
  onDependenciaChange: (dependenciaId: number | null) => void;
  onSubdependenciaChange: (subdependenciaId: number | null) => void;
  required?: boolean;
  disabled?: boolean;
  showSubdependencia?: boolean;
}

export default function CascadingLocationSelect({
  sedeId,
  dependenciaId,
  subdependenciaId,
  onSedeChange,
  onDependenciaChange,
  onSubdependenciaChange,
  required = false,
  disabled = false,
  showSubdependencia = true,
}: CascadingLocationSelectProps) {
  const [sedes, setSedes] = useState<Sede[]>([]);
  const [dependencias, setDependencias] = useState<Dependencia[]>([]);
  const [subdependencias, setSubdependencias] = useState<Subdependencia[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar sedes al montar el componente
  useEffect(() => {
    fetchSedes();
  }, []);

  // Cargar dependencias cuando cambia la sede
  useEffect(() => {
    if (sedeId) {
      fetchDependencias(sedeId);
    } else {
      setDependencias([]);
      setSubdependencias([]);
      onDependenciaChange(null);
      onSubdependenciaChange(null);
    }
  }, [sedeId]);

  // Cargar subdependencias cuando cambia la dependencia
  useEffect(() => {
    if (dependenciaId) {
      fetchSubdependencias(dependenciaId);
    } else {
      setSubdependencias([]);
      onSubdependenciaChange(null);
    }
  }, [dependenciaId]);

  const fetchSedes = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await axios.get(`${API_URL}/api/config/sedes/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { activo: true }
      });

      setSedes(response.data.results || response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error cargando sedes:', err);
      setError('Error al cargar las sedes');
    } finally {
      setLoading(false);
    }
  };

  const fetchDependencias = async (sedeIdParam: number) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await axios.get(`${API_URL}/api/config/dependencias/por_sede/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { sede_id: sedeIdParam }
      });

      setDependencias(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error cargando dependencias:', err);
      setError('Error al cargar las dependencias');
      setDependencias([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubdependencias = async (dependenciaIdParam: number) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await axios.get(`${API_URL}/api/config/subdependencias/por_dependencia/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { dependencia_id: dependenciaIdParam }
      });

      setSubdependencias(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error cargando subdependencias:', err);
      setError('Error al cargar las subdependencias');
      setSubdependencias([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSedeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onSedeChange(value ? Number(value) : null);
  };

  const handleDependenciaChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onDependenciaChange(value ? Number(value) : null);
  };

  const handleSubdependenciaChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onSubdependenciaChange(value ? Number(value) : null);
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Select Sede */}
      <div>
        <label className="block text-sm font-medium text-black mb-1">
          Sede {required && <span className="text-red-500">*</span>}
        </label>
        <select
          value={sedeId || ''}
          onChange={handleSedeChange}
          disabled={disabled || loading}
          required={required}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Seleccione una sede</option>
          {sedes.map((sede) => (
            <option key={sede.id} value={sede.id}>
              {sede.nombre} {sede.codigo && `(${sede.codigo})`}
            </option>
          ))}
        </select>
      </div>

      {/* Select Dependencia */}
      <div>
        <label className="block text-sm font-medium text-black mb-1">
          Dependencia {required && <span className="text-red-500">*</span>}
        </label>
        <select
          value={dependenciaId || ''}
          onChange={handleDependenciaChange}
          disabled={!sedeId || disabled || loading}
          required={required}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="">
            {!sedeId ? 'Primero seleccione una sede' : 'Seleccione una dependencia'}
          </option>
          {dependencias.map((dep) => (
            <option key={dep.id} value={dep.id}>
              {dep.nombre} {dep.codigo && `(${dep.codigo})`}
            </option>
          ))}
        </select>
      </div>

      {/* Select Subdependencia */}
      {showSubdependencia && (
        <div>
          <label className="block text-sm font-medium text-black mb-1">
            Subdependencia (Opcional)
          </label>
          <select
            value={subdependenciaId || ''}
            onChange={handleSubdependenciaChange}
            disabled={!dependenciaId || disabled || loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">
              {!dependenciaId ? 'Primero seleccione una dependencia' : 'Sin subdependencia'}
            </option>
            {subdependencias.map((sub) => (
              <option key={sub.id} value={sub.id}>
                {sub.nombre} {sub.codigo && `(${sub.codigo})`}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
