"""
Script para agregar manualmente las columnas faltantes a la base de datos.
Ejecutar con: python manage.py shell < fix_database.py
"""

from django.db import connection

def add_missing_columns():
    with connection.cursor() as cursor:
        # Verificar y agregar columnas faltantes en equipment
        print("Agregando columnas a equipment...")
        try:
            cursor.execute("""
                ALTER TABLE equipment 
                ADD COLUMN dependencia_rel_id bigint NULL,
                ADD CONSTRAINT equipment_dependencia_rel_id_fk 
                FOREIGN KEY (dependencia_rel_id) REFERENCES dependencia(id)
            """)
            print("✓ Agregada columna dependencia_rel_id a equipment")
        except Exception as e:
            print(f"⚠ dependencia_rel_id ya existe o error: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE equipment 
                ADD COLUMN sede_rel_id bigint NULL,
                ADD CONSTRAINT equipment_sede_rel_id_fk 
                FOREIGN KEY (sede_rel_id) REFERENCES sede(id)
            """)
            print("✓ Agregada columna sede_rel_id a equipment")
        except Exception as e:
            print(f"⚠ sede_rel_id ya existe o error: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE equipment 
                ADD COLUMN subdependencia_id bigint NULL,
                ADD CONSTRAINT equipment_subdependencia_id_fk 
                FOREIGN KEY (subdependencia_id) REFERENCES subdependencia(id)
            """)
            print("✓ Agregada columna subdependencia_id a equipment")
        except Exception as e:
            print(f"⚠ subdependencia_id ya existe o error: {e}")
        
        # Verificar y agregar columnas faltantes en maintenance
        print("\nAgregando columnas a maintenance...")
        try:
            cursor.execute("""
                ALTER TABLE maintenance 
                ADD COLUMN dependencia_rel_id bigint NULL,
                ADD CONSTRAINT maintenance_dependencia_rel_id_fk 
                FOREIGN KEY (dependencia_rel_id) REFERENCES dependencia(id)
            """)
            print("✓ Agregada columna dependencia_rel_id a maintenance")
        except Exception as e:
            print(f"⚠ dependencia_rel_id ya existe o error: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE maintenance 
                ADD COLUMN sede_rel_id bigint NULL,
                ADD CONSTRAINT maintenance_sede_rel_id_fk 
                FOREIGN KEY (sede_rel_id) REFERENCES sede(id)
            """)
            print("✓ Agregada columna sede_rel_id a maintenance")
        except Exception as e:
            print(f"⚠ sede_rel_id ya existe o error: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE maintenance 
                ADD COLUMN subdependencia_id bigint NULL,
                ADD CONSTRAINT maintenance_subdependencia_id_fk 
                FOREIGN KEY (subdependencia_id) REFERENCES subdependencia(id)
            """)
            print("✓ Agregada columna subdependencia_id a maintenance")
        except Exception as e:
            print(f"⚠ subdependencia_id ya existe o error: {e}")
        
        print("\n✅ Proceso completado")

if __name__ == "__main__":
    add_missing_columns()
