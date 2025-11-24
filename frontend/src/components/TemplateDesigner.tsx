import React, { useCallback, useEffect, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf';

pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type Marker = {
  key: string;
  x_pct: number;
  y_pct: number;
  page: number;
};

export default function TemplateDesigner({ templateId, onClose, sampleData }: { templateId: number; onClose: () => void; sampleData?: any }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [previewEnabled, setPreviewEnabled] = useState(false);
  const [previewOnCanvas, setPreviewOnCanvas] = useState(false);
  const [previewJson, setPreviewJson] = useState<string>('');
  const [previewObj, setPreviewObj] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState<{ key: string; offsetX: number; offsetY: number } | null>(null);
  const renderTaskRef = useRef<any>(null);
  const [zoom, setZoom] = useState<number>(1.5);
  const [activeField, setActiveField] = useState<string | null>(null);

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

  // Function that draws overlays with preview text directly on the canvas
  const drawOverlay = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.save();
    const fontSize = Math.max(10, Math.floor(canvas.width / 80));
    ctx.font = `${fontSize}px sans-serif`;
    ctx.textBaseline = 'top';

    markers.forEach((m) => {
      const text = previewEnabled ? (previewObj?.[m.key] ?? sampleData?.[m.key] ?? m.key) : m.key;
      const x = m.x_pct * canvas.width;
      const y = m.y_pct * canvas.height;
      const padding = 6;
      const metrics = ctx.measureText(text || '');
      const textWidth = metrics.width || 40;
      const textHeight = fontSize + 4;

      // Use indigo background with white text for better contrast
      ctx.fillStyle = 'rgba(59,130,246,0.95)'; // indigo-500
      ctx.fillRect(x, y, textWidth + padding * 2, textHeight + padding * 2);
      ctx.strokeStyle = 'rgba(255,255,255,0.9)';
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, textWidth + padding * 2, textHeight + padding * 2);
      ctx.fillStyle = 'rgba(255,255,255,0.95)';
      ctx.fillText(text, x + padding, y + padding);
    });

    ctx.restore();
  }, [markers, previewEnabled, previewObj, sampleData]);

  // Render base template (PDF or image) into canvas
  const renderTemplate = useCallback(async () => {
    if (!pdfUrl || !canvasRef.current) return;
    try {
      setLoading(true);
      setError(null);
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('No canvas context');

      // Clear
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Detect if URL points to an image
      const lower = pdfUrl.toLowerCase();
      if (lower.endsWith('.png') || lower.endsWith('.jpg') || lower.endsWith('.jpeg') || lower.endsWith('.webp')) {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          canvas.width = img.naturalWidth;
          canvas.height = img.naturalHeight;
          ctx.drawImage(img, 0, 0);
          // draw overlay if requested
          if (previewOnCanvas) drawOverlay();
          setLoading(false);
        };
        img.onerror = (e) => {
          console.error('Error loading image', e);
          setError('Error renderizando imagen');
          setLoading(false);
        };
        img.src = pdfUrl;
        return;
      }

      const loadingTask = pdfjsLib.getDocument(pdfUrl);
      const pdf = await loadingTask.promise;
      const page = await pdf.getPage(1);
      const viewport = page.getViewport({ scale: zoom });

      // Cancel any previous render task to avoid "same canvas" errors
      if (renderTaskRef.current && typeof renderTaskRef.current.cancel === 'function') {
        try {
          renderTaskRef.current.cancel();
        } catch (e) {
          // ignore cancellation errors
        }
        renderTaskRef.current = null;
      }

      canvas.width = viewport.width;
      canvas.height = viewport.height;
      // Ensure no leftover transforms
      ctx.setTransform(1, 0, 0, 1, 0, 0);

      const renderContext = {
        canvasContext: ctx,
        viewport,
      };
      const renderTask = page.render(renderContext);
      renderTaskRef.current = renderTask;
      await renderTask.promise;
      renderTaskRef.current = null;
      if (previewOnCanvas) drawOverlay();
    } catch (err: any) {
      // Suppress expected cancellation errors from pdfjs when we intentionally
      // cancel a previous render task (RenderingCancelledException). Don't
      // surface them as user-facing errors.
      if (err && (err.name === 'RenderingCancelledException' || err.message?.includes('Rendering cancelled'))) {
        // ignore
      } else {
        console.error(err);
        setError('Error renderizando plantilla');
      }
    } finally {
      setLoading(false);
    }
  }, [pdfUrl, previewOnCanvas, drawOverlay, zoom]);

  useEffect(() => {
    renderTemplate();
    return () => {
      // cancel any pending render on re-render/unmount
      if (renderTaskRef.current && typeof renderTaskRef.current.cancel === 'function') {
        try { renderTaskRef.current.cancel(); } catch (e) {}
      }
      renderTaskRef.current = null;
    };
  }, [pdfUrl, renderTemplate]);

  // When markers or preview data change, redraw overlay if enabled
  useEffect(() => {
    if (previewOnCanvas) {
      // small timeout to ensure base image is present
      const t = setTimeout(() => {
        drawOverlay();
      }, 50);
      return () => clearTimeout(t);
    }
    return;
  }, [markers, previewOnCanvas, previewEnabled, previewObj, sampleData, drawOverlay]);

  // Map page coordinates to percentages based on displayed size (use getBoundingClientRect to account for CSS scaling)
  const toPct = (x: number, y: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x_pct: 0, y_pct: 0 };
    const rect = canvas.getBoundingClientRect();
    const relX = x / rect.width; // x relative to displayed width
    const relY = y / rect.height;
    return { x_pct: relX, y_pct: relY };
  };

  const fromPct = (x_pct: number, y_pct: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return { x: x_pct * rect.width, y: y_pct * rect.height };
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
    // The marker element's offset is measured relative to the container, but canvas may be positioned within container.
    const x = e.clientX - containerRect.left - dragging.offsetX;
    const y = e.clientY - containerRect.top - dragging.offsetY;
    // Convert screen coordinate to canvas-local by calculating position relative to canvas bounding rect
    const canvas = canvasRef.current;
    if (!canvas) return;
    const canvasRect = canvas.getBoundingClientRect();
    const localX = e.clientX - canvasRect.left - dragging.offsetX;
    const localY = e.clientY - canvasRect.top - dragging.offsetY;
    const { x_pct, y_pct } = toPct(localX, localY);
    setMarkers((prev) => prev.map((m) => (m.key === dragging.key ? { ...m, x_pct: Math.max(0, Math.min(1, x_pct)), y_pct: Math.max(0, Math.min(1, y_pct)) } : m)));
  };

  // Click on canvas to position active field (if selected)
  const handleCanvasClick = (e: React.MouseEvent) => {
    if (!activeField) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const localX = e.clientX - rect.left;
    const localY = e.clientY - rect.top;
    const { x_pct, y_pct } = toPct(localX, localY);
    setMarkers((prev) => prev.map((m) => (m.key === activeField ? { ...m, x_pct: Math.max(0, Math.min(1, x_pct)), y_pct: Math.max(0, Math.min(1, y_pct)) } : m)));
  };

  const handleMouseUp = () => setDragging(null);

  const addMarker = () => {
    const key = `field_${Date.now()}`;
    setMarkers((prev) => [...prev, { key, x_pct: 0.1, y_pct: 0.1, page: 1 }]);
  };

  const removeMarker = (key: string) => setMarkers((prev) => prev.filter((m) => m.key !== key));

  const updateMarkerKey = (oldKey: string, newKeyRaw: string) => {
    const newKey = (newKeyRaw || '').trim();
    if (!newKey) return;
    setMarkers((prev) => {
      // Avoid duplicate keys by appending suffix if needed
      let finalKey = newKey;
      const others = prev.filter((p) => p.key !== oldKey).map((p) => p.key);
      let counter = 1;
      while (others.includes(finalKey)) {
        finalKey = `${newKey}_${counter}`;
        counter += 1;
      }
      return prev.map((m) => (m.key === oldKey ? { ...m, key: finalKey } : m));
    });
  };

  const updateMarkerPage = (key: string, page: number) => {
    setMarkers((prev) => prev.map((m) => (m.key === key ? { ...m, page } : m)));
  };

  const saveSchema = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const schemaObj: Record<string, any> = {};
      markers.forEach((m) => {
        schemaObj[m.key] = { page: m.page, x_pct: m.x_pct, y_pct: m.y_pct };
      });
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/templates/${templateId}/update/`, {
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

  const applyPreviewJson = () => {
    try {
      const obj = previewJson ? JSON.parse(previewJson) : {};
      setPreviewObj(obj);
      setPreviewEnabled(true);
    } catch (e) {
      setError('JSON de vista previa inválido');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-6 bg-black bg-opacity-50">
      <div className="bg-white rounded shadow-lg w-full max-w-4xl max-h-[90vh] overflow-auto p-4">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-bold">Editor visual de plantilla (PDF)</h2>
          <div className="flex gap-2">
            <button onClick={addMarker} className="px-3 py-1 bg-blue-600 text-white rounded">Añadir campo</button>
            <div className="flex items-center gap-2 bg-gray-100 px-2 py-1 rounded">
              <button onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))} className="px-2 py-1 bg-white border rounded">-</button>
              <span className="text-sm">Zoom: {Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom((z) => Math.min(3, z + 0.25))} className="px-2 py-1 bg-white border rounded">+</button>
            </div>
            <div className="flex items-center gap-2 bg-gray-100 px-2 py-1 rounded">
              <label className="text-sm">Campo activo:</label>
              <select value={activeField ?? ''} onChange={(e) => setActiveField(e.target.value || null)} className="px-2 py-1 border rounded bg-white text-sm">
                <option value="">(ninguno)</option>
                {markers.map((m) => (<option key={m.key} value={m.key}>{m.key}</option>))}
              </select>
            </div>
            <button onClick={saveSchema} className="px-3 py-1 bg-green-600 text-white rounded">Guardar posiciones</button>
            <button
              onClick={async () => {
                if (previewOnCanvas) {
                  setPreviewOnCanvas(false);
                  await renderTemplate();
                } else {
                  setPreviewOnCanvas(true);
                  // draw immediately if canvas already has content
                  drawOverlay();
                }
              }}
              className={`px-3 py-1 ${previewOnCanvas ? 'bg-orange-600 text-white' : 'bg-gray-200'} rounded`}
            >
              {previewOnCanvas ? 'Ocultar vista canvas' : 'Mostrar vista canvas'}
            </button>
            <button onClick={onClose} className="px-3 py-1 bg-gray-300 rounded">Cerrar</button>
          </div>
        </div>

        {loading && <div>Cargando plantilla...</div>}
        {error && <div className="text-red-600">{error}</div>}

        <div className="flex gap-4">
          <div ref={containerRef} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp} className="relative border flex-1" onClick={handleCanvasClick}>
            <canvas ref={canvasRef} style={{ display: pdfUrl ? 'block' : 'none', maxWidth: '100%', height: 'auto' }} />

            {/* Overlay markers */}
            {markers.map((m) => {
              const pos = fromPct(m.x_pct, m.y_pct);
              const previewText = previewEnabled ? (previewObj?.[m.key] ?? sampleData?.[m.key] ?? m.key) : m.key;
              return (
                <div
                    key={m.key}
                    onMouseDown={(e) => handleMouseDown(e, m.key)}
                    style={{ position: 'absolute', left: pos.x, top: pos.y, cursor: 'move' }}
                    className="bg-indigo-600 border border-indigo-700 px-2 py-1 rounded max-w-xs shadow-md"
                  >
                      <div className="flex items-center gap-2">
                        <strong className="text-xs text-white">{previewText}</strong>
                        <button onMouseDown={(e) => e.stopPropagation()} onClick={() => removeMarker(m.key)} className="text-xs text-red-200 hover:text-red-100">x</button>
                      </div>
                </div>
              );
            })}
          </div>

          {/* Side panel: editable list of markers */}
          <aside className="w-64 border-l pl-3">
            <h3 className="font-medium mb-2">Vista previa</h3>
            <div className="mb-2">
              <label className="text-xs text-gray-600">Datos de ejemplo (JSON)</label>
              <textarea value={previewJson} onChange={(e) => setPreviewJson(e.target.value)} rows={4} className="w-full border rounded p-2 font-mono text-sm mb-2" placeholder='Ej: { "client_name": "ACME" }' />
              <div className="flex gap-2">
                <button onClick={applyPreviewJson} className="px-3 py-1 bg-blue-600 text-white rounded">Aplicar vista previa</button>
                <button onClick={() => { setPreviewJson(''); setPreviewObj({}); setPreviewEnabled(false); }} className="px-3 py-1 bg-gray-200 rounded">Quitar vista</button>
              </div>
            </div>

            <h3 className="font-medium mb-2 mt-4">Campos</h3>
            <div className="space-y-2">
              {markers.map((m) => (
                <div key={m.key} className="p-2 border rounded bg-gray-50">
                  <label className="text-xs text-gray-600">Clave (nombre del campo)</label>
                  <input
                    value={m.key}
                    onChange={(e) => updateMarkerKey(m.key, e.target.value)}
                    className="w-full px-2 py-1 border rounded text-sm mb-1"
                  />

                  <label className="text-xs text-gray-600">Mapear a dato de muestra</label>
                  <select
                    className="w-full px-2 py-1 border rounded text-sm mb-1"
                    value={m.key}
                    onChange={(e) => updateMarkerKey(m.key, e.target.value)}
                  >
                    <option value={m.key}>(usar clave actual)</option>
                    {Object.keys(sampleData || {}).map((k) => (
                      <option key={k} value={k}>{k}</option>
                    ))}
                  </select>

                  <label className="text-xs text-gray-600">Página</label>
                  <input
                    type="number"
                    min={1}
                    value={m.page}
                    onChange={(e) => updateMarkerPage(m.key, Number(e.target.value) || 1)}
                    className="w-full px-2 py-1 border rounded text-sm mb-2"
                  />

                  <div className="flex gap-2">
                    <button onClick={() => setActiveField(m.key)} className="px-2 py-1 bg-blue-600 text-white text-xs rounded">Usar como activo</button>
                    <button onClick={() => removeMarker(m.key)} className="px-2 py-1 bg-red-200 text-red-800 text-xs rounded">Eliminar</button>
                  </div>
                </div>
              ))}
            </div>
          </aside>
        </div>

        <div className="mt-3 text-sm text-gray-600">Arrastra los campos sobre la plantilla. Se guardan en porcentajes relativos a la página.</div>
      </div>
    </div>
  );
}
