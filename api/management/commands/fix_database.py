from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Agrega las columnas faltantes para sedes, dependencias y subdependencias'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Agregar columnas legacy a equipment si no existen
            self.stdout.write("Verificando columnas legacy en equipment...")
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD COLUMN dependencia VARCHAR(255) NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna dependencia (legacy) a equipment'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ dependencia: {str(e)[:100]}'))
            
            # Verificar y agregar columnas faltantes en equipment
            self.stdout.write("\nAgregando columnas a equipment...")
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD COLUMN dependencia_rel_id BIGINT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna dependencia_rel_id a equipment'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ dependencia_rel_id: {str(e)[:100]}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD CONSTRAINT equipment_dependencia_rel_id_fk 
                    FOREIGN KEY (dependencia_rel_id) REFERENCES dependencia(id)
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregado FK dependencia_rel_id'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ FK dependencia_rel_id ya existe'))
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD COLUMN sede_rel_id BIGINT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna sede_rel_id a equipment'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ sede_rel_id: {str(e)[:100]}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD CONSTRAINT equipment_sede_rel_id_fk 
                    FOREIGN KEY (sede_rel_id) REFERENCES sede(id)
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregado FK sede_rel_id'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ FK sede_rel_id ya existe'))
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD COLUMN subdependencia_id BIGINT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna subdependencia_id a equipment'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ subdependencia_id: {str(e)[:100]}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE equipment 
                    ADD CONSTRAINT equipment_subdependencia_id_fk 
                    FOREIGN KEY (subdependencia_id) REFERENCES subdependencia(id)
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregado FK subdependencia_id'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ FK subdependencia_id ya existe'))
            
            # Verificar y agregar columnas faltantes en maintenance
            self.stdout.write("\nAgregando columnas a maintenance...")
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance 
                    ADD COLUMN dependencia_rel_id BIGINT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna dependencia_rel_id a maintenance'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ dependencia_rel_id: {str(e)[:100]}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance 
                    ADD CONSTRAINT maintenance_dependencia_rel_id_fk 
                    FOREIGN KEY (dependencia_rel_id) REFERENCES dependencia(id)
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregado FK dependencia_rel_id'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ FK dependencia_rel_id ya existe'))
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance 
                    ADD COLUMN sede_rel_id BIGINT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna sede_rel_id a maintenance'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ sede_rel_id: {str(e)[:100]}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance 
                    ADD CONSTRAINT maintenance_sede_rel_id_fk 
                    FOREIGN KEY (sede_rel_id) REFERENCES sede(id)
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregado FK sede_rel_id'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ FK sede_rel_id ya existe'))
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance 
                    ADD COLUMN subdependencia_id BIGINT NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregada columna subdependencia_id a maintenance'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ subdependencia_id: {str(e)[:100]}'))
            
            try:
                cursor.execute("""
                    ALTER TABLE maintenance 
                    ADD CONSTRAINT maintenance_subdependencia_id_fk 
                    FOREIGN KEY (subdependencia_id) REFERENCES subdependencia(id)
                """)
                self.stdout.write(self.style.SUCCESS('✓ Agregado FK subdependencia_id'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ FK subdependencia_id ya existe'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Proceso completado'))
