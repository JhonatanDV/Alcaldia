import React, { useState, useEffect } from 'react';
import * as pdfjsLib from 'pdfjs-dist';

// Configurar worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

interface PDFViewerProps {
  pdfUrl: string;
  onClose?: () => void;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ pdfUrl, onClose }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [pdfDoc, setPdfDoc] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadPDF();
  }, [pdfUrl]);

  useEffect(() => {
    if (pdfDoc) {
      renderPage(currentPage);
    }
  }, [currentPage, scale, pdfDoc]);

  const loadPDF = async () => {
    try {
      setLoading(true);
      const loadingTask = pdfjsLib.getDocument(pdfUrl);
      const pdf = await loadingTask.promise;
      setPdfDoc(pdf);
      setNumPages(pdf.numPages);
      setLoading(false);
    } catch (error) {
      console.error('Error loading PDF:', error);
      setLoading(false);
    }
  };

  const renderPage = async (pageNumber: number) => {
    if (!pdfDoc) return;

    const page = await pdfDoc.getPage(pageNumber);
    const canvas = document.getElementById('pdf-canvas') as HTMLCanvasElement;
    if (!canvas) return;

    const viewport = page.getViewport({ scale });
    const context = canvas.getContext('2d');
    
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    const renderContext = {
      canvasContext: context,
      viewport: viewport,
    };

    await page.render(renderContext).promise;
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < numPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handleZoomIn = () => {
    setScale(scale + 0.2);
  };

  const handleZoomOut = () => {
    if (scale > 0.4) {
      setScale(scale - 0.2);
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = `reporte_${Date.now()}.pdf`;
    link.click();
  };

  const handlePrint = () => {
    window.open(pdfUrl, '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-xl font-semibold">Cargando PDF...</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-95 z-50 flex flex-col">
      {/* Toolbar */}
      <div className="bg-gray-800 text-white p-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
          >
            ✕ Cerrar
          </button>
          
          <div className="flex items-center space-x-2 bg-gray-700 rounded-lg px-3 py-2">
            <button
              onClick={handlePreviousPage}
              disabled={currentPage === 1}
              className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ◀
            </button>
            <span className="px-3">
              Página {currentPage} de {numPages}
            </span>
            <button
              onClick={handleNextPage}
              disabled={currentPage === numPages}
              className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ▶
            </button>
          </div>

          <div className="flex items-center space-x-2 bg-gray-700 rounded-lg px-3 py-2">
            <button
              onClick={handleZoomOut}
              className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded"
            >
              🔍−
            </button>
            <span className="px-3">{Math.round(scale * 100)}%</span>
            <button
              onClick={handleZoomIn}
              className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded"
            >
              🔍+
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
          >
            ⬇ Descargar
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition"
          >
            🖨 Imprimir
          </button>
        </div>
      </div>

      {/* PDF Canvas Container */}
      <div className="flex-1 overflow-auto bg-gray-700 p-8 flex justify-center">
        <div className="bg-white shadow-2xl">
          <canvas id="pdf-canvas" className="max-w-full h-auto"></canvas>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;