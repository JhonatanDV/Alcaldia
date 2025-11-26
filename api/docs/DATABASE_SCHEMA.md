# Database Schema - Equipment Maintenance API

## Tables

### api_equipment
- id: INTEGER (PK, Auto)
- code: VARCHAR(50) UNIQUE
- name: VARCHAR(100)
- location: VARCHAR(100) NULL
- created_at: DATETIME

### api_maintenance
- id: INTEGER (PK, Auto)
- equipment_id: INTEGER (FK to api_equipment.id)
- description: TEXT
- maintenance_date: DATE
- performed_by: VARCHAR(100)
- created_at: DATETIME
- updated_at: DATETIME

### api_photo
- id: INTEGER (PK, Auto)
- maintenance_id: INTEGER (FK to api_maintenance.id)
- image: VARCHAR(100) (file path)
- uploaded_at: DATETIME

## Indexes
- api_equipment.code (unique)
- api_maintenance.equipment_id
- api_photo.maintenance_id

## Constraints
- Foreign keys with CASCADE delete
- Unique on equipment.code

## Migrations
Run `python manage.py makemigrations` and `python manage.py migrate` after model changes.
