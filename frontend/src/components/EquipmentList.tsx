"use client";

import { useState, useEffect } from "react";
import axios from "axios";

interface Equipment {
  id: number;
  code: string;
  name: string;
  location: string;
  maintenances: Maintenance[];
}

interface Maintenance {
  id: number;
  description: string;
  maintenance_date: string;
  performed_by: string;
  photos: Photo[];
  signature?: Signature;
  is_incident: boolean;
}

interface Photo {
  id: number;
  image: string;
  uploaded_at: string;
}

interface Signature {
  id: number;
  signature: string;
  uploaded_at: string;
}

interface EquipmentListProps {
  token: string;
  onSelectEquipment: (id: number) => void;
  selectedEquipment: number | null;
  userRole: 'admin' | 'technician' | null;
}

export default function EquipmentList({
  token,
  onSelectEquipment,
  selectedEquipment,
  userRole,
}: EquipmentListProps) {
  const [equipments, setEquipments] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    code: "",
    name: "",
    location: "",
  });
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState("");

  useEffect(() => {
    fetchEquipments();

    // Escuchar el evento de mantenimiento creado para refrescar la lista
    const handleMaintenanceCreated = () => {
      fetchEquipments();
    };

    window.addEventListener('maintenanceCreated', handleMaintenanceCreated);

    return () => {
      window.removeEventListener('maintenanceCreated', handleMaintenanceCreated);
    };
  }, [token]);

  const fetchEquipments = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/equipments/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEquipments(response.data);
    } catch (err) {
      setError("Error al cargar equipos");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEquipment = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError("");

    try {
      await axios.post(
        "http://127.0.0.1:8000/api/equipments/",
        createFormData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setShowCreateModal(false);
      setCreateFormData({ code: "", name: "", location: "" });
      fetchEquipments(); // Refresh the list
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || "Error al crear equipo");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCreateFormData((prev) => ({ ...prev, [name]: value }));
  };

  if (loading) {
    return <div className="text-center py-8">Cargando equipos...</div>;
  }

  if (error) {
    return <div className="text-red-600 text-center py-8">{error}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Equipos</h2>
        {userRole === 'admin' && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Crear Equipo
          </button>
        )}
      </div>
      <div className="space-y-2">
        {equipments.map((equipment) => (
          <div
            key={equipment.id}
            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedEquipment === equipment.id
                ? "border-indigo-500 bg-indigo-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
            onClick={() => onSelectEquipment(equipment.id)}
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-gray-900">
                  {equipment.code} - {equipment.name}
                </h3>
                <p className="text-sm text-gray-600">{equipment.location}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {equipment.maintenances.length} mantenimiento(s)
                </p>
              </div>
              <div className="text-right">
                <div className="flex flex-col items-end space-y-1">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Activo
                  </span>
                  {userRole === 'admin' && equipment.maintenances.some(m => m.is_incident) && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Incidencia
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Equipment Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Crear Nuevo Equipo</h3>
              <form onSubmit={handleCreateEquipment} className="space-y-4">
                <div>
                  <label htmlFor="code" className="block text-sm font-medium text-gray-700">
                    Código
                  </label>
                  <input
                    type="text"
                    id="code"
                    name="code"
                    required
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                    value={createFormData.code}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Nombre
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                    value={createFormData.name}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                    Ubicación
                  </label>
                  <input
                    type="text"
                    id="location"
                    name="location"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                    value={createFormData.location}
                    onChange={handleInputChange}
                  />
                </div>
                {createError && <div className="text-red-600 text-sm">{createError}</div>}
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={createLoading}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                  >
                    {createLoading ? "Creando..." : "Crear"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
