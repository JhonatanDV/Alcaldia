"""
Comando de gestión Django para verificar y convertir tablas a InnoDB.
Uso: python manage.py ensure_innodb [--convert]
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Verifica que todas las tablas usen el motor InnoDB y opcionalmente las convierte'

    def add_arguments(self, parser):
        parser.add_argument(
            '--convert',
            action='store_true',
            help='Convierte las tablas que no sean InnoDB a InnoDB',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Solo verifica sin convertir (por defecto)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Verificación de Motor de Almacenamiento ===\n'))

        with connection.cursor() as cursor:
            # Obtener motor por defecto
            cursor.execute("SELECT @@default_storage_engine")
            default_engine = cursor.fetchone()[0]
            self.stdout.write(f"Motor por defecto: {default_engine}")
            
            if default_engine != 'InnoDB':
                self.stdout.write(self.style.WARNING(
                    f'⚠️  El motor por defecto no es InnoDB. Se recomienda configurar InnoDB como motor por defecto en MySQL.'
                ))
            else:
                self.stdout.write(self.style.SUCCESS('✓ Motor por defecto es InnoDB'))

            # Listar todas las tablas y sus motores
            cursor.execute("""
                SELECT TABLE_NAME, ENGINE, TABLE_ROWS
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_NAME
            """)
            
            tables = cursor.fetchall()
            non_innodb_tables = []
            
            self.stdout.write('\n--- Estado de las tablas ---')
            for table_name, engine, rows in tables:
                if engine == 'InnoDB':
                    self.stdout.write(self.style.SUCCESS(f'✓ {table_name}: {engine} ({rows} filas)'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ {table_name}: {engine} ({rows} filas) - NO es InnoDB'))
                    non_innodb_tables.append(table_name)

            # Resumen
            total_tables = len(tables)
            innodb_tables = total_tables - len(non_innodb_tables)
            
            self.stdout.write(f'\n--- Resumen ---')
            self.stdout.write(f'Total de tablas: {total_tables}')
            self.stdout.write(self.style.SUCCESS(f'Tablas InnoDB: {innodb_tables}'))
            if non_innodb_tables:
                self.stdout.write(self.style.ERROR(f'Tablas NO InnoDB: {len(non_innodb_tables)}'))

            # Convertir si se especificó --convert
            if options['convert'] and non_innodb_tables:
                self.stdout.write(self.style.WARNING(
                    f'\n⚠️  Se convertirán {len(non_innodb_tables)} tabla(s) a InnoDB.'
                ))
                self.stdout.write(self.style.WARNING(
                    'IMPORTANTE: Se recomienda hacer un backup de la base de datos antes de continuar.'
                ))
                
                confirm = input('¿Desea continuar? (sí/no): ')
                if confirm.lower() not in ['sí', 'si', 's', 'yes', 'y']:
                    self.stdout.write(self.style.WARNING('Operación cancelada.'))
                    return

                self.stdout.write('\n--- Convirtiendo tablas ---')
                for table_name in non_innodb_tables:
                    try:
                        self.stdout.write(f'Convirtiendo {table_name}...', ending=' ')
                        cursor.execute(f'ALTER TABLE {table_name} ENGINE=InnoDB')
                        self.stdout.write(self.style.SUCCESS('✓ OK'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))

                # Verificar después de la conversión
                self.stdout.write('\n--- Verificación post-conversión ---')
                cursor.execute("""
                    SELECT TABLE_NAME, ENGINE
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME IN ({})
                """.format(','.join([f"'{t}'" for t in non_innodb_tables])))
                
                for table_name, engine in cursor.fetchall():
                    if engine == 'InnoDB':
                        self.stdout.write(self.style.SUCCESS(f'✓ {table_name}: {engine}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'✗ {table_name}: {engine} - Falló la conversión'))

                self.stdout.write(self.style.SUCCESS('\n✓ Proceso de conversión completado.'))
            
            elif options['convert'] and not non_innodb_tables:
                self.stdout.write(self.style.SUCCESS('\n✓ Todas las tablas ya usan InnoDB. No se requiere conversión.'))
            
            elif not options['convert'] and non_innodb_tables:
                self.stdout.write(self.style.WARNING(
                    f'\n⚠️  Para convertir las tablas a InnoDB, ejecute: python manage.py ensure_innodb --convert'
                ))
            else:
                self.stdout.write(self.style.SUCCESS('\n✓ Todas las tablas usan InnoDB correctamente.'))
