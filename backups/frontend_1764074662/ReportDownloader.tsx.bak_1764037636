"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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
  const [selectedReports, setSelectedReports] = useState<number[]>([]);
  const [packageLoading, setPackageLoading] = useState(false);

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

  useEffect(() => {
    fetchReports();
    fetchEquipments();
  }, []);

  // Restrict access to admin users only (render a message but keep hooks order stable)
  if (userRole !== 'admin') {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 text-lg font-semibold">Acceso Denegado</div>
        <p className="text-gray-600 mt-2">Solo los administradores pueden acceder a los reportes.</p>
      </div>
    );
  }

  const generateReport = async (maintenanceId?: number) => {
    setGeneratingReport(true);
    setError("");
    if (!maintenanceId) {
      setError('No se especificó un mantenimiento válido para generar el reporte');
      setGeneratingReport(false);
      return null;
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/reports/generate/",
        {
          maintenance_id: maintenanceId,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Refresh reports list
      await fetchReports();
      setSelectedReport(response.data.id);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al generar el reporte");
      throw err;
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

  const toggleSelectReport = (reportId: number) => {
    setSelectedReports((prev) =>
      prev.includes(reportId)
        ? prev.filter((id) => id !== reportId)
        : [...prev, reportId]
    );
  };

  const selectAllReports = () => {
    const filteredReports = reports.filter((report) => {
      const equipmentIdStr = report.equipment && report.equipment.id ? String(report.equipment.id) : '';
      const matchesEquipment = !selectedEquipment || equipmentIdStr === selectedEquipment;
      const matchesDate = !selectedDate || (report.report_data?.start_date && report.report_data.start_date === selectedDate);
      const matchesSection = !selectedSection || (
        report.maintenance?.sede === selectedSection ||
        report.maintenance?.dependencia === selectedSection ||
        report.maintenance?.oficina === selectedSection
      );
      const matchesType = !selectedType || report.maintenance?.maintenance_type === selectedType;
      return matchesEquipment && matchesDate && matchesSection && matchesType;
    });
    setSelectedReports(filteredReports.map((r) => r.id));
  };

  const clearSelection = () => {
    setSelectedReports([]);
  };

  const downloadPackage = async () => {
    if (selectedReports.length === 0) {
      setError("Selecciona al menos un reporte para empaquetar");
      return;
    }

    setPackageLoading(true);
    setError("");

    try {
      const response = await axios.post(
        `${API_URL}/api/reports/package/`,
        {
          report_ids: selectedReports,
          filename: `reportes_${new Date().toISOString().split('T')[0]}.zip`,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `reportes_${new Date().toISOString().split('T')[0]}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      clearSelection();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al empaquetar reportes");
    } finally {
      setPackageLoading(false);
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

          {/* Lista filtrada de reportes con checkboxes */}
          <div className="space-y-2">
            {/* Botones de selección */}
            <div className="flex justify-between items-center mb-2">
              <div className="flex gap-2">
                <button
                  onClick={selectAllReports}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                >
                  Seleccionar Todos
                </button>
                <button
                  onClick={clearSelection}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                >
                  Limpiar Selección
                </button>
              </div>
              <span className="text-sm text-gray-600">
                {selectedReports.length} seleccionado(s)
              </span>
            </div>

            {/* Lista de reportes con checkboxes */}
            <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-md p-2 space-y-1">
              {reports
                .filter((report) => {
                  const equipmentIdStr = report.equipment && report.equipment.id ? String(report.equipment.id) : '';
                  const matchesEquipment = !selectedEquipment || equipmentIdStr === selectedEquipment;
                  const matchesDate = !selectedDate || (report.report_data?.start_date && report.report_data.start_date === selectedDate);
                  const matchesSection = !selectedSection || (
                    report.maintenance?.sede === selectedSection ||
                    report.maintenance?.dependencia === selectedSection ||
                    report.maintenance?.oficina === selectedSection
                  );
                  const matchesType = !selectedType || report.maintenance?.maintenance_type === selectedType;
                  return matchesEquipment && matchesDate && matchesSection && matchesType;
                })
                .map((report) => {
                  const equipmentCode = report.equipment?.code ?? (report.report_data?.equipment_code ?? 'Sin equipo');
                  const equipmentName = report.equipment?.name ?? (report.report_data?.equipment_name ?? 'Sin nombre');
                  const maintenanceTypeLabel = report.maintenance?.maintenance_type === 'computer' ? 'Cómputo' : 'Impresora/Escáner';
                  const sectionLabel = report.maintenance?.oficina || report.maintenance?.dependencia || report.maintenance?.sede || 'Sin sección';
                  const dateLabel = report.report_data?.start_date || (report.created_at ? new Date(report.created_at).toLocaleDateString() : 'Sin fecha');

                  return (
                    <label
                      key={report.id}
                      className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedReports.includes(report.id)}
                        onChange={() => toggleSelectReport(report.id)}
                        className="mr-3 h-4 w-4"
                      />
                      <span className="text-sm">
                        {equipmentCode} - {equipmentName} ({maintenanceTypeLabel}) - {sectionLabel} ({dateLabel})
                      </span>
                    </label>
                  );
                })}
            </div>

            {/* Botones de acción */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-4">
              <button
                onClick={() => selectedReport && downloadReport(selectedReport)}
                disabled={!selectedReport}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                Ver Reporte Individual
              </button>
              <button
                onClick={downloadPackage}
                disabled={packageLoading || selectedReports.length === 0}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
              >
                {packageLoading ? "Empaquetando..." : `Descargar ZIP (${selectedReports.length})`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
