'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { MaintenanceReportButton } from '@/components/MaintenanceReportButton';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface Template {
  id: number;
  name: string;
  type: string;
}

interface Maintenance {
  id: number;
  maintenance_type: string;
  equipment: {
    id: number;
    code: string;
    equipment_type: string;
  };
  maintenance_date: string;
  sede_name?: string;
  dependencia_name?: string;
}

export default function CreateReportPage() {
  const router = useRouter();
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [maintenances, setMaintenances] = useState<Maintenance[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedMaintenance, setSelectedMaintenance] = useState('');
  const [reportTitle, setReportTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const role = typeof window !== 'undefined' ? (localStorage.getItem('user_role') as 'admin' | 'technician' | null) : null;
    setUserRole(role);
    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    router.push('/');
  };

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/');
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };

      // Fetch templates via axios (uses auth interceptor)
      try {
        const templatesRes = await axios.get(`${API_URL}/api/templates/`, { headers });
        setTemplates(templatesRes.data || []);
      } catch (e) {
        console.error('Error fetching templates', e);
      }

      // Fetch maintenances (use direct maintenances endpoint to include all items)
      try {
        const maintRes = await axios.get(`${API_URL}/api/maintenances/?page_size=1000`, { headers });
        const maintData = maintRes.data || [];
        const items = maintData.results || maintData;
        const normalized = items.map((m: any) => ({
          id: m.id,
          maintenance_type: m.maintenance_type || m.type || '',
          equipment: m.equipment || (m.equipment_info ? { id: m.equipment_info.id, code: m.equipment_info.code } : null),
          maintenance_date: m.scheduled_date || m.maintenance_date || m.created_at,
          sede_name: m.sede || (m.sede_rel && (m.sede_rel.nombre || m.sede_rel.name)) || null,
          dependencia_name: m.dependencia || (m.dependencia_rel && (m.dependencia_rel.nombre || m.dependencia_rel.name)) || null,
        }));
        setMaintenances(normalized);
      } catch (e) {
        console.error('Error fetching maintenances', e);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Error al cargar los datos');
    }
  };

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/');
        return;
      }

      if (!selectedTemplate) {
        setError('Por favor selecciona una plantilla');
        setLoading(false);
        return;
      }

      const payload: any = {
        title: reportTitle || 'Reporte de Mantenimiento',
      };

      if (selectedMaintenance) {
        payload.maintenance_id = parseInt(selectedMaintenance);
      }

      const headersPost = { Authorization: `Bearer ${token}` };
      try {
        const resp = await axios.post(
          `${API_URL}/api/templates/${selectedTemplate}/generate/`,
          payload,
          { headers: headersPost, responseType: 'blob' }
        );
        const blob = resp.data as Blob;
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (e: any) {
        const errMsg = e?.response?.data?.error || e.message || 'Error al generar el reporte';
        throw new Error(errMsg);
      }

      setSuccess('Reporte generado exitosamente');
      setReportTitle('');
      setSelectedMaintenance('');
    } catch (err: any) {
      console.error('Error generating report:', err);
      setError(err.message || 'Error al generar el reporte');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 lg:p-8">
            <div className="mb-6">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Generar Reporte</h1>
              <p className="mt-2 text-sm text-gray-600">
                Crea un nuevo reporte de mantenimiento usando las plantillas disponibles
              </p>
            </div>

            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                {success}
              </div>
            )}

            <form onSubmit={handleGenerateReport} className="space-y-6">
              <div>
                <label htmlFor="reportTitle" className="block text-sm font-medium text-gray-700 mb-2">
                  Título del Reporte
                </label>
                <input
                  type="text"
                  id="reportTitle"
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black"
                  placeholder="Ej: Reporte Mensual de Mantenimiento"
                />
              </div>

              <div>
                <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-2">
                  Plantilla <span className="text-red-500">*</span>
                </label>
                <select
                  id="template"
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black bg-white"
                  required
                >
                  <option value="">Selecciona una plantilla</option>
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name} ({template.type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="maintenance" className="block text-sm font-medium text-gray-700 mb-2">
                  Mantenimiento (Opcional)
                </label>
                <select
                  id="maintenance"
                  value={selectedMaintenance}
                  onChange={(e) => setSelectedMaintenance(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-black bg-white"
                >
                  <option value="">Selecciona un mantenimiento</option>
                  {maintenances.map((maintenance) => (
                    <option key={maintenance.id} value={maintenance.id}>
                      {maintenance.equipment?.code || `Equipo ${maintenance.id}`} - {maintenance.maintenance_type} ({new Date(maintenance.maintenance_date).toLocaleDateString()})
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Si seleccionas un mantenimiento, el reporte se generará con sus datos
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading || !selectedTemplate}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {loading ? 'Generando...' : 'Generar Reporte'}
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/reports/list')}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 font-medium"
                >
                  Ver Reportes Generados
                </button>
              </div>

              {/* Quick export button that uses the existing dropdowns */}
              {selectedTemplate && selectedMaintenance && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Exportar:</h4>
                  <MaintenanceReportButton
                    maintenanceId={Number(selectedMaintenance)}
                    templateId={selectedTemplate}
                  />
                </div>
              )}
            </form>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Notas:</h3>
              <ul className="text-xs text-gray-600 space-y-1 list-disc list-inside">
                <li>Asegúrate de tener plantillas configuradas antes de generar reportes</li>
                <li>Puedes generar reportes con o sin datos de mantenimiento específico</li>
                <li>El reporte se descargará automáticamente una vez generado</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
