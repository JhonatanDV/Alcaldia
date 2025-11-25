'use client';

import React from 'react';
import type { Dispatch, SetStateAction } from 'react';

interface Maintenance {
  id: number;
  equipment?: { id: number; code?: string; name?: string } | null;
  description?: string | null;
  date?: string | null;
  placa?: string | null;
  equipo_placa?: string | null;
  scheduled_date?: string | null;
  completion_date?: string | null;
  created_at?: string | null;
  sede?: string | null;
  dependencia?: string | null;
  sede_rel?: any;
  dependencia_rel?: any;
  [key: string]: any;
}

interface Props {
  maintenances: Maintenance[];
  page: number;
  totalPages: number;
  pageSize: number;
  setPage: (p: number) => void;
  setPageSize: (s: number) => void;
}

export default function MaintenanceTable({ maintenances, page, totalPages, pageSize, setPage, setPageSize }: Props) {

  const goToPage = (p: number) => {
    if (p < 1) return;
    if (p > totalPages) return;
    setPage(p);
    try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch(_) {}
  };

  const formatMaintenanceDate = (m: Maintenance) => {
    const dateOnly = m.scheduled_date || m.completion_date || m.created_at;
    if (!dateOnly) return '-';
    const time = m.hora_inicio || m.hora_final || null;
    try {
      if (time) {
        const combined = `${dateOnly}T${time}`;
        const d = new Date(combined);
        if (!isNaN(d.getTime())) return d.toLocaleString();
      }
      const d2 = new Date(dateOnly + 'T00:00:00');
      if (!isNaN(d2.getTime())) return d2.toLocaleDateString();
    } catch (e) {}
    return '-';
  };

  const renderPages = () => {
    const visible = 5;
    const start = Math.max(1, Math.min(page - Math.floor(visible / 2), Math.max(1, totalPages - visible + 1)));
    const pages: number[] = [];
    for (let i = 0; i < Math.min(visible, totalPages); i++) pages.push(start + i);
    return pages.map((p) => (
      <button
        key={p}
        onClick={() => goToPage(p)}
        className={`px-2 py-1 rounded ${p === page ? 'bg-indigo-600 text-white' : 'bg-white border text-gray-700'}`}
      >{p}</button>
    ));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4 sm:p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Listado</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">ID</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Equipo</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Sede</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Dependencia</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Descripción</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {maintenances.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-sm text-gray-500">No hay mantenimientos registrados</td>
              </tr>
            )}
            {maintenances.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{m.id}</td>
                <td className="px-4 py-3 text-sm text-gray-900">{m.equipo_placa ?? m.placa ?? (m.equipment?.code ?? m.equipment?.name) ?? 'Sin equipo'}</td>
                <td className="px-4 py-3 text-sm text-gray-900">{(m as any).sede_nombre || m.sede || (m.sede_rel && (m.sede_rel.nombre || m.sede_rel.name)) || m.sede_rel || '-'}</td>
                <td className="px-4 py-3 text-sm text-gray-900">{(m as any).dependencia_nombre || m.dependencia || (m.dependencia_rel && (m.dependencia_rel.nombre || m.dependencia_rel.name)) || m.dependencia_rel || '-'}</td>
                <td className="px-4 py-3 text-sm text-gray-900 truncate">{m.description ?? '-'}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{formatMaintenanceDate(m)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-2 mt-4">
        <button
          onClick={() => goToPage(page - 1)}
          disabled={page <= 1}
          className={`px-3 py-1.5 rounded-md text-sm ${page <= 1 ? 'bg-gray-200 text-gray-500' : 'bg-white border'}`}
        >Anterior</button>

        <div className="hidden sm:flex items-center gap-1">
          {renderPages()}
        </div>

        <button
          onClick={() => goToPage(page + 1)}
          disabled={page >= totalPages}
          className={`px-3 py-1.5 rounded-md text-sm ${page >= totalPages ? 'bg-gray-200 text-gray-500' : 'bg-white border'}`}
        >Siguiente</button>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-sm text-gray-600">Página {page} de {totalPages}</span>
          <select
            aria-label="Tamaño de página"
            value={pageSize}
            onChange={(e) => setPageSize(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>
    </div>
  );
}
