"use client";

import { useState } from "react";
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

  if (!token) {
    return <LoginForm onLogin={setToken} onRoleSet={setUserRole} />;
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
                  {userRole === 'admin' ? 'Administrador' : 'Técnico'}
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
