'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

interface DashboardStats {
  summary: {
    total_maintenances: number;
    total_equipments: number;
    total_reports: number;
    total_incidents: number;
  };
  maintenances_by_type: Array<{ maintenance_type: string; count: number }>;
  maintenances_by_dependency: Array<{ dependencia: string; count: number }>;
  maintenances_by_sede: Array<{ sede: string; count: number }>;
  maintenances_by_month: Array<{ month: string; count: number }>;
  recent_maintenances: Array<any>;
  top_equipment: Array<{ placa: string; maintenance_count: number }>;
  ratings_distribution: Array<{ rating: number; count: number }>;
}

interface EquipmentStats {
  equipment_with_last_maintenance: Array<{
    id: number;
    placa: string;
    equipment_type: string;
    last_maintenance_date: string;
    days_since_maintenance: number;
  }>;
  equipment_without_maintenance: Array<{
    id: number;
    placa: string;
    equipment_type: string;
  }>;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [equipmentStats, setEquipmentStats] = useState<EquipmentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
        
        if (!token) {
          // Redirect to login if not authenticated
          window.location.href = '/';
          return;
        }

        setUserRole(role);

        const headers = {
          Authorization: `Bearer ${token}`,
        };

        const [statsResponse, equipmentResponse] = await Promise.all([
          axios.get(`${API_URL}/api/dashboard/`, { headers }),
          axios.get(`${API_URL}/api/dashboard/equipment/`, { headers }),
        ]);

        setStats(statsResponse.data);
        setEquipmentStats(equipmentResponse.data);
        setLoading(false);
      } catch (err: any) {
        console.error('Error fetching dashboard:', err);
        setError(err.response?.data?.detail || 'Error al cargar el dashboard');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    window.location.href = '/';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard de Mantenimientos</h1>
            </div>
          </div>
        </header>
        <div className="max-w-7xl mx-auto p-8">
          <p className="text-gray-600">Cargando estadísticas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard de Mantenimientos</h1>
            </div>
          </div>
        </header>
        <div className="max-w-7xl mx-auto p-8">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (!stats || !equipmentStats) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Navigation */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">
                Sistema de Mantenimiento
              </h1>
              {userRole && (
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  userRole === 'admin'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {userRole === 'admin' ? 'Administrador' : 'Técnico'}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/equipment/new"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <svg
                  className="mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Nuevo Equipo
              </a>
              <a
                href="/maintenance/new"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
              >
                <svg
                  className="mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Nuevo Mantenimiento
              </a>
              {userRole === 'admin' && (
                <a
                  href="/admin/users"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700"
                >
                  Usuarios
                </a>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard de Mantenimientos</h2>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Total Mantenimientos</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {stats.summary.total_maintenances}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Total Equipos</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {stats.summary.total_equipments}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Reportes Generados</h3>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {stats.summary.total_reports}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Incidentes</h3>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {stats.summary.total_incidents}
            </p>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Maintenances by Month */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Mes (Últimos 12 meses)
            </h2>
            {stats.maintenances_by_month && stats.maintenances_by_month.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.maintenances_by_month}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" name="Mantenimientos" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-20">No hay datos disponibles</p>
            )}
          </div>

          {/* Maintenances by Type */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Tipo
            </h2>
            {stats.maintenances_by_type && stats.maintenances_by_type.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.maintenances_by_type}
                    dataKey="count"
                    nameKey="maintenance_type"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {stats.maintenances_by_type.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-20">No hay datos disponibles</p>
            )}
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Maintenances by Dependency */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Dependencia
            </h2>
            {stats.maintenances_by_dependency && stats.maintenances_by_dependency.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.maintenances_by_dependency}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="dependencia" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#82ca9d" name="Mantenimientos" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-20">No hay datos disponibles</p>
            )}
          </div>

          {/* Maintenances by Sede */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Sede
            </h2>
            {stats.maintenances_by_sede && stats.maintenances_by_sede.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.maintenances_by_sede}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="sede" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#8884d8" name="Mantenimientos" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-20">No hay datos disponibles</p>
            )}
          </div>
        </div>

        {/* Top Equipment */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Top 10 Equipos con Más Mantenimientos
          </h2>
          {stats.top_equipment && stats.top_equipment.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.top_equipment}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="placa" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="maintenance_count" fill="#FF8042" name="Mantenimientos" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-20">No hay datos disponibles</p>
          )}
        </div>

        {/* Equipment Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Equipment needing maintenance soon */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Equipos con Mantenimiento Reciente
            </h2>
            {equipmentStats.equipment_with_last_maintenance && equipmentStats.equipment_with_last_maintenance.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Placa
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Tipo
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Días desde mantenimiento
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {equipmentStats.equipment_with_last_maintenance.slice(0, 10).map((eq) => (
                      <tr key={eq.id} className={eq.days_since_maintenance > 180 ? 'bg-yellow-50' : ''}>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {eq.placa}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {eq.equipment_type}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {eq.days_since_maintenance} días
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-10">No hay equipos con mantenimientos registrados</p>
            )}
          </div>

          {/* Equipment without maintenance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Equipos sin Mantenimiento
              {equipmentStats.equipment_without_maintenance && (
                <span className="ml-2 text-sm text-red-600">
                  ({equipmentStats.equipment_without_maintenance.length})
                </span>
              )}
            </h2>
            {equipmentStats.equipment_without_maintenance && equipmentStats.equipment_without_maintenance.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Placa
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Tipo
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {equipmentStats.equipment_without_maintenance.slice(0, 10).map((eq) => (
                      <tr key={eq.id} className="bg-red-50">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {eq.placa}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {eq.equipment_type}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-10">Todos los equipos tienen mantenimientos registrados</p>
            )}
          </div>
        </div>

        {/* Recent Maintenances */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Últimos 5 Mantenimientos
          </h2>
          {stats.recent_maintenances && stats.recent_maintenances.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Fecha
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Equipo
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Tipo
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Dependencia
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Incidente
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.recent_maintenances.map((maint) => (
                    <tr key={maint.id}>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {new Date(maint.date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {maint.equipment_placa}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {maint.maintenance_type}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {maint.equipment_dependencia}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {maint.is_incident ? (
                          <span className="px-2 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">
                            Sí
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">
                            No
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-10">No hay mantenimientos registrados</p>
          )}
        </div>
      </div>
    </div>
  );
}
