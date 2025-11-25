from api.models import Maintenance, Photo, Signature

# Buscar mantenimientos completados con media
maintenances = Maintenance.objects.filter(
    equipment__equipment_type='computer', 
    status='completed'
).prefetch_related('photos', 'signatures')[:5]

for m in maintenances:
    photos = m.photos.all()
    sigs = m.signatures.all()
    print(f'\n=== Maintenance ID {m.id} - Equipment: {m.equipment.code} ===')
    print(f'Photos: {photos.count()}')
    for p in photos:
        print(f'  - Photo {p.id}: {p.image.name if p.image else "No file"}')
    print(f'Signatures: {sigs.count()}')
    for s in sigs:
        print(f'  - Signature {s.id}: {s.image.name if s.image else "No file"} (signer: {s.signer_name})')
    
    # Verificar second_signature
    try:
        second_sig = m.second_signature
        print(f'Second signature: {second_sig.image.name if second_sig and second_sig.image else "None"}')
    except:
        print('Second signature: None')
