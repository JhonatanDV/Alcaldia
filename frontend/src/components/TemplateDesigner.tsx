import React, { useEffect, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf';

pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type Marker = {
  key: string;
  x_pct: number;
  y_pct: number;
  page: number;
};

export default function TemplateDesigner({ templateId, onClose }: { templateId: number; onClose: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState<{ key: string; offsetX: number; offsetY: number } | null>(null);

  useEffect(() => {
    const fetchTemplate = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/templates/${templateId}/`, {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (!res.ok) throw new Error('No se pudo obtener la plantilla');
        const data = await res.json();
        if (data.template_file) {
          setPdfUrl(data.template_file);
        } else {
          setPdfUrl(null);
        }
        if (data.fields_schema) {
          setMarkers(Object.keys(data.fields_schema).map((k) => ({ key: k, ...data.fields_schema[k] } as Marker)));
        }
      } catch (err: any) {
        console.error(err);
        setError(err.message || 'Error cargando plantilla');
      } finally {
        setLoading(false);
      }
    };
    fetchTemplate();
  }, [templateId]);

  useEffect(() => {
    const renderPdf = async () => {
      if (!pdfUrl || !canvasRef.current) return;
      try {
        const loadingTask = pdfjsLib.getDocument(pdfUrl);
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: 1.5 });
        const canvas = canvasRef.current;
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        const ctx = canvas.getContext('2d');
        if (!ctx) throw new Error('No canvas context');
        const renderContext = {
          canvasContext: ctx,
          viewport,
        };
        await page.render(renderContext).promise;
      } catch (err) {
        console.error(err);
        setError('Error renderizando PDF');
      }
    };
    renderPdf();
  }, [pdfUrl]);

  const toPct = (x: number, y: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x_pct: 0, y_pct: 0 };
    return { x_pct: x / canvas.width, y_pct: y / canvas.height };
  };

  const fromPct = (x_pct: number, y_pct: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    return { x: x_pct * canvas.width, y: y_pct * canvas.height };
  };

  const handleMouseDown = (e: React.MouseEvent, key: string) => {
    const el = e.currentTarget as HTMLDivElement;
    const rect = el.getBoundingClientRect();
    const offsetX = e.clientX - rect.left;
    const offsetY = e.clientY - rect.top;
    setDragging({ key, offsetX, offsetY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragging || !containerRef.current) return;
    const containerRect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - containerRect.left - dragging.offsetX;
    const y = e.clientY - containerRect.top - dragging.offsetY;
    const { x_pct, y_pct } = toPct(x, y);
    setMarkers((prev) => prev.map((m) => (m.key === dragging.key ? { ...m, x_pct: Math.max(0, Math.min(1, x_pct)), y_pct: Math.max(0, Math.min(1, y_pct)) } : m)));
  };

  const handleMouseUp = () => setDragging(null);

  const addMarker = () => {
    const key = `field_${Date.now()}`;
    setMarkers((prev) => [...prev, { key, x_pct: 0.1, y_pct: 0.1, page: 1 }]);
  };

  const removeMarker = (key: string) => setMarkers((prev) => prev.filter((m) => m.key !== key));

  const saveSchema = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const schemaObj: Record<string, any> = {};
      markers.forEach((m) => {
        schemaObj[m.key] = { page: m.page, x_pct: m.x_pct, y_pct: m.y_pct };
      });
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/templates/${templateId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ fields_schema: JSON.stringify(schemaObj) }),
      });
      if (!res.ok) throw new Error('Error guardando esquema');
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error guardando esquema');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-6 bg-black bg-opacity-50">
      <div className="bg-white rounded shadow-lg w-full max-w-4xl max-h-[90vh] overflow-auto p-4">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-bold">Editor visual de plantilla (PDF)</h2>
          <div className="flex gap-2">
            <button onClick={addMarker} className="px-3 py-1 bg-blue-600 text-white rounded">Añadir campo</button>
            <button onClick={saveSchema} className="px-3 py-1 bg-green-600 text-white rounded">Guardar posiciones</button>
            <button onClick={onClose} className="px-3 py-1 bg-gray-300 rounded">Cerrar</button>
          </div>
        </div>

        {loading && <div>Cargando plantilla...</div>}
        {error && <div className="text-red-600">{error}</div>}

        <div ref={containerRef} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp} className="relative border">
          <canvas ref={canvasRef} style={{ display: pdfUrl ? 'block' : 'none', maxWidth: '100%', height: 'auto' }} />

          {/* Overlay markers */}
          {markers.map((m) => {
            const pos = fromPct(m.x_pct, m.y_pct);
            return (
              <div
                key={m.key}
                onMouseDown={(e) => handleMouseDown(e, m.key)}
                style={{ position: 'absolute', left: pos.x, top: pos.y, cursor: 'move' }}
                className="bg-yellow-300 border px-2 py-1 rounded"
              >
                <div className="flex items-center gap-2">
                  <strong className="text-xs">{m.key}</strong>
                  <button onClick={() => removeMarker(m.key)} className="text-xs text-red-600">x</button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-3 text-sm text-gray-600">Arrastra los campos sobre la plantilla. Se guardan en porcentajes relativos a la página.</div>
      </div>
    </div>
  );
}
