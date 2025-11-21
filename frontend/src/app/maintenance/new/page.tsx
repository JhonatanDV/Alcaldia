'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import MaintenanceForm from '@/components/MaintenanceForm';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Equipment {
  id: number;
  code: string;
  name: string;
  location: string;
}

export default function NewMaintenancePage() {
  const [equipments, setEquipments] = useState<Equipment[]>([]);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);
  const [token, setToken] = useState<string>('');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    window.location.href = '/';
  };

  const handleMaintenanceCreated = () => {
    // Reset selected equipment and show success
    setSelectedEquipment(null);
    alert('Mantenimiento creado exitosamente');
    window.location.href = '/dashboard';
  };

  useEffect(() => {
    const fetchEquipments = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');
        const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
        
        if (!accessToken) {
          window.location.href = '/';
          return;
        }

        setToken(accessToken);
        setUserRole(role);

        const headers = { Authorization: `Bearer ${accessToken}` };
        
        // Fetch all equipments handling pagination
        let allEquipments: Equipment[] = [];
        let nextUrl: string | null = `${API_URL}/api/equipments/?page_size=1000`;
        
        while (nextUrl) {
          const response: any = await axios.get(nextUrl, { headers });
          
          // Check if response is paginated or direct array
          if (response.data.results) {
            allEquipments = [...allEquipments, ...response.data.results];
            nextUrl = response.data.next;
          } else if (Array.isArray(response.data)) {
            allEquipments = response.data;
            nextUrl = null;
          } else {
            throw new Error('Formato de respuesta inesperado');
          }
        }
        
        setEquipments(allEquipments);
        setLoading(false);
      } catch (err: any) {
        console.error('Error fetching equipments:', err);
        setError(err.response?.data?.detail || 'Error al cargar equipos');
        setLoading(false);
      }
    };

    fetchEquipments();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Nuevo Mantenimiento</h1>
          <p className="text-gray-600">Cargando equipos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Nuevo Mantenimiento</h1>
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
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
                  {userRole === 'admin' ? 'Admin' : 'Técnico'}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/dashboard"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Dashboard
              </a>
              {userRole === 'admin' && (
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
              )}
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

      <div className="max-w-3xl mx-auto p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Nuevo Mantenimiento</h2>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">Seleccionar Equipo</h3>
          <select
            value={selectedEquipment?.id || ''}
            onChange={(e) => {
              const equipmentId = e.target.value ? parseInt(e.target.value) : null;
              const equipment = equipmentId 
                ? equipments.find(eq => eq.id === equipmentId) || null
                : null;
              setSelectedEquipment(equipment);
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
          >
            <option value="">Seleccione un equipo...</option>
            {equipments.map((equipment) => (
              <option key={equipment.id} value={equipment.id}>
                {equipment.code} - {equipment.name} ({equipment.location || 'Sin ubicación'})
              </option>
            ))}
          </select>
        </div>

        {selectedEquipment && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Información del Equipo Seleccionado</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-500">Código/Placa</p>
                <p className="text-lg text-gray-900">{selectedEquipment.code}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Nombre/Tipo</p>
                <p className="text-lg text-gray-900">{selectedEquipment.name}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Ubicación</p>
                <p className="text-lg text-gray-900">{selectedEquipment.location || 'No especificada'}</p>
              </div>
            </div>

            <MaintenanceForm 
              token={token}
              equipmentId={selectedEquipment.id}
              equipmentCode={selectedEquipment.code}
              equipmentName={selectedEquipment.name}
              equipmentLocation={selectedEquipment.location}
              onMaintenanceCreated={handleMaintenanceCreated}
            />
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Esta ventana está diseñada para abrirse de forma independiente.
          </p>
        </div>
      </div>
    </div>
  );
}
