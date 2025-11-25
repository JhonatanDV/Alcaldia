from api.models import Maintenance
from decimal import Decimal


def _format_field_for_template(value, empty='N/A', bool_labels=('Sí', 'No')):
    """Format a value for template rendering:
    - booleans -> 'Sí'/'No'
    - None or empty string -> 'N/A' (or provided empty)
    - Decimals -> formatted string
    - otherwise return str(value)
    """
    try:
        if isinstance(value, bool):
            return bool_labels[0] if value else bool_labels[1]
        if value is None:
            return empty
        if isinstance(value, str):
            s = value.strip()
            return s if s != '' else empty
        if isinstance(value, Decimal):
            return f"{value:,.2f}"
        # For numbers
        if isinstance(value, (int, float)):
            return str(value)
        # Fallback: return original (useful for lists/dicts)
        return value
    except Exception:
        return value


def serialize_maintenance(maintenance_id: int) -> dict:
    m = Maintenance.objects.select_related('equipment', 'technician', 'sede_rel', 'dependencia_rel').filter(id=maintenance_id).first()
    if not m:
        raise Maintenance.DoesNotExist()

    data = {
        'codigo': _format_field_for_template(m.codigo or str(m.id)),
        'description': _format_field_for_template(m.description),
        'maintenance_type': _format_field_for_template(m.get_maintenance_type_display() if m.maintenance_type else None),
        'status': _format_field_for_template(m.get_status_display() if m.status else None),
        'scheduled_date': m.scheduled_date.strftime('%d/%m/%Y') if m.scheduled_date else _format_field_for_template(None),
        'completion_date': m.completion_date.strftime('%d/%m/%Y') if m.completion_date else 'Pendiente',
        'hora_inicio': m.hora_inicio.strftime('%H:%M') if m.hora_inicio else _format_field_for_template(''),
        'hora_final': m.hora_final.strftime('%H:%M') if m.hora_final else _format_field_for_template(''),
        'equipment_code': _format_field_for_template(m.equipment.code if m.equipment else None),
        'equipment_name': _format_field_for_template(m.equipment.name if m.equipment else None),
        'equipment_serial': _format_field_for_template(m.equipment.serial_number if m.equipment else None),
        'technician_name': _format_field_for_template((m.technician.get_full_name() if m.technician else None) if hasattr(m, 'technician') else None),
        'technician_email': _format_field_for_template(m.technician.email if getattr(m, 'technician', None) else None),
        'sede': _format_field_for_template(m.sede or (m.sede_rel.nombre if getattr(m, 'sede_rel', None) else None)),
        'dependencia': _format_field_for_template(m.dependencia or (m.dependencia_rel.nombre if getattr(m, 'dependencia_rel', None) else None)),
        'subdependencia': _format_field_for_template(getattr(m, 'subdependencia', None) and getattr(m.subdependencia, 'nombre', None) or None),
        'ubicacion': _format_field_for_template(m.ubicacion),
        'oficina': _format_field_for_template(m.oficina),
        'observations': _format_field_for_template(m.observations),
        'observaciones_generales': _format_field_for_template(m.observaciones_generales),
        'observaciones_seguridad': _format_field_for_template(m.observaciones_seguridad),
        'activities': m.activities if m.activities else [],
        'elaborado_por': _format_field_for_template(m.elaborado_por),
        'revisado_por': _format_field_for_template(m.revisado_por),
        'aprobado_por': _format_field_for_template(m.aprobado_por),
        'cost': f"${m.cost:,.2f}" if m.cost else _format_field_for_template(None),
        'version': _format_field_for_template(m.version or '1.0'),
        'is_incident': _format_field_for_template(getattr(m, 'is_incident', None)),
        'incident_notes': _format_field_for_template(getattr(m, 'incident_notes', None)),
        'equipment_type': _format_field_for_template(getattr(m, 'equipment_type', None)),
    }

    return data
