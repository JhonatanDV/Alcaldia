'use client';

import { useState } from 'react';
import { reportService } from '@/lib/reportService';

export function MaintenanceReportButton({ maintenanceId, templateId: templateIdProp } : { maintenanceId: number, templateId?: string | number }) {
  const [loading, setLoading] = useState(false);
  const templateId = templateIdProp;

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const blob = await reportService.generateReport(maintenanceId, 'excel', templateId || undefined);
      const filename = `mantenimiento_${maintenanceId}.xlsx`;
      reportService.downloadFile(blob, filename);
    } catch (error: any) {
      alert(error?.message || 'Error generando reporte');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleGenerate}
      disabled={loading}
      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
    >
      {loading ? 'Generando...' : '📊 Generar Excel'}
    </button>
  );
}
