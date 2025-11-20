import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface DashboardStats {
  overview: {
    total_equipment: number;
    total_maintenances: number;
    total_incidents: number;
    total_users: number;
    recent_maintenances: number;
    recent_incidents: number;
  };
  equipment_status: {
    operational: number;
    in_maintenance: number;
    damaged: number;
  };
  maintenance_by_type: Array<{ tipo_mantenimiento: string; count: number }>;
  incidents_by_status: Array<{ estado: string; count: number }>;
}

interface ChartData {
  maintenances_per_month: Array<{ month: string; count: number }>;
  maintenances_by_technician: Array<{ tecnico_responsable__username: string; count: number }>;
  equipment_most_maintenances: Array<{ placa: string; tipo: string; maintenance_count: number }>;
  incidents_per_month: Array<{ month: string; count: number }>;
}

interface RecentActivity {
  recent_maintenances: Array<any>;
  recent_incidents: Array<any>;
  equipment_needing_maintenance: Array<any>;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const [statsRes, chartsRes, activityRes] = await Promise.all([
        axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/stats/`, config),
        axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/charts/`, config),
        axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/recent-activity/`, config),
      ]);

      setStats(statsRes.data);
      setChartData(chartsRes.data);
      setRecentActivity(activityRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl font-semibold">Cargando dashboard...</div>
      </div>
    );
  }

  if (!stats || !chartData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl font-semibold text-red-600">Error cargando datos</div>
      </div>
    );
  }

  // Chart configurations
  const equipmentStatusData = {
    labels: ['Operativos', 'En Mantenimiento', 'Dañados'],
    datasets: [{
      data: [
        stats.equipment_status.operational,
        stats.equipment_status.in_maintenance,
        stats.equipment_status.damaged,
      ],
      backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
      borderWidth: 0,
    }],
  };

  const maintenancesPerMonthData = {
    labels: chartData.maintenances_per_month.map(item => item.month),
    datasets: [{
      label: 'Mantenimientos',
      data: chartData.maintenances_per_month.map(item => item.count),
      backgroundColor: '#3b82f6',
      borderColor: '#2563eb',
      borderWidth: 1,
    }],
  };

  const incidentsPerMonthData = {
    labels: chartData.incidents_per_month.map(item => item.month),
    datasets: [{
      label: 'Incidentes',
      data: chartData.incidents_per_month.map(item => item.count),
      backgroundColor: '#ef4444',
      borderColor: '#dc2626',
      borderWidth: 1,
      tension: 0.4,
    }],
  };

  const technicianData = {
    labels: chartData.maintenances_by_technician.slice(0, 5).map(
      item => item.tecnico_responsable__username
    ),
    datasets: [{
      label: 'Mantenimientos Realizados',
      data: chartData.maintenances_by_technician.slice(0, 5).map(item => item.count),
      backgroundColor: '#8b5cf6',
      borderColor: '#7c3aed',
      borderWidth: 1,
    }],
  };

  const maintenanceTypeData = {
    labels: stats.maintenance_by_type.map(item => item.tipo_mantenimiento),
    datasets: [{
      data: stats.maintenance_by_type.map(item => item.count),
      backgroundColor: [
        '#3b82f6',
        '#10b981',
        '#f59e0b',
        '#ef4444',
        '#8b5cf6',
        '#ec4899',
      ],
      borderWidth: 0,
    }],
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Actualizar
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Equipos"
          value={stats.overview.total_equipment}
          color="blue"
          icon="🖥️"
        />
        <StatCard
          title="Total Mantenimientos"
          value={stats.overview.total_maintenances}
          subtitle={`${stats.overview.recent_maintenances} últimos 30 días`}
          color="green"
          icon="🔧"
        />
        <StatCard
          title="Total Incidentes"
          value={stats.overview.total_incidents}
          subtitle={`${stats.overview.recent_incidents} últimos 30 días`}
          color="red"
          icon="⚠️"
        />
        <StatCard
          title="Usuarios Activos"
          value={stats.overview.total_users}
          color="purple"
          icon="👥"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equipment Status */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Estado de Equipos</h2>
          <div className="h-64 flex items-center justify-center">
            <Doughnut data={equipmentStatusData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        {/* Maintenance Types */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Tipos de Mantenimiento</h2>
          <div className="h-64 flex items-center justify-center">
            <Pie data={maintenanceTypeData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        {/* Maintenances per Month */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Mantenimientos por Mes</h2>
          <div className="h-64">
            <Bar data={maintenancesPerMonthData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        {/* Incidents per Month */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Incidentes por Mes</h2>
          <div className="h-64">
            <Line data={incidentsPerMonthData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        {/* Top Technicians */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Top Técnicos</h2>
          <div className="h-64">
            <Bar 
              data={technicianData} 
              options={{ 
                indexAxis: 'y',
                maintainAspectRatio: false 
              }} 
            />
          </div>
        </div>

        {/* Equipment with Most Maintenances */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Equipos con Más Mantenimientos</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {chartData.equipment_most_maintenances.slice(0, 8).map((item, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <div>
                  <span className="font-medium">{item.placa}</span>
                  <span className="text-sm text-gray-500 ml-2">{item.tipo}</span>
                </div>
                <span className="font-semibold text-blue-600">{item.maintenance_count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {recentActivity && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Maintenances */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Mantenimientos Recientes</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {recentActivity.recent_maintenances.map((item, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                  <div className="flex justify-between">
                    <span className="font-medium">{item.equipo__placa}</span>
                    <span className="text-sm text-gray-500">
                      {new Date(item.fecha_mantenimiento).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {item.tipo_mantenimiento} - {item.tecnico_responsable__username}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Incidents */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Incidentes Recientes</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {recentActivity.recent_incidents.map((item, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded border-l-4 border-red-500">
                  <div className="flex justify-between">
                    <span className="font-medium">{item.equipo__placa}</span>
                    <span className="text-sm text-gray-500">
                      {new Date(item.fecha_reporte).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {item.tipo_incidente} - {item.estado}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {item.descripcion?.substring(0, 80)}...
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: number;
  subtitle?: string;
  color: 'blue' | 'green' | 'red' | 'purple';
  icon?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, color, icon }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
  };

  const bgColorClasses = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    red: 'bg-red-50',
    purple: 'bg-purple-50',
  };

  return (
    <div className={`${bgColorClasses[color]} p-6 rounded-lg shadow-md border border-gray-200`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className="text-4xl font-bold mt-2 text-gray-800">{value.toLocaleString()}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`text-4xl opacity-50`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;