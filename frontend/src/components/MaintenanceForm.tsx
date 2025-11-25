"use client";

import { useState, useRef } from "react";
import axios from "axios";
import SignaturePad from "react-signature-canvas";
import CascadingLocationSelect from './CascadingLocationSelect';

interface MaintenanceFormProps {
  token: string;
  equipmentId: number;
  equipmentCode?: string;
  equipmentName?: string;
  equipmentLocation?: string;
  equipmentDetails?: any;
  onMaintenanceCreated: () => void;
}

export default function MaintenanceForm({
  token,
  equipmentId,
  equipmentCode = "",
  equipmentName = "",
  equipmentLocation = "",
  equipmentDetails = null,
  onMaintenanceCreated,
}: MaintenanceFormProps) {
  const [formData, setFormData] = useState({
    maintenance_type: "preventivo",
    description: "",
    scheduled_date: "",
    performed_by: "",
  // relational ids (preferred)
  sede_rel: (equipmentDetails && equipmentDetails.sede_rel) ? (typeof equipmentDetails.sede_rel === 'object' ? equipmentDetails.sede_rel.id : equipmentDetails.sede_rel) : null as number | null,
  dependencia_rel: (equipmentDetails && equipmentDetails.dependencia_rel) ? (typeof equipmentDetails.dependencia_rel === 'object' ? equipmentDetails.dependencia_rel.id : equipmentDetails.dependencia_rel) : null as number | null,
  subdependencia: (equipmentDetails && equipmentDetails.subdependencia) ? (typeof equipmentDetails.subdependencia === 'object' ? equipmentDetails.subdependencia.id : equipmentDetails.subdependencia) : null as number | null,
  // legacy string fields (kept for compatibility)
  sede: equipmentLocation || "",
  dependencia: "",
  oficina: "",
    placa: equipmentCode || "",
    hora_inicio: "",
    hora_final: "",
    activities: {} as Record<string, boolean | null>,
    observaciones_generales: "",
    observaciones_seguridad: "",
    calificacion_servicio: "",
    observaciones_usuario: "",
    is_incident: false,
    incident_notes: "",
    equipment_type: "computer",
  });
  const [photos, setPhotos] = useState<File[]>([]);
  const [signature, setSignature] = useState<string | null>(null);
  const [secondSignature, setSecondSignature] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const sigPadRef = useRef<SignaturePad>(null);
  const secondSigPadRef = useRef<SignaturePad>(null);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSedeChange = (sedeId: number | null) => {
    setFormData((prev) => ({ ...prev, sede_rel: sedeId, dependencia_rel: null, subdependencia: null }));
  };

  const handleDependenciaChange = (dependenciaId: number | null) => {
    setFormData((prev) => ({ ...prev, dependencia_rel: dependenciaId, subdependencia: null }));
  };

  const handleSubdependenciaChange = (subId: number | null) => {
    setFormData((prev) => ({ ...prev, subdependencia: subId }));
  };

  const handleActivityChange = (activity: string, value: boolean | null) => {
    setFormData((prev) => ({
      ...prev,
      activities: { ...prev.activities, [activity]: value },
    }));
  };

  const handleMaintenanceTypeChange = (type: string) => {
    setFormData((prev) => ({
      ...prev,
      equipment_type: type,
      activities: {},
    }));
  };

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (photos.length + files.length > 5) {
      setError("Máximo 5 fotos permitidas");
      return;
    }
    setPhotos((prev) => [...prev, ...files]);
    setError("");
  };

  const removePhoto = (index: number) => {
    setPhotos((prev) => prev.filter((_, i) => i !== index));
  };

  const clearSignature = () => {
    sigPadRef.current?.clear();
    setSignature(null);
  };

  const saveSignature = () => {
    if (sigPadRef.current) {
      setSignature(sigPadRef.current.toDataURL());
    }
  };

  const clearSecondSignature = () => {
    secondSigPadRef.current?.clear();
    setSecondSignature(null);
  };

  const saveSecondSignature = () => {
    if (secondSigPadRef.current) {
      setSecondSignature(secondSigPadRef.current.toDataURL());
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formDataToSend = new FormData();
      
      // Asegurar que equipment se envíe correctamente
      formDataToSend.append("equipment", equipmentId.toString());
      formDataToSend.append("maintenance_type", formData.maintenance_type);
      formDataToSend.append("description", formData.description);
      formDataToSend.append("scheduled_date", formData.scheduled_date);
      formDataToSend.append("performed_by", formData.performed_by);
      // If relational IDs were not set in formData (e.g., equipmentDetails passed but not used), try to fill from equipmentDetails
      const sedeToSend = formData.sede_rel || (equipmentDetails && (equipmentDetails.sede_rel ? (typeof equipmentDetails.sede_rel === 'object' ? equipmentDetails.sede_rel.id : equipmentDetails.sede_rel) : null));
      const dependenciaToSend = formData.dependencia_rel || (equipmentDetails && (equipmentDetails.dependencia_rel ? (typeof equipmentDetails.dependencia_rel === 'object' ? equipmentDetails.dependencia_rel.id : equipmentDetails.dependencia_rel) : null));
      const subdepToSend = formData.subdependencia || (equipmentDetails && (equipmentDetails.subdependencia ? (typeof equipmentDetails.subdependencia === 'object' ? equipmentDetails.subdependencia.id : equipmentDetails.subdependencia) : null));

      if (sedeToSend) {
        formDataToSend.append("sede_rel", String(sedeToSend));
      } else {
        formDataToSend.append("sede", formData.sede);
      }

      if (dependenciaToSend) {
        formDataToSend.append("dependencia_rel", String(dependenciaToSend));
      } else {
        formDataToSend.append("dependencia", formData.dependencia);
      }

      if (subdepToSend) {
        formDataToSend.append("subdependencia", String(subdepToSend));
        if (formData.oficina) formDataToSend.append("oficina", formData.oficina);
      } else {
        formDataToSend.append("oficina", formData.oficina);
      }
      formDataToSend.append("placa", formData.placa);
      formDataToSend.append("hora_inicio", formData.hora_inicio);
      formDataToSend.append("hora_final", formData.hora_final);
      
      // Enviar activities como JSON string
      formDataToSend.append("activities", JSON.stringify(formData.activities));
      formDataToSend.append("observaciones_generales", formData.observaciones_generales);
      formDataToSend.append("observaciones_seguridad", formData.observaciones_seguridad);
      formDataToSend.append("calificacion_servicio", formData.calificacion_servicio);
      formDataToSend.append("observaciones_usuario", formData.observaciones_usuario);
      formDataToSend.append("is_incident", formData.is_incident.toString());
      formDataToSend.append("incident_notes", formData.incident_notes);

      photos.forEach((photo) => {
        formDataToSend.append("photos", photo);
      });

      if (signature) {
        const signatureBlob = await fetch(signature).then((res) => res.blob());
        formDataToSend.append("signature", signatureBlob, "signature.png");
      }

      if (secondSignature) {
        const secondSignatureBlob = await fetch(secondSignature).then((res) => res.blob());
        formDataToSend.append("second_signature", secondSignatureBlob, "second_signature.png");
      }

      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/maintenances/`,
        formDataToSend,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Reset form
      setFormData({
        maintenance_type: "preventivo",
        description: "",
        scheduled_date: "",
        performed_by: "",
        sede_rel: null,
        dependencia_rel: null,
        subdependencia: null,
        sede: equipmentLocation || "",
        dependencia: "",
        oficina: "",
        placa: equipmentCode || "",
        hora_inicio: "",
        hora_final: "",
        activities: {},
        observaciones_generales: "",
        observaciones_seguridad: "",
        calificacion_servicio: "",
        observaciones_usuario: "",
        is_incident: false,
        incident_notes: "",
        equipment_type: "computer",
      });
      setPhotos([]);
      setSignature(null);
      setSecondSignature(null);
      sigPadRef.current?.clear();
      secondSigPadRef.current?.clear();

      onMaintenanceCreated();
    } catch (err: any) {
      console.error('Error completo:', err);
      console.error('Respuesta del servidor:', err.response?.data);
      
      let errorMessage = "Error al crear mantenimiento";
      
      if (err.response?.data) {
        const errorData = err.response.data;
        
        if (typeof errorData === 'object' && !errorData.detail) {
          const fieldErrors = Object.entries(errorData)
            .map(([field, errors]: [string, any]) => {
              if (Array.isArray(errors)) {
                return `${field}: ${errors.join(', ')}`;
              }
              return `${field}: ${errors}`;
            })
            .join('\n');
          errorMessage = `Errores de validación:\n${fieldErrors}`;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const computerActivities = [
    "Limpieza interna de la torre",
    "Limpieza del teclado",
    "Limpieza del monitor",
    "Verificación de cables de poder y de datos",
    "Ajuste de tarjetas (Memoria - Video - Red)",
    "Lubricación del ventilador de la torre",
    "Lubricación del ventilador del procesador",
    "Crear partición de datos",
    "Mover información a partición de datos",
    "Reinstalar sistema operativo",
    "Instalar antivirus",
    "Análisis en busca de software malicioso",
    "Diagnosticar funcionamiento aplicaciones instaladas",
    "Suspender actualizaciones automáticas S.O.",
    "Instalar programas esenciales (ofimática, grabador de discos)",
    "Configurar usuarios administrador local",
    "Modificar contraseña de administrador",
    "Configurar nombre equipo",
    "El equipo tiene estabilizador",
    "El escritorio está limpio",
    "Desactivar aplicaciones al inicio de Windows",
    "Configurar página de inicio navegador",
    "Configurar fondo de pantalla institucional",
    "Configurar protector de pantalla institucional",
    "Verificar funcionamiento general",
    "Inventario de equipo",
    "Limpieza de registros y eliminación de archivos temporales",
    "Creación Punto de Restauración",
    "Verificar espacio en disco",
    "Desactivar software no autorizado",
    "Analizar disco duro",
    "El usuario de Windows tiene contraseña",
  ];

  const printerScannerActivities = [
    "Limpieza general",
    "Alineación de papel",
    "Configuración del equipo",
    "Pruebas de funcionamiento",
    "Limpieza de carcaza",
    "Limpieza tóner",
    "Limpieza tarjeta lógica",
    "Limpieza de sensores",
    "Limpieza de rodillo",
    "Limpieza de correas dentadas o guías",
    "Limpieza de ventiladores",
    "Limpieza de cabezal impresora matriz de punto e inyección tinta",
    "Limpieza de engranaje",
    "Limpieza de fusor",
    "Limpieza tarjeta de poder",
    "Alineación de rodillos alimentación de papel",
  ];

  const currentActivities = formData.equipment_type === 'computer' ? computerActivities : printerScannerActivities;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">
        Registro de Mantenimientos
      </h2>

      {/* Modo Selection */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Seleccionar Modo</h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <input
              type="radio"
              id="modo_normal"
              name="modo"
              checked={!formData.is_incident}
              onChange={() => setFormData((prev) => ({ ...prev, is_incident: false }))}
              className="mt-1"
            />
            <div>
              <label htmlFor="modo_normal" className="text-sm font-medium text-gray-700 cursor-pointer">
                Modo Normal
              </label>
              <p className="text-sm text-gray-600 mt-1">
                Todos los campos del formulario son obligatorios<br />
                Excepción: fotografías (opcionales)<br />
                Validación completa de datos<br />
                Firma del técnico requerida
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <input
              type="radio"
              id="modo_incidencia"
              name="modo"
              checked={formData.is_incident}
              onChange={() => setFormData((prev) => ({ ...prev, is_incident: true }))}
              className="mt-1"
            />
            <div>
              <label htmlFor="modo_incidencia" className="text-sm font-medium text-gray-700 cursor-pointer">
                Modo Incidencia
              </label>
              <p className="text-sm text-gray-600 mt-1">
                Campos obligatorios reducidos:<br />
                • Información actual del dispositivo<br />
                • Anotaciones descriptivas del incidente<br />
                • Firma del técnico (obligatoria)<br />
                • Evidencia del usuario que se niega (foto/archivo)<br />
                • Segunda firma opcional
              </p>
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {formData.is_incident && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-lg font-medium text-red-900 mb-4">
              Documentación Especial de Situaciones Problemáticas
            </h3>
            <div>
              <label
                htmlFor="incident_notes"
                className="block text-sm font-medium text-red-700"
              >
                Notas del Incidente
              </label>
              <textarea
                id="incident_notes"
                name="incident_notes"
                rows={4}
                className="mt-1 block w-full border-red-300 rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 sm:text-sm text-black"
                value={formData.incident_notes}
                onChange={handleInputChange}
                placeholder="Describa la situación problemática, razones por las que no se pudo realizar el mantenimiento, etc."
              />
            </div>
          </div>
        )}

        <div>
          <label
            htmlFor="equipment_type"
            className="block text-sm font-medium text-gray-700"
          >
            Tipo de Equipo
          </label>
          <select
            id="equipment_type"
            name="equipment_type"
            required={!formData.is_incident}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
            value={formData.equipment_type}
            onChange={(e) => handleMaintenanceTypeChange(e.target.value)}
          >
            <option value="computer">Rutina Mantenimiento Preventivo de Equipos de Cómputo</option>
            <option value="printer_scanner">Rutina de Mantenimiento Preventivo para Impresoras y Escáner</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Ubicación</label>
            <CascadingLocationSelect
              sedeId={formData.sede_rel}
              dependenciaId={formData.dependencia_rel}
              subdependenciaId={formData.subdependencia}
              onSedeChange={handleSedeChange}
              onDependenciaChange={handleDependenciaChange}
              onSubdependenciaChange={handleSubdependenciaChange}
              required={!formData.is_incident}
              disabled={false}
              showSubdependencia={true}
            />
          </div>

          <div>
            <label
              htmlFor="placa"
              className="block text-sm font-medium text-gray-700"
            >
              Placa {formData.maintenance_type === 'computer' ? '(Torre)' : ''}
            </label>
            <input
              type="text"
              id="placa"
              name="placa"
              required={!formData.is_incident}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.placa}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <label
              htmlFor="scheduled_date"
              className="block text-sm font-medium text-gray-700"
            >
              Fecha de Mantenimiento
            </label>
            <input
              type="date"
              id="scheduled_date"
              name="scheduled_date"
              required={!formData.is_incident}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.scheduled_date}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <label
              htmlFor="hora_inicio"
              className="block text-sm font-medium text-gray-700"
            >
              Hora Inicio
            </label>
            <input
              type="time"
              id="hora_inicio"
              name="hora_inicio"
              required={!formData.is_incident}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.hora_inicio}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <label
              htmlFor="hora_final"
              className="block text-sm font-medium text-gray-700"
            >
              Hora Final
            </label>
            <input
              type="time"
              id="hora_final"
              name="hora_final"
              required={!formData.is_incident}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.hora_final}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <label
              htmlFor="performed_by"
              className="block text-sm font-medium text-gray-700"
            >
              Realizado por
            </label>
            <input
              type="text"
              id="performed_by"
              name="performed_by"
              required={!formData.is_incident}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.performed_by}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700"
          >
            {formData.is_incident ? "Anotaciones descriptivas del incidente" : "Descripción"}
          </label>
          <textarea
            id="description"
            name="description"
            rows={3}
            required
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
            value={formData.description}
            onChange={handleInputChange}
            placeholder={formData.is_incident ? "Describa detalladamente el incidente y las razones por las que no se pudo realizar el mantenimiento" : ""}
          />
        </div>

        {!formData.is_incident && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {formData.equipment_type === 'computer' ? 'RUTINA DE HARDWARE' : 'RUTINA DE ESCÁNER'}
            </h3>
            <div className="space-y-2">
              {currentActivities.slice(0, formData.equipment_type === 'computer' ? 7 : 4).map((activity) => (
                <div key={activity} className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700 flex-1">{activity}</span>
                  <div className="flex space-x-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name={`activity-${activity}`}
                        value="true"
                        checked={formData.activities[activity] === true}
                        onChange={() => handleActivityChange(activity, true)}
                        className="mr-1"
                      />
                      SI
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name={`activity-${activity}`}
                        value="null"
                        checked={formData.activities[activity] === null}
                        onChange={() => handleActivityChange(activity, null)}
                        className="mr-1"
                      />
                      N.A.
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {formData.equipment_type === 'computer' && !formData.is_incident && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              RUTINA DE SOFTWARE
            </h3>
            <div className="space-y-2">
              {computerActivities.slice(7).map((activity) => (
                <div key={activity} className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700 flex-1">{activity}</span>
                  <div className="flex space-x-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name={`activity-${activity}`}
                        value="true"
                        checked={formData.activities[activity] === true}
                        onChange={() => handleActivityChange(activity, true)}
                        className="mr-1"
                      />
                      SI
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name={`activity-${activity}`}
                        value="null"
                        checked={formData.activities[activity] === null}
                        onChange={() => handleActivityChange(activity, null)}
                        className="mr-1"
                      />
                      N.A. / NO
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {formData.equipment_type === 'printer_scanner' && !formData.is_incident && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              RUTINA DE IMPRESORAS
            </h3>
            <div className="space-y-2">
              {printerScannerActivities.slice(4).map((activity) => (
                <div key={activity} className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700 flex-1">{activity}</span>
                  <div className="flex space-x-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name={`activity-${activity}`}
                        value="true"
                        checked={formData.activities[activity] === true}
                        onChange={() => handleActivityChange(activity, true)}
                        className="mr-1"
                      />
                      SI
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name={`activity-${activity}`}
                        value="null"
                        checked={formData.activities[activity] === null}
                        onChange={() => handleActivityChange(activity, null)}
                        className="mr-1"
                      />
                      N.A.
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="observaciones_generales"
              className="block text-sm font-medium text-gray-700"
            >
              Observaciones Generales
            </label>
            <textarea
              id="observaciones_generales"
              name="observaciones_generales"
              rows={3}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.observaciones_generales}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <label
              htmlFor="observaciones_seguridad"
              className="block text-sm font-medium text-gray-700"
            >
              Observaciones Seguridad de la Información
            </label>
            <textarea
              id="observaciones_seguridad"
              name="observaciones_seguridad"
              rows={3}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.observaciones_seguridad}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="calificacion_servicio"
              className="block text-sm font-medium text-gray-700"
            >
              Cómo califica el servicio
            </label>
            <select
              id="calificacion_servicio"
              name="calificacion_servicio"
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.calificacion_servicio}
              onChange={handleInputChange}
            >
              <option value="">Seleccionar...</option>
              <option value="excelente">Excelente</option>
              <option value="bueno">Bueno</option>
              <option value="regular">Regular</option>
              <option value="malo">Malo</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="observaciones_usuario"
              className="block text-sm font-medium text-gray-700"
            >
              Observaciones del usuario
            </label>
            <textarea
              id="observaciones_usuario"
              name="observaciones_usuario"
              rows={3}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              value={formData.observaciones_usuario}
              onChange={handleInputChange}
            />
          </div>
        </div>



        <div>
          <label htmlFor="photo-upload" className="block text-sm font-medium text-gray-700">
            Fotos (máximo 5, 5MB cada una)
          </label>
          <input
            id="photo-upload"
            type="file"
            multiple
            accept="image/*"
            onChange={handlePhotoChange}
            aria-label="Subir fotos del mantenimiento"
            className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
          {photos.length > 0 && (
            <div className="mt-2 space-y-2">
              {photos.map((photo, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{photo.name}</span>
                  <button
                    type="button"
                    onClick={() => removePhoto(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Eliminar
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Firma Digital del Técnico
          </label>
          <div className="border border-gray-300 rounded-md p-4">
            <SignaturePad
              ref={sigPadRef}
              canvasProps={{
                className: "w-full h-32 border border-gray-200 rounded",
              }}
            />
            <div className="mt-2 flex space-x-2">
              <button
                type="button"
                onClick={saveSignature}
                className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              >
                Guardar Firma
              </button>
              <button
                type="button"
                onClick={clearSignature}
                className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>

        {formData.is_incident && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Segunda Firma (Opcional)
            </label>
            <div className="border border-gray-300 rounded-md p-4">
              <SignaturePad
                ref={secondSigPadRef}
                canvasProps={{
                  className: "w-full h-32 border border-gray-200 rounded",
                }}
              />
              <div className="mt-2 flex space-x-2">
                <button
                  type="button"
                  onClick={saveSecondSignature}
                  className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Guardar Firma
                </button>
                <button
                  type="button"
                  onClick={clearSecondSignature}
                  className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Limpiar
                </button>
              </div>
            </div>
          </div>
        )}

        {error && <div className="text-red-600 text-sm">{error}</div>}

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? "Creando..." : "Crear Mantenimiento"}
        </button>
      </form>
    </div>
  );
}
