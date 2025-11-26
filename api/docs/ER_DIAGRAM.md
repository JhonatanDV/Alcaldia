# ER Diagram - Equipment Maintenance API

## Entities and Relationships

### Equipment
- **Attributes**: id (PK), code (unique), name, location, created_at
- **Relationships**: 1:N with Maintenance

### Maintenance
- **Attributes**: id (PK), equipment_id (FK), description, maintenance_date, performed_by, created_at, updated_at
- **Relationships**: N:1 with Equipment, 1:N with Photo

### Photo
- **Attributes**: id (PK), maintenance_id (FK), image (file), uploaded_at
- **Relationships**: N:1 with Maintenance

## Diagram (Text Representation)

```
Equipment (1) -----> (N) Maintenance (1) -----> (N) Photo
    |                       |                       |
    +-- code                +-- description        +-- image
    +-- name                 +-- maintenance_date   +-- uploaded_at
    +-- location             +-- performed_by
    +-- created_at           +-- created_at
                            +-- updated_at
```

## Notes
- All relationships are CASCADE on delete.
- Photos are uploaded to 'maintenance_photos/' directory.
- Maintenance dates are stored as DateField (no time).
