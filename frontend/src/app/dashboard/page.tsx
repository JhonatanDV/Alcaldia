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

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setError('No está autenticado');
          setLoading(false);
          return;
        }

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
          <p className="text-gray-600">Cargando estadísticas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard de Mantenimientos</h1>

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
          </div>

          {/* Maintenances by Type */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Tipo
            </h2>
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
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Maintenances by Dependency */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Dependencia
            </h2>
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
          </div>

          {/* Maintenances by Sede */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Mantenimientos por Sede
            </h2>
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
          </div>
        </div>

        {/* Top Equipment */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Top 10 Equipos con Más Mantenimientos
          </h2>
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
        </div>

        {/* Equipment Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Equipment needing maintenance soon */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Equipos con Mantenimiento Reciente
            </h2>
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
          </div>

          {/* Equipment without maintenance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Equipos sin Mantenimiento
              <span className="ml-2 text-sm text-red-600">
                ({equipmentStats.equipment_without_maintenance.length})
              </span>
            </h2>
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
          </div>
        </div>

        {/* Recent Maintenances */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Últimos 5 Mantenimientos
          </h2>
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
        </div>
      </div>
    </div>
  );
}
