"use client";

import { useState, useEffect } from "react";
import axios from "axios";

interface Report {
  id: number;
  equipment: {
    id: number;
    code: string;
    name: string;
  };
  generated_by: {
    id: number;
    username: string;
  };
  report_data: any;
  pdf_file: string;
  file_url: string;
  created_at: string;
  expires_at: string;
  maintenance?: {
    maintenance_type: string;
    sede?: string;
    dependencia?: string;
    oficina?: string;
  };
}

interface ReportDownloaderProps {
  token: string;
  userRole: 'admin' | 'technician' | null;
}

export default function ReportDownloader({ token, userRole }: ReportDownloaderProps) {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedReport, setSelectedReport] = useState<number | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<string>("");
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedSection, setSelectedSection] = useState<string>("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [equipments, setEquipments] = useState<{id: number, code: string, name: string}[]>([]);
  const [sections, setSections] = useState<string[]>([]);
  const [generatingReport, setGeneratingReport] = useState(false);

  // Restrict access to admin users only
  if (userRole !== 'admin') {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 text-lg font-semibold">Acceso Denegado</div>
        <p className="text-gray-600 mt-2">Solo los administradores pueden acceder a los reportes.</p>
      </div>
    );
  }

  useEffect(() => {
    fetchReports();
    fetchEquipments();
  }, []);

  const fetchEquipments = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/equipments/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEquipments(response.data.map((eq: any) => ({ id: eq.id, code: eq.code, name: eq.name })));
    } catch (err) {
      console.error("Error al cargar equipos:", err);
    }
  };

  const fetchReports = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/reports/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setReports(response.data);

      // Collect unique sections from reports
      const uniqueSections = new Set<string>();
      response.data.forEach((report: Report) => {
        if (report.maintenance?.oficina) uniqueSections.add(report.maintenance.oficina);
        if (report.maintenance?.dependencia) uniqueSections.add(report.maintenance.dependencia);
        if (report.maintenance?.sede) uniqueSections.add(report.maintenance.sede);
      });
      setSections(Array.from(uniqueSections).sort());
    } catch (err) {
      setError("Error al cargar reportes");
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    if (!selectedEquipment || !selectedDate) {
      setError("Selecciona un equipo y una fecha para generar el reporte");
      return;
    }

    setGeneratingReport(true);
    setError("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/reports/generate/",
        {
          equipment_id: parseInt(selectedEquipment),
          date: selectedDate,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Refresh reports list
      await fetchReports();
      setSelectedReport(response.data.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al generar el reporte");
    } finally {
      setGeneratingReport(false);
    }
  };

  const downloadReport = async (reportId: number) => {
    try {
      const report = reports.find(r => r.id === reportId);
      if (!report) return;

      // Open in new tab instead of downloading
      window.open(report.file_url, '_blank');
    } catch (err) {
      setError("Error al abrir el reporte");
    }
  };

  if (loading) {
    return <div className="text-center py-8">Cargando reportes...</div>;
  }

  if (error) {
    return <div className="text-red-600 text-center py-8">{error}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Descargar Reportes</h2>
        <span className="text-sm text-gray-600">{reports.length} reporte(s)</span>
      </div>

      {/* Generar nuevo reporte */}
      <div className="bg-white p-4 rounded-lg shadow-sm border space-y-4">
        <h3 className="text-sm font-medium text-gray-700">Generar Nuevo Reporte</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="equipment-select" className="block text-sm font-medium text-gray-700">
              Equipo
            </label>
            <select
              id="equipment-select"
              value={selectedEquipment}
              onChange={(e) => setSelectedEquipment(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Seleccionar equipo...</option>
              {equipments.map((equipment) => (
                <option key={equipment.id} value={equipment.id.toString()}>
                  {equipment.code} - {equipment.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="date-select" className="block text-sm font-medium text-gray-700">
              Fecha
            </label>
            <input
              type="date"
              id="date-select"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
        <button
          onClick={generateReport}
          disabled={generatingReport || !selectedEquipment || !selectedDate}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          {generatingReport ? "Generando..." : "Generar Reporte"}
        </button>
      </div>

      {/* Filtros y Lista de reportes existentes */}
      {reports.length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow-sm border space-y-4">
          <h3 className="text-sm font-medium text-gray-700">Reportes Existentes</h3>

          {/* Filtros */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label htmlFor="equipment-filter" className="block text-sm font-medium text-gray-700">
                Equipo
              </label>
              <select
                id="equipment-filter"
                value={selectedEquipment}
                onChange={(e) => setSelectedEquipment(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Todos los equipos</option>
                {equipments.map((equipment) => (
                  <option key={equipment.id} value={equipment.id.toString()}>
                    {equipment.code} - {equipment.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="date-filter" className="block text-sm font-medium text-gray-700">
                Fecha
              </label>
              <input
                type="date"
                id="date-filter"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label htmlFor="section-filter" className="block text-sm font-medium text-gray-700">
                Sección
              </label>
              <select
                id="section-filter"
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Todas las secciones</option>
                {sections.map((section) => (
                  <option key={section} value={section}>
                    {section}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700">
                Tipo de Mantenimiento
              </label>
              <select
                id="type-filter"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Todos los tipos</option>
                <option value="computer">Equipos de Cómputo</option>
                <option value="printer_scanner">Impresoras y Escáner</option>
              </select>
            </div>
          </div>

          {/* Lista filtrada de reportes */}
          <div className="space-y-2">
            <select
              value={selectedReport || ""}
              onChange={(e) => setSelectedReport(e.target.value ? parseInt(e.target.value) : null)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Seleccionar reporte...</option>
              {reports
                .filter((report) => {
                  const matchesEquipment = !selectedEquipment || String(report.equipment.id) === selectedEquipment;
                  const matchesDate = !selectedDate || (report.report_data?.start_date && report.report_data.start_date === selectedDate);
                  const matchesSection = !selectedSection || (
                    report.maintenance?.sede === selectedSection ||
                    report.maintenance?.dependencia === selectedSection ||
                    report.maintenance?.oficina === selectedSection
                  );
                  const matchesType = !selectedType || report.maintenance?.maintenance_type === selectedType;
                  return matchesEquipment && matchesDate && matchesSection && matchesType;
                })
                .map((report) => (
                  <option key={report.id} value={report.id}>
                    {report.equipment.code} - {report.equipment.name} ({report.maintenance?.maintenance_type === 'computer' ? 'Cómputo' : 'Impresora/Escáner'}) - {report.maintenance?.oficina || report.maintenance?.dependencia || report.maintenance?.sede || 'Sin sección'} ({report.report_data?.start_date || new Date(report.created_at).toLocaleDateString()})
                  </option>
                ))}
            </select>

            {selectedReport && (
              <button
                onClick={() => downloadReport(selectedReport)}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Descargar Reporte
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
