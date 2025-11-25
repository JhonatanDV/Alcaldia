"""
Script para crear datos de prueba para mantenimiento de impresora/escáner.
"""
import os
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Maintenance, Photo, Signature, SecondSignature, Equipment
from django.core.files.base import ContentFile
from datetime import datetime, time
from django.db import models

def create_test_image(text: str, size=(400, 300), bg_color='lightcoral'):
    """Crea una imagen de prueba."""
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, text, fill='white', font=font)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_test_signature(name: str):
    """Crea firma simulada."""
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

# Buscar o crear un equipo tipo impresora
equipment = Equipment.objects.filter(
    models.Q(name__icontains='impresora') | 
    models.Q(name__icontains='printer')
).first()

if not equipment:
    # Crear un equipo de prueba
    from api.models import Sede, Dependencia
    sede = Sede.objects.first()
    
    equipment = Equipment.objects.create(
        name='Impresora HP LaserJet',
        code='IMP-001',
        serial_number='HP123456',
        model='LaserJet Pro M404dn',
        brand='HP',
        location='Oficina Principal',
        sede_rel=sede
    )
    print(f"✓ Creado equipo de prueba: {equipment}")
else:
    print(f"✓ Usando equipo existente: {equipment}")

# Crear o actualizar mantenimiento
maintenance, created = Maintenance.objects.get_or_create(
    equipment=equipment,
    defaults={
        'status': 'completed',
        'description': 'Mantenimiento preventivo impresora'
    }
)

if created:
    print(f"✓ Creado mantenimiento ID {maintenance.id}")
else:
    print(f"✓ Actualizando mantenimiento ID {maintenance.id}")

# Actualizar datos
maintenance.sede = "Sede Central"
maintenance.dependencia = "Administrativo"
maintenance.ubicacion = "Piso 2 - Oficina 201"
maintenance.placa = equipment.code
maintenance.completion_date = datetime.now().date()
maintenance.scheduled_date = datetime.now().date()
maintenance.hora_inicio = time(10, 0)
maintenance.hora_final = time(11, 30)
maintenance.status = 'completed'

# Actividades específicas para impresora
maintenance.activities = {
    # Actividades de impresora
    "Limpiéza de carcaza": True,
    "Limpieza de engranaje": True,
    "Limpieza toner": True,
    "Limpieza de fusor o rodillo": True,
    "Limpiéza tarjeta logica": True,
    "Limpieza tarjeta de poder": False,
    "Limpiéza de sensores": True,
    "Alineacion de  rodillos alimentación de": True,
    "Configuracion del Equipo": True,
    "Pruebas de funcionamiento": True,
    "Limpieza de correas dentadas o guias": {"si": True, "na": False},
    "Limpieza de Ventiladores": {"si": True, "na": False},
    
    # Si es multifuncional, actividades de escáner
    "Limpieza general": True,
    "Alineacion de Papel": True,
}

maintenance.observaciones_generales = "Mantenimiento preventivo completo. Se realizó limpieza profunda de todos los componentes. Toner al 60%. Equipo funcionando correctamente."
maintenance.observaciones_seguridad = "Se verificó configuración de red y accesos. Firmware actualizado."
maintenance.calificacion_servicio = "excelente"

# Técnico
if maintenance.technician:
    maintenance.elaborado_por = f"{maintenance.technician.first_name} {maintenance.technician.last_name}"
else:
    maintenance.elaborado_por = "Carlos Rodríguez"

maintenance.revisado_por = "Ana Martínez"

maintenance.save()
print("✓ Datos básicos actualizados")

# Limpiar media previa
Photo.objects.filter(maintenance=maintenance).delete()
Signature.objects.filter(maintenance=maintenance).delete()
SecondSignature.objects.filter(maintenance=maintenance).delete()
print("✓ Limpieza de media previa")

# Crear fotos
for i in range(2):
    photo_img = create_test_image(
        f"Foto {i+1}\nImpresora\n{equipment.code}", 
        bg_color=['lightcoral', 'lightpink'][i]
    )
    photo = Photo.objects.create(
        maintenance=maintenance,
        caption=f"Foto del mantenimiento - vista {i+1}"
    )
    photo.photo.save(f"test_printer_{maintenance.id}_{i+1}.png", ContentFile(photo_img.read()), save=True)
    print(f"✓ Foto {i+1} creada: {photo.photo.name}")

# Crear firma técnico
sig_img = create_test_signature(maintenance.elaborado_por)
signature = Signature.objects.create(
    maintenance=maintenance,
    signer_name=maintenance.elaborado_por,
    signer_role="Técnico de Mantenimiento"
)
signature.signature_image.save(f"firma_tecnico_printer_{maintenance.id}.png", ContentFile(sig_img.read()), save=True)
print(f"✓ Firma técnico creada: {signature.signature_image.name}")

# Crear firma usuario
sig2_img = create_test_signature(maintenance.revisado_por)
signature2 = SecondSignature.objects.create(
    maintenance=maintenance,
    signer_name=maintenance.revisado_por,
    signer_role="Usuario del Equipo"
)
signature2.signature_image.save(f"firma_usuario_printer_{maintenance.id}.png", ContentFile(sig2_img.read()), save=True)
print(f"✓ Firma usuario creada: {signature2.signature_image.name}")

print(f"\n✅ Mantenimiento de impresora {maintenance.id} preparado:")
print(f"   - Equipment: {equipment.name} ({equipment.code})")
print(f"   - Photos: {maintenance.photos.count()}")
print(f"   - Signatures: {maintenance.signatures.count() + SecondSignature.objects.filter(maintenance=maintenance).count()}")
print(f"   - Activities: {len(maintenance.activities)}")
print(f"   - Status: {maintenance.status}")
print(f"\nAhora ejecuta: python manage.py generate_printer_scanner_reports --maintenance-id {maintenance.id}")
