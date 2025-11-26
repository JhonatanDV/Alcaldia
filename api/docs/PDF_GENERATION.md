# Generación de Reportes PDF - Manual de Usuario

## Descripción General

El sistema permite generar reportes PDF profesionales de los mantenimientos realizados. Los reportes incluyen:

- Información detallada del equipo
- Datos del mantenimiento (fecha, hora, técnico)
- Descripción del trabajo realizado
- Actividades realizadas
- Observaciones (generales, de seguridad, del usuario)
- Fotografías del mantenimiento
- Firmas del técnico y usuario

## Componentes del Sistema

### Backend (Django)

#### 1. Modelo de Reporte (`api/models.py`)

```python
class Report(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    pdf_file = models.FileField(upload_to='maintenance_reports/', blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
```

#### 2. Generador de PDF (`api/reports.py`)

La clase `MaintenanceReportPDF` genera PDFs usando ReportLab con las siguientes secciones:

- **Encabezado**: Logo, título, información del municipio
- **Información del Equipo**: Código, nombre, ubicación
- **Información del Mantenimiento**: Fecha programada, hora inicio/fin, técnico, calificación
- **Descripción del Trabajo**: Descripción general y actividades realizadas
- **Observaciones**: Generales, de seguridad, del usuario
- **Fotografías**: Imágenes del mantenimiento
- **Firmas**: Firma del técnico y segunda firma (si aplica)
- **Pie de página**: Número de página

#### 3. Endpoint de Generación (`api/views.py`)

**URL**: `POST /api/reports/generate/`

**Autenticación**: JWT Token (Admin o Técnico)

**Request Body**:
```json
{
  "maintenance_id": 123
}
```

**Response (201 Created)**:
```json
{
  "id": 45,
  "pdf_file": "http://localhost:8000/media/maintenance_reports/reporte_mantenimiento_123_20240115_143522.pdf",
  "title": "Reporte de Mantenimiento - EQ-001",
  "generated_at": "2024-01-15T14:35:22.123456Z"
}
```

**Response (400 Bad Request)**:
```json
{
  "error": "maintenance_id es requerido"
}
```

**Response (404 Not Found)**:
```json
{
  "error": "Mantenimiento no encontrado"
}
```

### Frontend (Next.js/React)

#### 1. Componente Reutilizable (`MaintenancePDFGenerator.tsx`)

Componente standalone para generar PDFs desde cualquier vista:

```tsx
import MaintenancePDFGenerator from '@/components/MaintenancePDFGenerator';

<MaintenancePDFGenerator
  maintenanceId={123}
  token={token}
  buttonText="Generar Reporte PDF"
  className="w-full"
/>
```

**Props**:
- `maintenanceId` (number, requerido): ID del mantenimiento
- `token` (string, requerido): JWT token de autenticación
- `buttonText` (string, opcional): Texto del botón (default: "Generar Reporte PDF")
- `className` (string, opcional): Clases CSS adicionales

**Características**:
- Muestra spinner de carga durante la generación
- Mensajes de error y éxito automáticos
- Abre el PDF en nueva pestaña automáticamente
- Auto-limpieza de mensajes después de 3-5 segundos

#### 2. Integración en Dashboard (`dashboard/page.tsx`)

En la tabla de "Últimos 5 Mantenimientos" se agregó un botón inline que:

1. Llama al endpoint `/api/reports/generate/`
2. Envía el `maintenance_id` del mantenimiento seleccionado
3. Recibe la URL del PDF generado
4. Abre el PDF en una nueva pestaña del navegador

```tsx
<button
  onClick={async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
      const response = await axios.post(
        `${API_URL}/api/reports/generate/`,
        { maintenance_id: maint.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.pdf_file) {
        const pdfUrl = response.data.pdf_file.startsWith('http') 
          ? response.data.pdf_file 
          : `${API_URL}${response.data.pdf_file}`;
        window.open(pdfUrl, '_blank');
      }
    } catch (error) {
      console.error('Error generando PDF:', error);
      alert('Error al generar el reporte PDF');
    }
  }}
  className="px-3 py-1 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
>
  Generar PDF
</button>
```

## Uso del Sistema

### 1. Desde el Dashboard (Admin/Técnico)

1. Navegar a `/dashboard`
2. Buscar la sección "Últimos 5 Mantenimientos"
3. Localizar el mantenimiento deseado
4. Hacer clic en el botón "Generar PDF" en la columna "Acciones"
5. El PDF se generará y se abrirá automáticamente en una nueva pestaña

### 2. Desde Vistas Personalizadas (Usando el Componente)

Para integrar la generación de PDFs en cualquier otra vista:

```tsx
'use client';

import { useEffect, useState } from 'react';
import MaintenancePDFGenerator from '@/components/MaintenancePDFGenerator';

export default function MyCustomPage() {
  const [token, setToken] = useState('');
  const [maintenanceId, setMaintenanceId] = useState(null);

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    setToken(accessToken || '');
  }, []);

  return (
    <div>
      {maintenanceId && token && (
        <MaintenancePDFGenerator
          maintenanceId={maintenanceId}
          token={token}
          buttonText="Descargar Reporte"
          className="mt-4"
        />
      )}
    </div>
  );
}
```

## Estructura del PDF Generado

El PDF tiene el siguiente formato:

### Encabezado (todas las páginas)
- Logo de la alcaldía (si existe en `/media/logo.png`)
- Título: "REPORTE DE MANTENIMIENTO"
- Subtítulo: "ALCALDÍA MUNICIPAL DE [NOMBRE]"

### Cuerpo del Documento

#### 1. Información del Equipo
| Campo | Valor |
|-------|-------|
| Código | equipment.code |
| Nombre | equipment.name |
| Ubicación | equipment.location |

#### 2. Información del Mantenimiento
| Campo | Valor |
|-------|-------|
| Fecha Programada | maintenance.scheduled_date |
| Hora de Inicio | maintenance.hora_inicio |
| Hora Final | maintenance.hora_final |
| Técnico | maintenance.technician |
| Calificación del Servicio | maintenance.calificacion_servicio |

#### 3. Descripción del Trabajo Realizado
- **Descripción**: maintenance.description
- **Actividades Realizadas**: Lista de actividades desde el campo JSON `activities`

#### 4. Observaciones
- **Observaciones Generales**: maintenance.observaciones_generales
- **Observaciones de Seguridad**: maintenance.observaciones_seguridad
- **Observaciones del Usuario**: maintenance.observaciones_usuario

#### 5. Fotografías
- Hasta 6 fotografías por página
- Tamaño ajustado automáticamente
- Muestra foto del mantenimiento

#### 6. Firmas
- **Firma del Técnico**: maintenance.signatures (primera firma)
- **Segunda Firma**: maintenance.second_signatures (si existe)

### Pie de Página (todas las páginas)
- "Página X de Y"

## Campos del Modelo Maintenance Utilizados

```python
maintenance.equipment.code          # Código del equipo
maintenance.equipment.name          # Nombre del equipo
maintenance.equipment.location      # Ubicación
maintenance.scheduled_date          # Fecha programada
maintenance.hora_inicio             # Hora de inicio
maintenance.hora_final              # Hora final
maintenance.technician              # Técnico responsable
maintenance.calificacion_servicio   # Calificación (1-5)
maintenance.description             # Descripción del trabajo
maintenance.activities              # JSON con actividades
maintenance.observaciones_generales # Observaciones generales
maintenance.observaciones_seguridad # Observaciones de seguridad
maintenance.observaciones_usuario   # Observaciones del usuario
maintenance.photos.all()            # Fotos del mantenimiento
maintenance.signatures.first()      # Primera firma
maintenance.second_signatures.first() # Segunda firma
```

## Permisos Requeridos

Para generar reportes PDF, el usuario debe:

1. Estar autenticado (token JWT válido)
2. Tener rol de **Admin** o **Técnico** (`IsAdminOrTechnician`)

Los usuarios sin permisos recibirán un error 403 (Forbidden).

## Manejo de Errores

### Frontend

El componente maneja automáticamente:
- **401 Unauthorized**: Token inválido o expirado
- **403 Forbidden**: Usuario sin permisos
- **404 Not Found**: Mantenimiento no existe
- **500 Internal Server Error**: Error en la generación del PDF

Los mensajes de error se muestran automáticamente al usuario.

### Backend

Errores capturados:
- `Maintenance.DoesNotExist`: Retorna 404
- Excepciones de generación de PDF: Retorna 500 con traceback en logs
- Validaciones de entrada: Retorna 400

## Ejemplo Completo de Flujo

1. **Usuario accede al dashboard**
   ```
   GET /dashboard
   ```

2. **Sistema carga mantenimientos recientes**
   ```
   GET /api/dashboard/recent-activity/
   ```

3. **Usuario hace clic en "Generar PDF"**
   ```
   POST /api/reports/generate/
   {
     "maintenance_id": 123
   }
   ```

4. **Backend procesa la solicitud**
   - Valida el token JWT
   - Verifica permisos del usuario
   - Obtiene el mantenimiento de la BD
   - Genera el PDF usando ReportLab
   - Guarda el archivo en media/maintenance_reports/
   - Crea el registro en la tabla Report
   - Retorna la URL del PDF

5. **Frontend abre el PDF**
   ```javascript
   window.open(pdfUrl, '_blank');
   ```

6. **Usuario visualiza/descarga el PDF**

## Archivos Modificados

### Backend
- `api/models.py`: Modelo Report actualizado
- `api/reports.py`: Clase MaintenanceReportPDF actualizada con nuevos campos
- `api/views.py`: ReportGenerateView actualizado para usar maintenance_id
- `core/urls.py`: Ruta ya configurada en `path('api/reports/generate/', ...)`

### Frontend
- `frontend/src/components/MaintenancePDFGenerator.tsx`: Nuevo componente
- `frontend/src/components/ReportDownloader.tsx`: Actualizado para usar maintenance_id
- `frontend/src/app/dashboard/page.tsx`: Agregada columna "Acciones" con botón

## Próximos Pasos / Mejoras Futuras

1. **Generación masiva de PDFs**: Permitir seleccionar múltiples mantenimientos y generar un ZIP
2. **Plantillas personalizables**: Permitir a los admins personalizar el formato del PDF
3. **Envío por email**: Enviar el PDF generado por correo electrónico
4. **Firma digital**: Integrar firma digital en los PDFs
5. **Historial de reportes**: Vista para ver todos los reportes generados
6. **Filtros avanzados**: Filtrar reportes por fecha, equipo, técnico, etc.
7. **Preview del PDF**: Vista previa antes de generar
8. **Marca de agua**: Agregar marca de agua o QR code con información del reporte

## Soporte y Troubleshooting

### El PDF no se genera

1. Verificar que el mantenimiento existe en la BD
2. Revisar logs del backend para errores de ReportLab
3. Verificar que el directorio `media/maintenance_reports/` existe y tiene permisos de escritura
4. Verificar que ReportLab está instalado: `pip install reportlab`

### El PDF se genera pero no se abre

1. Verificar que `MEDIA_URL` y `MEDIA_ROOT` están configurados en settings.py
2. Verificar que el servidor está sirviendo archivos de media
3. Verificar que la URL del PDF es accesible desde el navegador

### Faltan datos en el PDF

1. Verificar que el mantenimiento tiene todos los campos requeridos
2. Revisar la clase MaintenanceReportPDF para asegurar que usa los campos correctos
3. Verificar que las relaciones ForeignKey están correctamente cargadas

## Logs Útiles

Para debugging, revisar:

```bash
# Logs del backend
python manage.py runserver --noreload

# Logs de generación de PDF
# En api/views.py, línea 166-168:
except Exception as e:
    import traceback
    print(f"Error generando reporte: {str(e)}")
    print(traceback.format_exc())
```

## Contacto

Para soporte adicional, contactar al equipo de desarrollo.
