import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.services import generate_equipment_report
from api.models import Equipment, Maintenance
from django.contrib.auth.models import User

try:
    # Get data
    equipment = Equipment.objects.first()
    maintenance = Maintenance.objects.first()
    user = User.objects.first()
    
    if not equipment or not maintenance or not user:
        print("❌ No hay datos de prueba disponibles")
    else:
        print(f"✓ Equipo: {equipment.code} - {equipment.name}")
        print(f"✓ Mantenimiento: {maintenance.id} - {maintenance.maintenance_date}")
        print(f"✓ Usuario: {user.username}")
        print(f"✓ Fotos: {maintenance.photos.count()}")
        print(f"✓ Firma: {'Sí' if hasattr(maintenance, 'signature') else 'No'}")
        
        # Generate report
        print("\nGenerando reporte PDF...")
        report = generate_equipment_report(
            equipment_id=equipment.id,
            start_date=maintenance.maintenance_date,
            end_date=maintenance.maintenance_date,
            user=user
        )
        
        print(f"\n✓ Reporte PDF generado exitosamente!")
        print(f"  ID: {report.id}")
        print(f"  PDF URL: {report.pdf_file.url}")
        print(f"  Tamaño: {report.file_size} bytes")
        print(f"\n✓ El PDF se guardó en MinIO")
        print(f"  Bucket: maintenance-reports")
        
except Exception as e:
    print(f"\n❌ Error:")
    print(f"  {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
