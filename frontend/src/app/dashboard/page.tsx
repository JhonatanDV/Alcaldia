'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import Layout from '../../components/Layout';
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
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Search filters state
  const [searchFilters, setSearchFilters] = useState<any>({});
  const [filteredStats, setFilteredStats] = useState<DashboardStats | null>(null);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
    
    // Debug: Log token information
    console.log('=== DASHBOARD TOKEN DEBUG ===');
    console.log('Token exists:', !!token);
    console.log('Token length:', token?.length);
    console.log('Token preview:', token?.substring(0, 20) + '...');
    console.log('User role:', role);
    
    if (!token) {
      console.log('No token found, redirecting to login...');
      setIsAuthenticated(false);
      window.location.href = '/';
      return;
    }

    setIsAuthenticated(true);
    setUserRole(role);

    try {
      const headers = {
        Authorization: `Bearer ${token}`,
      };
      
      console.log('Request headers:', headers);
      console.log('Making requests to:', API_URL);

      // Cambiar las URLs para que coincidan con las rutas del backend
      const [statsResponse, chartsResponse, recentActivityResponse] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats/`, { headers }),
        axios.get(`${API_URL}/api/dashboard/charts/`, { headers }),
        axios.get(`${API_URL}/api/dashboard/recent-activity/`, { headers }),
      ]);

      // Combinar los datos de las diferentes respuestas
      const combinedStats = {
        summary: {
          total_maintenances: statsResponse.data.overview.total_maintenances,
          total_equipments: statsResponse.data.overview.total_equipment,
          total_reports: statsResponse.data.overview.total_reports,
          total_incidents: statsResponse.data.overview.total_incidents,
        },
        maintenances_by_type: statsResponse.data.maintenance_by_type,
        maintenances_by_month: chartsResponse.data.maintenances_per_month,
        maintenances_by_dependency: [], // Este dato no está en las vistas actuales
        maintenances_by_sede: [], // Este dato no está en las vistas actuales
        recent_maintenances: recentActivityResponse.data.recent_maintenances,
        top_equipment: chartsResponse.data.equipment_most_maintenances,
        ratings_distribution: [],
      };

      const combinedEquipmentStats = {
        equipment_with_last_maintenance: recentActivityResponse.data.recent_maintenances.map((m: any) => ({
          id: m.id,
          placa: m.equipment__code,
          equipment_type: m.maintenance_type,
          last_maintenance_date: m.maintenance_date,
          days_since_maintenance: 0,
        })),
        equipment_without_maintenance: recentActivityResponse.data.equipment_needing_maintenance.map((e: any) => ({
          id: e.id,
          placa: e.code,
          equipment_type: 'N/A',
        })),
      };

      setStats(combinedStats);
      setFilteredStats(combinedStats); // Initialize filtered stats
      setEquipmentStats(combinedEquipmentStats);
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching dashboard:', err);
      setError(err.response?.data?.detail || 'Error al cargar el dashboard');
      setLoading(false);
    }
  };

  // Initial fetch on mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      fetchDashboardData();
    }, 30000); // 30 segundos

    // Cleanup interval on unmount
    return () => clearInterval(refreshInterval);
  }, []);

  // Function to apply filters to dashboard stats
  const applyFilters = (stats: DashboardStats, filters: any) => {
    let filtered = { ...stats };

    // Filter maintenances by type
    if (filters.maintenance_type) {
      filtered.maintenances_by_type = stats.maintenances_by_type.filter(
        (item) => item.maintenance_type === filters.maintenance_type
      );
    }

    // Filter by status (if we had status data)
    // Note: Current backend doesn't provide status breakdown, but we can add it

    // Filter by sede (if we had sede data)
    // Note: Current backend doesn't provide sede breakdown, but we can add it

    // Filter by dependencia (if we had dependencia data)
    // Note: Current backend doesn't provide dependencia breakdown, but we can add it

    setFilteredStats(filtered);
  };

  // Apply filters when searchFilters change
  useEffect(() => {
    if (stats) {
      applyFilters(stats, searchFilters);
    }
  }, [searchFilters, stats]);

  // No renderizar nada si no está autenticado
  if (!isAuthenticated) {
    return null;
  }

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
          <p className="text-gray-600">Cargando estadísticas...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout userRole={userRole} onLogout={handleLogout}>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </Layout>
    );
  }

  if (!stats || !equipmentStats) {
    return null;
  }

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">{/* Header con acciones rápidas */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Dashboard de Mantenimientos
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Vista general del sistema
              </p>
            </div>
            <div className="flex flex-wrap gap-2 w-full sm:w-auto">
              {userRole === 'admin' && (
                <a
                  href="/equipment/new"
                  className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
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
              )}
              <a
                href="/maintenance/new"
                className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
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
            </div>
          </div>
        </div>

        {/* Search Filters */}
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filtros del Dashboard</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label htmlFor="dashboard-search" className="block text-sm font-medium text-gray-700">
                Búsqueda General
              </label>
              <input
                type="text"
                id="dashboard-search"
                value={searchFilters.search || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, search: e.target.value }))}
                placeholder="Buscar por equipo, dependencia..."
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              />
            </div>
            <div>
              <label htmlFor="dashboard-dependencia" className="block text-sm font-medium text-gray-700">
                Dependencia
              </label>
              <input
                type="text"
                id="dashboard-dependencia"
                value={searchFilters.equipment_dependencia || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, equipment_dependencia: e.target.value }))}
                placeholder="Filtrar por dependencia"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              />
            </div>
            <div>
              <label htmlFor="dashboard-sede" className="block text-sm font-medium text-gray-700">
                Sede
              </label>
              <input
                type="text"
                id="dashboard-sede"
                value={searchFilters.sede || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, sede: e.target.value }))}
                placeholder="Filtrar por sede"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              />
            </div>
            <div>
              <label htmlFor="dashboard-status" className="block text-sm font-medium text-gray-700">
                Estado
              </label>
              <select
                id="dashboard-status"
                value={searchFilters.status || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, status: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              >
                <option value="">Todos los estados</option>
                <option value="pending">Pendiente</option>
                <option value="in_progress">En Progreso</option>
                <option value="completed">Completado</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
            <div>
              <label htmlFor="dashboard-type" className="block text-sm font-medium text-gray-700">
                Tipo de Mantenimiento
              </label>
              <select
                id="dashboard-type"
                value={searchFilters.maintenance_type || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, maintenance_type: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              >
                <option value="">Todos los tipos</option>
                <option value="preventivo">Preventivo</option>
                <option value="correctivo">Correctivo</option>
                <option value="predictivo">Predictivo</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setSearchFilters({})}
                className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Limpiar Filtros
              </button>
            </div>
          </div>
        </div>

        <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard de Mantenimientos</h2>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Total Mantenimientos</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {filteredStats?.summary.total_maintenances || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Total Equipos</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {filteredStats?.summary.total_equipments || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Reportes Generados</h3>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {filteredStats?.summary.total_reports || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium">Incidentes</h3>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {filteredStats?.summary.total_incidents || 0}
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
            {filteredStats?.maintenances_by_type && filteredStats.maintenances_by_type.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={filteredStats?.maintenances_by_type || []}
                    dataKey="count"
                    nameKey="maintenance_type"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {filteredStats?.maintenances_by_type.map((entry, index) => (
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
            {filteredStats?.top_equipment && filteredStats.top_equipment.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={filteredStats?.top_equipment || []}>
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
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Acciones
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
                      <td className="px-4 py-3 text-sm">
                        <button
                          onClick={async () => {
                            const token = localStorage.getItem('access_token');
                            if (!token) return;
                            
                            try {
                              const response = await axios.post(
                                `${API_URL}/api/reports/generate/`,
                                { maintenance_id: maint.id },
                                { headers: { Authorization: `Bearer ${token}` } }
                              );
                              
                              if (response.data.pdf_file) {
                                const pdfUrl = response.data.pdf_file.startsWith('http') 
                                  ? response.data.pdf_file 
                                  : `${API_URL}${response.data.pdf_file}`;
                                window.open(pdfUrl, '_blank');
                              }
                            } catch (error) {
                              console.error('Error generando PDF:', error);
                              alert('Error al generar el reporte PDF');
                            }
                          }}
                          className="px-3 py-1 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                        >
                          Generar PDF
                        </button>
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
    </Layout>
  );
}
