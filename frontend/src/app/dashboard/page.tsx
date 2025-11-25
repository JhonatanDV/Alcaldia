'use client';

import axios from 'axios';
import { useEffect, useState } from 'react';
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis, YAxis
} from 'recharts';
import Layout from '../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

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
  const [dependenciasOptions, setDependenciasOptions] = useState<string[]>([]);
  const [sedesOptions, setSedesOptions] = useState<string[]>([]);
  const [subdependenciasOptions, setSubdependenciasOptions] = useState<string[]>([]);
  const [equiposOptions, setEquiposOptions] = useState<string[]>([]);

  const fetchDashboardData = async (filters: any = {}) => {
  const token = localStorage.getItem('access_token');
  // Normalize stored role in case backend returned spanish/variant values
  const { normalizeRole } = await import('@/lib/role');
  const rawRole = localStorage.getItem('user_role');
  const role = normalizeRole(rawRole) as 'admin' | 'technician' | null;
    
    if (!token) {
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
      // Request headers prepared; executing API calls. Pass client filters to endpoints that accept them.
      const [statsResponse, chartsResponse, recentActivityResponse, filterOptionsResponse, equipmentListResponse, subdependenciasResponse] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats/`, { headers, params: filters }),
        axios.get(`${API_URL}/api/dashboard/charts/`, { headers, params: filters }),
        axios.get(`${API_URL}/api/dashboard/recent-activity/`, { headers, params: filters }),
        axios.get(`${API_URL}/api/dashboard/filter-options/`, { headers }),
        axios.get(`${API_URL}/api/dashboard/equipment/`, { headers, params: filters }),
        axios.get(`${API_URL}/api/ubicaciones/subdependencias/`, { headers }),
      ]);

      const overview = statsResponse.data.overview || {};
      // Combinar los datos de las diferentes respuestas (usar overview devuelto por el servidor)
      const combinedStats = {
        summary: {
          total_maintenances: overview.total_maintenances || 0,
          total_equipments: overview.total_equipment || 0,
          total_reports: overview.total_reports || 0,
          total_incidents: overview.total_incidents || 0,
        },
        // removed detailed breakdown by type/status — keep empty arrays for compatibility
        maintenances_by_type: [],
        maintenances_by_month: chartsResponse.data.maintenances_per_month,
        maintenances_by_dependency: [],
        maintenances_by_sede: [],
        recent_maintenances: statsResponse.data.recent_maintenances || recentActivityResponse.data.recent_maintenances,
        top_equipment: chartsResponse.data.equipment_most_maintenances,
        ratings_distribution: [],
      };

      const combinedEquipmentStats = {
        equipment_with_last_maintenance: (combinedStats.recent_maintenances || []).map((m: any, idx: number) => ({
          id: m.id || idx,
          placa: m.equipment_serial || m.equipment_name || (`EQ-${idx}`),
          equipment_type: m.maintenance_type,
          last_maintenance_date: m.scheduled_date || m.completion_date,
          days_since_maintenance: 0,
        })),
        equipment_without_maintenance: (recentActivityResponse.data.equipment_needing_maintenance || []).map((e: any) => ({
          id: e.id,
          placa: e.serial || e.name || String(e.id),
          equipment_type: 'N/A',
        })),
      };

      setStats(combinedStats);
      setFilteredStats(combinedStats); // Initialize filtered stats (server already applied filters)
      setEquipmentStats(combinedEquipmentStats);

      // populate filter dropdown options from filter-options endpoint and equipment/subdependencias endpoints
      const filtersResp = filterOptionsResponse.data || {};
      setSedesOptions((filtersResp.sedes || []).slice().sort());
      setDependenciasOptions((filtersResp.dependencias || []).slice().sort());

      // equipos list from /api/dashboard/equipment/
      const equipmentList = equipmentListResponse.data || [];
      const eqSet = new Set<string>(equipmentList.map((e: any) => e.serial || e.equipment_serial || e.name || String(e.id)));
      setEquiposOptions(Array.from(eqSet).sort());

      // subdependencias from config endpoint
      const subsList = subdependenciasResponse.data || [];
      setSubdependenciasOptions(subsList.map((s: any) => s.nombre).sort());
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

  // Filters are applied server-side: when `searchFilters` changes we re-fetch stats (see useEffect above)

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
      <div className="space-y-6">{/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-black">Dashboard de Mantenimientos</h1>
              <p className="text-sm text-black mt-1">Vista general del sistema</p>
            </div>
          </div>
        </div>

        {/* Search Filters (simplified) */}
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-black mb-4">Filtros del Dashboard</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label htmlFor="dashboard-search" className="block text-sm font-medium text-black">Búsqueda General</label>
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
              <label htmlFor="dashboard-dependencia" className="block text-sm font-medium text-black">Dependencia</label>
              <select
                id="dashboard-dependencia"
                value={searchFilters.equipment_dependencia || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, equipment_dependencia: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black bg-white"
              >
                <option value="">(Todas)</option>
                {dependenciasOptions.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="dashboard-sede" className="block text-sm font-medium text-black">Sede</label>
              <select
                id="dashboard-sede"
                value={searchFilters.sede || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, sede: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black bg-white"
              >
                <option value="">(Todas)</option>
                {sedesOptions.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="dashboard-subdependencia" className="block text-sm font-medium text-black">Subdependencia</label>
              <select
                id="dashboard-subdependencia"
                value={searchFilters.subdependencia || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, subdependencia: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black bg-white"
              >
                <option value="">(Todas)</option>
                {subdependenciasOptions.map((sd) => <option key={sd} value={sd}>{sd}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="dashboard-equipo" className="block text-sm font-medium text-black">Equipo (Placa)</label>
              <select
                id="dashboard-equipo"
                value={searchFilters.equipment_placa || ''}
                onChange={(e) => setSearchFilters((prev: any) => ({ ...prev, equipment_placa: e.target.value }))}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black bg-white"
              >
                <option value="">(Todas)</option>
                {equiposOptions.map((eq) => <option key={eq} value={eq}>{eq}</option>)}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setSearchFilters({})}
                className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-black bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Limpiar Filtros
              </button>
            </div>
          </div>
        </div>

  <h2 className="text-3xl font-bold text-black mb-8">Dashboard de Mantenimientos</h2>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-black text-sm font-medium">Total Mantenimientos</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {filteredStats?.summary.total_maintenances || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-black text-sm font-medium">Total Equipos</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {filteredStats?.summary.total_equipments || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-black text-sm font-medium">Reportes Generados</h3>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {filteredStats?.summary.total_reports || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-black text-sm font-medium">Incidentes</h3>
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
              <p className="text-black text-center py-20">No hay datos disponibles</p>
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
              <p className="text-black text-center py-20">No hay datos disponibles</p>
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
              <p className="text-black text-center py-20">No hay datos disponibles</p>
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
              <p className="text-black text-center py-10">No hay equipos con mantenimientos registrados</p>
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
              <p className="text-black text-center py-10">Todos los equipos tienen mantenimientos registrados</p>
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
            <p className="text-black text-center py-10">No hay mantenimientos registrados</p>
          )}
        </div>
      </div>
    </Layout>
  );
}
