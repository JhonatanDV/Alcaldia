from api.models import Maintenance


def serialize_maintenance(maintenance_id: int) -> dict:
    m = Maintenance.objects.select_related('equipment', 'technician', 'sede_rel', 'dependencia_rel').filter(id=maintenance_id).first()
    if not m:
        raise Maintenance.DoesNotExist()

    data = {
        'codigo': m.codigo or str(m.id),
        'description': m.description or '',
        'maintenance_type': m.get_maintenance_type_display() if m.maintenance_type else '',
        'status': m.get_status_display() if m.status else '',
        'scheduled_date': m.scheduled_date.strftime('%d/%m/%Y') if m.scheduled_date else 'N/A',
        'completion_date': m.completion_date.strftime('%d/%m/%Y') if m.completion_date else 'Pendiente',
        'hora_inicio': m.hora_inicio.strftime('%H:%M') if m.hora_inicio else '',
        'hora_final': m.hora_final.strftime('%H:%M') if m.hora_final else '',
        'equipment_code': m.equipment.code if m.equipment else 'N/A',
        'equipment_name': m.equipment.name if m.equipment else 'N/A',
        'equipment_serial': m.equipment.serial_number if m.equipment else 'N/A',
        'technician_name': (m.technician.get_full_name() if m.technician else '') if hasattr(m, 'technician') else '',
        'technician_email': m.technician.email if getattr(m, 'technician', None) else '',
        'sede': m.sede or (m.sede_rel.nombre if getattr(m, 'sede_rel', None) else ''),
        'dependencia': m.dependencia or (m.dependencia_rel.nombre if getattr(m, 'dependencia_rel', None) else ''),
        'subdependencia': getattr(m, 'subdependencia', None) and getattr(m.subdependencia, 'nombre', '') or '',
        'ubicacion': m.ubicacion or '',
        'oficina': m.oficina or '',
        'observations': m.observations or '',
        'observaciones_generales': m.observaciones_generales or '',
        'observaciones_seguridad': m.observaciones_seguridad or '',
        'activities': m.activities if m.activities else [],
        'elaborado_por': m.elaborado_por or '',
        'revisado_por': m.revisado_por or '',
        'aprobado_por': m.aprobado_por or '',
        'cost': f"${m.cost:,.2f}" if m.cost else 'N/A',
        'version': m.version or '1.0',
    }

    return data
