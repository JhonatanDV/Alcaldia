"use client";

import { useState, useEffect } from "react";
import EquipmentList from "@/components/EquipmentList";
import MaintenanceForm from "@/components/MaintenanceForm";
import PhotoGallery from "@/components/PhotoGallery";
import ReportDownloader from "@/components/ReportDownloader";
import LoginForm from "@/components/LoginForm";

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'equipment' | 'gallery' | 'reports'>('equipment');
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [selectedDependencia, setSelectedDependencia] = useState<string>("");
  const [selectedSede, setSelectedSede] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [selectedType, setSelectedType] = useState<string>("");

  useEffect(() => {
    // Check if user is already logged in
    const storedToken = localStorage.getItem('access_token');
    const storedRole = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
    
    if (storedToken) {
      // Redirect to dashboard if already authenticated
      window.location.href = '/dashboard';
    }
  }, []);

  if (!token) {
    return <LoginForm onLogin={(newToken) => {
      setToken(newToken);
      localStorage.setItem('access_token', newToken);
    }} onRoleSet={(role) => {
      setUserRole(role);
      localStorage.setItem('user_role', role || '');
    }} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
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
            <button
              onClick={() => {
                setToken(null);
                setUserRole(null);
              }}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Filters */}
        {activeTab === 'equipment' && (
          <div className="mb-8 bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Filtros de Búsqueda</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label htmlFor="search" className="block text-sm font-medium text-gray-700">
                  Búsqueda General
                </label>
                <input
                  type="text"
                  id="search"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Buscar por nombre, serial, marca..."
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                />
              </div>
              <div>
                <label htmlFor="dateFrom" className="block text-sm font-medium text-gray-700">
                  Fecha Desde
                </label>
                <input
                  type="date"
                  id="dateFrom"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                />
              </div>
              <div>
                <label htmlFor="dateTo" className="block text-sm font-medium text-gray-700">
                  Fecha Hasta
                </label>
                <input
                  type="date"
                  id="dateTo"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                />
              </div>
              <div>
                <label htmlFor="dependencia" className="block text-sm font-medium text-gray-700">
                  Dependencia
                </label>
                <input
                  type="text"
                  id="dependencia"
                  value={selectedDependencia}
                  onChange={(e) => setSelectedDependencia(e.target.value)}
                  placeholder="Filtrar por dependencia"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                />
              </div>
              <div>
                <label htmlFor="sede" className="block text-sm font-medium text-gray-700">
                  Sede
                </label>
                <input
                  type="text"
                  id="sede"
                  value={selectedSede}
                  onChange={(e) => setSelectedSede(e.target.value)}
                  placeholder="Filtrar por sede"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
                />
              </div>
              <div>
                <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                  Estado
                </label>
                <select
                  id="status"
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
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
                <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                  Tipo de Mantenimiento
                </label>
                <select
                  id="type"
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
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
                  onClick={() => {
                    setSearchQuery("");
                    setDateFrom("");
                    setDateTo("");
                    setSelectedDependencia("");
                    setSelectedSede("");
                    setSelectedStatus("");
                    setSelectedType("");
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Limpiar Filtros
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tabs and Actions */}
        <div className="mb-8 flex justify-between items-center">
          <nav className="flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('equipment')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'equipment'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Equipos y Mantenimientos
            </button>
            <button
              onClick={() => setActiveTab('gallery')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'gallery'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Galería de Fotos
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'reports'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Descargar Reportes
            </button>
          </nav>

          <div className="flex gap-2">
            <a
              href="/maintenance/new"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
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
            {userRole === 'admin' && (
              <>
                <a
                  href="/dashboard"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Dashboard
                </a>
                <a
                  href="/admin/users"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                >
                  Usuarios
                </a>
              </>
            )}
          </div>
        </div>

        {activeTab === 'equipment' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <EquipmentList
                token={token}
                onSelectEquipment={setSelectedEquipment}
                selectedEquipment={selectedEquipment}
                userRole={userRole}
                searchFilters={{
                  search: searchQuery,
                  scheduled_date_from: dateFrom,
                  scheduled_date_to: dateTo,
                  equipment_dependencia: selectedDependencia,
                  sede: selectedSede,
                  status: selectedStatus,
                  maintenance_type: selectedType,
                }}
              />
            </div>
            <div>
              {selectedEquipment && (
                <MaintenanceForm
                  token={token}
                  equipmentId={selectedEquipment}
                  onMaintenanceCreated={() => {
                    // Ya no recarga la página completa, se maneja con eventos
                  }}
                />
              )}
            </div>
          </div>
        )}

        {activeTab === 'gallery' && (
          <PhotoGallery token={token} userRole={userRole} />
        )}

        {activeTab === 'reports' && (
          <ReportDownloader token={token} userRole={userRole} />
        )}
      </main>
    </div>
  );
}
