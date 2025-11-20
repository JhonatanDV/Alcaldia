"use client";

import { useState, useEffect } from "react";
import axios from "axios";

interface Photo {
  id: number;
  image: string;
  thumbnail: string;
  uploaded_at: string;
  maintenance: number;
  maintenance_details?: Maintenance;
}

interface Maintenance {
  id: number;
  description: string;
  maintenance_date: string;
  performed_by: string;
  maintenance_type: string;
  sede?: string;
  dependencia?: string;
  oficina?: string;
  equipment: {
    id: number;
    code: string;
    name: string;
  };
}

interface PhotoGalleryProps {
  token: string;
  userRole: 'admin' | 'technician' | null;
}

export default function PhotoGallery({ token, userRole }: PhotoGalleryProps) {
  const [photos, setPhotos] = useState<(Photo & { maintenance_details?: Maintenance })[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<string>("");
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedSection, setSelectedSection] = useState<string>("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [equipments, setEquipments] = useState<{id: number, code: string, name: string}[]>([]);
  const [sections, setSections] = useState<string[]>([]);

  // Restrict access to admin users only
  if (userRole !== 'admin') {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 text-lg font-semibold">Acceso Denegado</div>
        <p className="text-gray-600 mt-2">Solo los administradores pueden acceder a la galería de fotos.</p>
      </div>
    );
  }

  useEffect(() => {
    fetchEquipments();
    fetchPhotos();
  }, []);

  const fetchEquipments = async () => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      
      // Fetch all equipments handling pagination
      let allEquipments: any[] = [];
      let nextUrl: string | null = "http://127.0.0.1:8000/api/equipments/?page_size=1000";
      
      while (nextUrl) {
        const response: any = await axios.get(nextUrl, { headers });
        
        // Check if response is paginated or direct array
        if (response.data.results) {
          allEquipments = [...allEquipments, ...response.data.results];
          nextUrl = response.data.next;
        } else if (Array.isArray(response.data)) {
          allEquipments = response.data;
          nextUrl = null;
        } else {
          throw new Error('Formato de respuesta inesperado');
        }
      }
      
      setEquipments(allEquipments.map((eq: any) => ({ id: eq.id, code: eq.code, name: eq.name })));
    } catch (err) {
      console.error("Error al cargar equipos:", err);
    }
  };

  const fetchPhotos = async () => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      
      // Fetch all maintenances handling pagination
      let allMaintenances: any[] = [];
      let nextUrl: string | null = "http://127.0.0.1:8000/api/maintenances/?page_size=1000";
      
      while (nextUrl) {
        const response: any = await axios.get(nextUrl, { headers });
        
        // Check if response is paginated or direct array
        if (response.data.results) {
          allMaintenances = [...allMaintenances, ...response.data.results];
          nextUrl = response.data.next;
        } else if (Array.isArray(response.data)) {
          allMaintenances = response.data;
          nextUrl = null;
        } else {
          throw new Error('Formato de respuesta inesperado');
        }
      }

      const allPhotos: (Photo & { maintenance_details?: Maintenance })[] = [];
      const uniqueSections = new Set<string>();

      // Collect all photos from maintenances
      allMaintenances.forEach((maintenance: Maintenance & { photos: Photo[] }) => {
        if (maintenance.photos && maintenance.photos.length > 0) {
          maintenance.photos.forEach((photo) => {
            allPhotos.push({
              ...photo,
              maintenance_details: {
                id: maintenance.id,
                description: maintenance.description,
                maintenance_date: maintenance.maintenance_date,
                performed_by: maintenance.performed_by,
                maintenance_type: maintenance.maintenance_type,
                sede: maintenance.sede,
                dependencia: maintenance.dependencia,
                oficina: maintenance.oficina,
                equipment: maintenance.equipment,
              },
            });
          });
        }

        // Collect unique sections
        if (maintenance.oficina) uniqueSections.add(maintenance.oficina);
        if (maintenance.dependencia) uniqueSections.add(maintenance.dependencia);
        if (maintenance.sede) uniqueSections.add(maintenance.sede);
      });

      // Sort by upload date (newest first)
      allPhotos.sort((a, b) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime());

      setPhotos(allPhotos);
      setSections(Array.from(uniqueSections).sort());
    } catch (err) {
      setError("Error al cargar fotos");
    } finally {
      setLoading(false);
    }
  };

  const openModal = (photo: Photo) => {
    setSelectedPhoto(photo);
  };

  const closeModal = () => {
    setSelectedPhoto(null);
  };

  // Filter photos based on selected filters
  const filteredPhotos = photos.filter((photo) => {
    const matchesEquipment = !selectedEquipment || String(photo.maintenance_details?.equipment?.id) === selectedEquipment;
    const matchesDate = !selectedDate || (photo.maintenance_details?.maintenance_date && photo.maintenance_details.maintenance_date.split('T')[0] === selectedDate);
    const matchesSection = !selectedSection || (
      photo.maintenance_details?.sede === selectedSection ||
      photo.maintenance_details?.dependencia === selectedSection ||
      photo.maintenance_details?.oficina === selectedSection
    );
    const matchesType = !selectedType || photo.maintenance_details?.maintenance_type === selectedType;
    return matchesEquipment && matchesDate && matchesSection && matchesType;
  });

  if (loading) {
    return <div className="text-center py-8">Cargando fotos...</div>;
  }

  if (error) {
    return <div className="text-red-600 text-center py-8">{error}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Galería de Fotos</h2>
        <span className="text-sm text-gray-600">{filteredPhotos.length} foto(s)</span>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow-sm border space-y-4">
        <h3 className="text-sm font-medium text-gray-700">Filtros</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label htmlFor="equipment-filter" className="block text-sm font-medium text-gray-700">
              Equipo
            </label>
            <select
              id="equipment-filter"
              value={selectedEquipment}
              onChange={(e) => setSelectedEquipment(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Todos los equipos</option>
              {equipments.map((equipment) => (
                <option key={equipment.id} value={equipment.id.toString()}>
                  {equipment.code} - {equipment.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="date-filter" className="block text-sm font-medium text-gray-700">
              Fecha de Mantenimiento
            </label>
              <input
                type="date"
                id="date-filter"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
              />
          </div>
          <div>
            <label htmlFor="section-filter" className="block text-sm font-medium text-gray-700">
              Sección
            </label>
            <select
              id="section-filter"
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Todas las secciones</option>
              {sections.map((section) => (
                <option key={section} value={section}>
                  {section}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700">
              Tipo de Mantenimiento
            </label>
            <select
              id="type-filter"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Todos los tipos</option>
              <option value="computer">Equipos de Cómputo</option>
              <option value="printer_scanner">Impresoras y Escáner</option>
            </select>
          </div>
        </div>
      </div>

      {filteredPhotos.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay fotos</h3>
          <p className="mt-1 text-sm text-gray-500">Las fotos de mantenimientos aparecerán aquí.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredPhotos.map((photo) => (
            <div
              key={photo.id}
              className="group relative bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => openModal(photo)}
            >
              <div className="aspect-w-1 aspect-h-1">
                <img
                  src={photo.thumbnail || photo.image}
                  alt={`Foto mantenimiento ${photo.maintenance}`}
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
                />
              </div>
              <div className="p-3">
                <p className="text-xs text-gray-600 truncate">
                  {photo.maintenance_details?.equipment.code} - {photo.maintenance_details?.equipment.name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {photo.maintenance_details?.maintenance_type === 'computer' ? 'Cómputo' : 'Impresora/Escáner'} - {photo.maintenance_details?.oficina || photo.maintenance_details?.dependencia || photo.maintenance_details?.sede || 'Sin sección'}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(photo.uploaded_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal para foto completa */}
      {selectedPhoto && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="p-4 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Foto del Mantenimiento
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedPhoto.maintenance_details?.equipment.code} - {selectedPhoto.maintenance_details?.equipment.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    Tipo: {selectedPhoto.maintenance_details?.maintenance_type === 'computer' ? 'Equipos de Cómputo' : 'Impresoras y Escáner'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Sección: {selectedPhoto.maintenance_details?.oficina || selectedPhoto.maintenance_details?.dependencia || selectedPhoto.maintenance_details?.sede || 'Sin sección'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Realizado por: {selectedPhoto.maintenance_details?.performed_by}
                  </p>
                  <p className="text-sm text-gray-500">
                    Fecha: {new Date(selectedPhoto.maintenance_details?.maintenance_date || '').toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="p-4">
              <img
                src={selectedPhoto.image}
                alt="Foto completa"
                className="w-full h-auto max-h-[60vh] object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
