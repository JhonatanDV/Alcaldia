'use client';

import { useState } from 'react';
import { TemplateService } from '@/lib/templateService';
import dynamic from 'next/dynamic';

const TemplateDesigner = dynamic(() => import('./TemplateDesigner'), { ssr: false });

export default function TemplateEditor() {
  const [templateType, setTemplateType] = useState('report');
  const [jsonData, setJsonData] = useState('');
  const [sampleMaintenanceId, setSampleMaintenanceId] = useState('');
  const [loadingSample, setLoadingSample] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [fieldsSchema, setFieldsSchema] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingTemplateId, setEditingTemplateId] = useState<number | null>(null);

  const service = new TemplateService();

  const handleGeneratePDF = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = jsonData ? JSON.parse(jsonData) : {};
      const blob = await service.generatePDF(templateType, data);
      service.downloadFile(blob, `${templateType}_${Date.now()}.pdf`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error generando PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateExcel = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = jsonData ? JSON.parse(jsonData) : {};
      const blob = await service.generateExcel(templateType, data);
      service.downloadFile(blob, `${templateType}_${Date.now()}.xlsx`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error generando Excel');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadTemplate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const fd = new FormData();
      if (!templateName) throw new Error('El nombre de plantilla es requerido');
      fd.append('name', templateName);
      fd.append('type', templateType === 'report' ? 'pdf' : templateType === 'invoice' ? 'excel' : 'pdf');
      if (file) fd.append('template_file', file);
      if (fieldsSchema) fd.append('fields_schema', fieldsSchema);

      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/templates/upload/`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: fd,
      });

      if (!res.ok) {
        // Construir mensaje de error útil incluso si la respuesta no es JSON
        let errMsg = `${res.status} ${res.statusText}`;
        try {
          const contentType = res.headers.get('content-type') || '';
          if (contentType.includes('application/json')) {
            const errBody = await res.json();
            errMsg = errBody?.error || errBody?.detail || JSON.stringify(errBody) || errMsg;
          } else {
            const text = await res.text().catch(() => null);
            if (text) errMsg = text.length < 800 ? text : errMsg;
          }
        } catch (e) {
          // ignore parse errors
        }
        if (res.status === 404) {
          errMsg += ' — Endpoint no encontrado. Verifica `NEXT_PUBLIC_API_URL` y que el backend esté corriendo en la URL esperada.';
        }
        throw new Error(errMsg || 'Error subiendo plantilla');
      }

      const data = await res.json().catch(() => null);
      setSuccess('Plantilla creada: ' + data.name);
      // abrir diseñador para posicionar campos en PDF inmediatamente
      if (data.id) setEditingTemplateId(data.id);
      setTemplateName('');
      setFile(null);
      setFieldsSchema('');
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error subiendo plantilla');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Editor de Plantillas (básico)</h1>

      <div className="bg-white shadow rounded p-6 template-editor-form">
        <label className="block text-sm font-medium mb-2 text-gray-700">Nombre de la plantilla <span className="text-red-600">*</span></label>
        <input
          type="text"
          value={templateName}
          onChange={(e) => setTemplateName(e.target.value)}
          className="w-full px-3 py-2 border rounded-md mb-3 text-black placeholder-black/60"
          placeholder="Nombre de la plantilla"
        />

        <label className="block text-sm font-medium mb-2 text-gray-700">Archivo de plantilla (imagen / pdf / xlsx)</label>
        <input
          type="file"
          accept=".png,.jpg,.jpeg,.pdf,.xlsx"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-3 text-black"
        />

        <label className="block text-sm font-medium mb-2 text-gray-700">Fields schema (JSON opcional)</label>
        <textarea
          value={fieldsSchema}
          onChange={(e) => setFieldsSchema(e.target.value)}
          rows={4}
          className="w-full border rounded p-2 font-mono text-sm mb-3 text-black placeholder-black/60"
          placeholder='Ej: { "client_name": {"page":1,"x_pct":0.1,"y_pct":0.2} }'
        />

        <label className="block text-sm font-medium mb-2 text-gray-700">Tipo de plantilla</label>
        <select
          value={templateType}
          onChange={(e) => setTemplateType(e.target.value)}
          className="border rounded px-2 py-1 text-black"
        >
          <option value="report">Reporte</option>
          <option value="invoice">Factura</option>
          <option value="default">Default (mapa de celdas)</option>
        </select>

        <label className="block text-sm font-medium mt-4 mb-2 text-gray-700">Datos (JSON)</label>
        <div className="flex items-center gap-2 mb-2">
          <input
            type="text"
            value={sampleMaintenanceId}
            onChange={(e) => setSampleMaintenanceId(e.target.value)}
            placeholder="ID de mantenimiento (opcional)"
            className="border rounded px-2 py-1 text-black"
            style={{ width: 220 }}
          />
          <button
            type="button"
            onClick={async () => {
              setLoadingSample(true);
              setError(null);
              try {
                const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
                const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/templates/sample-data/${sampleMaintenanceId ? `?maintenance_id=${encodeURIComponent(sampleMaintenanceId)}` : ''}`;
                const res = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : undefined });
                if (!res.ok) {
                  const text = await res.text().catch(() => null);
                  throw new Error(`${res.status} ${res.statusText} ${text || ''}`);
                }
                const data = await res.json();
                setJsonData(JSON.stringify(data, null, 2));
                setSuccess('Datos de ejemplo cargados');
              } catch (err: any) {
                setError(err.message || 'Error cargando datos de ejemplo');
              } finally {
                setLoadingSample(false);
              }
            }}
            className="px-3 py-1 bg-gray-800 text-white rounded"
            disabled={loadingSample}
          >
            {loadingSample ? 'Cargando...' : 'Cargar datos de mantenimiento'}
          </button>
        </div>
        <textarea
          value={jsonData}
          onChange={(e) => setJsonData(e.target.value)}
          rows={8}
          className="w-full border rounded p-2 font-mono text-sm text-black placeholder-black/60"
          placeholder='Ej: { "title": "Mi reporte", "table_data": [["A",1,2],["B",3,4]] }'
        />

        {error && <div className="text-red-600 mt-2">{error}</div>}
        {success && <div className="text-green-600 mt-2">{success}</div>}

        <div className="mt-4 flex gap-3">
          <button onClick={handleGeneratePDF} disabled={loading} className="px-4 py-2 bg-red-600 text-white rounded">{loading ? 'Generando...' : 'Generar PDF'}</button>
          <button onClick={handleGenerateExcel} disabled={loading} className="px-4 py-2 bg-green-600 text-white rounded">{loading ? 'Generando...' : 'Generar Excel'}</button>
            <button onClick={handleUploadTemplate} disabled={loading || !templateName.trim()} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50" aria-disabled={!templateName.trim()}>{loading ? 'Subiendo...' : 'Subir Plantilla'}</button>
        </div>
      </div>
      {editingTemplateId && (
        <TemplateDesigner
          templateId={editingTemplateId}
          onClose={() => setEditingTemplateId(null)}
          sampleData={jsonData ? (() => { try { return JSON.parse(jsonData); } catch { return {}; } })() : {}}
        />
      )}
    </div>
  );
}

