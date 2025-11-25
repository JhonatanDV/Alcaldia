'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

type TabType = 'system' | 'users' | 'locations' | 'templates';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('system');
  const [loading, setLoading] = useState(false);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>('admin');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [systemSettings, setSystemSettings] = useState({
    site_name: 'Sistema de Gestión de Mantenimiento',
    reports_per_page: 10,
    auto_backup_enabled: false,
    maintenance_reminder_days: 30,
  });
  const [userSettings, setUserSettings] = useState({
    allow_user_registration: false,
    default_role: 'technician',
  });

  // onLogout function for Sidebar logout button
  const onLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;

    if (!token) {
      setIsAuthenticated(false);
      window.location.href = '/';
      return;
    }

    // Verificar que solo admins accedan
    if (role !== 'admin') {
      window.location.href = '/dashboard';
      return;
    }

    setIsAuthenticated(true);
    setUserRole(role);
  }, []);

  const handleSystemSettingChange = (key: string, value: any) => {
    setSystemSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/api/config/settings/`,
        systemSettings,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      alert('Configuración guardada exitosamente');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error al guardar la configuración');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return <div className="p-8">Verificando permisos...</div>;
  }

  return (
    <Layout userRole={userRole} onLogout={onLogout}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Configuración del Sistema
          </h1>

          {/* Tabs */}
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">

                <button
                  onClick={() => setActiveTab('system')}
                  className={`px-6 py-4 text-sm font-medium border-b-2 ${
                    activeTab === 'system'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    strokeWidth={1.5} 
                    stroke="currentColor" 
                    className="w-5 h-5 inline mr-2"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" 
                    />
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" 
                    />
                  </svg>
                  Sistema
                </button>

                <button
                  onClick={() => setActiveTab('users')}
                  className={`px-6 py-4 text-sm font-medium border-b-2 ${
                    activeTab === 'users'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    strokeWidth={1.5} 
                    stroke="currentColor" 
                    className="w-5 h-5 inline mr-2"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" 
                    />
                  </svg>
                  Usuarios
                </button>
              </nav>
            </div>
          </div>

          {/* Content */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            {activeTab === 'system' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Ajustes del sistema</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Nombre del sitio</label>
                    <input
                      value={systemSettings.site_name}
                      onChange={(e) => handleSystemSettingChange('site_name', e.target.value)}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Reportes por página</label>
                    <input
                      type="number"
                      value={systemSettings.reports_per_page}
                      onChange={(e) => handleSystemSettingChange('reports_per_page', Number(e.target.value))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Recordatorio de mantenimiento (días)</label>
                    <input
                      type="number"
                      value={systemSettings.maintenance_reminder_days}
                      onChange={(e) => handleSystemSettingChange('maintenance_reminder_days', Number(e.target.value))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                    />
                  </div>

                  <div className="flex items-center gap-3">
                    <input
                      id="auto_backup"
                      type="checkbox"
                      checked={systemSettings.auto_backup_enabled}
                      onChange={(e) => handleSystemSettingChange('auto_backup_enabled', e.target.checked)}
                    />
                    <label htmlFor="auto_backup" className="text-sm text-gray-700">Habilitar backups automáticos</label>
                  </div>
                </div>

                <div className="mt-6">
                  <button onClick={handleSaveSettings} className="px-4 py-2 bg-blue-600 text-white rounded">Guardar ajustes</button>
                </div>
              </div>
            )}

            {activeTab === 'users' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Configuración de Usuarios</h2>
                <p className="text-sm text-gray-600 mb-4">Ajustes generales relacionados con la creación y el rol por defecto de los usuarios.</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Permitir registro de usuarios</label>
                    <div className="mt-2">
                      <label className="inline-flex items-center">
                        <input
                          type="checkbox"
                          checked={userSettings.allow_user_registration}
                          onChange={(e) => setUserSettings((s) => ({ ...s, allow_user_registration: e.target.checked }))}
                        />
                        <span className="ml-2 text-sm text-gray-700">Activar</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Rol por defecto</label>
                    <select
                      value={userSettings.default_role}
                      onChange={(e) => setUserSettings((s) => ({ ...s, default_role: e.target.value }))}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                    >
                      <option value="technician">Técnico</option>
                      <option value="user">Usuario</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                </div>

                <div className="mt-6">
                  <button
                    onClick={async () => {
                      setLoading(true);
                      try {
                        const token = localStorage.getItem('access_token');
                        await axios.post(`${API_URL}/api/config/settings/`, { user_settings: userSettings }, { headers: { Authorization: `Bearer ${token}` } });
                        alert('Ajustes de usuario guardados');
                      } catch (err) {
                        console.error(err);
                        alert('Error al guardar ajustes de usuario');
                      } finally {
                        setLoading(false);
                      }
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded"
                  >
                    Guardar ajustes de usuario
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
