"use client";

import { useState } from "react";
import axios from "axios";

interface MaintenancePDFGeneratorProps {
  maintenanceId: number;
  token: string;
  buttonText?: string;
  className?: string;
}

export default function MaintenancePDFGenerator({
  maintenanceId,
  token,
  buttonText = "Generar Reporte PDF",
  className = "",
}: MaintenancePDFGeneratorProps) {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const generatePDF = async () => {
    setGenerating(true);
    setError("");
    setSuccess(false);

    try {
      const response = await axios.post(
        `${API_URL}/api/reports/generate/`,
        {
          maintenance_id: maintenanceId,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setSuccess(true);
      
      // Si hay un PDF disponible, abrirlo en nueva pestaña
      if (response.data.pdf_file) {
        const pdfUrl = response.data.pdf_file.startsWith('http') 
          ? response.data.pdf_file 
          : `${API_URL}${response.data.pdf_file}`;
        window.open(pdfUrl, '_blank');
      }

      // Auto-limpiar mensaje de éxito después de 3 segundos
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 
                       err.response?.data?.detail || 
                       "Error al generar el reporte PDF";
      setError(errorMsg);
      
      // Auto-limpiar mensaje de error después de 5 segundos
      setTimeout(() => setError(""), 5000);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-2">
      <button
        onClick={generatePDF}
        disabled={generating}
        className={`
          px-4 py-2 rounded-md font-medium text-white
          transition-colors duration-200
          ${generating 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
          }
          disabled:opacity-50
          ${className}
        `}
      >
        {generating ? (
          <span className="flex items-center gap-2">
            <svg 
              className="animate-spin h-4 w-4" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24"
            >
              <circle 
                className="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4"
              />
              <path 
                className="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Generando...
          </span>
        ) : (
          buttonText
        )}
      </button>

      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-100 border border-green-400 text-green-700 rounded-md text-sm">
          ✓ Reporte generado exitosamente
        </div>
      )}
    </div>
  );
}
