'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import MaintenanceForm from '@/components/MaintenanceForm';
import Layout from '../../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

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
    localStorage.removeItem('username');
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
      <Layout userRole={userRole} onLogout={handleLogout}>
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Nuevo Mantenimiento</h1>
          <p className="text-gray-600">Cargando equipos...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout userRole={userRole} onLogout={handleLogout}>
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h1 className="text-3xl font-bold text-gray-900">Nuevo Mantenimiento</h1>
          </div>
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <>
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Nuevo Mantenimiento
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Registra un nuevo mantenimiento para un equipo
          </p>
        </div>

        {/* Quick actions removed — use Sidebar for navigation */}
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-4 sm:mb-6 lg:mb-8">Nuevo Mantenimiento</h2>

        <div className="bg-white rounded-lg shadow-sm border p-4 sm:p-6 mb-4 sm:mb-6">
          <h3 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Seleccionar Equipo</h3>
          <select
            value={selectedEquipment?.id || ''}
            onChange={(e) => {
              const equipmentId = e.target.value ? parseInt(e.target.value) : null;
              const equipment = equipmentId 
                ? equipments.find(eq => eq.id === equipmentId) || null
                : null;
              setSelectedEquipment(equipment);
            }}
            className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black"
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
          <div className="bg-white rounded-lg shadow-sm border p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Información del Equipo Seleccionado</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6 p-3 sm:p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-500">Código/Placa</p>
                <p className="text-sm sm:text-base lg:text-lg text-gray-900 truncate">{selectedEquipment.code}</p>
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-500">Nombre/Tipo</p>
                <p className="text-sm sm:text-base lg:text-lg text-gray-900 truncate">{selectedEquipment.name}</p>
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-500">Ubicación</p>
                <p className="text-sm sm:text-base lg:text-lg text-gray-900 truncate">{selectedEquipment.location || 'No especificada'}</p>
              </div>
            </div>

            <MaintenanceForm 
              token={token}
              equipmentId={selectedEquipment.id}
              equipmentCode={selectedEquipment.code}
              equipmentName={selectedEquipment.name}
              equipmentLocation={selectedEquipment.location}
              equipmentDetails={selectedEquipment}
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
    </Layout>
    </>
  );
}
