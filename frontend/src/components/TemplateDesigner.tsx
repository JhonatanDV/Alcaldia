import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf';
import React, { useCallback, useEffect, useRef, useState } from 'react';

pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type Marker = {
  key: string;
  x_pct: number;
  y_pct: number;
  page: number;
  map_to?: string;
};

export default function TemplateDesigner({ templateId, onClose, sampleData }: { templateId: string | number; onClose: () => void; sampleData?: any }) {
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
  const draggingRef = useRef<{ key: string; offsetX: number; offsetY: number } | null>(null);
  const ghostRef = useRef<HTMLDivElement | null>(null);
  const renderTaskRef = useRef<any>(null);
  const [zoom, setZoom] = useState<number>(1.5);
  const [activeField, setActiveField] = useState<string | null>(null);
  const [localKeys, setLocalKeys] = useState<Record<string, string>>({});
  const [notice, setNotice] = useState<string>('');

  // Build a flattened list of sample-data keys for use in selects/datalists.
  // If a sample value is an object (but not an array), expose its nested keys
  // as `parent.child` so template authors can map to granular fields like
  // activities.<task name> or equipment.serial_number.
  const getSampleOptions = React.useCallback((): string[] => {
    try {
      const data = sampleData || {};
      const out: string[] = [];
      // Always include canonical maintenance field names so templates map to
      // expected keys even when `sampleData` is empty or minimal.
      const MAINTENANCE_FIELDS = [
        'codigo','description','maintenance_type','status','scheduled_date','completion_date','hora_inicio','hora_final',
        'equipment_code','equipment_name','equipment_serial','technician_name','technician_email',
        'sede','dependencia','subdependencia','ubicacion','oficina','observations','observaciones_generales','observaciones_seguridad',
        'activities','elaborado_por','revisado_por','aprobado_por','cost','version'
      ];

      // Seed with canonical fields first
      MAINTENANCE_FIELDS.forEach((f) => out.push(f));

      // Then expand actual sample data keys (including nested object keys)
      Object.keys(data).forEach((k) => {
        out.push(k);
        const v = (data as any)[k];
        if (v && typeof v === 'object' && !Array.isArray(v)) {
          Object.keys(v).forEach((sub) => {
            out.push(`${k}.${sub}`);
          });
        }
        // If activities is an array of objects, expand first-level keys
        if (Array.isArray(v)) {
          v.forEach((item: any, idx: number) => {
            if (item && typeof item === 'object') {
              Object.keys(item).forEach((sub) => out.push(`${k}[${idx}].${sub}`));
            }
          });
        }
      });
      // dedupe
      return Array.from(new Set(out));
    } catch (e) {
      return [];
    }
  }, [sampleData]);

  useEffect(() => {
    const fetchTemplate = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        const id = encodeURIComponent(String(templateId));
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/templates/${id}/`, {
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
      const mappedKey = localKeys[m.key] ?? m.key;
      const text = previewEnabled ? (previewObj?.[mappedKey] ?? sampleData?.[mappedKey] ?? m.key) : m.key;
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
  }, [markers, previewEnabled, previewObj, sampleData, localKeys]);

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

      // Before asking pdfjs to load the URL, do a lightweight HEAD request
      // to verify the file exists (avoids pdfjs throwing MissingPDFException
      // which is noisy and less actionable). Some storage backends may return
      // URLs that no longer point to files; handle that gracefully.
      // Try HEAD check; if it fails, attempt heuristic alternatives before giving up
      const tryUrls: string[] = [pdfUrl];
      const urlObj = new URL(pdfUrl, window.location.href);
      try {
        const fname = urlObj.pathname.split('/').pop() || '';
        const decoded = decodeURIComponent(fname);
        // Add decoded filename if it differs
        if (decoded !== fname) {
          tryUrls.push(`${urlObj.origin}${urlObj.pathname.replace(fname, encodeURIComponent(decoded))}`);
          tryUrls.push(`${urlObj.origin}${urlObj.pathname.replace(fname, decoded)}`);
        }
        // Heuristic: strip trailing underscore+token before extension (e.g. _RibwlEF.pdf)
        const baseNoToken = decoded.replace(/_[A-Za-z0-9]+(?=\.pdf$)/i, '');
        if (baseNoToken && baseNoToken !== decoded) {
          tryUrls.push(`${urlObj.origin}${urlObj.pathname.replace(fname, encodeURIComponent(baseNoToken))}`);
          tryUrls.push(`${urlObj.origin}${urlObj.pathname.replace(fname, baseNoToken)}`);
        }
      } catch (e) {
        // ignore URL parsing errors and fall back to original
      }

      let foundPdfUrl: string | null = null;
      for (const u of tryUrls) {
        try {
          const head = await fetch(u, { method: 'HEAD' });
          if (head.ok) {
            foundPdfUrl = u;
            break;
          }
        } catch (err) {
          // try next
        }
      }
      if (!foundPdfUrl) {
        console.error('PDF HEAD check failed for all heuristics', pdfUrl, tryUrls);
        setError(`No se encontró el archivo PDF en la URL: ${pdfUrl}`);
        setLoading(false);
        return;
      }

      const loadingTask = pdfjsLib.getDocument(foundPdfUrl);
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

  // Initialize/merge a local editable copy of marker keys. Do not overwrite
  // user edits when only marker positions change — preserve existing localKeys
  // entries and only add missing keys from markers. This prevents losing the
  // "map_to" values when the user drags/moves fields.
  useEffect(() => {
    setLocalKeys((prev) => {
      const map: Record<string, string> = { ...prev };
      markers.forEach((m) => {
        // if we've already got an entry for this marker key, keep it
        if (!(m.key in map)) {
          map[m.key] = (m as any).map_to ?? m.key;
        }
      });
      // remove keys that no longer exist in markers
      Object.keys(map).forEach((k) => {
        if (!markers.find((m) => m.key === k)) delete map[k];
      });
      return map;
    });
    // Intentionally do not depend on localKeys here — we merge into it.
  }, [markers]);

  // Ensure ghost element exists for dragging without causing React re-renders
  useEffect(() => {
    if (!ghostRef.current && containerRef.current) {
      const el = document.createElement('div');
      el.style.position = 'absolute';
      el.style.display = 'none';
      el.style.pointerEvents = 'none';
      el.className = 'bg-indigo-600 border border-indigo-700 px-2 py-1 rounded max-w-xs shadow-md text-white text-xs';
      containerRef.current.appendChild(el);
      ghostRef.current = el;
    }
    return () => {
      try {
        if (ghostRef.current && containerRef.current) {
          containerRef.current.removeChild(ghostRef.current);
        }
      } catch (e) {
        // ignore
      }
      ghostRef.current = null;
    };
  }, []);

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
    const info = { key, offsetX, offsetY };
    setDragging(info);
    draggingRef.current = info;

    // position and show ghost
    const canvasRect = canvasRef.current?.getBoundingClientRect();
    const marker = markers.find((m) => m.key === key);
    if (ghostRef.current && canvasRect && marker) {
      const { x, y } = fromPct(marker.x_pct, marker.y_pct);
      ghostRef.current.style.left = `${x}px`;
      ghostRef.current.style.top = `${y}px`;
      ghostRef.current.style.display = 'block';
      ghostRef.current.textContent = (previewEnabled ? (previewObj?.[localKeys[marker.key] ?? marker.key] ?? sampleData?.[localKeys[marker.key] ?? marker.key] ?? marker.key) : marker.key) as string;
    }
  };

  // We will track pointer movement globally while dragging but avoid updating React state
  // on every move. Instead we move a ghost DOM element (ghostRef) and commit the new
  // marker position on mouseup.
  const handleGlobalMouseMove = (e: MouseEvent) => {
    const info = draggingRef.current;
    if (!info) return;
    const canvas = canvasRef.current;
    if (!canvas || !ghostRef.current) return;
    const canvasRect = canvas.getBoundingClientRect();
    const localX = e.clientX - canvasRect.left - info.offsetX;
    const localY = e.clientY - canvasRect.top - info.offsetY;
    // Clamp to canvas bounds
    const clampedX = Math.max(0, Math.min(canvasRect.width, localX));
    const clampedY = Math.max(0, Math.min(canvasRect.height, localY));
    ghostRef.current.style.left = `${clampedX}px`;
    ghostRef.current.style.top = `${clampedY}px`;
  };

  const handleGlobalMouseUp = (e: MouseEvent) => {
    const info = draggingRef.current;
    if (!info) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const canvasRect = canvas.getBoundingClientRect();
    const localX = e.clientX - canvasRect.left - info.offsetX;
    const localY = e.clientY - canvasRect.top - info.offsetY;
    const { x_pct, y_pct } = toPct(localX, localY);
    setMarkers((prev) => prev.map((m) => (m.key === info.key ? { ...m, x_pct: Math.max(0, Math.min(1, x_pct)), y_pct: Math.max(0, Math.min(1, y_pct)) } : m)));

    // hide ghost and clear dragging refs
    if (ghostRef.current) ghostRef.current.style.display = 'none';
    draggingRef.current = null;
    setDragging(null);
  };

  useEffect(() => {
    window.addEventListener('mousemove', handleGlobalMouseMove);
    window.addEventListener('mouseup', handleGlobalMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleGlobalMouseMove);
      window.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [markers, previewEnabled, previewObj, sampleData]);

  // After each render where markers or canvas dimensions change, update the
  // absolute position of overlay DOM nodes using direct DOM APIs. This avoids
  // using the JSX `style` prop (which the linter flags) while keeping
  // positions accurate and dynamic.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    markers.forEach((m) => {
      try {
        const el = containerRef.current?.querySelector(`[data-marker-key="${m.key}"]`) as HTMLElement | null;
        if (el) {
          const { x, y } = fromPct(m.x_pct, m.y_pct);
          el.style.left = `${x}px`;
          el.style.top = `${y}px`;
        }
      } catch (e) {
        // ignore per-element errors
      }
    });
  }, [markers, pdfUrl, zoom]);

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
    // Assign a sensible default mapping for the new marker: prefer a canonical
    // maintenance field that is not yet used as a mapping, fallback to marker key.
    setLocalKeys((prev) => {
      const next = { ...prev };
      const opts = getSampleOptions();
      // prefer first MAINTENANCE_FIELDS-like option (opts already seeds them first)
      const preferred = opts.find((o) => !Object.values(next).includes(o));
      next[key] = preferred || key;
      return next;
    });
  };

  // Auto-map heuristic: try to match marker keys to the available sample options
  // and canonical maintenance fields. Only assign mappings for markers that
  // currently equal their key (i.e., user hasn't manually mapped them).
  const autoMap = () => {
    const opts = getSampleOptions();
    const normalize = (s: string) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
    const normOpts = opts.map((o) => ({ raw: o, norm: normalize(o) }));

    setLocalKeys((prev) => {
      const next = { ...prev };
      const used = new Set(Object.values(prev));

      markers.forEach((m) => {
        const current = prev[m.key] ?? m.key;
        // Don't overwrite explicit mappings
        if (current && current !== m.key) return;
        const mk = m.key;
        const nmk = normalize(mk);

        // 1) exact normalized match
        let found = normOpts.find((o) => o.norm === nmk);
        // 2) contains/substring match
        if (!found) found = normOpts.find((o) => o.norm.includes(nmk) || nmk.includes(o.norm));
        // 3) token match (split marker key)
        if (!found) {
          const tokens = mk.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
          for (const t of tokens) {
            found = normOpts.find((o) => o.norm.includes(t));
            if (found) break;
          }
        }
        // 4) fallback to first unused option
        if (!found) {
          const firstUnused = normOpts.find((o) => !used.has(o.raw));
          found = firstUnused || normOpts[0];
        }

        if (found) {
          next[m.key] = found.raw;
          used.add(found.raw);
        } else {
          next[m.key] = m.key;
        }
      });

      return next;
    });

    // show brief inline notice instead of blocking alert
    try {
      setNotice('Auto-map completado');
      setTimeout(() => setNotice(''), 2500);
    } catch (e) {}
  };

  const removeMarker = (key: string) => {
    setMarkers((prev) => prev.filter((m) => m.key !== key));
    setLocalKeys((prev) => {
      const next = { ...prev };
      if (key in next) delete next[key];
      return next;
    });
  };

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
    // Move any existing localKeys mapping from the old key to the new one,
    // so the user's "map_to" selection is preserved when renaming a field.
    setLocalKeys((prev) => {
      const next = { ...prev };
      if (oldKey in next) {
        next[newKey] = next[oldKey];
        delete next[oldKey];
      } else {
        next[newKey] = newKey;
      }
      return next;
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
        schemaObj[m.key] = { page: m.page, x_pct: m.x_pct, y_pct: m.y_pct, map_to: localKeys[m.key] ?? m.key };
      });
      const id = encodeURIComponent(String(templateId));
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/templates/${id}/update/`, {
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

  // After zoom changes we may need to re-render the PDF and ensure DOM overlay
  // positions are recalculated. Trigger a small redraw/refresh so markers' DOM
  // positions (which rely on getBoundingClientRect) are in sync with the
  // rendered canvas.
  useEffect(() => {
    const t = setTimeout(async () => {
      try {
        await renderTemplate();
        if (previewOnCanvas) drawOverlay();
        // nudge a React render so computed positions in JSX are recalculated
        setMarkers((prev) => [...prev]);
      } catch (e) {
        // ignore
      }
    }, 80);
    return () => clearTimeout(t);
  }, [zoom]);

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
              <label htmlFor="active-field-select" className="text-sm">Campo activo:</label>
              <select 
                id="active-field-select"
                value={activeField ?? ''} 
                onChange={(e) => setActiveField(e.target.value || null)} 
                aria-label="Seleccionar campo activo para posicionar"
                className="px-2 py-1 border rounded bg-white text-sm"
              >
                <option value="">(ninguno)</option>
                {markers.map((m) => (<option key={m.key} value={m.key}>{m.key}</option>))}
              </select>
            </div>
            <button onClick={autoMap} className="px-3 py-1 bg-yellow-500 text-white rounded">Auto-map</button>
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
          {notice && <div className="ml-3 text-sm text-green-600">{notice}</div>}
        </div>

        {loading && <div>Cargando plantilla...</div>}
        {error && <div className="text-red-600">{error}</div>}

        <div className="flex flex-col md:flex-row gap-4">
          <div ref={containerRef} onMouseUp={handleMouseUp} className="relative border flex-1 min-h-[200px]" onClick={handleCanvasClick}>
            <canvas ref={canvasRef} className={`${pdfUrl ? 'block' : 'hidden'} max-w-full h-auto`} />

            {/* Overlay markers */}
            {markers.map((m) => {
              const pos = fromPct(m.x_pct, m.y_pct);
              const mappedKey = localKeys[m.key] ?? m.key;
              const previewText = previewEnabled ? (previewObj?.[mappedKey] ?? sampleData?.[mappedKey] ?? m.key) : m.key;
              return (
                <div
                    key={m.key}
                    onMouseDown={(e) => handleMouseDown(e, m.key)}
                    data-marker-key={m.key}
                    className="absolute cursor-move bg-indigo-600 border border-indigo-700 px-2 py-1 rounded max-w-xs shadow-md"
                  >
                      <div className="flex items-center gap-2">
                        <strong className="text-xs text-white">{previewText}</strong>
                        <button onMouseDown={(e) => e.stopPropagation()} onClick={() => removeMarker(m.key)} className="text-xs text-red-200 hover:text-red-100">x</button>
                      </div>
                </div>
              );
            })}
            {/* Position overlays via DOM after render to avoid inline JSX styles (linter) */}
            {null}
          </div>

          {/* Side panel: editable list of markers */}
          <aside className="w-full md:w-64 border-l md:pl-3 pt-4 md:pt-0">
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
                    value={localKeys[m.key] ?? m.key}
                    list={`field-suggestions-${m.key}`}
                    onChange={(e) => setLocalKeys((prev) => ({ ...prev, [m.key]: e.target.value }))}
                    onBlur={() => {
                      const newVal = (localKeys[m.key] || '').trim();
                      if (newVal && newVal !== m.key) updateMarkerKey(m.key, newVal);
                    }}
                    onKeyDown={(e) => { if (e.key === 'Enter') { (e.target as HTMLInputElement).blur(); } }}
                    className="w-full px-2 py-1 border rounded text-sm mb-1"
                    placeholder={`Clave para ${m.key}`}
                    aria-label={`Clave para ${m.key}`}
                  />

                  <label htmlFor={`field-map-${m.key}`} className="text-xs text-gray-600">Mapear a dato de muestra</label>
                  <select
                    id={`field-map-${m.key}`}
                    className="w-full px-2 py-1 border rounded text-sm mb-1"
                    value={localKeys[m.key] ?? m.key}
                    onChange={(e) => setLocalKeys((prev) => ({ ...prev, [m.key]: e.target.value }))}
                    aria-label={`Mapear campo ${m.key} a dato de muestra`}
                  >
                    <option value={m.key}>(usar clave actual)</option>
                    {getSampleOptions().map((k) => (
                      <option key={k} value={k}>{k}</option>
                    ))}
                  </select>
                  <datalist id={`field-suggestions-${m.key}`}>
                    {getSampleOptions().map((k) => (<option key={k} value={k} />))}
                  </datalist>

                  <label htmlFor={`field-page-${m.key}`} className="text-xs text-gray-600">Página</label>
                  <input
                    id={`field-page-${m.key}`}
                    type="number"
                    min={1}
                    value={m.page}
                    onChange={(e) => updateMarkerPage(m.key, Number(e.target.value) || 1)}
                    aria-label={`Número de página para campo ${m.key}`}
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
