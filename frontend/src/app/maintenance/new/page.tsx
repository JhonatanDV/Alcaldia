'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Equipment {
  id: number;
  placa: string;
  tipo: string;
  sede: string;
  dependencia: string;
  oficina: string;
}

export default function NewMaintenancePage() {
  const [equipments, setEquipments] = useState<Equipment[]>([]);
  const [selectedEquipment, setSelectedEquipment] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEquipments = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          setError('No está autenticado. Por favor, inicie sesión.');
          setLoading(false);
          return;
        }

        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get(`${API_URL}/api/equipments/`, { headers });
        setEquipments(response.data);
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Nuevo Mantenimiento</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Seleccionar Equipo</h2>
          <select
            value={selectedEquipment || ''}
            onChange={(e) => setSelectedEquipment(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Seleccione un equipo...</option>
            {equipments.map((equipment) => (
              <option key={equipment.id} value={equipment.id}>
                {equipment.placa} - {equipment.tipo} ({equipment.dependencia}, {equipment.sede})
              </option>
            ))}
          </select>
        </div>

        {selectedEquipment && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Información del Equipo</h2>
            <div className="space-y-4">
              {equipments
                .filter((eq) => eq.id === selectedEquipment)
                .map((equipment) => (
                  <div key={equipment.id} className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Placa</p>
                      <p className="text-lg text-gray-900">{equipment.placa}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Tipo</p>
                      <p className="text-lg text-gray-900">{equipment.tipo}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Sede</p>
                      <p className="text-lg text-gray-900">{equipment.sede}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Dependencia</p>
                      <p className="text-lg text-gray-900">{equipment.dependencia}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Oficina</p>
                      <p className="text-lg text-gray-900">{equipment.oficina}</p>
                    </div>
                  </div>
                ))}
            </div>

            <div className="mt-8">
              <p className="text-gray-600 text-center">
                El formulario de mantenimiento completo se mostrará aquí.
              </p>
              <p className="text-gray-500 text-sm text-center mt-2">
                Nota: Reutiliza el componente MaintenanceForm existente para implementar el formulario completo.
              </p>
            </div>
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
