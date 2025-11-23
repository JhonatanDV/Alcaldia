from django.db import migrations, connection


def create_missing(apps, schema_editor):
    """Create missing hierarchy tables/columns if they don't exist.

    This migration is defensive: it will not fail if objects already exist.
    """
    with connection.cursor() as cursor:
        # Create subdependencia table if missing
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'subdependencia';")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                CREATE TABLE subdependencia (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    codigo VARCHAR(50) NULL,
                    responsable VARCHAR(255) NULL,
                    activo TINYINT(1) NOT NULL DEFAULT 1,
                    created_at DATETIME(6) NOT NULL,
                    updated_at DATETIME(6) NOT NULL,
                    dependencia_id BIGINT NOT NULL,
                    CONSTRAINT fk_subdependencia_dependencia FOREIGN KEY (dependencia_id) REFERENCES dependencia (id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            # Add unique constraint on (dependencia, nombre)
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS subdependencia_dependencia_nombre_uniq ON subdependencia (dependencia_id, nombre);")
            except Exception:
                # MySQL older versions don't support IF NOT EXISTS for CREATE INDEX; ignore if fails
                try:
                    cursor.execute("CREATE UNIQUE INDEX subdependencia_dependencia_nombre_uniq ON subdependencia (dependencia_id, nombre);")
                except Exception:
                    pass

        # Ensure dependencia.sede_id exists and FK present
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'dependencia' AND column_name = 'sede_id';")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE dependencia ADD COLUMN sede_id BIGINT NULL;")
            try:
                cursor.execute("ALTER TABLE dependencia ADD CONSTRAINT fk_dependencia_sede FOREIGN KEY (sede_id) REFERENCES sede (id) ON DELETE CASCADE;")
            except Exception:
                # ignore if FK creation fails
                pass

        # Ensure subdependencia_id exists on equipment and maintenance and add FK
        for table in ('equipment', 'maintenance'):
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = %s AND column_name = 'subdependencia_id';",
                [table],
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN subdependencia_id BIGINT NULL;")
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD CONSTRAINT fk_{table}_subdependencia FOREIGN KEY (subdependencia_id) REFERENCES subdependencia (id) ON DELETE SET NULL;")
                except Exception:
                    pass


def noop_reverse(apps, schema_editor):
    # Reverse is intentionally a no-op because we don't want to drop columns/tables automatically
    return


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_missing, noop_reverse),
    ]
