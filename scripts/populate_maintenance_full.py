"""
Script para crear datos de prueba completos en un mantenimiento:
- Actividades completas (hardware y software)
- Fotos de mantenimiento
- Firmas (técnico y usuario)
- Todos los campos del formulario
"""
import os
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Maintenance, Photo, Signature
from django.core.files.base import ContentFile
from datetime import datetime, time

def create_test_image(text: str, size=(400, 300), bg_color='lightblue'):
    """Crea una imagen de prueba con texto."""
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Intentar usar font, si no disponible usar default
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Centrar texto
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, text, fill='black', font=font)
    
    # Guardar a bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_test_signature(name: str):
    """Crea una imagen de firma simulada."""
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 30), name, fill='blue', font=font)
    draw.line([(20, 70), (280, 70)], fill='blue', width=2)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

# Obtener o crear mantenimiento de prueba
maintenance_id = 3
maintenance = Maintenance.objects.get(id=maintenance_id)

print(f"Preparando mantenimiento ID {maintenance_id}...")

# Actualizar datos básicos
maintenance.sede = "Sede Principal"
maintenance.dependencia = "Sistemas"
maintenance.ubicacion = "Oficina 301"
maintenance.placa = maintenance.equipment.code or "EQ-TEST-001"
maintenance.completion_date = datetime.now().date()
maintenance.scheduled_date = datetime.now().date()
maintenance.hora_inicio = time(9, 0)
maintenance.hora_final = time(11, 30)
maintenance.status = 'completed'

# Actividades completas (hardware y software)
maintenance.activities = {
    # Hardware
    "limpieza": True,
    "Limpieza interna de la torre": True,
    "Limpieza del teclado": True,
    "Limpieza del monitor": True,
    "Verificación de cables de poder y de datos": True,
    "Ajuste de tarjetas (Memoria - Video - Red)": True,
    "Lubricación del ventilador de la torre": False,
    "Lubricación del ventilador de la fuente": {"si": False, "na": True},
    "Lubricación del ventilador del procesador": {"si": False, "na": True},
    
    # Software
    "Reinstalar sistema operativo": False,
    "Instalar antivirus": True,
    "Análisis en busca de software malicioso": True,
    "Suspender actualizaciones automáticas S.O.": True,
    "actualizacion": True,
    "Instalar programas esenciales (ofimática, grabador de discos)": True,
    "Configurar usuarios administrador local": True,
    "Modificar contraseña de administrador": True,
    "Configurar nombre equipo": True,
    "Desactivar aplicaciones al inicio de Windows": True,
    "Configurar página de inicio navegador": True,
    "Configurar fondo de pantalla institucional": True,
    "Verificar funcionamiento general": True,
    "revision": True,
    "Limpieza de registros y eliminación de archivos temporales": True,
    "Creación Punto de Restauración": True,
    "Verificar espacio en disco": True,
    "Analizar disco duro": True,
    "El equipo tiene estabilizador": True,
    "El escritorio está limpio": True,
    "El usuario de Windows tiene contraseña": True,
}

maintenance.observaciones_generales = "Mantenimiento preventivo completo. Se realizó limpieza profunda y optimización del sistema operativo. Equipo funcionando correctamente."
maintenance.observaciones_seguridad = "Se verificó antivirus actualizado y políticas de seguridad aplicadas. Contraseñas configuradas correctamente."
maintenance.observaciones_usuario = "Equipo entregado en óptimas condiciones."
maintenance.calificacion_servicio = "excelente"
maintenance.incident_notes = "Sin incidentes reportados durante el mantenimiento."

# Técnico
if maintenance.technician:
    maintenance.elaborado_por = f"{maintenance.technician.first_name} {maintenance.technician.last_name}"
else:
    maintenance.elaborado_por = "Juan Pérez"

maintenance.revisado_por = "María González"

maintenance.save()
print("✓ Datos básicos actualizados")

# Limpiar fotos y firmas existentes
Photo.objects.filter(maintenance=maintenance).delete()
Signature.objects.filter(maintenance=maintenance).delete()
print("✓ Limpieza de media previa")

# Crear fotos de prueba
for i in range(3):
    photo_img = create_test_image(f"Foto {i+1}\nMantenimiento\nEquipo {maintenance.equipment.code}", 
                                   bg_color=['lightblue', 'lightgreen', 'lightyellow'][i])
    photo = Photo.objects.create(
        maintenance=maintenance,
        caption=f"Foto de prueba {i+1} del mantenimiento"
    )
    photo.photo.save(f"test_photo_{maintenance.id}_{i+1}.png", ContentFile(photo_img.read()), save=True)
    print(f"✓ Foto {i+1} creada: {photo.photo.name}")

# Crear firma del técnico
sig_img = create_test_signature(maintenance.elaborado_por)
signature = Signature.objects.create(
    maintenance=maintenance,
    signer_name=maintenance.elaborado_por,
    signer_role="Técnico de Mantenimiento"
)
signature.signature_image.save(f"firma_tecnico_{maintenance.id}.png", ContentFile(sig_img.read()), save=True)
print(f"✓ Firma técnico creada: {signature.signature_image.name}")

# Crear segunda firma (usuario)
from api.models import SecondSignature
sig2_img = create_test_signature(maintenance.revisado_por)
signature2 = SecondSignature.objects.create(
    maintenance=maintenance,
    signer_name=maintenance.revisado_por,
    signer_role="Usuario del Equipo"
)
signature2.signature_image.save(f"firma_usuario_{maintenance.id}.png", ContentFile(sig2_img.read()), save=True)
print(f"✓ Firma usuario creada: {signature2.signature_image.name}")

print(f"\n✅ Mantenimiento {maintenance.id} preparado con datos completos:")
print(f"   - Photos: {maintenance.photos.count()}")
print(f"   - Signatures: {maintenance.signatures.count()}")
print(f"   - Activities: {len(maintenance.activities)} actividades")
print(f"   - Status: {maintenance.status}")
print(f"\nAhora ejecuta: python manage.py generate_rutinas_excel --maintenance-id {maintenance.id}")
