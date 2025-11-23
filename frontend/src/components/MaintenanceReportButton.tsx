'use client';

import { useState } from 'react';
import { reportService } from '@/lib/reportService';

export function MaintenanceReportButton({ maintenanceId }: { maintenanceId: number }) {
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (format: 'pdf' | 'excel' | 'image') => {
    try {
      setLoading(true);
      const blob = await reportService.generateReport(maintenanceId, format);
      const ext = format === 'excel' ? 'xlsx' : format === 'image' ? 'png' : 'pdf';
      const filename = `mantenimiento_${maintenanceId}.${ext}`;
      reportService.downloadFile(blob, filename);
    } catch (error: any) {
      alert(error?.message || 'Error generando reporte');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => handleGenerate('pdf')}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        📄 PDF
      </button>
      <button
        onClick={() => handleGenerate('excel')}
        disabled={loading}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
      >
        📊 Excel
      </button>
      <button
        onClick={() => handleGenerate('image')}
        disabled={loading}
        className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
      >
        🖼️ Imagen
      </button>
    </div>
  );
}
